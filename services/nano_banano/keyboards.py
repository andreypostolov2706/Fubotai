"""
Nano Banano — Клавиатуры
"""
from .config import SERVICE_ID, ASPECT_RATIOS, OUTPUT_FORMATS, RESOLUTIONS


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

def cancel_keyboard() -> list:
    """Кнопка отмены"""
    return [
        [_btn("❌ Отмена", _cb("cancel"))],
    ]


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


def edit_params_keyboard() -> list:
    """Меню изменения параметров"""
    return [
        [_btn("📝 Промпт", _cb("edit_param", "prompt"))],
        [_btn("🚫 Негативный промпт", _cb("edit_param", "negative"))],
        [_btn("🤖 Модель", _cb("edit_param", "model"))],
        [_btn("📐 Размер", _cb("edit_param", "ratio"))],
        [_btn("🖼 Формат", _cb("edit_param", "format"))],
        [_btn("📊 Разрешение", _cb("edit_param", "resolution"))],
        [_btn("◀️ Назад к подтверждению", _cb("back_to_confirm"))],
    ]


def generation_result_keyboard(generation_id: int, gallery_enabled: bool = False) -> list:
    """Результат генерации"""
    keyboard = [
        [_btn("🔄 Ещё раз", _cb("repeat", generation_id))],
    ]
    
    if gallery_enabled:
        keyboard.append([_btn("📤 В галерею", _cb("gallery", "confirm", generation_id))])
    
    keyboard.append([_btn("◀️ Меню", _cb("main"))])
    
    return keyboard


def insufficient_balance_keyboard() -> list:
    """Недостаточно средств"""
    return [
        [_btn("💳 Пополнить", "top_up")],
        [_btn("◀️ Назад", _cb("main"))],
    ]


# ==================== РЕДАКТИРОВАНИЕ ФОТО ====================

def images_received_keyboard() -> list:
    """Получены фото"""
    return [
        [_btn("📷 Добавить ещё", _cb("add_more_images"))],
        [_btn("✅ Готово", _cb("images_done"))],
        [_btn("❌ Отмена", _cb("cancel"))],
    ]


# ==================== НАСТРОЙКИ ====================

def settings_keyboard() -> list:
    """Меню настроек"""
    return [
        [_btn("🤖 Модель", _cb("settings", "model"))],
        [_btn("📐 Размер", _cb("settings", "ratio"))],
        [_btn("🖼 Формат", _cb("settings", "format"))],
        [_btn("📊 Разрешение", _cb("settings", "resolution"))],
        [_btn("◀️ Назад", _cb("main"))],
    ]


def model_selection_keyboard(current: str) -> list:
    """Выбор модели"""
    models = [
        ("nano_banana", "Nano Banana"),
        ("nano_banana_pro", "Nano Banana Pro"),
    ]
    
    keyboard = []
    for model_id, model_name in models:
        mark = " ✓" if model_id == current else ""
        keyboard.append([_btn(f"{model_name}{mark}", _cb("set", "model", model_id))])
    
    keyboard.append([_btn("◀️ Назад", _cb("settings"))])
    return keyboard


def aspect_ratio_keyboard(current: str) -> list:
    """Выбор размера"""
    ratios = list(ASPECT_RATIOS.keys())
    
    # Разбиваем на ряды по 3
    keyboard = []
    row = []
    for ratio in ratios:
        mark = " ✓" if ratio == current else ""
        row.append(_btn(f"{ratio}{mark}", _cb("set", "ratio", ratio.replace(":", "-"))))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    keyboard.append([_btn("◀️ Назад", _cb("settings"))])
    return keyboard


def format_keyboard(current: str) -> list:
    """Выбор формата"""
    keyboard = []
    row = []
    for fmt in OUTPUT_FORMATS:
        mark = " ✓" if fmt == current else ""
        row.append(_btn(f"{fmt.upper()}{mark}", _cb("set", "format", fmt)))
    keyboard.append(row)
    
    keyboard.append([_btn("◀️ Назад", _cb("settings"))])
    return keyboard


def resolution_keyboard(current: str, is_pro: bool) -> list:
    """Выбор разрешения"""
    keyboard = []
    
    if is_pro:
        row = []
        for res in RESOLUTIONS:
            mark = " ✓" if res == current else ""
            row.append(_btn(f"{res}{mark}", _cb("set", "resolution", res)))
        keyboard.append(row)
    else:
        keyboard.append([_btn("⚠️ Только для Nano Banana Pro", _cb("settings"))])
    
    keyboard.append([_btn("◀️ Назад", _cb("settings"))])
    return keyboard


# ==================== ИСТОРИЯ ====================

def history_keyboard(page: int, total_pages: int, generations: list) -> list:
    """Список генераций с пагинацией"""
    keyboard = []
    
    # Превью генераций (по 3 в ряд)
    row = []
    for i, gen in enumerate(generations):
        row.append(_btn(f"🖼 {i + 1}", _cb("history", "view", gen.id)))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    # Пагинация
    if total_pages > 1:
        nav_row = []
        if page > 1:
            nav_row.append(_btn("◀️", _cb("history", "page", page - 1)))
        nav_row.append(_btn(f"{page}/{total_pages}", _cb("history")))
        if page < total_pages:
            nav_row.append(_btn("▶️", _cb("history", "page", page + 1)))
        keyboard.append(nav_row)
    
    keyboard.append([_btn("◀️ Назад", _cb("main"))])
    return keyboard


def generation_view_keyboard(generation_id: int, gallery_enabled: bool = False) -> list:
    """Просмотр генерации"""
    keyboard = [
        [_btn("🔄 Повторить", _cb("repeat", generation_id))],
    ]
    
    if gallery_enabled:
        keyboard.append([_btn("📤 В галерею", _cb("gallery", "confirm", generation_id))])
    
    keyboard.append([_btn("🗑 Удалить", _cb("delete", generation_id))])
    keyboard.append([_btn("◀️ Назад", _cb("history"))])
    
    return keyboard


# ==================== ГАЛЕРЕЯ ====================

def gallery_confirm_keyboard(generation_id: int) -> list:
    """Подтверждение публикации в галерею"""
    return [
        [_btn("✅ Опубликовать", _cb("gallery", "publish", generation_id))],
        [_btn("❌ Отмена", _cb("history", "view", generation_id))],
    ]


def back_to_main_keyboard() -> list:
    """Кнопка возврата в меню"""
    return [
        [_btn("◀️ Меню", _cb("main"))],
    ]
