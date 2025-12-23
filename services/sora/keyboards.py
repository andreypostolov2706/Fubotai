"""
Sora 2 Service Keyboards
"""
from .config import SERVICE_ID, ASPECT_RATIOS, DURATIONS


def _btn(text: str, callback_data: str) -> dict:
    return {"text": text, "callback_data": callback_data}


def _cb(action: str, params: str = "") -> str:
    if params:
        return f"service:{SERVICE_ID}:{action}:{params}"
    return f"service:{SERVICE_ID}:{action}"


def main_menu_keyboard() -> list:
    """Главное меню сервиса"""
    return [
        [_btn("✨ Создать видео", _cb("generate"))],
        [_btn("📷 Анимировать фото", _cb("image_to_video"))],
        [_btn("📂 Мои генерации", _cb("history"))],
        [_btn("⚙️ Настройки", _cb("settings"))],
        [_btn("◀️ Главное меню", "main_menu")],
    ]


def back_to_main_keyboard() -> list:
    """Кнопка возврата в главное меню сервиса"""
    return [
        [_btn("◀️ Назад", _cb("main"))],
    ]


def cancel_keyboard() -> list:
    """Кнопка отмены"""
    return [
        [_btn("❌ Отмена", _cb("cancel"))],
    ]


def confirm_generation_keyboard() -> list:
    """Подтверждение генерации"""
    return [
        [_btn("✅ Создать", _cb("confirm"))],
        [_btn("📐 Соотношение", _cb("change_aspect"))],
        [_btn("⏱ Длительность", _cb("change_duration"))],
        [_btn("❌ Отмена", _cb("cancel"))],
    ]


def aspect_ratio_keyboard(current: str = "16:9") -> list:
    """Выбор соотношения сторон"""
    keyboard = []
    for ratio in ASPECT_RATIOS:
        mark = "✅ " if ratio == current else ""
        keyboard.append([_btn(f"{mark}{ratio}", _cb("set_aspect", ratio))])
    keyboard.append([_btn("◀️ Назад", _cb("back_to_confirm"))])
    return keyboard


def duration_keyboard(current: int = 4) -> list:
    """Выбор длительности"""
    keyboard = []
    for dur in DURATIONS:
        mark = "✅ " if dur == current else ""
        keyboard.append([_btn(f"{mark}{dur} сек", _cb("set_duration", str(dur)))])
    keyboard.append([_btn("◀️ Назад", _cb("back_to_confirm"))])
    return keyboard


def settings_keyboard() -> list:
    """Меню настроек"""
    return [
        [_btn("📐 Соотношение сторон", _cb("settings_aspect"))],
        [_btn("⏱ Длительность", _cb("settings_duration"))],
        [_btn("◀️ Назад", _cb("main"))],
    ]


def settings_aspect_keyboard(current: str = "16:9") -> list:
    """Выбор соотношения в настройках"""
    keyboard = []
    for ratio in ASPECT_RATIOS:
        mark = "✅ " if ratio == current else ""
        keyboard.append([_btn(f"{mark}{ratio}", _cb("save_aspect", ratio))])
    keyboard.append([_btn("◀️ Назад", _cb("settings"))])
    return keyboard


def settings_duration_keyboard(current: int = 4) -> list:
    """Выбор длительности в настройках"""
    keyboard = []
    for dur in DURATIONS:
        mark = "✅ " if dur == current else ""
        keyboard.append([_btn(f"{mark}{dur} сек", _cb("save_duration", str(dur)))])
    keyboard.append([_btn("◀️ Назад", _cb("settings"))])
    return keyboard


def history_keyboard(generations: list, page: int = 0, per_page: int = 5) -> list:
    """Клавиатура истории генераций"""
    keyboard = []
    
    start = page * per_page
    end = start + per_page
    page_items = generations[start:end]
    
    for gen in page_items:
        prompt_short = gen.get("prompt", "")[:30] + "..." if len(gen.get("prompt", "")) > 30 else gen.get("prompt", "")
        keyboard.append([_btn(f"🎬 {prompt_short}", _cb("view", str(gen.get("id", 0))))])
    
    # Пагинация
    nav_row = []
    if page > 0:
        nav_row.append(_btn("◀️", _cb("history", str(page - 1))))
    if end < len(generations):
        nav_row.append(_btn("▶️", _cb("history", str(page + 1))))
    if nav_row:
        keyboard.append(nav_row)
    
    keyboard.append([_btn("◀️ Назад", _cb("main"))])
    return keyboard


def generation_result_keyboard(generation_id: int) -> list:
    """Клавиатура результата генерации"""
    return [
        [_btn("🔄 Повторить", _cb("retry", str(generation_id)))],
        [_btn("◀️ В меню", _cb("main"))],
    ]
