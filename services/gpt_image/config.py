"""
GPT-Image 1.5 — Конфигурация
"""

SERVICE_ID = "gpt_image"
SERVICE_NAME = "GPT-Image 1.5"
SERVICE_ICON = "🎨"
SERVICE_VERSION = "1.0.0"
SERVICE_DESCRIPTION = "Генерация изображений с помощью OpenAI GPT Image 1.5"

# API Endpoints
FAL_ENDPOINT = "fal-ai/gpt-image-1.5"
FAL_EDIT_ENDPOINT = "fal-ai/gpt-image-1.5/edit"

# Цены fal.ai (USD)
PRICES = {
    "low": {
        "1024x1024": 0.009,
        "1536x1024": 0.013,
        "1024x1536": 0.013,
    },
    "medium": {
        "1024x1024": 0.034,
        "1536x1024": 0.050,
        "1024x1536": 0.051,
    },
    "high": {
        "1024x1024": 0.133,
        "1536x1024": 0.199,
        "1024x1536": 0.200,
    },
}

# Размеры изображений
IMAGE_SIZES = {
    "1024x1024": "1024×1024 (квадрат)",
    "1536x1024": "1536×1024 (альбом)",
    "1024x1536": "1024×1536 (портрет)",
}

# Качество
QUALITY_OPTIONS = {
    "low": "🟢 Низкое (быстро, дёшево)",
    "medium": "🟡 Среднее",
    "high": "🔴 Высокое (детализация)",
}

# Фон
BACKGROUND_OPTIONS = {
    "auto": "🔄 Авто",
    "transparent": "🔲 Прозрачный",
    "opaque": "⬜ Непрозрачный",
}

# Форматы вывода
OUTPUT_FORMATS = {
    "png": "PNG",
    "jpeg": "JPEG",
    "webp": "WebP",
}

# Настройки по умолчанию
DEFAULT_USER_SETTINGS = {
    "quality": "high",
    "image_size": "1024x1024",
    "background": "auto",
    "output_format": "png",
    "num_images": 1,
}

# Лимиты
MAX_PROMPT_LENGTH = 4000
MAX_IMAGES_PER_REQUEST = 4
MIN_IMAGES = 1

# Анимация прогресса
PROGRESS_FRAMES = [
    "🎨 Генерирую изображение",
    "🎨 Генерирую изображение.",
    "🎨 Генерирую изображение..",
    "🎨 Генерирую изображение...",
]

# Режимы генерации
GENERATION_MODES = {
    "text_to_image": "🎨 Текст → Изображение",
    "image_to_image": "🖼 Изображение → Изображение",
}
