"""
Veo Service — Конфигурация
"""

# ID сервиса
SERVICE_ID = "veo"
SERVICE_NAME = "Veo 2"
SERVICE_ICON = "🎬"

# API Endpoints
ENDPOINTS = {
    "text_to_video": "fal-ai/veo2",
    "image_to_video": "fal-ai/veo2/image-to-video",
}

# Цены в USD (базовые, без маржи)
PRICES = {
    "5s": 2.50,
    "6s": 3.00,
    "7s": 3.50,
    "8s": 4.00,
}

# Маржа по умолчанию (30%)
DEFAULT_MARGIN = 0.30

# Доступные длительности
DURATIONS = ["5s", "6s", "7s", "8s"]

# Соотношения сторон
ASPECT_RATIOS_TEXT = ["16:9", "9:16"]
ASPECT_RATIOS_IMAGE = ["auto", "auto_prefer_portrait", "16:9", "9:16"]

# Настройки по умолчанию для пользователя
DEFAULT_USER_SETTINGS = {
    "duration": "5s",
    "aspect_ratio": "16:9",
    "enhance_prompt": True,
}

# Лимиты
MAX_PROMPT_LENGTH = 2000

# Анимация прогресса
PROGRESS_FRAMES = [
    "🎬 Генерация видео.",
    "🎬 Генерация видео..",
    "🎬 Генерация видео...",
    "🎥 Обработка кадров.",
    "🎥 Обработка кадров..",
    "🎥 Обработка кадров...",
    "📽 Рендеринг.",
    "📽 Рендеринг..",
    "📽 Рендеринг...",
]

# Названия для UI
DURATION_NAMES = {
    "5s": "5 секунд",
    "6s": "6 секунд",
    "7s": "7 секунд",
    "8s": "8 секунд",
}

ASPECT_RATIO_NAMES = {
    "16:9": "16:9 (горизонтальное)",
    "9:16": "9:16 (вертикальное)",
    "auto": "Авто",
    "auto_prefer_portrait": "Авто (портрет)",
}
