"""
Russian Localization (Main)
"""

from __future__ import annotations

LANGUAGE_CODE = "ru"
LANGUAGE_NAME = "Русский"
LANGUAGE_FLAG = "🇷🇺"

# ==================== COMMON ====================

COMMON = {
    "back": "◀️ Назад",
    "cancel": "❌ Отмена",
    "confirm": "✅ Подтвердить",
    "yes": "Да",
    "no": "Нет",
    "save": "💾 Сохранить",
    "delete": "🗑 Удалить",
    "edit": "✏️ Редактировать",
    "loading": "⏳ Загрузка...",
    "error": "❌ Произошла ошибка",
    "success": "✅ Успешно!",
    "not_found": "Не найдено",
    "coming_soon": "🚧 Скоро будет доступно",
    "enabled": "Включено",
    "disabled": "Отключено",
}

# ==================== MAIN MENU ====================

MAIN_MENU = {
    "title": "🏠 <b>Главное меню</b>",
    "balance": "💰 Баланс: {balance} GTON",
    "balance_with_fiat": "💰 Баланс: {balance} GTON (~{fiat} ₽)",
    "top_up": "💳 Пополнить",
    "promocode": "🎟 Промокод",
    "settings": "⚙️ Настройки",
    "help": "❓ Помощь",
    "partner": "🤝 Партнёрская программа",
    "daily_bonus": "🎁 Ежедневный бонус",
    "daily_bonus_ready": "🎁 Забрать бонус ({gton} GTON)",
}

# ==================== TOP UP ====================

TOP_UP = {
    "title": "💳 <b>Пополнение баланса</b>",
    "current_balance": "Текущий баланс: {balance} GTON (~{fiat} ₽)",
    "current_balance_gton": "Ваш баланс: {balance}",
    "rate": "Курс: 1 GTON = {rate} ₽",
    "select_amount": "Выберите сумму:",
    "custom_amount": "💬 Другая сумма",
    "enter_amount": "Введите сумму в рублях:",
    "min_amount": "Минимальная сумма: {min} ₽",
    "max_amount": "Максимальная сумма: {max} ₽",
    "invalid_amount": "❌ Некорректная сумма",
    
    # Payment methods
    "select_method": "Выберите способ оплаты:",
    "method_card": "💳 Банковская карта",
    "method_sbp": "📱 СБП",
    "method_yoomoney": "🟡 ЮMoney",
    "method_crypto": "₿ Криптовалюта",
    
    # Result
    "payment_created": "🔗 Ссылка на оплату создана",
    "payment_success": "✅ Оплата прошла успешно!\n\n💰 Зачислено: {gton} GTON (~{fiat} ₽)",
    "payment_failed": "❌ Ошибка оплаты",
    "payment_pending": "⏳ Ожидание оплаты...",
    
    # Promocode
    "enter_promocode": "🎁 Ввести промокод",
    "promocode_placeholder": "🎁 Введите промокод:",
}

# ==================== SETTINGS ====================

SETTINGS = {
    "title": "⚙️ <b>Настройки</b>",
    "language": "🌐 Язык",
    "language_current": "Текущий язык: {language}",
    "language_select": "Выберите язык:",
    "language_changed": "✅ Язык изменён на {language}",
    "notifications": "🔔 Уведомления",
    "notifications_title": "🔔 <b>Уведомления</b>",
    "notifications_description": "Настройка уведомлений будет доступна в ближайшее время.",
    "notifications_on": "Уведомления включены",
    "notifications_off": "Уведомления отключены",
}

# ==================== PARTNER ====================

PARTNER = {
    "title": "🤝 <b>Партнёрская программа</b>",
    "description": "Приглашайте друзей и получайте {percent}% от их платежей!",
    
    # Stats
    "stats_title": "📊 Ваша статистика:",
    "stats_referrals": "Рефералов: {count}",
    "stats_earned": "Заработано: {amount} ₽",
    "stats_available": "Доступно к выводу: {amount} ₽",
    
    # Link
    "your_link": "🔗 Ваша ссылка:",
    "link_copied": "✅ Ссылка скопирована",
    
    # Menu
    "my_referrals": "📋 Мои рефералы",
    "withdraw": "💸 Вывести средства",
    "become_partner": "💰 Стать партнёром",
    "partner_cabinet": "🤝 Партнёрский кабинет",
    
    # Application
    "application_title": "📝 <b>Заявка на партнёрство</b>",
    "application_text": "Расскажите о себе и как планируете привлекать пользователей:",
    "application_sent": "✅ Заявка отправлена!\n\nМы рассмотрим её в ближайшее время.",
    "application_pending": "⏳ Ваша заявка на рассмотрении",
    
    # Withdrawal
    "withdraw_title": "💸 <b>Вывод средств</b>",
    "withdraw_available": "Доступно: {amount} ₽",
    "withdraw_min": "Минимальная сумма: {min} ₽",
    "withdraw_enter_amount": "Введите сумму для вывода:",
    "withdraw_select_method": "Выберите способ вывода:",
    "withdraw_enter_details": "Введите реквизиты ({method}):",
    "withdraw_confirm": "Подтвердите вывод:\n\nСумма: {amount} ₽\nМетод: {method}\nРеквизиты: {details}",
    "withdraw_success": "✅ Заявка на вывод создана!\n\nОжидайте обработки.",
    "withdraw_insufficient": "❌ Недостаточно средств",
}

# ==================== HELP ====================

HELP = {
    "title": "❓ <b>Помощь</b>",
    "description": "Если у вас возникли вопросы, свяжитесь с поддержкой:",
    "support": "📩 Написать в поддержку",
    "faq": "📖 Частые вопросы",
}

# ==================== ERRORS ====================

ERRORS = {
    "not_enough_balance": "❌ Недостаточно GTON!\n\nНужно: {required} GTON\nУ вас: {balance} GTON",
    "user_blocked": "🚫 Ваш аккаунт заблокирован.\n\nПричина: {reason}",
    "user_blocked_temp": "🚫 Ваш аккаунт заблокирован.\n\nПричина: {reason}\nДо разблокировки: {days} дн.",
    "rate_limit": "⏳ Слишком много запросов. Подождите немного.",
    "maintenance": "🔧 Бот на обслуживании. Попробуйте позже.",
    "unknown_command": "❓ Неизвестная команда",
    "invalid_input": "❌ Некорректный ввод",
    "service_unavailable": "❌ Сервис временно недоступен",
}

# ==================== DAILY BONUS ====================

