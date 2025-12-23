"""
Тексты для ЛК пользователя

Этот файл содержит все тексты, которые отображаются пользователю.
При смене сервисов достаточно изменить тексты здесь.

Использование:
    from core.locales.user_texts import USER_TEXTS
    text = USER_TEXTS["main_menu"]["title"]
"""

# ==================== ГЛАВНОЕ МЕНЮ ====================
# Текст над кнопками в главном меню

MAIN_MENU_TITLE = "🤖 <b>AI Full Bot</b>"

MAIN_MENU_DESCRIPTION = """
Генерация изображений и видео с помощью нейросетей.

<b>🖼 Изображения:</b>
• 🍌 <b>Nano Banano Pro</b> — Gemini (от {nano_banano_gton} GTON)
• ✨ <b>FLUX 2 Flex</b> — Black Forest Labs (от {flux2_flex_gton} GTON)
• 🎨 <b>GPT-Image 1.5</b> — OpenAI (от {gpt_image_gton} GTON)

<b>🎬 Видео:</b>
• 🎬 <b>Sora 2</b> — OpenAI (от {sora_gton} GTON)
• 🎬 <b>Veo 2</b> — Google (от {veo_gton} GTON)
• 🎬 <b>Kling v2.6</b> — Kuaishou (от {kling_gton} GTON)

Выберите сервис:
"""

# Описание для админа с полной информацией о ценах
MAIN_MENU_DESCRIPTION_ADMIN = """
Генерация изображений и видео с помощью нейросетей.

<b>🖼 Изображения:</b>

🍌 <b>Nano Banano Pro</b> (Gemini)
   Закупка: ${nano_banano_cost} ({nano_banano_cost_rub} ₽) | +{nano_banano_margin}%: ${nano_banano_usd}
   {nano_banano_gton} GTON | {nano_banano_ton} TON | {nano_banano_rub} ₽

✨ <b>FLUX 2 Flex</b> (Black Forest Labs)
   Закупка: ${flux2_flex_cost} ({flux2_flex_cost_rub} ₽) | +{flux2_flex_margin}%: ${flux2_flex_usd}
   {flux2_flex_gton} GTON | {flux2_flex_ton} TON | {flux2_flex_rub} ₽

🎨 <b>GPT-Image 1.5</b> (OpenAI)
   Закупка: ${gpt_image_cost} ({gpt_image_cost_rub} ₽) | +{gpt_image_margin}%: ${gpt_image_usd}
   {gpt_image_gton} GTON | {gpt_image_ton} TON | {gpt_image_rub} ₽

<b>🎬 Видео:</b>

🎬 <b>Veo 2</b> (Google)
   Закупка: ${veo_cost} ({veo_cost_rub} ₽) | +{veo_margin}%: ${veo_usd}
   {veo_gton} GTON | {veo_ton} TON | {veo_rub} ₽

🎬 <b>Sora 2</b> (OpenAI)
   Закупка: ${sora_cost} ({sora_cost_rub} ₽) | +{sora_margin}%: ${sora_usd}
   {sora_gton} GTON | {sora_ton} TON | {sora_rub} ₽

🎬 <b>Kling v2.6</b> (Kuaishou)
   Закупка: ${kling_cost} ({kling_cost_rub} ₽) | +{kling_margin}%: ${kling_usd}
   {kling_gton} GTON | {kling_ton} TON | {kling_rub} ₽

Выберите сервис:
"""

# ==================== БАЛАНС ====================

BALANCE_TEXT = "💰 Баланс: {balance} GTON"
BALANCE_WITH_FIAT = "💰 Баланс: {balance} GTON (~{fiat} ₽)"

# ==================== ПОПОЛНЕНИЕ ====================

TOP_UP_TITLE = "💳 <b>Пополнение баланса</b>"

TOP_UP_DESCRIPTION = """
Пополните баланс для использования сервисов.

Текущий баланс: {balance} GTON (~{fiat} ₽)
Курс: 1 GTON ≈ {rate} ₽
"""

