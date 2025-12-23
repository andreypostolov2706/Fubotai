"""
Admin Services Management
"""
import json
from sqlalchemy import select

from core.locales import t
from core.database import get_db
from core.platform.telegram.utils import build_keyboard


async def admin_services(query, lang: str, action: str = None, params: str = None):
    """Admin services handler"""
    if action == "view" and params:
        await view_service(query, lang, params)
    elif action == "config" and params:
        await view_service_config(query, lang, params)
    elif action == "edit_config" and params:
        # params format: service_id:key
        parts = params.split(":", 1)
        if len(parts) == 2:
            await edit_config_key(query, lang, parts[0], parts[1])
    elif action == "disable" and params:
        await toggle_service(query, lang, params, False)
    elif action == "enable" and params:
        await toggle_service(query, lang, params, True)
    else:
        await services_list(query, lang)


async def services_list(query, lang: str):
    """Show services list"""
    from core.database.models import Service
    
    async with get_db() as session:
        result = await session.execute(select(Service))
        services = result.scalars().all()
    
    text = t(lang, "ADMIN.services_title") + "\n\n"
    
    keyboard = []
    
    if not services:
        text += t(lang, "ADMIN.services_empty") + "\n\n"
        text += t(lang, "ADMIN.services_install_hint")
    else:
        for service in services:
            status = "✅" if service.status == "active" else "❌"
            text += f"{status} <b>{service.name}</b> v{service.version}\n"
            text += f"   ID: <code>{service.id}</code>\n\n"
            
            # Кнопка для каждого сервиса
            keyboard.append([{
                "text": f"{service.icon or '📦'} {service.name}",
                "callback_data": f"admin:services:view:{service.id}"
            }])
    
    keyboard.append([{"text": t(lang, "ADMIN.services_refresh"), "callback_data": "admin:services"}])
    keyboard.append([{"text": t(lang, "COMMON.back"), "callback_data": "admin"}])
    
    await query.edit_message_text(
        text,
        reply_markup=build_keyboard(keyboard),
        parse_mode="HTML"
    )


async def view_service(query, lang: str, service_id: str):
    """View service details"""
    from core.database.models import Service
    
    async with get_db() as session:
        result = await session.execute(
            select(Service).where(Service.id == service_id)
        )
        service = result.scalar_one_or_none()
    
    if not service:
        await query.answer(t(lang, "ADMIN.services_not_found"), show_alert=True)
        return
    
    status = t(lang, "ADMIN.services_active") if service.status == "active" else t(lang, "ADMIN.services_disabled")
    author = service.author or t(lang, "ADMIN.services_author_unknown")
    
    text = f"📦 <b>{service.name}</b>\n\n"
    text += f"ID: <code>{service.id}</code>\n"
    text += t(lang, "ADMIN.services_version", version=service.version) + "\n"
    text += t(lang, "ADMIN.services_author", author=author) + "\n"
    text += t(lang, "ADMIN.services_status", status=status) + "\n"
    if service.installed_at:
        text += t(lang, "ADMIN.services_installed", date=service.installed_at.strftime('%d.%m.%Y %H:%M')) + "\n"
    
    if service.description:
        text += f"\n📝 {service.description}"
    
    keyboard = []
    
    # Кнопка настроек конфига
    keyboard.append([{
        "text": "⚙️ Настройки",
        "callback_data": f"admin:services:config:{service_id}"
    }])
    
    if service.status == "active":
        keyboard.append([{
            "text": t(lang, "ADMIN.services_disable"), 
            "callback_data": f"admin:services:disable:{service_id}"
        }])
    else:
        keyboard.append([{
            "text": t(lang, "ADMIN.services_enable"), 
            "callback_data": f"admin:services:enable:{service_id}"
        }])
    
    keyboard.append([{"text": t(lang, "COMMON.back"), "callback_data": "admin:services"}])
    
    await query.edit_message_text(
        text,
        reply_markup=build_keyboard(keyboard),
        parse_mode="HTML"
)


CONFIG_KEY_NAMES = {
    "fal_api_key": "🔑 API ключ fal.ai",
    "margin_multiplier": "💰 Маржа",
    "prices": "💵 Цены",
    "gallery_channel_id": "📢 ID канала галереи",
    "gallery_enabled": "🖼 Публикация в галерею",
    "referral_bonus_enabled": "👥 Реферальный бонус",
    "referral_bonus_percent": "📊 Процент рефералу",
}


async def view_service_config(query, lang: str, service_id: str):
    """View and edit service config"""
    from core.database.models import Service
    
    async with get_db() as session:
        result = await session.execute(
            select(Service).where(Service.id == service_id)
        )
        service = result.scalar_one_or_none()
    
    if not service:
        await query.answer("Сервис не найден", show_alert=True)
        return
    
    config = service.config or {}
    
    text = f"⚙️ <b>Настройки {service.name}</b>\n\n"
    
    # Отображаем конфиг
    for key, value in config.items():
        key_name = CONFIG_KEY_NAMES.get(key, key)
        
        if key == "fal_api_key":
            display_value = value[:10] + "..." if value else "❌ Не задан"
        elif key == "prices":
            display_value = f"{len(value)} позиций"
        elif key == "margin_multiplier":
            display_value = f"{int(value * 100)}%" if value else "0%"
        elif isinstance(value, bool):
            display_value = "✅ Да" if value else "❌ Нет"
        elif isinstance(value, (int, float)):
            display_value = str(value)
        else:
            display_value = str(value) if value else "—"
        
        text += f"• <b>{key_name}</b>: {display_value}\n"
    
    keyboard = []
    
    # Кнопки для редактирования основных настроек
    editable_keys = ["fal_api_key", "margin_multiplier", "gallery_channel_id", "gallery_enabled"]
    
    for key in editable_keys:
        if key in config:
            key_name = CONFIG_KEY_NAMES.get(key, key)
            keyboard.append([{
                "text": f"✏️ {key_name}",
                "callback_data": f"admin:services:edit_config:{service_id}:{key}"
            }])
    
    keyboard.append([{"text": "◀️ Назад", "callback_data": f"admin:services:view:{service_id}"}])
    
    await query.edit_message_text(
        text,
        reply_markup=build_keyboard(keyboard),
        parse_mode="HTML"
    )


