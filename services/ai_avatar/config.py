"""
AI Avatar — Конфигурация
"""
from decimal import Decimal

# ID сервиса
SERVICE_ID = "ai_avatar"
SERVICE_NAME = "AI Avatar"
SERVICE_ICON = "🎭"
SERVICE_VERSION = "1.0.0"
SERVICE_AUTHOR = "FuBot Team"
SERVICE_DESCRIPTION = "Превращает фото в говорящее видео с синхронизацией губ"

# fal.ai endpoint
FAL_ENDPOINT = "fal-ai/creatify/aurora"

# Базовые цены fal.ai в USD (за секунду видео)
FAL_PRICES_USD = {
    "480p": Decimal("0.10"),  # $0.10/сек
    "720p": Decimal("0.14"),  # $0.14/сек
}

# Доступные качества видео
VIDEO_QUALITIES = {
    "480p": "480p (стандарт)",
    "720p": "720p (HD)",
}

# Поддерживаемые форматы
SUPPORTED_IMAGE_FORMATS = ["jpg", "jpeg", "png", "webp"]
SUPPORTED_AUDIO_FORMATS = ["mp3", "wav", "m4a", "ogg", "aac"]

# Лимиты
MAX_VIDEO_DURATION = 60  # секунд
MIN_VIDEO_DURATION = 1   # секунда
MAX_FILE_SIZE_MB = 10    # МБ для загружаемых файлов

# Примерное время генерации (секунды)
ESTIMATED_GENERATION_TIME = {
    "480p": 30,  # ~30 сек для 480p
    "720p": 45,  # ~45 сек для 720p
}

# Настройки по умолчанию для пользователя
DEFAULT_USER_SETTINGS = {
    "quality": "480p",
    "use_tts": False,  # Использовать TTS вместо загрузки аудио
}

# Настройки сервиса по умолчанию (админ)
DEFAULT_SERVICE_CONFIG = {
    "fal_api_key": "",
    "margin_multiplier": 0.3,  # +30%
    "prices": {
        "480p": 0.10,
        "720p": 0.14,
    },
    "referral_bonus_enabled": True,
    "referral_bonus_percent": 10,
    "gallery_channel_id": "",
    "gallery_enabled": False,
    "max_video_duration": 60,
    "max_file_size_mb": 10,
}

# Анимация прогресса
PROGRESS_FRAMES = [
    "🎭⬜⬜⬜⬜⬜⬜⬜⬜⬜",
    "🎭🎭⬜⬜⬜⬜⬜⬜⬜⬜",
    "🎭🎭🎭⬜⬜⬜⬜⬜⬜⬜",
    "🎭🎭🎭🎭⬜⬜⬜⬜⬜⬜",
    "🎭🎭🎭🎭🎭⬜⬜⬜⬜⬜",
    "🎭🎭🎭🎭🎭🎭⬜⬜⬜⬜",
    "🎭🎭🎭🎭🎭🎭🎭⬜⬜⬜",
    "🎭🎭🎭🎭🎭🎭🎭🎭⬜⬜",
    "🎭🎭🎭🎭🎭🎭🎭🎭🎭⬜",
    "🎭🎭🎭🎭🎭🎭🎭🎭🎭🎭",
]

# Промпты визуального стиля (опциональные)
VISUAL_STYLE_PROMPTS = {
    "default": "4K studio quality, professional lighting, medium close-up",
    "interview": "4K studio interview, soft key-light, neutral background",
    "presentation": "Professional presentation, corporate setting, bright lighting",
    "casual": "Natural lighting, casual setting, relaxed atmosphere",
    "cinematic": "Cinematic lighting, dramatic shadows, film quality",
}
