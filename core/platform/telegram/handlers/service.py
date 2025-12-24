"""
Service Handler - Routes callbacks to services
"""
from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes
from loguru import logger
from telegram.error import BadRequest

from core.plugins.registry import service_registry
from core.plugins.base_service import CallbackContext
from core.plugins.core_api import CoreAPI
from core.platform.telegram.utils import (
    get_or_create_user,
    build_keyboard
)
from core.platform.telegram.media_sender import send_photo_robust, send_video_robust


async def _safe_answer_callback(query, text: str | None = None, *, show_alert: bool = False):
    try:
        if text is None:
            await query.answer()
        else:
            await query.answer(text, show_alert=show_alert)
    except BadRequest as e:
        # CallbackQuery has a short lifetime; after long-running operations it may expire.
        logger.debug(f"Could not answer callback query (likely expired): {e}")
    except Exception as e:
        logger.debug(f"Could not answer callback query: {e}")


async def service_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle service callbacks"""
    query = update.callback_query
    
    telegram_user = update.effective_user
    user_id = await get_or_create_user(telegram_user.id, telegram_user)
    
    # Parse callback: service:{service_id}:{action}:{params}
    parts = query.data.split(":")
    if len(parts) < 3:
        await query.answer("Invalid callback", show_alert=True)
        return
    
    service_id = parts[1]
    action = parts[2]
    params = {}
    
    # Парсим все дополнительные параметры
    if len(parts) > 3:
        params["id"] = parts[3]
        params["0"] = parts[3]
    if len(parts) > 4:
        params["1"] = parts[4]
    if len(parts) > 5:
        params["2"] = parts[5]
    
    # Get service
    service = service_registry.get(service_id)
    if not service:
        await _safe_answer_callback(query, "Service not found", show_alert=True)
        return
    
    await _safe_answer_callback(query)
    
    # Build context
    ctx = CallbackContext(
        message_id=query.message.message_id,
        chat_id=query.message.chat_id,
        user_id=user_id,
        bot=context.bot
    )
    
    # Handle callback
    try:
        response = await service.handle_callback(user_id, action, params, ctx)
        
        # Process response
        keyboard = None
        if response.keyboard:
            keyboard = build_keyboard(response.keyboard)
        
        if response.action == "edit":
            try:
                await query.edit_message_text(
                    response.text,
                    reply_markup=keyboard,
                    parse_mode=response.parse_mode
                )
            except Exception as edit_error:
                # Если не удалось отредактировать (например, сообщение с фото), отправляем новое
                logger.debug(f"Could not edit message: {edit_error}, sending new message")
                await _safe_answer_callback(query)
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=response.text,
                    reply_markup=keyboard,
                    parse_mode=response.parse_mode
                )
        elif response.action == "send":
            # Отвечаем на callback чтобы убрать "часики" (может протухнуть на долгих операциях)
            await _safe_answer_callback(query)
            
            # Отправка с медиа
            if response.media_type == "photo":
                media = response.media_file_id or response.media_url
                logger.info(f"Sending photo: {media[:50] if media else 'None'}...")
                if media:
                    await send_photo_robust(
                        context.bot,
                        chat_id=query.message.chat_id,
                        photo=media,
                        caption=response.text,
                        reply_markup=keyboard,
                        parse_mode=response.parse_mode,
                    )
                else:
                    await context.bot.send_message(
                        chat_id=query.message.chat_id,
                        text=response.text,
                        reply_markup=keyboard,
                        parse_mode=response.parse_mode
                    )
            elif response.media_type == "video":
                media = response.media_file_id or response.media_url
                if media:
                    await send_video_robust(
                        context.bot,
                        chat_id=query.message.chat_id,
                        video=media,
                        caption=response.text,
                        reply_markup=keyboard,
                        parse_mode=response.parse_mode,
                    )
                else:
                    await context.bot.send_message(
                        chat_id=query.message.chat_id,
                        text=response.text,
                        reply_markup=keyboard,
                        parse_mode=response.parse_mode
                    )
            else:
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=response.text,
                    reply_markup=keyboard,
                    parse_mode=response.parse_mode
                )
        elif response.action == "answer":
            await _safe_answer_callback(query, response.text, show_alert=response.show_alert)
        
        # Handle state
        if response.set_state:
            api = CoreAPI(service_id)
            await api.set_user_state(user_id, response.set_state, response.state_data)
        elif response.clear_state:
            api = CoreAPI(service_id)
            await api.clear_user_state(user_id)
        
        # Handle redirect
        if response.redirect_to:
            query.data = response.redirect_to
            from .router import callback_router
            await callback_router(update, context)
            
    except Exception as e:
        logger.error(f"Error handling service callback: {e}")
        await _safe_answer_callback(query, "Error occurred", show_alert=True)
