"""
AI Avatar — Клавиатуры
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню сервиса"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎬 Создать видео", callback_data="ai_avatar:generate")],
        [InlineKeyboardButton("📋 История", callback_data="ai_avatar:history")],
        [InlineKeyboardButton("⚙️ Настройки", callback_data="ai_avatar:settings")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")],
    ])


def input_mode_keyboard() -> InlineKeyboardMarkup:
    """Выбор режима ввода (аудио или текст)"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎤 Загрузить аудио", callback_data="ai_avatar:mode:audio")],
        [InlineKeyboardButton("📝 Ввести текст (TTS)", callback_data="ai_avatar:mode:text")],
        [InlineKeyboardButton("❌ Отмена", callback_data="ai_avatar:cancel")],
    ])


def skip_prompt_keyboard() -> InlineKeyboardMarkup:
    """Пропустить ввод промпта"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏭ Пропустить", callback_data="ai_avatar:skip_prompt")],
        [InlineKeyboardButton("❌ Отмена", callback_data="ai_avatar:cancel")],
    ])


def confirmation_keyboard() -> InlineKeyboardMarkup:
    """Подтверждение генерации"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Создать видео", callback_data="ai_avatar:confirm")],
        [InlineKeyboardButton("⚙️ Изменить настройки", callback_data="ai_avatar:settings")],
        [InlineKeyboardButton("❌ Отмена", callback_data="ai_avatar:cancel")],
    ])


def result_keyboard(generation_id: int) -> InlineKeyboardMarkup:
    """Кнопки после генерации"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Создать ещё", callback_data="ai_avatar:generate")],
        [InlineKeyboardButton("📥 Файл не пришёл", callback_data=f"ai_avatar:file_issue:{generation_id}")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")],
    ])


def settings_menu_keyboard() -> InlineKeyboardMarkup:
    """Меню настроек"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎬 Качество видео", callback_data="ai_avatar:settings:quality")],
        [InlineKeyboardButton("🔙 Назад", callback_data="ai_avatar:main")],
    ])


def quality_settings_keyboard(current_quality: str) -> InlineKeyboardMarkup:
    """Настройки качества"""
    buttons = []
    
    qualities = {
        "480p": "480p (Стандарт)",
        "720p": "720p (HD)",
    }
    
    for quality, label in qualities.items():
        if quality == current_quality:
            label = f"✅ {label}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"ai_avatar:set_quality:{quality}")])
    
    buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="ai_avatar:settings")])
    
    return InlineKeyboardMarkup(buttons)


def history_keyboard(page: int = 0, has_more: bool = False) -> InlineKeyboardMarkup:
    """Клавиатура истории с пагинацией"""
    buttons = []
    
    # Навигация по страницам
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"ai_avatar:history:{page-1}"))
    if has_more:
        nav_buttons.append(InlineKeyboardButton("Вперёд ➡️", callback_data=f"ai_avatar:history:{page+1}"))
    
    if nav_buttons:
        buttons.append(nav_buttons)
    
    buttons.append([InlineKeyboardButton("🔙 Главное меню", callback_data="ai_avatar:main")])
    
    return InlineKeyboardMarkup(buttons)


def history_item_keyboard(generation_id: int) -> InlineKeyboardMarkup:
    """Кнопки для элемента истории"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📥 Скачать", callback_data=f"ai_avatar:download:{generation_id}")],
        [InlineKeyboardButton("🔄 Повторить", callback_data=f"ai_avatar:repeat:{generation_id}")],
        [InlineKeyboardButton("🔙 К истории", callback_data="ai_avatar:history")],
    ])


def cancel_keyboard() -> InlineKeyboardMarkup:
    """Кнопка отмены"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Отмена", callback_data="ai_avatar:cancel")],
    ])


def back_to_main_keyboard() -> InlineKeyboardMarkup:
    """Возврат в главное меню"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Главное меню", callback_data="ai_avatar:main")],
    ])
