"""
Kling Video v2.6 — Клавиатуры
"""
from .config import (
    SERVICE_ID,
    DURATION_OPTIONS,
    ASPECT_RATIOS,
    AUDIO_OPTIONS,
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
        [_btn("✨ Текст → Видео", _cb("generate"))],
        [_btn("🖼 Фото → Видео", _cb("edit"))],
        [_btn("⚙️ Настройки", _cb("settings"))],
        [_btn("◀️ Назад", "main_menu")],
    ]


# ==================== ГЕНЕРАЦИЯ ====================

def confirm_keyboard(action: str = "generate") -> list:
    """Клавиатура подтверждения генерации"""
    return [
        [_btn("✅ Генерировать", _cb("confirm", action))],
        [_btn("✏️ Изменить промпт", _cb("generate"))],
        [_btn("⚙️ Настройки", _cb("edit_params", action))],
        [_btn("❌ Отмена", _cb("cancel"))],
    ]


def edit_params_keyboard(action: str = "generate") -> list:
    """Клавиатура изменения параметров"""
    return [
        [_btn("⏱ Длительность", _cb("set_param", "duration", action)), _btn("📐 Соотношение", _cb("set_param", "aspect", action))],
        [_btn("🔊 Аудио", _cb("set_param", "audio", action))],
        [_btn("◀️ Назад", _cb("back_to_confirm", action))],
    ]


def duration_keyboard(current: str, action: str = "generate") -> list:
    """Клавиатура выбора длительности"""
    keyboard = []
    for key, name in DURATION_OPTIONS.items():
        mark = "✓ " if key == current else ""
        keyboard.append([_btn(f"{mark}{name}", _cb("duration", key, action))])
    keyboard.append([_btn("◀️ Назад", _cb("edit_params", action))])
    return keyboard


def aspect_ratio_keyboard(current: str, action: str = "generate") -> list:
    """Клавиатура выбора соотношения сторон"""
    keyboard = []
    for key, name in ASPECT_RATIOS.items():
        mark = "✓ " if key == current else ""
        keyboard.append([_btn(f"{mark}{name}", _cb("aspect", key, action))])
    keyboard.append([_btn("◀️ Назад", _cb("edit_params", action))])
    return keyboard


def audio_keyboard(current: str, action: str = "generate") -> list:
    """Клавиатура выбора аудио"""
    keyboard = []
    for key, name in AUDIO_OPTIONS.items():
        mark = "✓ " if key == current else ""
        keyboard.append([_btn(f"{mark}{name}", _cb("audio", key, action))])
    keyboard.append([_btn("◀️ Назад", _cb("edit_params", action))])
    return keyboard


# ==================== НАСТРОЙКИ ====================

def settings_keyboard() -> list:
    """Клавиатура настроек"""
    return [
        [_btn("⏱ Длительность", _cb("settings", "duration")), _btn("📐 Соотношение", _cb("settings", "aspect"))],
        [_btn("🔊 Аудио", _cb("settings", "audio"))],
        [_btn("◀️ Назад", _cb("main"))],
    ]


def settings_duration_keyboard(current: str) -> list:
    """Клавиатура выбора длительности в настройках"""
    keyboard = []
    for key, name in DURATION_OPTIONS.items():
        mark = "✓ " if key == current else ""
        keyboard.append([_btn(f"{mark}{name}", _cb("set", "duration", key))])
    keyboard.append([_btn("◀️ Назад", _cb("settings"))])
    return keyboard


def settings_aspect_keyboard(current: str) -> list:
    """Клавиатура выбора соотношения в настройках"""
    keyboard = []
    for key, name in ASPECT_RATIOS.items():
        mark = "✓ " if key == current else ""
        keyboard.append([_btn(f"{mark}{name}", _cb("set", "aspect", key))])
    keyboard.append([_btn("◀️ Назад", _cb("settings"))])
    return keyboard


def settings_audio_keyboard(current: str) -> list:
    """Клавиатура выбора аудио в настройках"""
    keyboard = []
    for key, name in AUDIO_OPTIONS.items():
        mark = "✓ " if key == current else ""
        keyboard.append([_btn(f"{mark}{name}", _cb("set", "audio", key))])
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
