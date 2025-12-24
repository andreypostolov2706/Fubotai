"""
Documents Handler - Terms and Privacy Policy
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from core.platform.telegram.utils import get_or_create_user, get_user_language


async def documents_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /doc command - show documents menu"""
    telegram_user = update.effective_user
    user_id = await get_or_create_user(telegram_user.id, telegram_user)
    
    text = (
        "📚 <b>Документы FuBotai</b>\n\n"
        "Здесь вы можете ознакомиться с нашими документами:\n\n"
        "📄 <b>Пользовательское соглашение</b>\n"
        "Условия использования бота и сервисов\n\n"
        "🔒 <b>Политика конфиденциальности</b>\n"
        "Как мы обрабатываем ваши данные\n\n"
        "<i>Выберите документ для просмотра:</i>"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "📄 Пользовательское соглашение",
            url="https://telegra.ph/Politika-konfidencialnosti-AIFull-12-24"
        )],
        [InlineKeyboardButton(
            "🔒 Политика конфиденциальности",
            url="https://telegra.ph/Polzovatelskoe-soglashenie-AIFull-12-24"
        )],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")],
    ])
    
    await update.message.reply_text(
        text,
        reply_markup=keyboard,
        parse_mode="HTML",
        disable_web_page_preview=True
    )


async def documents_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle documents callback"""
    query = update.callback_query
    await query.answer()
    
    telegram_user = update.effective_user
    user_id = await get_or_create_user(telegram_user.id, telegram_user)
    
    text = (
        "📚 <b>Документы FuBotai</b>\n\n"
        "Здесь вы можете ознакомиться с нашими документами:\n\n"
        "📄 <b>Пользовательское соглашение</b>\n"
        "Условия использования бота и сервисов\n\n"
        "🔒 <b>Политика конфиденциальности</b>\n"
        "Как мы обрабатываем ваши данные\n\n"
        "<i>Выберите документ для просмотра:</i>"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "📄 Пользовательское соглашение",
            url="https://telegra.ph/Politika-konfidencialnosti-AIFull-12-24"
        )],
        [InlineKeyboardButton(
            "🔒 Политика конфиденциальности",
            url="https://telegra.ph/Polzovatelskoe-soglashenie-AIFull-12-24"
        )],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")],
    ])
    
    await query.edit_message_text(
        text,
        reply_markup=keyboard,
        parse_mode="HTML",
        disable_web_page_preview=True
    )
