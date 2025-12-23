"""
Nano Banano — Конфигурация
"""
from decimal import Decimal

# ID сервиса
SERVICE_ID = "nano_banano"
SERVICE_NAME = "Nano Banano Pro"
SERVICE_ICON = "🍌"
SERVICE_VERSION = "1.0.0"
SERVICE_AUTHOR = "FuBot Team"
SERVICE_DESCRIPTION = "Генерация и редактирование изображений с помощью ИИ"

# fal.ai endpoints
FAL_ENDPOINTS = {
    "nano_banana": {
        "generate": "fal-ai/nano-banana",
        "edit": "fal-ai/nano-banana/edit",
    },
    "nano_banana_pro": {
        "generate": "fal-ai/nano-banana-pro",
        "edit": "fal-ai/nano-banana-pro/edit",
    },
}

# Базовые цены fal.ai в USD
FAL_PRICES_USD = {
    "nano_banana": Decimal("0.04"),
    "nano_banana_pro_1k": Decimal("0.15"),
    "nano_banana_pro_2k": Decimal("0.22"),
    "nano_banana_pro_4k": Decimal("0.30"),
}

# Доступные размеры изображений
ASPECT_RATIOS = {
    "1:1": "1:1",
    "16:9": "16:9",
    "9:16": "9:16",
    "4:3": "4:3",
    "3:4": "3:4",
}

# Форматы вывода
OUTPUT_FORMATS = ["png", "jpeg", "webp"]

# Разрешения (только для Pro)
RESOLUTIONS = ["1K", "2K", "4K"]

# Примерное время генерации (секунды)
ESTIMATED_GENERATION_TIME = {
    "nano_banana": 10,
    "nano_banana_pro_1k": 15,
    "nano_banana_pro_2k": 20,
    "nano_banana_pro_4k": 30,
}

# Лимиты
MAX_IMAGES_PER_REQUEST = 4
MAX_INPUT_IMAGES = 4

# Настройки по умолчанию для пользователя
DEFAULT_USER_SETTINGS = {
    "model": "nano_banana",
    "aspect_ratio": "1:1",
    "output_format": "png",
    "resolution": "1K",
}

# Настройки сервиса по умолчанию (админ)
DEFAULT_SERVICE_CONFIG = {
    "fal_api_key": "",
    "margin_multiplier": 0.3,  # +30%
    "prices": {
        "nano_banana": 0.04,
        "nano_banana_pro_1k": 0.15,
        "nano_banana_pro_2k": 0.22,
        "nano_banana_pro_4k": 0.30,
    },
    "referral_bonus_enabled": True,
    "referral_bonus_percent": 10,
    "gallery_channel_id": "",
    "gallery_enabled": False,
    "max_images_per_request": 4,
    "max_input_images": 4,
}

# Анимация прогресса
PROGRESS_FRAMES = [
    "🍌⬜⬜⬜⬜⬜⬜⬜⬜⬜",
    "🍌🍌⬜⬜⬜⬜⬜⬜⬜⬜",
    "🍌🍌🍌⬜⬜⬜⬜⬜⬜⬜",
    "🍌🍌🍌🍌⬜⬜⬜⬜⬜⬜",
    "🍌🍌🍌🍌🍌⬜⬜⬜⬜⬜",
    "🍌🍌🍌🍌🍌🍌⬜⬜⬜⬜",
    "🍌🍌🍌🍌🍌🍌🍌⬜⬜⬜",
    "🍌🍌🍌🍌🍌🍌🍌🍌⬜⬜",
    "🍌🍌🍌🍌🍌🍌🍌🍌🍌⬜",
    "🍌🍌🍌🍌🍌🍌🍌🍌🍌🍌",
]
