"""
Top Up Command Handler
"""
from telegram import Update
from telegram.ext import ContextTypes

from core.platform.telegram.utils import get_or_create_user, get_user_language
from .topup import show_topup_menu


async def topup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /topup command - quick access to balance top-up"""
    telegram_user = update.effective_user
    user_id = await get_or_create_user(telegram_user.id, telegram_user)
    lang = await get_user_language(user_id)
    
    # Create a mock query object for show_topup_menu
    class MockQuery:
        def __init__(self, message):
            self.message = message
        
        async def edit_message_text(self, text, reply_markup=None, parse_mode=None):
            await self.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
    
    mock_query = MockQuery(update.message)
    await show_topup_menu(mock_query, user_id, lang)
