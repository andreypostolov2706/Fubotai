"""
FLUX 2 Flex — Конфигурация
"""

SERVICE_ID = "flux2_flex"
SERVICE_NAME = "FLUX 2 Flex"
SERVICE_ICON = "✨"
SERVICE_VERSION = "1.0.0"
SERVICE_AUTHOR = "FuBot Team"
SERVICE_DESCRIPTION = "Генерация изображений с помощью FLUX.2 [flex]"

# fal.ai endpoint
FAL_ENDPOINT = "fal-ai/flux-2-flex"

# Цена fal.ai: $0.06 за мегапиксель
# Примерные цены для разных размеров:
PRICES = {
    "square": 0.06,           # 1024x1024 = 1MP
    "square_hd": 0.09,        # 1.5MP
    "landscape_4_3": 0.06,    # ~1MP
    "landscape_16_9": 0.06,   # ~1MP
    "portrait_4_3": 0.06,     # ~1MP
    "portrait_16_9": 0.06,    # ~1MP
}

# Размеры изображений
IMAGE_SIZES = {
    "square": "1024×1024 (квадрат)",
    "square_hd": "1536×1536 (HD квадрат)",
    "landscape_4_3": "1365×1024 (альбом 4:3)",
    "landscape_16_9": "1820×1024 (альбом 16:9)",
    "portrait_4_3": "1024×1365 (портрет 4:3)",
    "portrait_16_9": "1024×1820 (портрет 16:9)",
}

# Форматы вывода
OUTPUT_FORMATS = {
    "jpeg": "JPEG",
    "png": "PNG",
}

# Настройки по умолчанию
DEFAULT_USER_SETTINGS = {
    "image_size": "square",
    "output_format": "jpeg",
    "guidance_scale": 3.5,
    "num_inference_steps": 28,
    "enable_prompt_expansion": True,
}

# Настройки сервиса по умолчанию
DEFAULT_SERVICE_CONFIG = {
    "fal_api_key": "",
    "margin_multiplier": 0.3,
    "prices": PRICES,
    "gallery_channel_id": "",
    "gallery_enabled": False,
}

# Лимиты
MAX_PROMPT_LENGTH = 4000

# Анимация прогресса
PROGRESS_FRAMES = [
    "✨ Генерирую изображение",
    "✨ Генерирую изображение.",
    "✨ Генерирую изображение..",
    "✨ Генерирую изображение...",
]