async def edit_config_key(query, lang: str, service_id: str, key: str):
    """Start editing a config key"""
    from core.database.models import Service
    from core.plugins.core_api import CoreAPI
    
    async with get_db() as session:
        result = await session.execute(
            select(Service).where(Service.id == service_id)
        )
        service = result.scalar_one_or_none()
    
    if not service:
        await query.answer("Сервис не найден", show_alert=True)
        return
    
    config = service.config or {}
    current_value = config.get(key, "")
    
    # Для boolean - сразу переключаем
    if key == "gallery_enabled":
        new_value = not config.get(key, False)
        config[key] = new_value
        
        async with get_db() as session:
            result = await session.execute(
                select(Service).where(Service.id == service_id)
            )
            service = result.scalar_one_or_none()
            if service:
                service.config = config
                await session.commit()
        
        await query.answer(f"{'✅ Включено' if new_value else '❌ Выключено'}")
        await view_service_config(query, lang, service_id)
        return
    
    # Для остальных - запрашиваем ввод
    key_name = CONFIG_KEY_NAMES.get(key, key)
    text = f"✏️ <b>{key_name}</b>\n\n"
    
    if key == "fal_api_key":
        text += "Введите API ключ fal.ai:\n\n"
        text += f"Текущий: <code>{current_value[:20]}...</code>" if current_value else "Текущий: ❌ не задан"
    elif key == "margin_multiplier":
        current_percent = f"{int(float(current_value) * 100)}%" if current_value else "0%"
        text += "Введите маржу (например, 0.3 для 30%):\n\n"
        text += f"Текущая: <b>{current_percent}</b>"
    elif key == "gallery_channel_id":
        text += "Введите ID канала для галереи:\n"
        text += "<i>Формат: -1001234567890 или @channel_name</i>\n\n"
        text += f"Текущий: <code>{current_value}</code>" if current_value else "Текущий: ❌ не задан"
    
    # Сохраняем состояние для ввода
    api = CoreAPI("core")
    user_id = query.from_user.id
    
    # Получаем внутренний user_id
    from core.platform.telegram.utils import get_or_create_user
    internal_user_id = await get_or_create_user(user_id, query.from_user)
    
    await api.set_user_state(internal_user_id, "admin_service_config_edit", {
        "service_id": service_id,
        "key": key,
    })
    
    keyboard = [
        [{"text": "❌ Отмена", "callback_data": f"admin:services:config:{service_id}"}]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=build_keyboard(keyboard),
        parse_mode="HTML"
    )


async def toggle_service(query, lang: str, service_id: str, enable: bool):
    """Enable or disable a service"""
    from core.plugins.registry import service_registry
    
    if enable:
        # Включаем сервис и загружаем в память
        success = await service_registry.enable(service_id)
        if not success:
            await query.answer("❌ Не удалось включить сервис")
            return
    else:
        # Выключаем сервис и выгружаем из памяти
        success = await service_registry.disable(service_id)
        if not success:
            await query.answer("❌ Не удалось выключить сервис")
            return
    
    status = "включен" if enable else "выключен"
    await query.answer(f"✅ Сервис {status}")
    await view_service(query, lang, service_id)


async def handle_service_config_input(update, context, user_id: int, lang: str, service_id: str, key: str):
    """Handle text input for service config editing"""
    from core.database.models import Service
    from core.plugins.core_api import CoreAPI
    
    value = update.message.text.strip()
    
    async with get_db() as session:
        result = await session.execute(
            select(Service).where(Service.id == service_id)
        )
        service = result.scalar_one_or_none()
        
        if not service:
            await update.message.reply_text("❌ Сервис не найден")
            return
        
        config = service.config or {}
        
        # Валидация и преобразование значения
        if key == "margin_multiplier":
            try:
                value = float(value)
                if value < 0 or value > 100:
                    await update.message.reply_text("❌ Маржа должна быть от 0 до 100 (например, 3 для 300%)")
                    return
            except ValueError:
                await update.message.reply_text("❌ Введите число (например, 0.3)")
                return
        elif key == "gallery_channel_id":
            # Может быть числом или @username
            if value.startswith("@"):
                pass  # OK
            else:
                try:
                    value = int(value)
                except ValueError:
                    await update.message.reply_text("❌ Введите ID канала (число) или @username")
                    return
        
        # Обновляем конфиг
        config[key] = value
        service.config = config
        
        # Помечаем JSON-поле как изменённое
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(service, "config")
        
        await session.commit()
    
    # Очищаем состояние
    api = CoreAPI("core")
    await api.clear_user_state(user_id)
    
    await update.message.reply_text(
        f"✅ Настройка <b>{key}</b> обновлена!",
        parse_mode="HTML"
    )
    
    # Показываем конфиг сервиса
    # Создаём фейковый query для вызова view_service_config
    # Это не идеально, но работает
    keyboard = [
        [{"text": "◀️ К настройкам", "callback_data": f"admin:services:config:{service_id}"}]
    ]
    
    await update.message.reply_text(
        "Нажмите кнопку для возврата к настройкам:",
        reply_markup=build_keyboard(keyboard)
    )
