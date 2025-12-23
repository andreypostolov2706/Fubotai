"""
Main Menu Keyboard
"""
from core.locales import t
from core.config import config
from core.plugins.registry import service_registry
from core.plugins.base_service import MenuItem, UserServiceDTO
from core.platform.telegram.utils import build_keyboard, get_user_telegram_id
from loguru import logger


async def main_menu_kb(user_id: int, lang: str = "ru"):
    """
    Build main menu keyboard.
    
    Порядок:
    1. Nano Banano (order=10)
    2. Veo (order=20)
    3. Пополнить (order=100)
    4. Партнёрская программа (order=200)
    5. Помощь (order=400)
    
    Кнопки в 2 ряда.
    """
    # Base menu items (без промокода — он есть в пополнении)
    menu_items: list[MenuItem] = [
        MenuItem(
            text=t(lang, "MAIN_MENU.top_up"), 
            callback="top_up", 
            order=100
        ),
        MenuItem(
            text=t(lang, "MAIN_MENU.partner"), 
            callback="partner", 
            order=200
        ),
        MenuItem(
            text=t(lang, "MAIN_MENU.help"), 
            callback="help", 
            order=400
        ),
    ]
    
    # Add service menu items
    for service in service_registry.get_active():
        try:
            user_data = UserServiceDTO()  # TODO: load from DB
            service_items = service.get_user_menu_items(user_id, user_data)
            menu_items.extend(service_items)
        except Exception as e:
            logger.error(f"Error getting menu items from {service.info.id}: {e}")
    
    # Sort by order
    menu_items.sort(key=lambda x: x.order)
    
    # Build keyboard in 2 columns
    keyboard = []
    row = []
    for item in menu_items:
        if item.visible:
            btn_text = item.text
            if item.badge:
                btn_text += f" {item.badge}"
            row.append({"text": btn_text, "callback_data": item.callback})
            
            if len(row) == 2:
                keyboard.append(row)
                row = []
    
    # Add remaining button if odd number
    if row:
        keyboard.append(row)
    
    # Add admin buttons if admin
    telegram_id = await get_user_telegram_id(user_id)
    if telegram_id and config.is_admin(telegram_id):
        keyboard.append([
            {"text": "⚙️ Глобальные настройки", "callback_data": "global_settings"},
            {"text": "🔧 Админ-панель", "callback_data": "admin"},
        ])
    
    return build_keyboard(keyboard)
