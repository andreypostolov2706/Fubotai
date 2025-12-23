"""
GPT-Image 1.5 — Клавиатуры
"""
from .config import (
    SERVICE_ID,
    IMAGE_SIZES,
    QUALITY_OPTIONS,
    BACKGROUND_OPTIONS,
    OUTPUT_FORMATS,
)


def _btn(text: str, callback: str) -> dict:
    """Создать кнопку"""
    return {"text": text, "callback_data": callback}


def _cb(action: str, *params) -> str:
    """Создать callback_data для сервиса"""
    parts = [f"service:{SERVICE_ID}:{action}"]
    if params:
        parts.extend(str(p) for p in params)
    return ":".join(parts)


# ==================== ГЛАВНОЕ МЕНЮ ====================

def main_menu_keyboard() -> list:
    """Главное меню сервиса"""
    return [
        [_btn("✨ Создать изображение", _cb("generate"))],
        [_btn("🖼 Редактировать фото", _cb("edit"))],
        [_btn("📂 Мои генерации", _cb("history"))],
        [_btn("⚙️ Настройки", _cb("settings"))],
        [_btn("◀️ Главное меню", "main_menu")],
    ]


# ==================== ГЕНЕРАЦИЯ ====================

def confirm_keyboard(action: str = "generate") -> list:
    """Клавиатура подтверждения генерации"""
    return [
        [_btn("🎨 Генерировать", _cb("confirm", action))],
        [_btn("⚙️ Изменить", _cb("edit_params", action))],
        [_btn("❌ Отмена", _cb("cancel"))],
    ]


def edit_params_keyboard(action: str = "generate") -> list:
    """Клавиатура изменения параметров"""
    return [
        [_btn("🎚 Качество", _cb("set_param", "quality", action)), _btn("📐 Размер", _cb("set_param", "size", action))],
        [_btn("🖼 Фон", _cb("set_param", "background", action)), _btn("📁 Формат", _cb("set_param", "format", action))],
        [_btn("◀️ Назад", _cb("back_to_confirm", action))],
    ]


def quality_keyboard(current: str, action: str = "generate") -> list:
    """Клавиатура выбора качества"""
    keyboard = []
    for key, name in QUALITY_OPTIONS.items():
        mark = "✓ " if key == current else ""
        keyboard.append([_btn(f"{mark}{name}", _cb("quality", key, action))])
    keyboard.append([_btn("◀️ Назад", _cb("edit_params", action))])
    return keyboard


def size_keyboard(current: str, action: str = "generate") -> list:
    """Клавиатура выбора размера"""
    keyboard = []
    for key, name in IMAGE_SIZES.items():
        mark = "✓ " if key == current else ""
        keyboard.append([_btn(f"{mark}{name}", _cb("size", key, action))])
    keyboard.append([_btn("◀️ Назад", _cb("edit_params", action))])
    return keyboard


def background_keyboard(current: str, action: str = "generate") -> list:
    """Клавиатура выбора фона"""
    keyboard = []
    for key, name in BACKGROUND_OPTIONS.items():
        mark = "✓ " if key == current else ""
        keyboard.append([_btn(f"{mark}{name}", _cb("background", key, action))])
    keyboard.append([_btn("◀️ Назад", _cb("edit_params", action))])
    return keyboard


def format_keyboard(current: str, action: str = "generate") -> list:
    """Клавиатура выбора формата"""
    keyboard = []
    for key, name in OUTPUT_FORMATS.items():
        mark = "✓ " if key == current else ""
        keyboard.append([_btn(f"{mark}{name}", _cb("format", key, action))])
    keyboard.append([_btn("◀️ Назад", _cb("edit_params", action))])
    return keyboard


# ==================== НАСТРОЙКИ ====================

def settings_keyboard() -> list:
    """Клавиатура настроек"""
    return [
        [_btn("🎚 Качество", _cb("settings", "quality")), _btn("📐 Размер", _cb("settings", "size"))],
        [_btn("🖼 Фон", _cb("settings", "background")), _btn("📁 Формат", _cb("settings", "format"))],
        [_btn("◀️ Назад", _cb("main"))],
    ]


def settings_quality_keyboard(current: str) -> list:
    """Клавиатура выбора качества в настройках"""
    keyboard = []
    for key, name in QUALITY_OPTIONS.items():
        mark = "✓ " if key == current else ""
        keyboard.append([_btn(f"{mark}{name}", _cb("set", "quality", key))])
    keyboard.append([_btn("◀️ Назад", _cb("settings"))])
    return keyboard


def settings_size_keyboard(current: str) -> list:
    """Клавиатура выбора размера в настройках"""
    keyboard = []
    for key, name in IMAGE_SIZES.items():
        mark = "✓ " if key == current else ""
        keyboard.append([_btn(f"{mark}{name}", _cb("set", "size", key))])
    keyboard.append([_btn("◀️ Назад", _cb("settings"))])
    return keyboard


def settings_background_keyboard(current: str) -> list:
    """Клавиатура выбора фона в настройках"""
    keyboard = []
    for key, name in BACKGROUND_OPTIONS.items():
        mark = "✓ " if key == current else ""
        keyboard.append([_btn(f"{mark}{name}", _cb("set", "background", key))])
    keyboard.append([_btn("◀️ Назад", _cb("settings"))])
    return keyboard


def settings_format_keyboard(current: str) -> list:
    """Клавиатура выбора формата в настройках"""
    keyboard = []
    for key, name in OUTPUT_FORMATS.items():
        mark = "✓ " if key == current else ""
        keyboard.append([_btn(f"{mark}{name}", _cb("set", "format", key))])
    keyboard.append([_btn("◀️ Назад", _cb("settings"))])
    return keyboard


# ==================== РЕЗУЛЬТАТ ====================

def result_keyboard(generation_id: int) -> list:
    """Клавиатура после генерации"""
    return [
        [_btn("✏️ Изменить промпт", _cb("generate"))],
        [_btn("📥 Файл не пришёл", _cb("resend", generation_id))],
        [_btn("◀️ Назад", _cb("main"))],
    ]


# ==================== ИСТОРИЯ ====================

def history_keyboard(page: int, total_pages: int) -> list:
    """Клавиатура истории с пагинацией"""
    keyboard = []
    
    nav_row = []
    if page > 1:
        nav_row.append(_btn("◀️", _cb("history", "page", page - 1)))
    nav_row.append(_btn(f"{page}/{total_pages}", "noop"))
    if page < total_pages:
        nav_row.append(_btn("▶️", _cb("history", "page", page + 1)))
    
    if nav_row:
        keyboard.append(nav_row)
    
    keyboard.append([_btn("◀️ Назад", _cb("main"))])
    
    return keyboard


def history_item_keyboard(generation_id: int) -> list:
    """Клавиатура для элемента истории"""
    return [
        [_btn("🔄 Повторить", _cb("repeat", generation_id)), _btn("🗑 Удалить", _cb("delete", generation_id))],
        [_btn("◀️ К истории", _cb("history"))],
    ]


# ==================== ОБЩИЕ ====================

def cancel_keyboard() -> list:
    """Клавиатура отмены"""
    return [
        [_btn("❌ Отмена", _cb("cancel"))],
    ]


def back_keyboard(callback: str = "main") -> list:
    """Клавиатура с кнопкой назад"""
    return [
        [_btn("◀️ Назад", _cb(callback))],
    ]
