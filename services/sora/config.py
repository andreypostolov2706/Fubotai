"""
Sora 2 Service Configuration
"""

SERVICE_ID = "sora"
SERVICE_NAME = "Sora 2"
SERVICE_VERSION = "1.0.0"
SERVICE_AUTHOR = "FuBot Team"
SERVICE_DESCRIPTION = "Генерация видео с помощью OpenAI Sora 2"
SERVICE_ICON = "🎬"

# fal.ai endpoints
FAL_TEXT_TO_VIDEO = "fal-ai/sora-2/text-to-video"
FAL_IMAGE_TO_VIDEO = "fal-ai/sora-2/image-to-video/pro"

# Доступные параметры
RESOLUTIONS = ["720p"]
ASPECT_RATIOS = ["16:9", "9:16"]
DURATIONS = [4, 8, 12]  # секунды

# Базовые цены в USD (fal.ai pricing)
PRICES = {
    "4s": 0.50,    # 4 секунды
    "8s": 1.00,    # 8 секунд
    "12s": 1.50,   # 12 секунд
}

# Настройки сервиса по умолчанию
DEFAULT_SERVICE_CONFIG = {
    "fal_api_key": "",
    "margin_multiplier": 0.3,
    "prices": PRICES,
    "gallery_channel_id": "",
    "gallery_enabled": False,
}

# Настройки пользователя по умолчанию
DEFAULT_USER_SETTINGS = {
    "aspect_ratio": "16:9",
    "duration": 4,
}
