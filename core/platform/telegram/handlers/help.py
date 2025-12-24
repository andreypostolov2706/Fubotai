"""
Help Handler
"""
from telegram import Update
from telegram.ext import ContextTypes

from core.locales import t
from core.platform.telegram.utils import (
    get_or_create_user, 
    get_user_language,
    build_keyboard
)
from core.settings import settings


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    telegram_user = update.effective_user
    user_id = await get_or_create_user(telegram_user.id, telegram_user)
    lang = await get_user_language(user_id)
    
    # Get support username from settings
    support_username = await settings.get("general.support_username") or "@support"
    if not support_username.startswith("@"):
        support_username = f"@{support_username}"
    
    text = t(lang, "HELP.title") + "\n\n"
    text += t(lang, "HELP.description") + f" {support_username}"
    
    keyboard = [
        [{"text": t(lang, "HELP.support"), "url": f"https://t.me/{support_username.lstrip('@')}"}],
        [{"text": t(lang, "COMMON.back"), "callback_data": "main_menu"}]
    ]
    
    await update.message.reply_text(
        text,
        reply_markup=build_keyboard(keyboard),
        parse_mode="HTML"
    )


async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle help callback"""
    query = update.callback_query
    await query.answer()
    
    telegram_user = update.effective_user
    user_id = await get_or_create_user(telegram_user.id, telegram_user)
    lang = await get_user_language(user_id)
    
    # Get support username from settings
    support_username = await settings.get("general.support_username") or "@support"
    if not support_username.startswith("@"):
        support_username = f"@{support_username}"
    
    text = t(lang, "HELP.title") + "\n\n"
    text += t(lang, "HELP.description") + f" {support_username}"
    
    keyboard = [
        [{"text": t(lang, "HELP.support"), "url": f"https://t.me/{support_username.lstrip('@')}"}],
        [{"text": t(lang, "COMMON.back"), "callback_data": "main_menu"}]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=build_keyboard(keyboard),
        parse_mode="HTML"
    )