# ==================== ПАРТНЁРСКАЯ ПРОГРАММА ====================

PARTNER_TITLE = "🤝 <b>Партнёрская программа</b>"

PARTNER_DESCRIPTION = """
Приглашайте друзей и получайте {percent}% от их платежей!

Ваша реферальная ссылка:
"""

# ==================== ПОМОЩЬ ====================

HELP_TITLE = "❓ <b>Помощь</b>"

HELP_DESCRIPTION = """
<b>🖼 Генерация изображений:</b>
• 🍌 <b>Nano Banano</b> — Gemini, редактирование фото
• 🎨 <b>GPT-Image</b> — OpenAI, высокое качество

<b>🎬 Генерация видео:</b>
• 🎬 <b>Veo</b> — Google Veo 2, реалистичные видео
• 🎬 <b>Kling</b> — Kling AI v2.6, генерация речи

<b>📖 Как пользоваться:</b>
1. Выберите сервис в главном меню
2. Нажмите "Создать" или "Анимировать"
3. Введите описание (промпт)
4. Настройте параметры и подтвердите

<b>💳 Оплата:</b>
• Баланс в GTON (внутренняя валюта)
• Пополнение через карту, СБП, криптовалюту

Вопросы? Свяжитесь с поддержкой:
"""

# ==================== ЕЖЕДНЕВНЫЙ БОНУС ====================

DAILY_BONUS_TITLE = "🎁 <b>Ежедневный бонус</b>"

DAILY_BONUS_DESCRIPTION = """
Заходите каждый день и получайте бесплатные GTON!

🔥 Серия: {streak} дней
📅 День {current} из {total}
🎁 Награда: {reward} GTON
"""

# ==================== ПРОМОКОД ====================

PROMOCODE_TITLE = "🎁 <b>Промокод</b>"

PROMOCODE_DESCRIPTION = """
Введите промокод для получения бонуса:
"""

# ==================== НАСТРОЙКИ ====================

SETTINGS_TITLE = "⚙️ <b>Настройки</b>"

SETTINGS_DESCRIPTION = """
Настройте бота под себя:
"""

# ==================== СЕРВИСЫ ====================

# Nano Banano
NANO_BANANO_TITLE = "🍌 <b>Nano Banano</b>"
NANO_BANANO_DESCRIPTION = """
Генерация изображений с помощью ИИ.

Введите описание того, что хотите увидеть на изображении:
"""

# Veo
VEO_TITLE = "🎬 <b>Veo</b>"
VEO_DESCRIPTION = """
Генерация видео с помощью Google Veo 2.

Выберите режим генерации:
"""

# ==================== СЛОВАРЬ ДЛЯ УДОБНОГО ДОСТУПА ====================

USER_TEXTS = {
    "main_menu": {
        "title": MAIN_MENU_TITLE,
        "description": MAIN_MENU_DESCRIPTION,
        "description_admin": MAIN_MENU_DESCRIPTION_ADMIN,
        "balance": BALANCE_TEXT,
        "balance_with_fiat": BALANCE_WITH_FIAT,
    },
    "top_up": {
        "title": TOP_UP_TITLE,
        "description": TOP_UP_DESCRIPTION,
    },
    "partner": {
        "title": PARTNER_TITLE,
        "description": PARTNER_DESCRIPTION,
    },
    "help": {
        "title": HELP_TITLE,
        "description": HELP_DESCRIPTION,
    },
    "daily_bonus": {
        "title": DAILY_BONUS_TITLE,
        "description": DAILY_BONUS_DESCRIPTION,
    },
    "promocode": {
        "title": PROMOCODE_TITLE,
        "description": PROMOCODE_DESCRIPTION,
    },
    "settings": {
        "title": SETTINGS_TITLE,
        "description": SETTINGS_DESCRIPTION,
    },
    "services": {
        "nano_banano": {
            "title": NANO_BANANO_TITLE,
            "description": NANO_BANANO_DESCRIPTION,
        },
        "veo": {
            "title": VEO_TITLE,
            "description": VEO_DESCRIPTION,
        },
    },
}