DAILY_BONUS = {
    "title": "🎁 <b>Ежедневный бонус</b>",
    
    # Status
    "streak": "🔥 Серия: {days} дней",
    "day_of": "День {current} из {total}",
    "reward": "Награда: {gton} GTON",
    "next_reward": "Завтра: {gton} GTON",
    "next_in": "⏰ Следующий через: {time}",
    
    # Actions
    "claim": "🎁 Забрать бонус",
    "claim_short": "🎁 Забрать",
    "history": "📊 История",
    
    # Result
    "claimed_title": "✅ Бонус получен!",
    "claimed_gton": "🎁 +{gton} GTON",
    "new_balance": "💰 Баланс: {balance} GTON (~{fiat} ₽)",
    "new_streak": "🔥 Серия: {days} дней",
    
    # Already claimed
    "already_claimed": "✅ Сегодня уже получен",
    "dont_miss": "💡 Не пропускай дни, чтобы не потерять серию!",
    
    # Streak lost
    "streak_lost_title": "😔 Серия прервана!",
    "streak_lost_text": "Вы пропустили день и серия сбросилась. Начинаем заново!",
    
    # Day 7
    "day7_tomorrow": "📅 Завтра: {gton} GTON (день 7!)",
    "day7_congrats": "🎉 Поздравляем! Максимальная награда!",
}

# ==================== PROMOCODE ====================

PROMOCODE = {
    "enter_code": "🎁 Введите промокод:",
    "activated": "✅ Промокод активирован!",
    "reward_gton": "🎁 Вам начислено: {amount} GTON (~{fiat} ₽)",
    "reward_subscription": "⭐ Вам активирована подписка {plan} на {days} дней",
    "reward_discount": "💸 Скидка {percent}% применена",
    "new_balance": "💰 Новый баланс: {balance} GTON (~{fiat} ₽)",
    
    # Errors
    "invalid": "❌ Промокод недействителен",
    "expired": "❌ Срок действия промокода истёк",
    "already_used": "❌ Вы уже использовали этот промокод",
    "limit_reached": "❌ Лимит активаций промокода исчерпан",
    "new_users_only": "❌ Промокод только для новых пользователей",
    "first_deposit_only": "❌ Промокод только для первого пополнения",
}

# ==================== MODERATION ====================

MODERATION = {
    # Reasons
    "reason_spam": "Спам",
    "reason_abuse": "Оскорбления",
    "reason_fraud": "Мошенничество",
    "reason_terms_violation": "Нарушение правил",
    "reason_other": "Другое",
    
    # Warnings
    "warning_issued": "⚠️ Вам выдано предупреждение",
    "warning_reason": "Причина: {reason}",
    "warning_count": "Предупреждений: {current}/{max}",
    "warning_notice": "При получении {max} предупреждений ваш аккаунт будет временно заблокирован.",
    
    # Ban
    "banned_title": "🚫 Ваш аккаунт заблокирован",
    "banned_reason": "Причина: {reason}",
    "banned_permanent": "Срок: навсегда",
    "banned_temporary": "Срок: {days} дней",
    "banned_until": "Разблокировка: {date}",
    "banned_days_left": "До разблокировки: {days} дней",
    "banned_appeal": "Если вы считаете это ошибкой, обратитесь в поддержку.",
    
    # Unban
    "unbanned": "✅ Ваш аккаунт разблокирован",
}

# ==================== NOTIFICATIONS ====================

NOTIFICATIONS = {
    "settings_title": "🔔 Настройки уведомлений",
    "email_not_set": "📧 Email: не указан",
    "email_set": "📧 Email: {email}",
    "add_email": "Добавить email",
    "change_email": "Изменить email",
    
    "receive_title": "Получать уведомления:",
    "category_payment": "💳 Платежи и баланс",
    "category_subscription": "⭐ Подписки",
    "category_referral": "🤝 Рефералы",
    "category_promo": "🎁 Акции и промо",
    "category_reminder": "🔔 Напоминания",
    "category_service": "📦 От сервисов",
    
    # Trigger messages
    "low_balance_title": "⚠️ Низкий баланс",
    "low_balance_text": "У вас осталось {balance} GTON. Пополните баланс.",
    "subscription_expiring_title": "⏰ Подписка истекает",
    "subscription_expiring_text": "Ваша подписка истекает через {days} дн.",
    "inactive_title": "👋 Мы скучаем!",
    "inactive_text": "Вы не заходили уже {days} дней. Возвращайтесь!",
}

# ==================== ADMIN ====================

