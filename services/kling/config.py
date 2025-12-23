"""
Kling Video v2.6 — Конфигурация
"""

SERVICE_ID = "kling"
SERVICE_NAME = "Kling v2.6"
SERVICE_ICON = "🎬"
SERVICE_VERSION = "1.0.0"
SERVICE_DESCRIPTION = "Генерация видео с помощью Kling AI v2.6"

# API Endpoints
FAL_TEXT_TO_VIDEO = "fal-ai/kling-video/v2.6/pro/text-to-video"
FAL_IMAGE_TO_VIDEO = "fal-ai/kling-video/v2.6/pro/image-to-video"

# Цены fal.ai (USD за секунду)
PRICE_PER_SECOND_NO_AUDIO = 0.07
PRICE_PER_SECOND_WITH_AUDIO = 0.14

# Длительность видео
DURATION_OPTIONS = {
    "5": "5 секунд",
    "10": "10 секунд",
}

# Соотношение сторон
ASPECT_RATIOS = {
    "16:9": "16:9 (альбом)",
    "9:16": "9:16 (портрет)",
    "1:1": "1:1 (квадрат)",
}

# Настройки аудио
AUDIO_OPTIONS = {
    "off": "🔇 Без аудио",
    "on": "🔊 С аудио",
}

# Настройки по умолчанию
DEFAULT_USER_SETTINGS = {
    "duration": "5",
    "aspect_ratio": "16:9",
    "audio": "off",
}

# Лимиты
MAX_PROMPT_LENGTH = 2500

# Анимация прогресса
PROGRESS_FRAMES = [
    "🎬 Генерирую видео",
    "🎬 Генерирую видео.",
    "🎬 Генерирую видео..",
    "🎬 Генерирую видео...",
]

# Режимы генерации
GENERATION_MODES = {
    "text_to_video": "📝 Текст → Видео",
    "image_to_video": "🖼 Изображение → Видео",
}
