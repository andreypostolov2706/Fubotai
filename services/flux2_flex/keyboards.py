"""
FLUX 2 Flex — Клавиатуры
"""
from . import config


def main_menu_keyboard():
    """Главное меню сервиса"""
    return [
        [{"text": "✨ Сгенерировать", "callback_data": f"service:{config.SERVICE_ID}:generate"}],
        [
            {"text": "⚙️ Настройки", "callback_data": f"service:{config.SERVICE_ID}:settings"},
            {"text": "📜 История", "callback_data": f"service:{config.SERVICE_ID}:history:0"},
        ],
        [{"text": "🔙 Главное меню", "callback_data": "main_menu"}],
    ]


def cancel_keyboard():
    """Клавиатура отмены"""
    return [
        [{"text": "❌ Отмена", "callback_data": f"service:{config.SERVICE_ID}:cancel"}],
    ]


def confirm_keyboard():
    """Клавиатура подтверждения генерации"""
    return [
        [{"text": "✅ Сгенерировать", "callback_data": f"service:{config.SERVICE_ID}:confirm"}],
        [
            {"text": "📐 Размер", "callback_data": f"service:{config.SERVICE_ID}:change_size"},
            {"text": "📄 Формат", "callback_data": f"service:{config.SERVICE_ID}:change_format"},
        ],
        [{"text": "❌ Отмена", "callback_data": f"service:{config.SERVICE_ID}:cancel"}],
    ]


def size_keyboard(current: str):
    """Клавиатура выбора размера"""
    keyboard = []
    for size_id, size_name in config.IMAGE_SIZES.items():
        mark = "✅ " if size_id == current else ""
        keyboard.append([{
            "text": f"{mark}{size_name}",
            "callback_data": f"service:{config.SERVICE_ID}:set_size:{size_id}"
        }])
    keyboard.append([{"text": "🔙 Назад", "callback_data": f"service:{config.SERVICE_ID}:back_to_confirm"}])
    return keyboard


def format_keyboard(current: str):
    """Клавиатура выбора формата"""
    keyboard = []
    for fmt_id, fmt_name in config.OUTPUT_FORMATS.items():
        mark = "✅ " if fmt_id == current else ""
        keyboard.append([{
            "text": f"{mark}{fmt_name}",
            "callback_data": f"service:{config.SERVICE_ID}:set_format:{fmt_id}"
        }])
    keyboard.append([{"text": "🔙 Назад", "callback_data": f"service:{config.SERVICE_ID}:back_to_confirm"}])
    return keyboard


def settings_keyboard():
    """Клавиатура настроек"""
    return [
        [{"text": "📐 Размер", "callback_data": f"service:{config.SERVICE_ID}:settings_size"}],
        [{"text": "📄 Формат", "callback_data": f"service:{config.SERVICE_ID}:settings_format"}],
        [{"text": "🔢 Шаги", "callback_data": f"service:{config.SERVICE_ID}:settings_steps"}],
        [{"text": "🔙 Назад", "callback_data": f"service:{config.SERVICE_ID}:main"}],
    ]


def settings_size_keyboard(current: str):
    """Клавиатура выбора размера в настройках"""
    keyboard = []
    for size_id, size_name in config.IMAGE_SIZES.items():
        mark = "✅ " if size_id == current else ""
        keyboard.append([{
            "text": f"{mark}{size_name}",
            "callback_data": f"service:{config.SERVICE_ID}:save_size:{size_id}"
        }])
    keyboard.append([{"text": "🔙 Назад", "callback_data": f"service:{config.SERVICE_ID}:settings"}])
    return keyboard


def settings_format_keyboard(current: str):
    """Клавиатура выбора формата в настройках"""
    keyboard = []
    for fmt_id, fmt_name in config.OUTPUT_FORMATS.items():
        mark = "✅ " if fmt_id == current else ""
        keyboard.append([{
            "text": f"{mark}{fmt_name}",
            "callback_data": f"service:{config.SERVICE_ID}:save_format:{fmt_id}"
        }])
    keyboard.append([{"text": "🔙 Назад", "callback_data": f"service:{config.SERVICE_ID}:settings"}])
    return keyboard


def settings_steps_keyboard(current: int):
    """Клавиатура выбора количества шагов"""
    steps_options = [10, 20, 28, 35, 50]
    keyboard = []
    for steps in steps_options:
        mark = "✅ " if steps == current else ""
        keyboard.append([{
            "text": f"{mark}{steps} шагов",
            "callback_data": f"service:{config.SERVICE_ID}:save_steps:{steps}"
        }])
    keyboard.append([{"text": "🔙 Назад", "callback_data": f"service:{config.SERVICE_ID}:settings"}])
    return keyboard


def history_keyboard(page: int, total_pages: int):
    """Клавиатура истории"""
    keyboard = []
    
    nav_row = []
    if page > 0:
        nav_row.append({"text": "⬅️", "callback_data": f"service:{config.SERVICE_ID}:history:{page - 1}"})
    nav_row.append({"text": f"{page + 1}/{total_pages}", "callback_data": f"service:{config.SERVICE_ID}:noop"})
    if page < total_pages - 1:
        nav_row.append({"text": "➡️", "callback_data": f"service:{config.SERVICE_ID}:history:{page + 1}"})
    
    if nav_row:
        keyboard.append(nav_row)
    
    keyboard.append([{"text": "🔙 Назад", "callback_data": f"service:{config.SERVICE_ID}:main"}])
    return keyboard


def back_to_main_keyboard():
    """Кнопка возврата в главное меню"""
    return [
        [{"text": "🔙 Назад", "callback_data": f"service:{config.SERVICE_ID}:main"}],
    ]