ADMIN = {
    "title": "🔧 <b>Админ-панель</b>",
    "partners": "👥 Партнёры",
    "statistics": "📊 Статистика",
    "broadcast": "📢 Рассылка",
    "settings": "⚙️ Настройки",
    "services": "📦 Сервисы",
    "users": "👤 Пользователи",
    "languages": "🌐 Языки",
    
    # Main menu buttons
    "menu_stats": "📊 Статистика",
    "menu_users": "👤 Пользователи",
    "menu_partners": "👥 Партнёры",
    "menu_moderation": "🛡 Модерация",
    "menu_promocodes": "🎁 Промокоды",
    "menu_services": "📦 Сервисы",
    "menu_broadcast": "📢 Рассылка",
    "menu_settings": "⚙️ Настройки",
    "menu_languages": "🌐 Языки",
    
    # Settings
    "settings_title": "⚙️ <b>Настройки</b>",
    "settings_select_category": "Выберите категорию для настройки:",
    "settings_general": "🤖 Общие",
    "settings_tokens": "💰 Токены и баланс",
    "settings_payments": "💰 GTON и платежи",
    "settings_referral": "👥 Реферальная система",
    "settings_moderation": "🛡 Модерация",
    "settings_daily_bonus": "🎁 Ежедневный бонус",
    "settings_notifications": "🔔 Уведомления",
    
    # Payment settings labels
    "setting_gton_ton_rate": "1 GTON = X TON",
    "setting_min_deposit": "Мин. депозит (GTON)",
    "setting_max_deposit": "Макс. депозит (GTON)",
    "setting_fee_deposit": "Комиссия на пополнение (%)",
    "setting_fee_payout": "Комиссия на вывод (%)",
    "setting_welcome_bonus": "Приветственный бонус (GTON)",
    "settings_changed": "✅ Настройка сохранена",
    "settings_enter_value": "Введите новое значение:",
    "settings_enter_number": "Введите число:",
    "settings_enter_json": "Введите JSON (например: [1,2,3,5,5,7,10]):",
    "settings_invalid_number": "❌ Введите число",
    "settings_invalid_json": "❌ Неверный формат JSON",
    
    # Languages
    "languages_title": "🌐 <b>Языки</b>",
    "languages_current": "Ваш язык: {flag} {name}",
    "languages_select": "Выберите язык интерфейса:",
    "languages_changed": "✅ Язык изменён",
    
    # Promocodes
    "promocodes_title": "🎁 <b>Промокоды</b>",
    "promo_type_gton": "🪙 GTON",
    "promo_type_subscription": "⭐ Подписка",
    "promo_type_discount": "💸 Скидка",
    "promo_stats_title": "📊 <b>Статистика промокодов</b>",
    "promo_stats_today": "📅 Сегодня: {count} активаций",
    "promo_stats_week": "📆 За неделю: {count} активаций",
    "promo_stats_gton": "🪙 Выдано GTON: {count}",
    "promo_stats_top": "<b>Топ промокодов:</b>",
    
    # Promocodes - List & View
    "promo_list_title": "🎁 <b>Промокоды</b>",
    "promo_activations": "Активаций",
    "filter_all": "Все",
    "promo_status_active": "Активен",
    "promo_status_disabled": "Отключён",
    "promo_status_expired": "Истёк",
    "promo_status_exhausted": "Лимит исчерпан",
    "promo_view_status": "Статус",
    "promo_view_type": "Тип",
    "promo_view_value": "Значение",
    "promo_view_activations": "Активации",
    "promo_view_dates": "Даты",
    "promo_view_conditions": "Условия",
    "promo_current": "Текущих",
    "promo_per_user": "На пользователя",
    "promo_starts": "Начало",
    "promo_expires": "Истекает",
    "promo_created": "Создан",
    "promo_only_new": "Только для новых",
    "promo_first_deposit": "Только первый депозит",
    "promo_min_balance": "Мин. баланс: {amount}",
    "promo_bound_to": "Для пользователя: {user}",
    "gton": "GTON",
    "days": "дней",
    
    # Promocodes - Edit buttons
    "promo_edit_value": "💰 Значение",
    "promo_edit_limits": "📊 Лимиты",
    "promo_edit_dates": "📅 Даты",
    "promo_edit_binding": "👤 Привязка",
    "promo_history": "📋 История",
    "promo_enable": "▶️ Включить",
    "promo_disable": "⏸ Отключить",
    "promo_delete": "🗑 Удалить",
    
    # Promocodes - Creation wizard
    "promo_create_value_title": "💰 <b>Создание: {type}</b>",
    "promo_create_value_gton": "Выберите количество GTON:",
    "promo_create_value_subscription": "Выберите дни подписки:",
    "promo_create_value_discount": "Выберите процент скидки:",
    "promo_create_code_title": "📝 <b>Промокод</b>",
    "promo_create_code_prompt": "Выберите вариант кода:",
    "promo_code_generate": "🎲 Сгенерировать",
    "promo_code_custom": "✏️ Ввести свой",
    "promo_enter_code": "Введите промокод (3-20 символов):",
    "promo_code_set": "✅ Код установлен: <code>{code}</code>",
    "promo_code_invalid_length": "❌ Код должен быть 3-20 символов",
    "promo_code_exists": "❌ Такой код уже существует",
    "promo_create_limits_title": "📊 <b>Лимиты активаций</b>",
    "promo_code": "Код",
    "promo_max_activations": "Макс. активаций",
    "promo_limit_total": "Всего",
    "promo_limit_per_user": "На пользователя",
    "promo_next": "Далее ➡️",
    "promo_create_dates_title": "📅 <b>Срок действия</b>",
    "promo_now": "Сейчас",
    "promo_never": "Бессрочно",
    "promo_no_expiry": "♾ Бессрочно",
    "promo_create_binding_title": "👤 <b>Привязка к пользователю</b>",
    "promo_only_new_users": "Только для новых пользователей",
    "promo_bind_user": "👤 Привязать к пользователю",
    "promo_bind_partner": "👥 Привязать к партнёру (рефералы)",
    "promo_for_all": "👥 Для всех",
    "promo_enter_partner_id": "Введите ID партнёра, ID пользователя, Telegram ID или @username:",
    "promo_partner_not_found": "❌ Партнёр не найден",
    "promo_partner_bound": "✅ Привязан к партнёру: {partner}\n\nПользователи, активировавшие этот промокод, станут рефералами этого партнёра.",
    "promo_finish": "✅ Создать промокод",
    "promo_enter_user_id": "Введите ID, Telegram ID или @username:",
    "promo_user_not_found": "❌ Пользователь не найден",
    "promo_user_bound": "✅ Привязан к: {user}",
    "promo_continue": "Продолжить ➡️",
    "promo_created_success": "✅ <b>Промокод создан!</b>",
    "promo_view": "👁 Просмотр",
    "promo_create_another": "➕ Создать ещё",
    
    # Promocodes - History & Delete
    "promo_history_title": "📋 <b>История: {code}</b>",
    "promo_no_activations": "Пока нет активаций",
    "promo_delete_confirm": "🗑 Удалить промокод <b>{code}</b>?\n\nЭто действие нельзя отменить.",
    "promo_delete_yes": "🗑 Да, удалить",
    "promo_deleted": "✅ Промокод удалён",
    "promocodes_active": "Активных: {count}",
    "promocodes_total_activations": "Всего активаций: {count}",
    "promocodes_create": "➕ Создать промокод",
    "promocodes_list": "📋 Список промокодов",
    "promocodes_stats": "📊 Статистика",
    "promocodes_empty": "Нет промокодов",
    "promocodes_not_found": "Промокод не найден",
    "promocodes_toggled": "Промокод {status}",
    "promocodes_select_reward": "Выберите тип награды:",
    "promocodes_enabled": "включён",
    "promocodes_disabled": "отключён",
    
    # Services
    "services_title": "📦 <b>Сервисы</b>",
    "services_empty": "Нет установленных сервисов.",
    "services_install_hint": "Для установки сервиса:\n1. Поместите папку сервиса в <code>services/</code>\n2. Перезапустите бота",
    "services_refresh": "🔄 Обновить",
    "services_not_found": "Сервис не найден",
    "services_version": "Версия: {version}",
    "services_author": "Автор: {author}",
    "services_status": "Статус: {status}",
    "services_installed": "Установлен: {date}",
    "services_active": "✅ Активен",
    "services_disabled": "❌ Отключён",
    "services_disable": "❌ Отключить",
    "services_enable": "✅ Включить",
    "services_author_unknown": "не указан",
    
    # Settings labels
    "setting_bot_name": "Название бота",
    "setting_support": "Поддержка",
    "setting_default_language": "Язык по умолчанию",
    "setting_gton_ton_rate": "1 GTON = X TON",
    "setting_min_deposit_gton": "Мин. депозит (GTON)",
    "setting_max_deposit_gton": "Макс. депозит (GTON)",
    "setting_fee_percent": "Комиссия (%)",
    "setting_welcome_bonus_gton": "Приветственный бонус (GTON)",
    "setting_referral_enabled": "Включена",
    "setting_commission_enabled": "Комиссии включены",
    "setting_level1": "Комиссия реферера (%)",
    "setting_partner_level1": "Комиссия партнёра (%)",
    "setting_level2": "Уровень 2 (%)",
    "setting_level2_enabled": "Уровень 2 включён",
    "setting_min_payout": "Мин. вывод (GTON)",
    "setting_fee_payout": "Комиссия вывода (%)",
    "setting_fee_deposit": "Комиссия пополнения (%)",
    "setting_min_deposit": "Мин. пополнение (GTON)",
    "setting_max_deposit": "Макс. пополнение (GTON)",
    "setting_welcome_bonus": "Приветственный бонус (GTON)",
    "setting_stars_enabled": "Stars включены",
    "setting_stars_rate": "Курс: 1 Star = X ₽",
    "setting_stars_min": "Мин. Stars",
    "setting_stars_max": "Макс. Stars",
    "setting_warnings_before_ban": "Предупреждений до бана",
    "setting_ban_duration": "Длительность бана (дней)",
    "setting_daily_enabled": "Включён",
    "setting_daily_rewards": "Награды (JSON)",
    "setting_notif_new_users": "Новые пользователи",
    "setting_notif_payments": "Платежи",
    "setting_notif_errors": "Ошибки",
    "setting_notif_channel": "Канал уведомлений",
    "setting_quiet_start": "Тихий режим с (час)",
    "setting_quiet_end": "Тихий режим до (час)",
    "setting_category_not_found": "Категория не найдена",
    "settings_general": "Общие",
    "settings_payments": "GTON и платежи",
    "settings_referral": "Реферальная система",
    "settings_moderation": "Модерация",
    "settings_daily_bonus": "Ежедневный бонус",
    "settings_notifications": "Уведомления",
    "settings_enter_number": "Введите число:",
    "settings_enter_json": "Введите JSON (например: [1,2,3,5,5,7,10]):",
    "settings_enter_value": "Введите новое значение:",
    
    # Time ago
    "time_just_now": "только что",
    "time_min_ago": "{min} мин назад",
    "time_hours_ago": "{hours} ч назад",
    
    # Moderation
    "mod_user_not_found": "Пользователь не найден",
    "mod_reason_3_warnings": "Автобан: 3 предупреждения",
    "mod_reason": "Причина: {reason}",
    "mod_warnings_count": "Предупреждений: {count}/3",
    "mod_temp_ban_reason": "Временный бан",
    "mod_perm_ban_reason": "Перманентный бан",
    "mod_until": "До: {date}",
    "mod_rules_violation": "Нарушение правил",
    "mod_no_history": "Нет записей",
    
    # Partners - Main
    "partners_title": "👥 <b>Партнёры</b>",
    "partners_total": "📊 Всего: {count}",
    "partners_active": "Активных: {count}",
    "partners_pending": "📝 Заявок: {count}",
    "partners_payouts_pending": "💸 На вывод: {count}",
    "partners_list": "📋 Список партнёров",
    "partners_applications": "📝 Заявки ({count})",
    "partners_payouts": "💸 Выводы ({count})",
    "partners_stats": "📊 Статистика",
    
    # Partners - Filters
    "partners_filter_all": "Все",
    "partners_filter_active": "Активные",
    "partners_filter_pending": "Ожидают",
    "partners_filter_rejected": "Отклонённые",
    
    # Partners - List
    "partners_list_title": "👥 <b>Список партнёров</b>",
    "partners_empty": "Нет партнёров",
    "partner_status_active": "✅",
    "partner_status_pending": "⏳",
    "partner_status_rejected": "❌",
    "partner_status_inactive": "🔴",
    
    # Partners - Card
    "partner_card_title": "👤 <b>Партнёр #{id}</b>",
    "partner_user": "👤 {name}",
    "partner_since": "📅 Партнёр с: {date}",
    "partner_status": "📊 Статус: {status}",
    "partner_status_text_active": "✅ Активен",
    "partner_status_text_pending": "⏳ Ожидает",
    "partner_status_text_rejected": "❌ Отклонён",
    "partner_status_text_inactive": "🔴 Неактивен",
    
    # Partners - Finance
    "partner_finance_title": "💰 <b>Финансы:</b>",
    "partner_balance": "Баланс: {amount} ₽",
    "partner_total_earned": "Всего заработано: {amount} ₽",
    "partner_withdrawn": "Выведено: {amount} ₽",
    
    # Partners - Referrals
    "partner_referrals_title": "👥 <b>Рефералы:</b>",
    "partner_referrals_total": "Всего: {count}",
    "partner_referrals_active": "Активных: {count}",
    "partner_referrals_earned": "Заработок от них: {amount} ₽",
    "partner_commission": "📈 Комиссия: {percent}%",
    
    # Partners - Actions
    "partner_action_payout": "💸 Выплатить",
    "partner_action_commission": "✏️ Комиссия",
    "partner_action_referrals": "👥 Рефералы",
    "partner_action_history": "📋 История",
    "partner_action_deactivate": "🚫 Деактивировать",
    "partner_action_activate": "✅ Активировать",
    
    # Partners - Commission
    "partner_commission_title": "✏️ <b>Изменить комиссию</b>",
    "partner_commission_current": "Текущая комиссия: {percent}%",
    "partner_commission_select": "Выберите новую комиссию:",
    "partner_commission_success": "✅ Комиссия изменена на {percent}%",
    
    # Partners - Applications
    "partners_apps_title": "📝 <b>Заявки на партнёрство</b>",
    "partners_apps_pending": "Ожидают рассмотрения: {count}",
    "partners_apps_empty": "Нет новых заявок",
    "partner_app_ago": "{time} назад",
    "partner_app_referrals": "Рефералов: {count}",
    "partner_app_spent": "Потратили: {amount} ₽",
    "partner_app_review": "👤 Рассмотреть",
    
    # Partners - Application Review
    "partner_review_title": "📝 <b>Заявка на партнёрство</b>",
    "partner_review_submitted": "📅 Подана: {date}",
    "partner_review_user_stats": "📊 <b>Статистика пользователя:</b>",
    "partner_review_member_since": "В системе с: {date}",
    "partner_review_own_spent": "Свои расходы: {amount} ₽",
    "partner_review_approve": "✅ Одобрить ({percent}%)",
    "partner_review_reject": "❌ Отклонить",
    
    # Partners - Payouts
    "partners_payouts_title": "💸 <b>Заявки на вывод</b>",
    "partners_payouts_waiting": "Ожидают: {count}",
    "partners_payouts_sum": "На сумму: {amount} ₽",
    "partners_payouts_empty": "Нет заявок на вывод",
    "partner_payout_method_card": "💳 Карта",
    "partner_payout_method_sbp": "📱 СБП",
    "partner_payout_process": "💳 Обработать",
    
    # Partners - Payout Process
    "partner_payout_title": "💸 <b>Вывод средств</b>",
    "partner_payout_partner": "Партнёр: {name} (#{id})",
    "partner_payout_amount": "Сумма: {amount} ₽",
    "partner_payout_method": "Способ: {method}",
    "partner_payout_details": "Реквизиты: {details}",
    "partner_payout_confirm": "✅ Выплачено",
    "partner_payout_reject": "❌ Отклонить",
    "partner_payout_success": "✅ Выплата подтверждена",
    "partner_payout_rejected": "❌ Заявка отклонена",
    
    # Partners - History
    "partner_history_title": "📋 <b>История выплат</b> #{id}",
    "partner_history_empty": "Нет выплат",
    "partner_history_paid": "✅ Выплачено",
    "partner_history_rejected": "❌ Отклонено",
    "partner_history_pending": "⏳ Ожидает",
    
    # Partners - Stats
    "partners_stats_title": "📊 <b>Статистика партнёрки</b>",
    "partners_stats_total": "👥 Всего партнёров: {count}",
    "partners_stats_active": "✅ Активных: {count}",
    "partners_stats_referrals": "👤 Всего рефералов: {count}",
    "partners_stats_paid_month": "💸 Выплачено за месяц: {amount} ₽",
    "partners_stats_paid_total": "💰 Выплачено всего: {amount} ₽",
    "partners_stats_top": "🏆 <b>Топ партнёров:</b>",
    
    # Partners - Notifications
    "notify_partner_approved": "🎉 <b>Заявка одобрена!</b>\n\nВы стали партнёром!\nВаша комиссия: {percent}%\n\nПриглашайте друзей и зарабатывайте!",
    "notify_partner_rejected": "❌ <b>Заявка отклонена</b>\n\nК сожалению, ваша заявка на партнёрство была отклонена.",
    "notify_partner_payout_done": "💸 <b>Выплата выполнена!</b>\n\nСумма: {amount} ₽\nСпособ: {method}\n\nСпасибо за сотрудничество!",
    "notify_partner_payout_rejected": "❌ <b>Заявка на вывод отклонена</b>\n\nСумма: {amount} ₽\nОбратитесь в поддержку для уточнения.",
    "notify_partner_deactivated": "🔴 <b>Партнёрство приостановлено</b>\n\nВаш партнёрский аккаунт был деактивирован.",
    "notify_partner_activated": "✅ <b>Партнёрство восстановлено</b>\n\nВаш партнёрский аккаунт снова активен!",
    
    # Users - Main
    "users_title": "👤 <b>Пользователи</b>",
    "users_total": "📊 Всего: {count}",
    "users_active": "Активных: {count}",
    "users_new": "Новых: +{count}",
    "users_recent": "Последние регистрации:",
    "users_search": "🔍 Поиск",
    "users_filters": "📊 Фильтры",
    
    # Users - Filters
    "filter_all": "Все",
    "filter_active": "Активные (7д)",
    "filter_today": "Новые (сегодня)",
    "filter_with_balance": "С балансом",
    "filter_blocked": "Заблокированные",
    
    # Users - Search
    "users_search_title": "🔍 <b>Поиск пользователя</b>",
    "users_search_prompt": "Введите ID, Telegram ID, @username или имя:",
    "users_search_not_found": "❌ Пользователь не найден",
    "users_search_results": "🔍 <b>Результаты поиска:</b>",
    "users_search_by_id": "По ID",
    "users_search_by_username": "По @username",
    "users_search_by_name": "По имени",
    
    # Users - Card
    "user_card_title": "👤 <b>Пользователь #{id}</b>",
    "user_telegram": "📱 @{username}",
    "user_telegram_no": "📱 Нет username",
    "user_name": "👤 {name}",
    "user_language": "🌐 Язык: {language}",
    "user_registered": "📅 Регистрация: {date}",
    "user_last_activity": "🕐 Последняя активность: {time}",
    "user_status_active": "✅ Активен",
    "user_status_blocked": "🚫 Заблокирован",
    
    # Users - Balance
    "user_balance_title": "💰 <b>Баланс:</b>",
    "user_balance_main": "Основной: {amount} GTON (~{fiat} ₽)",
    "user_balance_bonus": "Бонусный: {amount} GTON",
    
    # Users - Stats
    "user_stats_title": "📊 <b>Статистика:</b>",
    "user_stats_spent": "Потрачено: {amount} GTON",
    "user_stats_transactions": "Транзакций: {count}",
    "user_stats_deposits": "Пополнений: {count} ({amount} ₽)",
    
    # Users - Referral
    "user_referrer": "🤝 Реферер: {name} (#{id})",
    "user_referrer_none": "🤝 Реферер: нет",
    "user_referrals_count": "👥 Привёл: {count} чел.",
    
    # Users - Actions
    "user_action_balance": "💰 Баланс",
    "user_action_message": "📨 Сообщение",
    "user_action_moderation": "⚠️ Модерация",
    "user_action_transactions": "📋 Транзакции",
    "user_action_to_user": "👤 К пользователю",
    "user_new_balance": "💰 Новый баланс: {balance} GTON (~{fiat} ₽)",
    
    # Users - Balance Change
    "balance_change_title": "💰 <b>Изменить баланс</b>",
    "balance_change_user": "Пользователь: {name} (#{id})",
    "balance_change_current": "Текущий баланс: {amount} GTON (~{fiat} ₽)",
    "balance_add": "➕ Начислить",
    "balance_subtract": "➖ Списать",
    "balance_enter_amount": "Введите сумму GTON:",
    "balance_enter_reason": "Введите причину:",
    "balance_confirm": "Подтвердить {action} {amount} GTON?",
    "balance_success_add": "✅ Начислено {amount} GTON",
    "balance_success_subtract": "✅ Списано {amount} GTON",
    "balance_error_insufficient": "❌ Недостаточно средств",
    
    # Users - Message
    "message_title": "📨 <b>Сообщение пользователю</b>",
    "message_enter_text": "Введите текст сообщения:",
    "message_sent": "✅ Сообщение отправлено",
    "message_error": "❌ Ошибка отправки",
    
    # Users - Transactions
    "transactions_title": "📋 <b>Транзакции</b> #{id}",
    "transactions_empty": "Нет транзакций",
    "transaction_deposit": "💳 Пополнение",
    "transaction_usage": "🔥 Списание",
    "transaction_bonus": "🎁 Бонус",
    "transaction_refund": "↩️ Возврат",
    "transaction_referral": "🤝 Реферальная комиссия",
    "transaction_promocode": "🎁 Промокод",
    
    # Users - Pagination
    "page_info": "Страница {current} из {total}",
    "page_prev": "◀️ Назад",
    "page_next": "Вперёд ▶️",
    
    # Users - Notifications to user
    "notify_balance_added": "💰 <b>Баланс пополнен</b>\n\nВам начислено {amount} GTON.\nНовый баланс: {balance} GTON",
    "notify_balance_subtracted": "💸 <b>Списание с баланса</b>\n\nСписано {amount} GTON.\nНовый баланс: {balance} GTON",
    "notify_warning": "⚠️ <b>Предупреждение</b>\n\nВам выдано предупреждение.\nПричина: {reason}\n\nПредупреждений: {current}/{max}",
    "notify_ban_temp": "🚫 <b>Временная блокировка</b>\n\nВаш аккаунт заблокирован на {days} дней.\nПричина: {reason}\n\nРазблокировка: {until}",
    "notify_ban_perm": "⛔ <b>Блокировка аккаунта</b>\n\nВаш аккаунт заблокирован навсегда.\nПричина: {reason}",
    "notify_unban": "✅ <b>Разблокировка</b>\n\nВаш аккаунт разблокирован. Добро пожаловать обратно!",
    "notify_warning_autoban": "🚫 <b>Автоматическая блокировка</b>\n\nВы получили {max} предупреждений.\nАккаунт заблокирован на {days} дней.",
    
    # Stats - Main
    "stats_title": "📊 <b>Статистика</b>",
    "stats_users_btn": "👥 Пользователи",
    "stats_finance_btn": "💰 Финансы",
    "stats_bonus_btn": "🎁 Ежедневный бонус",
    "stats_referrals_btn": "🤝 Рефералы",
    "stats_analytics_btn": "📈 Аналитика",
    "stats_refresh": "🔄 Обновить",
    
    # Stats - Periods
    "period_today": "Сегодня",
    "period_week": "Неделя",
    "period_month": "Месяц",
    "period_all": "Всё время",
    
    # Stats - Users
    "stats_users_title": "👥 <b>Пользователи</b>",
    "stats_users_total": "📊 Всего: {count}",
    "stats_users_today": "Сегодня: +{count}",
    "stats_users_week": "За неделю: +{count}",
    "stats_users_month": "За месяц: +{count}",
    "stats_activity": "📈 <b>Активность:</b>",
    "stats_active_7d": "Активных (7д): {count} ({percent}%)",
    "stats_active_30d": "Активных (30д): {count} ({percent}%)",
    "stats_inactive": "Неактивных: {count}",
    "stats_blocked": "🚫 Заблокировано: {count}",
    "stats_registrations": "📅 <b>Регистрации (7 дней):</b>",
    
    # Stats - Finance
    "stats_finance_title": "💰 <b>Финансы</b> ({period})",
    "stats_total_balance": "💳 Общий баланс: {amount} токенов",
    "stats_revenue": "📈 <b>Выручка:</b>",
    "stats_revenue_today": "Сегодня: {amount} ₽",
    "stats_revenue_period": "За период: {amount} ₽",
    "stats_transactions": "📊 Транзакций: {count}",
    "stats_avg_check": "💵 Средний чек: {amount} ₽",
    "stats_spent": "🔥 Потрачено: {amount} токенов",
    "stats_top_spenders": "🏆 <b>Топ плательщиков:</b>",
    
    # Stats - Daily Bonus
    "stats_bonus_title": "🎁 <b>Ежедневный бонус</b> ({period})",
    "stats_claims_today": "📊 Собрали сегодня: {count}",
    "stats_claims_period": "📈 За период: {count}",
    "stats_tokens_given": "🪙 Выдано токенов: {amount}",
    "stats_streaks": "🔥 <b>Стрики:</b>",
    "stats_streak_avg": "Средний: {days} дней",
    "stats_streak_max": "Максимальный: {days} дней",
    "stats_streak_active": "Активных: {count}",
    
    # Stats - Referrals
    "stats_referrals_title": "🤝 <b>Рефералы</b> ({period})",
    "stats_referrals_total": "📊 Всего рефералов: {count}",
    "stats_referrals_period": "📈 За период: +{count}",
    "stats_partners_active": "👥 Активных партнёров: {count}",
    "stats_commissions_paid": "💰 Выплачено комиссий: {amount} ₽",
    "stats_top_referrers": "🏆 <b>Топ рефереров:</b>",
    
    # Stats - Analytics
    "stats_analytics_title": "📈 <b>Аналитика</b> ({period})",
    "stats_events_total": "📊 Событий: {count}",
    "stats_unique_users": "👥 Уникальных пользователей: {count}",
    "stats_categories": "📁 <b>Категории:</b>",
    "stats_popular_events": "🔥 <b>Популярные события:</b>",
    
    # Days of week
    "day_mon": "Пн",
    "day_tue": "Вт",
    "day_wed": "Ср",
    "day_thu": "Чт",
    "day_fri": "Пт",
    "day_sat": "Сб",
    "day_sun": "Вс",
    
    # Broadcast - Main
    "broadcast_title": "📢 <b>Рассылки</b>",
    "broadcast_stats": "📊 <b>Статистика:</b>",
    "broadcast_sent_today": "📤 Отправлено сегодня: {count}",
    "broadcast_delivered": "✅ Доставлено: {count} ({percent}%)",
    "broadcast_triggers_active": "🔄 Автоматических: {count} активно",
    "broadcast_scheduled": "📅 Запланировано: {count}",
    
    # Broadcast - Buttons
    "broadcast_create": "✏️ Создать рассылку",
    "broadcast_history": "📋 История рассылок",
    "broadcast_triggers": "⚙️ Автоматические",
    
    # Broadcast - Create
    "broadcast_create_title": "✏️ <b>Создание рассылки</b>",
    "broadcast_create_prompt": "Отправьте текст сообщения для рассылки.",
    "broadcast_create_hint": "Поддерживается HTML и переменные:\n• {name} — имя пользователя\n• {username} — @username\n• {balance} — баланс",
    
    # Broadcast - Target
    "broadcast_select_target": "👥 <b>Выберите аудиторию</b>",
    "broadcast_select_target_hint": "Выберите кому отправить рассылку:",
    
    # Broadcast - Preview
    "broadcast_preview_title": "📢 <b>Предпросмотр рассылки</b>",
    "broadcast_preview_text": "📝 Текст:",
    "broadcast_preview_target": "👥 Аудитория: {target}",
    "broadcast_preview_recipients": "📊 Получателей: {count}",
    "broadcast_preview_media": "📎 Медиа: {type}",
    "broadcast_preview_buttons": "🔘 Кнопок: {count}",
    
    # Broadcast - Actions
    "broadcast_send_now": "✅ Отправить сейчас",
    "broadcast_schedule": "📅 Запланировать",
    "broadcast_ab_test": "🔀 A/B тест",
    "broadcast_add_button": "🔘 Добавить кнопку",
    "broadcast_add_media": "📎 Добавить медиа",
    "broadcast_started": "✅ Рассылка запущена!",
    
    # Broadcast - History
    "broadcast_history_title": "📋 <b>История рассылок</b>",
    "broadcast_history_empty": "Нет рассылок",
    "broadcast_view_title": "📢 <b>Рассылка #{id}</b>",
    "broadcast_status": "📊 Статус: {status}",
    "broadcast_created_at": "📅 Создана: {date}",
    "broadcast_started_at": "🚀 Запущена: {date}",
    "broadcast_completed_at": "✅ Завершена: {date}",
    "broadcast_sent_count": "📤 Отправлено: {sent}/{total}",
    "broadcast_delivered_count": "✅ Доставлено: {count}",
    "broadcast_failed_count": "❌ Ошибок: {count}",
    "broadcast_delivery_rate": "📈 Доставляемость: {rate}%",
    "broadcast_text_preview": "📝 Текст:",
    "broadcast_pause": "⏸ Приостановить",
    "broadcast_resume": "▶️ Продолжить",
    "broadcast_cancel": "❌ Отменить",
    "broadcast_paused": "⏸ Рассылка приостановлена",
    "broadcast_resumed": "▶️ Рассылка продолжена",
    "broadcast_cancelled": "❌ Рассылка отменена",
    "broadcast_status_completed": "✅ Завершена",
    "broadcast_status_sending": "📤 Отправляется",
    "broadcast_status_paused": "⏸ Приостановлена",
    "broadcast_status_scheduled": "📅 Запланирована",
    "broadcast_status_cancelled": "❌ Отменена",
    "broadcast_status_draft": "📝 Черновик",
    "broadcast_coming_soon": "🔧 Функция в разработке",
    
    # Audiences
    "audience_all": "👥 Все пользователи",
    "audience_active_7d": "🟢 Активные (7 дней)",
    "audience_active_30d": "🟡 Активные (30 дней)",
    "audience_with_balance": "💰 С балансом > 0",
    "audience_with_subscription": "⭐ С подпиской",
    "audience_new_week": "🆕 Новые (неделя)",
    "audience_inactive_30d": "😴 Неактивные (30+ дней)",
    
    # Broadcast - Schedule
    "broadcast_schedule_title": "📅 <b>Запланировать рассылку</b>",
    "broadcast_schedule_prompt": "Введите дату и время отправки:",
    "broadcast_schedule_format": "Формат: ДД.ММ.ГГГГ ЧЧ:ММ\nПример: 25.12.2024 10:00",
    "broadcast_schedule_error": "❌ Неверный формат. Используйте: ДД.ММ.ГГГГ ЧЧ:ММ",
    "broadcast_schedule_past": "❌ Дата должна быть в будущем",
    "broadcast_scheduled_success": "✅ Рассылка запланирована на {time}",
    
    # Broadcast - A/B Test
    "broadcast_ab_title": "🔀 <b>A/B тестирование</b>",
    "broadcast_ab_prompt": "Введите текст для варианта B:\n\n(Вариант A — текущий текст)",
    
    # Broadcast - Button
    "broadcast_button_title": "🔘 <b>Добавить кнопку</b>",
    "broadcast_button_prompt": "Введите текст кнопки и URL:",
    "broadcast_button_format": "Формат: Текст кнопки | https://url.com",
    "broadcast_button_added": "✅ Кнопка добавлена",
    "broadcast_button_error": "❌ Неверный формат. Используйте: Текст | URL",
    
    # Broadcast - Media
    "broadcast_media_title": "📎 <b>Добавить медиа</b>",
    "broadcast_media_prompt": "Отправьте фото, видео или GIF:",
    "broadcast_media_added": "✅ Медиа добавлено ({type})",
    "broadcast_media_error": "❌ Отправьте фото, видео или GIF",
    
    # Triggers
    "triggers_title": "⚙️ <b>Автоматические рассылки</b>",
    "triggers_empty": "Нет настроенных триггеров",
    "trigger_create": "➕ Создать триггер",
    "trigger_select_type": "📌 <b>Выберите тип триггера:</b>",
    "trigger_create_title": "⚙️ <b>Создание триггера: {type}</b>",
    "trigger_enter_name": "Введите название триггера:",
    "trigger_enter_text": "Введите текст сообщения:",
    "trigger_created": "✅ Триггер создан и активирован!",
    
    # Trigger types
    "trigger_type_low_balance": "💰 Низкий баланс",
    "trigger_type_low_balance_desc": "Отправка пользователям с низким балансом",
    "trigger_type_subscription_expiring": "⏰ Подписка истекает",
    "trigger_type_subscription_expiring_desc": "Отправка за N дней до истечения подписки",
    "trigger_type_subscription_expired": "❌ Подписка истекла",
    "trigger_type_subscription_expired_desc": "Отправка после истечения подписки",
    "trigger_type_inactive": "😴 Неактивные",
    "trigger_type_inactive_desc": "Отправка неактивным пользователям",
    "trigger_type_welcome": "👋 Приветствие",
    "trigger_type_welcome_desc": "Отправка новым пользователям",
    "trigger_type_after_deposit": "💳 После депозита",
    "trigger_type_after_deposit_desc": "Отправка после пополнения баланса",
    
    # Trigger condition labels
    "cond_balance_less_than": "Баланс меньше",
    "cond_days_before_expiry": "Дней до истечения",
    "cond_hours_after_expiry": "Часов после истечения",
    "cond_inactive_days": "Дней неактивности",
    "cond_exclude_new_users_days": "Исключить новых (дней)",
    "cond_hours_after_registration": "Часов после регистрации",
    "cond_only_if_inactive": "Только неактивным",
    "cond_min_amount": "Мин. сумма",
    "cond_first_deposit_only": "Только первое пополнение",
    
    # Trigger messages
    "trigger_not_found": "Триггер не найден",
    "trigger_no_matching": "📭 <b>Нет подходящих пользователей</b>\n\nТриггер: {name}\nУсловия не соответствуют ни одному пользователю.",
    "trigger_send_complete": "✅ <b>Рассылка завершена</b>\n\nТриггер: {name}\n\n📤 Отправлено: {sent}\n❌ Ошибок: {failed}",
    "trigger_status_active": "Активен",
    "trigger_status_disabled": "Отключён",
    "trigger_toggled": "Триггер {status}",
    "trigger_yes": "Да",
    "trigger_no": "Нет",
    
    # Trigger edit
    "trigger_edit_text_title": "📝 <b>Редактирование текста</b>\n\nТриггер: {name}\n\n",
    "trigger_edit_text_current": "Текущий текст:\n",
    "trigger_edit_text_empty": "Текст не задан\n",
    "trigger_edit_text_prompt": "Отправьте новый текст:",
    "trigger_edit_media_title": "🖼 <b>Редактирование медиа</b>\n\nТриггер: {name}\n\n",
    "trigger_edit_media_current": "Текущее медиа: {type}\n\n",
    "trigger_edit_media_none": "Медиа не прикреплено\n\n",
    "trigger_edit_media_prompt": "Отправьте фото, видео или GIF:",
    "trigger_media_removed": "Медиа удалено",
    "trigger_edit_buttons_title": "🔘 <b>Редактирование кнопок</b>\n\nТриггер: {name}\n\n",
    "trigger_edit_buttons_current": "Текущие кнопки:\n",
    "trigger_edit_buttons_none": "Кнопок нет\n",
    "trigger_buttons_removed": "Кнопки удалены",
    "trigger_edit_cond_title": "🎯 <b>Редактирование условий</b>\n\nТриггер: {name}\nТип: {type}\n\n",
    "trigger_edit_cond_current": "Текущие условия:\n",
    "trigger_edit_behavior_title": "🔄 <b>Редактирование поведения</b>\n\nТриггер: {name}\n\n",
    "trigger_edit_behavior_current": "Текущие настройки:\n",
    "trigger_edit_param": "Параметр: {label}\nТекущее значение: <code>{value}</code>\n\nВведите новое значение:",
    
    # Behavior labels
    "behavior_max_sends": "Макс. отправок на пользователя",
    "behavior_repeat_days": "Повтор через (дней)",
    "behavior_send_time": "Время отправки",
    "behavior_send_time_hint": "Формат: 9-21 (час начала - час конца)",
    "behavior_delay": "Задержка перед отправкой",
    "behavior_delay_hint": "Минут",
    
    # Triggers list
    "triggers_auto_desc": "Триггеры автоматически отправляют сообщения пользователям при определённых условиях.",
    "triggers_type": "Тип: {type}",
    "triggers_conditions": "Условия для триггера:",
    "trigger_conditions": "🎯 Условия",
    "trigger_view_status": "📊 Статус: {status}",
    "trigger_stats_title": "Статистика",
    "trigger_stats_sent": "Отправлено",
    "trigger_stats_delivered": "Доставлено",
    "trigger_message": "Сообщение",
    "trigger_btn_text": "✏️ Текст",
    "trigger_btn_media": "📎 Медиа",
    "trigger_btn_buttons": "🔘 Кнопки",
    "trigger_btn_conditions": "🎯 Условия",
    "trigger_btn_behavior": "🔄 Поведение",
    "trigger_btn_enable": "▶️ Включить",
    "trigger_btn_disable": "⏸ Отключить",
    "triggers_stats": "📊 Всего: {total} | Активных: {active}",
    "trigger_deleted": "🗑 Триггер удалён",
    "trigger_text_updated": "✅ Текст триггера обновлён",
    "trigger_media_invalid": "❌ Отправьте фото, видео или GIF",
    "trigger_media_added": "✅ Медиа добавлено ({type})",
    "trigger_button_format_error": "❌ Неверный формат. Используйте: Текст | URL",
    "trigger_button_added": "✅ Кнопка добавлена",
    "trigger_cond_updated": "✅ Условие обновлено: {param} = {value}",
    "trigger_behavior_updated": "✅ Настройка обновлена",
    "trigger_error_number": "❌ Введите число",
    "trigger_error_time_format": "❌ Формат: 9-21",
    "trigger_error_minutes": "❌ Введите число минут",
    
    # Moderation - Main Menu
    "moderation_title": "🛡 <b>Модерация</b>",
    "moderation_stats": "📊 <b>Статистика:</b>",
    "moderation_banned": "🚫 Забанено: {count}",
    "moderation_banned_temp": "Временных: {count}",
    "moderation_banned_perm": "Перманентных: {count}",
    "moderation_warnings": "⚠️ С предупреждениями: {count}",
    "moderation_actions_today": "📋 Действий сегодня: {count}",
    
    # Moderation - Buttons
    "moderation_search": "🔍 Найти пользователя",
    "moderation_banned_list": "🚫 Забаненные ({count})",
    "moderation_warnings_list": "⚠️ Предупреждения ({count})",
    "moderation_log": "📋 Журнал действий",
    
    # Moderation - Search
    "moderation_search_prompt": "🔍 <b>Поиск пользователя</b>",
    "moderation_search_hint": "Введите ID, Telegram ID, @username или имя:",
    
    # Moderation - Banned List
    "moderation_banned_title": "🚫 <b>Забаненные пользователи</b>",
    "moderation_banned_count": "Всего: {count}",
    "moderation_banned_empty": "Нет забаненных пользователей",
    "moderation_ban_forever": "навсегда",
    "moderation_ban_until": "до {date}",
    "moderation_filter_temp": "Временные",
    "moderation_filter_perm": "Перманентные",
    
    # Moderation - Warnings List
    "moderation_warnings_title": "⚠️ <b>Пользователи с предупреждениями</b>",
    "moderation_warnings_count": "Всего: {count}",
    "moderation_warnings_empty": "Нет пользователей с предупреждениями",
    
    # Moderation - Log
    "moderation_log_title": "📋 <b>Журнал модерации</b>",
    "moderation_log_empty": "Нет записей",
    "moderation_filter_bans": "Баны",
    "moderation_filter_unbans": "Разбаны",
    "moderation_filter_warns": "⚠️",
    
    # Moderation - User Card
    "moderation_user_title": "🛡 <b>Модерация #{id}</b>",
    "moderation_user_name": "👤 {name}",
    "moderation_user_registered": "📅 Регистрация: {date}",
    "moderation_user_status_title": "📊 <b>Статус:</b>",
    "moderation_status_active": "✅ Активен",
    "moderation_status_banned": "🚫 Забанен",
    "moderation_user_warnings": "⚠️ Предупреждений: {current}/{max}",
    "moderation_user_last_active_days": "🕐 Был {days} дн. назад",
    "moderation_user_last_active_hours": "🕐 Был {hours} ч. назад",
    "moderation_user_last_active_minutes": "🕐 Был {minutes} мин. назад",
    "moderation_user_ban_info": "🚫 <b>Информация о бане:</b>",
    "moderation_user_ban_reason": "Причина: {reason}",
    "moderation_user_recent": "📋 <b>Последние действия:</b>",
    
    # Moderation - Actions
    "moderation_action_warn": "⚠️ Предупреждение",
    "moderation_action_ban": "🚫 Бан",
    "moderation_action_ban_perm": "⛔ Перманентный бан",
    "moderation_action_unban": "✅ Разбанить",
    "moderation_action_revoke_warn": "↩️ Снять предупреждение",
    "moderation_action_history": "📋 История",
    
    # Moderation - Alerts
    "moderation_no_warnings": "У пользователя нет активных предупреждений",
    "moderation_warn_revoked": "✅ Предупреждение снято",
    "moderation_warned": "✅ Предупреждение выдано",
    "moderation_unbanned": "✅ Пользователь разбанен",
    "moderation_select_reason": "⚠️ <b>Выберите причину:</b>",
    "moderation_enter_reason": "Введите причину:",
    "moderation_enter_days": "Введите срок бана (дней):",
    
    # Moderation - Reasons
    "reason_spam": "📢 Спам",
    "reason_abuse": "🤬 Оскорбления",
    "reason_fraud": "🚨 Мошенничество",
    "reason_terms_violation": "📜 Нарушение правил",
    "reason_other": "❓ Другое",
    "mod_autoban_info": "🚫 Автобан: {days} дней",
    "mod_autoban_reason": "(лимит 3 предупреждения)",
    
    # Moderation - Notifications
    "notify_unban_auto": "✅ <b>Разблокировка</b>\n\nСрок вашей блокировки истёк. Добро пожаловать обратно!",
}

