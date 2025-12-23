"""
Veo Service — Клавиатуры
"""
from .config import SERVICE_ID, DURATIONS, ASPECT_RATIOS_TEXT, ASPECT_RATIOS_IMAGE, DURATION_NAMES, ASPECT_RATIO_NAMES


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
        [_btn("✨ Создать видео", _cb("generate"))],
        [_btn("📷 Анимировать фото", _cb("image_to_video"))],
        [_btn("📂 Мои генерации", _cb("history"))],
        [_btn("⚙️ Настройки", _cb("settings"))],
        [_btn("◀️ Главное меню", "main_menu")],
    ]


def back_to_main_keyboard() -> list:
    """Кнопка назад в меню сервиса"""
    return [
        [_btn("◀️ Меню Veo", _cb("main"))],
    ]


def cancel_keyboard() -> list:
    """Кнопка отмены"""
    return [
        [_btn("❌ Отмена", _cb("cancel"))],
    ]


# ==================== ГЕНЕРАЦИЯ ====================

def skip_negative_keyboard() -> list:
    """Пропустить негативный промпт"""
    return [
        [_btn("⏭ Пропустить", _cb("skip_negative"))],
        [_btn("❌ Отмена", _cb("cancel"))],
    ]


def confirm_generation_keyboard() -> list:
    """Подтверждение генерации"""
    return [
        [_btn("✅ Создать", _cb("confirm", "create"))],
        [_btn("✏️ Изменить", _cb("confirm", "edit"))],
        [_btn("❌ Отмена", _cb("cancel"))],
    ]


def edit_params_keyboard(mode: str = "text_to_video") -> list:
    """Меню изменения параметров"""
    keyboard = [
        [_btn("📝 Промпт", _cb("edit_param", "prompt"))],
    ]
    
    if mode == "text_to_video":
        keyboard.append([_btn("🚫 Негативный промпт", _cb("edit_param", "negative"))])
    
    keyboard.extend([
        [_btn("⏱ Длительность", _cb("edit_param", "duration"))],
        [_btn("📐 Соотношение", _cb("edit_param", "ratio"))],
    ])
    
    if mode == "text_to_video":
        keyboard.append([_btn("✨ Улучшение промпта", _cb("edit_param", "enhance"))])
    
    keyboard.append([_btn("◀️ Назад к подтверждению", _cb("back_to_confirm"))])
    
    return keyboard


def generation_result_keyboard(generation_id: int, gallery_enabled: bool = False) -> list:
    """Результат генерации"""
    keyboard = [
        [_btn("🔄 Ещё раз", _cb("repeat", generation_id))],
    ]
    
    if gallery_enabled:
        keyboard.append([_btn("📤 Опубликовать", _cb("publish", generation_id))])
    
    keyboard.extend([
        [_btn("✨ Новое видео", _cb("generate"))],
        [_btn("◀️ Меню", _cb("main"))],
    ])
    
    return keyboard


def insufficient_balance_keyboard() -> list:
    """Недостаточно средств"""
    return [
        [_btn("💳 Пополнить", "top_up")],
        [_btn("◀️ Назад", _cb("main"))],
    ]


# ==================== НАСТРОЙКИ ====================

def settings_keyboard() -> list:
    """Меню настроек"""
    return [
        [_btn("⏱ Длительность", _cb("settings", "duration"))],
        [_btn("📐 Соотношение", _cb("settings", "ratio"))],
        [_btn("✨ Улучшение промпта", _cb("settings", "enhance"))],
        [_btn("◀️ Назад", _cb("main"))],
    ]


def duration_keyboard(current: str) -> list:
    """Выбор длительности"""
    keyboard = []
    for duration in DURATIONS:
        mark = " ✓" if duration == current else ""
        name = DURATION_NAMES.get(duration, duration)
        keyboard.append([_btn(f"{name}{mark}", _cb("set", "duration", duration))])
    
    keyboard.append([_btn("◀️ Назад", _cb("settings"))])
    return keyboard


def aspect_ratio_keyboard(current: str, mode: str = "text_to_video") -> list:
    """Выбор соотношения сторон"""
    ratios = ASPECT_RATIOS_IMAGE if mode == "image_to_video" else ASPECT_RATIOS_TEXT
    
    keyboard = []
    for ratio in ratios:
        mark = " ✓" if ratio == current else ""
        name = ASPECT_RATIO_NAMES.get(ratio, ratio)
        # Заменяем : на - для callback
        ratio_cb = ratio.replace(":", "-")
        keyboard.append([_btn(f"{name}{mark}", _cb("set", "ratio", ratio_cb))])
    
    keyboard.append([_btn("◀️ Назад", _cb("settings"))])
    return keyboard


def enhance_keyboard(current: bool) -> list:
    """Выбор улучшения промпта"""
    on_mark = " ✓" if current else ""
    off_mark = " ✓" if not current else ""
    
    return [
        [_btn(f"✅ Включено{on_mark}", _cb("set", "enhance", "true"))],
        [_btn(f"❌ Выключено{off_mark}", _cb("set", "enhance", "false"))],
        [_btn("◀️ Назад", _cb("settings"))],
    ]


# ==================== ИСТОРИЯ ====================

def history_keyboard(page: int, total_pages: int, items: list) -> list:
    """Клавиатура истории"""
    keyboard = []
    
    # Кнопки для каждой генерации
    for item in items:
        keyboard.append([
            _btn(f"🎬 #{item['id']} — {item['date']}", _cb("history", "view", item['id']))
        ])
    
    # Пагинация
    nav_row = []
    if page > 1:
        nav_row.append(_btn("◀️", _cb("history", "page", page - 1)))
    nav_row.append(_btn(f"{page}/{total_pages}", _cb("noop")))
    if page < total_pages:
        nav_row.append(_btn("▶️", _cb("history", "page", page + 1)))
    
    if nav_row:
        keyboard.append(nav_row)
    
    keyboard.append([_btn("◀️ Меню", _cb("main"))])
    
    return keyboard


def view_generation_keyboard(generation_id: int, has_video: bool = True) -> list:
    """Просмотр генерации"""
    keyboard = []
    
    if has_video:
        keyboard.append([_btn("🔄 Повторить", _cb("repeat", generation_id))])
    
    keyboard.extend([
        [_btn("🗑 Удалить", _cb("history", "delete", generation_id))],
        [_btn("◀️ К истории", _cb("history"))],
    ])
    
    return keyboard