# ==================== PROMOCODE ====================

PROMOCODE = {
    "enter_code": "🎁 <b>Введите промокод:</b>",
    "activated": "✅ <b>Промокод активирован!</b>",
    "reward_tokens": "🎁 Вам начислено: {amount} токенов",
    "reward_subscription": "⭐ Вам активирована подписка {plan} на {days} дней",
    "reward_discount": "💸 Скидка {percent}% применена",
    "new_balance": "💰 Новый баланс: {balance} токенов",
    
    # Errors
    "invalid": "❌ Промокод недействителен",
    "expired": "❌ Срок действия промокода истёк",
    "already_used": "❌ Вы уже использовали этот промокод",
    "limit_reached": "❌ Лимит активаций промокода исчерпан",
    "new_users_only": "❌ Промокод только для новых пользователей",
    "first_deposit_only": "❌ Промокод только для первого пополнения",
}

# ==================== MODERATION MESSAGES ====================

MODERATION = {
    # Reasons
    "reason_spam": "Спам",
    "reason_abuse": "Оскорбления",
    "reason_fraud": "Мошенничество",
    "reason_terms_violation": "Нарушение правил",
    "reason_other": "Другое",
    
    # Warnings
    "warning_issued": "⚠️ Вам выдано предупреждение",
    "warning_reason": "Причина: {reason}",
    "warning_count": "Предупреждений: {current}/{max}",
    "warning_notice": "При получении {max} предупреждений ваш аккаунт будет временно заблокирован.",
    
    # Ban
    "banned_title": "🚫 Ваш аккаунт заблокирован",
    "banned_reason": "Причина: {reason}",
    "banned_permanent": "Срок: навсегда",
    "banned_temporary": "Срок: {days} дней",
    "banned_until": "Разблокировка: {date}",
    "banned_days_left": "До разблокировки: {days} дней",
    "banned_appeal": "Если вы считаете это ошибкой, обратитесь в поддержку.",
    
    # Unban
    "unbanned": "✅ Ваш аккаунт разблокирован",
}
