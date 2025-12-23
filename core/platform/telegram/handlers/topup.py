"""
Top Up Handler — Пополнение баланса GTON
"""
import asyncio
from decimal import Decimal, InvalidOperation

from telegram import Update
from telegram.ext import ContextTypes
from loguru import logger

from core.locales import t
from core.platform.telegram.utils import (
    get_or_create_user, 
    get_user_language,
    get_user_balance_with_fiat,
    format_gton,
    build_keyboard
)
from core.payments.converter import currency_converter
from core.payments.service import payment_service
from core.payments.providers.manager import provider_manager
from core.plugins.core_api import CoreAPI


# Predefined amounts for CryptoBot by currency
CRYPTO_AMOUNTS = {
    "TON": [1, 3, 5, 10, 25, 50],
    "USDT": [5, 10, 25, 50, 100, 250],
    "BTC": [0.0005, 0.001, 0.002, 0.005, 0.01, 0.02],
    "ETH": [0.005, 0.01, 0.02, 0.05, 0.1, 0.2],
    "LTC": [0.1, 0.25, 0.5, 1, 2, 5],
    "BNB": [0.01, 0.025, 0.05, 0.1, 0.25, 0.5],
    "TRX": [50, 100, 250, 500, 1000, 2500],
    "USDC": [5, 10, 25, 50, 100, 250],
}

# Currency display info
CRYPTO_INFO = {
    "TON": {"icon": "💎", "name": "Toncoin"},
    "USDT": {"icon": "💵", "name": "Tether"},
    "BTC": {"icon": "₿", "name": "Bitcoin"},
    "ETH": {"icon": "⟠", "name": "Ethereum"},
    "LTC": {"icon": "Ł", "name": "Litecoin"},
    "BNB": {"icon": "🔶", "name": "BNB"},
    "TRX": {"icon": "⚡", "name": "TRON"},
    "USDC": {"icon": "💲", "name": "USD Coin"},
}


async def topup_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle top_up callback"""
    query = update.callback_query
    await query.answer()
    
    telegram_user = update.effective_user
    user_id = await get_or_create_user(telegram_user.id, telegram_user)
    lang = await get_user_language(user_id)
    
    data = query.data
    parts = data.split(":")
    
    # Route to specific handler
    if len(parts) >= 2:
        action = parts[1]
        
        if action == "providers":
            await show_providers(query, user_id, lang)
            return
        elif action == "crypto":
            if len(parts) >= 3:
                await show_crypto_amounts(query, user_id, lang, parts[2])
            else:
                await show_crypto_amounts(query, user_id, lang, "TON")
            return
        elif action == "currencies":
            await show_all_currencies(query, user_id, lang)
            return
        elif action == "pay":
            if len(parts) >= 4:
                await create_crypto_payment(query, user_id, lang, parts[2], parts[3])
            return
        elif action == "custom":
            if len(parts) >= 3:
                await ask_custom_amount(query, user_id, lang, parts[2])
            return
        elif action == "check":
            if len(parts) >= 3:
                await check_payment_status(query, user_id, lang, parts[2])
            return
        elif action == "stars":
            await show_stars_menu(query, user_id, lang)
            return
        elif action == "stars_pay":
            if len(parts) >= 3:
                await create_stars_invoice(query, user_id, lang, int(parts[2]))
            return
        elif action == "stars_custom":
            await ask_stars_custom_amount(query, user_id, lang)
            return

        elif action == "sbp":
            await show_sbp_menu(query, user_id, lang)
            return

        elif action == "sbp_pay":
            if len(parts) >= 3:
                await create_sbp_payment(query, user_id, lang, int(parts[2]))
            return

        elif action == "sbp_custom":
            await ask_sbp_custom_amount(query, user_id, lang)
            return
    
    # Default: show main top-up menu
    await show_topup_menu(query, user_id, lang)


async def show_topup_menu(query, user_id: int, lang: str):
    """Show main top-up menu with balance"""
    gton_balance, fiat_balance = await get_user_balance_with_fiat(user_id)
    
    # Format balance
    if fiat_balance is not None:
        fiat_str = f"{fiat_balance:,.0f}".replace(",", " ")
        balance_str = f"{format_gton(gton_balance)} GTON (~{fiat_str} ₽)"
    else:
        balance_str = f"{format_gton(gton_balance)} GTON"
    
    # Get rates info
    rates_info = ""
    try:
        gton_rates = await currency_converter.get_gton_rates()
        if "RUB" in gton_rates:
            rub_rate = gton_rates["RUB"]
            rates_info = f"\n💱 Курс: 1 GTON ≈ {rub_rate:,.0f} ₽".replace(",", " ")
    except:
        pass
    
    text = t(lang, "TOP_UP.title") + "\n\n"
    text += t(lang, "TOP_UP.current_balance_gton", balance=balance_str) + rates_info + "\n\n"
    text += "Выберите способ оплаты:"
    
    # Check available providers
    providers = provider_manager.get_available_providers()
    
    keyboard = []
    
    if provider_manager.is_provider_available("cryptobot"):
        keyboard.append([{
            "text": "🤖 CryptoBot (TON, USDT)", 
            "callback_data": "top_up:crypto:TON"
        }])

    if provider_manager.is_provider_available("platega"):
        keyboard.append([{
            "text": "🏦 СБП (Platega)",
            "callback_data": "top_up:sbp"
        }])
    
    # Telegram Stars
    from core.payments.providers.stars import stars_provider
    if await stars_provider.is_enabled():
        keyboard.append([{
            "text": "⭐ Telegram Stars", 
            "callback_data": "top_up:stars"
        }])
    
    # TODO: Add more providers
    # if provider_manager.is_provider_available("yookassa"):
    #     keyboard.append([{
    #         "text": "💳 Банковская карта", 
    #         "callback_data": "top_up:card"
    #     }])
    
    if not keyboard:
        text += "\n\n⚠️ Платёжные системы временно недоступны"
    
    keyboard.append([{"text": t(lang, "TOP_UP.enter_promocode"), "callback_data": "promocode"}])
    keyboard.append([{"text": t(lang, "COMMON.back"), "callback_data": "main_menu"}])
    
    await query.edit_message_text(
        text,
        reply_markup=build_keyboard(keyboard),
        parse_mode="HTML"
    )


async def show_sbp_menu(query, user_id: int, lang: str):
    """Show SBP amounts menu"""
    gton_balance, fiat_balance = await get_user_balance_with_fiat(user_id)

    text = "🏦 <b>Пополнение через СБП</b>\n\n"
    text += f"💰 Баланс: {format_gton(gton_balance)} GTON\n\n"
    text += "Выберите сумму в рублях:\n\n"

    amounts = [50, 100, 200, 500, 1000, 2000, 5000, 10000]

    # Show conversion info for first 3 amounts
    try:
        gton_rates = await currency_converter.get_gton_rates()
        rub_rate = Decimal(str(gton_rates.get("RUB", 100)))
    except Exception:
        rub_rate = Decimal("100")

    for rub_amount in amounts[:3]:
        gton_amount = Decimal(str(rub_amount)) / rub_rate if rub_rate else Decimal("0")
        text += f"• {rub_amount} ₽ → ~{format_gton(gton_amount)} GTON\n"

    keyboard = []
    row = []
    for amount in amounts:
        row.append({
            "text": f"{amount} ₽",
            "callback_data": f"top_up:sbp_pay:{amount}",
        })
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    keyboard.append([
        {"text": "✏️ Своя сумма", "callback_data": "top_up:sbp_custom"}
    ])
    keyboard.append([
        {"text": t(lang, "COMMON.back"), "callback_data": "top_up"}
    ])

    await query.edit_message_text(
        text,
        reply_markup=build_keyboard(keyboard),
        parse_mode="HTML",
    )


async def create_sbp_payment(query, user_id: int, lang: str, rub_amount: int):
    """Create SBP payment via Platega"""
    try:
        gton_rates = await currency_converter.get_gton_rates()
        rub_rate = Decimal(str(gton_rates.get("RUB", 100)))
        gton_amount = Decimal(str(rub_amount)) / rub_rate if rub_rate else Decimal("0")
    except Exception as e:
        await query.answer(f"Ошибка конвертации: {e}", show_alert=True)
        return

    await query.edit_message_text(
        "⏳ Создаём платёж...",
        parse_mode="HTML",
    )

    result = await payment_service.create_payment(
        user_id=user_id,
        amount_gton=gton_amount,
        provider="platega",
        currency="RUB",
    )

    if not result.success:
        text = f"❌ <b>Ошибка создания платежа</b>\n\n{result.error}"
        keyboard = [[{"text": t(lang, "COMMON.back"), "callback_data": "top_up:sbp"}]]
        await query.edit_message_text(
            text,
            reply_markup=build_keyboard(keyboard),
            parse_mode="HTML",
        )
        return

    text = "✅ <b>Платёж создан!</b>\n\n"
    text += f"💵 Сумма: {rub_amount} ₽\n"
    text += f"💰 Получите: ~{format_gton(gton_amount)} GTON\n\n"
    text += "Нажмите кнопку ниже для оплаты через СБП:\n"
    text += "<i>⏰ Платёж действителен 15 минут</i>"

    keyboard = [
        [{"text": f"💳 Оплатить {rub_amount} ₽", "url": result.payment_url}],
        [{"text": "🔄 Проверить оплату", "callback_data": f"top_up:check:{result.payment_uuid}"}],
        [{"text": t(lang, "COMMON.back"), "callback_data": "top_up:sbp"}],
    ]

    await query.edit_message_text(
        text,
        reply_markup=build_keyboard(keyboard),
        parse_mode="HTML",
    )

    logger.info(f"SBP payment created: {result.payment_uuid} for user {user_id}, {rub_amount} RUB")


async def ask_sbp_custom_amount(query, user_id: int, lang: str):
    """Ask user to enter custom SBP amount"""
    core_api = CoreAPI("core")
    await core_api.set_user_state(user_id, "sbp_custom_amount", {})

    text = "✏️ <b>Введите сумму в рублях</b>\n\n"
    text += "Минимум: 50 ₽\n"
    text += "Максимум: 100 000 ₽\n\n"
    text += "Введите число:"

    keyboard = [[{"text": "❌ Отмена", "callback_data": "top_up:sbp"}]]

    await query.edit_message_text(
        text,
        reply_markup=build_keyboard(keyboard),
        parse_mode="HTML",
    )


async def handle_sbp_custom_input(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, lang: str):
    """Handle custom SBP amount input"""
    core_api = CoreAPI("core")
    text_input = update.message.text.strip() if update.message and update.message.text else ""

    try:
        rub_amount = int(text_input.replace(" ", "").replace(",", ""))
    except ValueError:
        await update.message.reply_text("❌ Введите целое число")
        return

    if rub_amount < 50:
        await update.message.reply_text("❌ Минимальная сумма: 50 ₽")
        return
    if rub_amount > 100000:
        await update.message.reply_text("❌ Максимальная сумма: 100 000 ₽")
        return

    await core_api.clear_user_state(user_id)

    try:
        gton_rates = await currency_converter.get_gton_rates()
        rub_rate = Decimal(str(gton_rates.get("RUB", 100)))
        gton_amount = Decimal(str(rub_amount)) / rub_rate if rub_rate else Decimal("0")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка конвертации: {e}")
        return

    loading_msg = await update.message.reply_text(
        "⏳ Создаём платёж...",
        parse_mode="HTML",
    )

    result = await payment_service.create_payment(
        user_id=user_id,
        amount_gton=gton_amount,
        provider="platega",
        currency="RUB",
    )

    if not result.success:
        await loading_msg.edit_text(
            f"❌ <b>Ошибка создания платежа</b>\n\n{result.error}",
            parse_mode="HTML",
        )
        return

    text = "✅ <b>Платёж создан!</b>\n\n"
    text += f"💵 Сумма: {rub_amount} ₽\n"
    text += f"💰 Получите: ~{format_gton(gton_amount)} GTON\n\n"
    text += "Нажмите кнопку ниже для оплаты через СБП:\n"
    text += "<i>⏰ Платёж действителен 15 минут</i>"

    keyboard = [
        [{"text": f"💳 Оплатить {rub_amount} ₽", "url": result.payment_url}],
        [{"text": "🔄 Проверить оплату", "callback_data": f"top_up:check:{result.payment_uuid}"}],
        [{"text": t(lang, "COMMON.back"), "callback_data": "top_up:sbp"}],
    ]

    await loading_msg.edit_text(
        text,
        reply_markup=build_keyboard(keyboard),
        parse_mode="HTML",
    )

    logger.info(f"SBP custom payment created: {result.payment_uuid} for user {user_id}, {rub_amount} RUB")


async def show_crypto_amounts(query, user_id: int, lang: str, asset: str = "TON"):
    """Show crypto payment amounts"""
    gton_balance, fiat_balance = await get_user_balance_with_fiat(user_id)
    
    # Get currency info
    info = CRYPTO_INFO.get(asset, {"icon": "💰", "name": asset})
    amounts = CRYPTO_AMOUNTS.get(asset, [1, 5, 10, 25, 50, 100])
    
    # Get GTON rates
    try:
        gton_rates = await currency_converter.get_gton_rates()
        asset_rate = gton_rates.get(asset, Decimal("1"))
    except:
        asset_rate = Decimal("1")
    
    text = f"🤖 <b>Пополнение через CryptoBot</b>\n\n"
    text += f"💰 Баланс: {format_gton(gton_balance)} GTON\n"
    text += f"{info['icon']} Валюта: {info['name']} ({asset})\n\n"
    text += "Выберите сумму пополнения:\n\n"
    
    # Show conversion info for first 3 amounts
    for amount in amounts[:3]:
        gton_amount = Decimal(str(amount)) / asset_rate if asset_rate else Decimal("0")
        text += f"• {amount} {asset} → ~{format_gton(gton_amount)} GTON\n"
    
    # Amount buttons
    keyboard = []
    row = []
    for amount in amounts:
        # Format amount nicely
        if amount >= 1:
            amount_str = f"{int(amount)}" if amount == int(amount) else f"{amount}"
        else:
            amount_str = f"{amount}"
        
        row.append({
            "text": f"{amount_str} {asset}",
            "callback_data": f"top_up:pay:{asset}:{amount}"
        })
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    # Currency selection - row 1 (popular)
    keyboard.append([
        {"text": f"{'• ' if asset == 'TON' else ''}💎 TON{'  •' if asset == 'TON' else ''}", "callback_data": "top_up:crypto:TON"},
        {"text": f"{'• ' if asset == 'USDT' else ''}💵 USDT{'  •' if asset == 'USDT' else ''}", "callback_data": "top_up:crypto:USDT"},
        {"text": f"{'• ' if asset == 'BTC' else ''}₿ BTC{'  •' if asset == 'BTC' else ''}", "callback_data": "top_up:crypto:BTC"},
    ])
    
    # Currency selection - row 2
    keyboard.append([
        {"text": f"{'• ' if asset == 'ETH' else ''}⟠ ETH{'  •' if asset == 'ETH' else ''}", "callback_data": "top_up:crypto:ETH"},
        {"text": f"{'• ' if asset == 'LTC' else ''}Ł LTC{'  •' if asset == 'LTC' else ''}", "callback_data": "top_up:crypto:LTC"},
        {"text": f"{'• ' if asset == 'TRX' else ''}⚡ TRX{'  •' if asset == 'TRX' else ''}", "callback_data": "top_up:crypto:TRX"},
    ])
    
    # Custom amount button
    keyboard.append([
        {"text": "✏️ Своя сумма", "callback_data": f"top_up:custom:{asset}"},
    ])
    
    # More currencies button
    keyboard.append([
        {"text": "📋 Все валюты", "callback_data": "top_up:currencies"},
    ])
    
    keyboard.append([{"text": t(lang, "COMMON.back"), "callback_data": "top_up"}])
    
    await query.edit_message_text(
        text,
        reply_markup=build_keyboard(keyboard),
        parse_mode="HTML"
    )


async def show_all_currencies(query, user_id: int, lang: str):
    """Show all available currencies"""
    text = "🤖 <b>Выберите криптовалюту</b>\n\n"
    text += "Доступные валюты для пополнения:\n\n"
    
    for asset, info in CRYPTO_INFO.items():
        text += f"{info['icon']} <b>{info['name']}</b> ({asset})\n"
    
    keyboard = []
    
    # Row 1
    keyboard.append([
        {"text": "💎 TON", "callback_data": "top_up:crypto:TON"},
        {"text": "💵 USDT", "callback_data": "top_up:crypto:USDT"},
    ])
    
    # Row 2
    keyboard.append([
        {"text": "₿ BTC", "callback_data": "top_up:crypto:BTC"},
        {"text": "⟠ ETH", "callback_data": "top_up:crypto:ETH"},
    ])
    
    # Row 3
    keyboard.append([
        {"text": "Ł LTC", "callback_data": "top_up:crypto:LTC"},
        {"text": "🔶 BNB", "callback_data": "top_up:crypto:BNB"},
    ])
    
    # Row 4
    keyboard.append([
        {"text": "⚡ TRX", "callback_data": "top_up:crypto:TRX"},
        {"text": "💲 USDC", "callback_data": "top_up:crypto:USDC"},
    ])
    
    keyboard.append([{"text": t(lang, "COMMON.back"), "callback_data": "top_up"}])
    
    await query.edit_message_text(
        text,
        reply_markup=build_keyboard(keyboard),
        parse_mode="HTML"
    )


async def create_crypto_payment(query, user_id: int, lang: str, asset: str, amount_str: str):
    """Create CryptoBot payment"""
    try:
        amount = Decimal(amount_str)
    except:
        await query.answer("Неверная сумма", show_alert=True)
        return
    
    # Convert crypto amount to GTON
    conv_result = await currency_converter.convert_to_gton(amount, asset)
    if not conv_result.success:
        await query.answer(f"Ошибка конвертации: {conv_result.error}", show_alert=True)
        return
    
    gton_amount = conv_result.gton_amount
    
    # Show loading
    await query.edit_message_text(
        "⏳ Создаём платёж...",
        parse_mode="HTML"
    )
    
    # Create payment
    result = await payment_service.create_payment(
        user_id=user_id,
        amount_gton=gton_amount,
        provider="cryptobot",
        currency=asset
    )
    
    if not result.success:
        text = f"❌ <b>Ошибка создания платежа</b>\n\n{result.error}"
        keyboard = [[{"text": t(lang, "COMMON.back"), "callback_data": "top_up:crypto:" + asset}]]
        await query.edit_message_text(
            text,
            reply_markup=build_keyboard(keyboard),
            parse_mode="HTML"
        )
        return
    
    # Success - show payment link
    info = CRYPTO_INFO.get(asset, {"icon": "💰", "name": asset})
    
    text = f"✅ <b>Платёж создан!</b>\n\n"
    text += f"{info['icon']} Сумма: {amount} {asset}\n"
    text += f"💰 Получите: ~{format_gton(gton_amount)} GTON\n\n"
    text += f"Нажмите кнопку ниже для оплаты через @CryptoBot:\n"
    
    keyboard = [
        [{"text": f"💳 Оплатить {amount} {asset}", "url": result.payment_url}],
        [{"text": "🔄 Проверить оплату", "callback_data": f"top_up:check:{result.payment_uuid}"}],
        [{"text": t(lang, "COMMON.back"), "callback_data": "top_up:crypto:" + asset}]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=build_keyboard(keyboard),
        parse_mode="HTML"
    )
    
    logger.info(f"Payment created: {result.payment_uuid} for user {user_id}, {amount} {asset}")


async def check_payment_status(query, user_id: int, lang: str, payment_uuid: str):
    """Check payment status"""
    from core.database import get_db
    from core.database.models import Payment
    from sqlalchemy import select
    
    try:
        async with get_db() as session:
            result = await session.execute(
                select(Payment).where(
                    Payment.uuid == payment_uuid,
                    Payment.user_id == user_id
                )
            )
            payment = result.scalar_one_or_none()
        
        if not payment:
            await query.answer("Платёж не найден", show_alert=True)
            return
        
        # Already completed - show success
        if payment.status == "completed":
            gton_balance, fiat_balance = await get_user_balance_with_fiat(user_id)
            text = f"✅ <b>Платёж успешно завершён!</b>\n\n"
            text += f"💰 Ваш баланс: {format_gton(gton_balance)} GTON (~{fiat_balance:.0f} ₽)"
            
            keyboard = [[{"text": "🏠 Главное меню", "callback_data": "main_menu"}]]
            await query.edit_message_text(
                text,
                reply_markup=build_keyboard(keyboard),
                parse_mode="HTML"
            )
            return
        
        if payment.status == "expired":
            await query.answer("⏰ Платёж истёк. Создайте новый.", show_alert=True)
            return
        
        if payment.status == "failed":
            await query.answer(f"❌ Ошибка: {payment.error_message or 'Неизвестная ошибка'}", show_alert=True)
            return
        
        # Check with provider
        provider = provider_manager.get_provider(payment.provider)
        if provider and payment.provider_payment_id:
            from core.payments.providers.base import PaymentStatus
            
            try:
                status = await provider.check_payment(payment.provider_payment_id)
            except Exception as e:
                logger.error(f"Error checking payment status: {e}")
                await query.answer("⚠️ Ошибка проверки. Попробуйте позже.", show_alert=True)
                return
            
            if status == PaymentStatus.COMPLETED:
                # Confirm payment with retry for database locks
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        success = await payment_service.confirm_payment(
                            payment_uuid=payment_uuid,
                            provider_payment_id=payment.provider_payment_id
                        )
                        if success:
                            break
                    except Exception as e:
                        if "database is locked" in str(e).lower() and attempt < max_retries - 1:
                            logger.warning(f"Database locked on attempt {attempt + 1}, retrying...")
                            await asyncio.sleep(0.5)  # Wait before retry
                            continue
                        else:
                            logger.error(f"Error confirming payment: {e}")
                            await query.answer("⚠️ Ошибка подтверждения. Попробуйте ещё раз.", show_alert=True)
                            return
                
                # Check if payment was actually completed
                async with get_db() as session:
                    result = await session.execute(
                        select(Payment).where(Payment.uuid == payment_uuid)
                    )
                    updated_payment = result.scalar_one()
                
                if updated_payment.status == "completed":
                    gton_balance, fiat_balance = await get_user_balance_with_fiat(user_id)
                    text = f"✅ <b>Оплата получена!</b>\n\n"
                    text += f"💰 Начислено: {format_gton(payment.amount_gton)} GTON\n"
                    text += f"💳 Баланс: {format_gton(gton_balance)} GTON (~{fiat_balance:.0f} ₽)"
                    
                    keyboard = [[{"text": "🏠 Главное меню", "callback_data": "main_menu"}]]
                    await query.edit_message_text(
                        text,
                        reply_markup=build_keyboard(keyboard),
                        parse_mode="HTML"
                    )
                    return
                else:
                    await query.answer("⚠️ Ошибка зачисления. Обратитесь в поддержку.", show_alert=True)
                    return
                    
            elif status == PaymentStatus.EXPIRED:
                async with get_db() as session:
                    result = await session.execute(
                        select(Payment).where(Payment.uuid == payment_uuid)
                    )
                    p = result.scalar_one_or_none()
                    if p:
                        p.status = "expired"
                await query.answer("⏰ Платёж истёк", show_alert=True)
                return
        
        # Still pending
        await query.answer("⏳ Ожидаем оплату... Нажмите кнопку оплаты.", show_alert=True)
        
    except Exception as e:
        logger.error(f"Error in check_payment_status: {e}")
        await query.answer("⚠️ Произошла ошибка. Попробуйте позже.", show_alert=True)


async def ask_custom_amount(query, user_id: int, lang: str, asset: str):
    """Ask user to enter custom amount"""
    from core.database.models import UserService
    from sqlalchemy import select
    
    info = CRYPTO_INFO.get(asset, {"icon": "💰", "name": asset})
    
    # Get min/max for this currency
    amounts = CRYPTO_AMOUNTS.get(asset, [1, 5, 10, 25, 50, 100])
    min_amount = min(amounts) / 2  # Allow half of minimum preset
    max_amount = max(amounts) * 10  # Allow 10x of maximum preset
    
    text = f"✏️ <b>Введите сумму</b>\n\n"
    text += f"{info['icon']} Валюта: {info['name']} ({asset})\n\n"
    text += f"Введите сумму от {min_amount} до {max_amount} {asset}:\n\n"
    text += f"<i>Например: 15 или 7.5</i>"
    
    keyboard = [[{"text": t(lang, "COMMON.back"), "callback_data": f"top_up:crypto:{asset}"}]]
    
    await query.edit_message_text(
        text,
        reply_markup=build_keyboard(keyboard),
        parse_mode="HTML"
    )
    
    # Save state for message handler
    async with get_db() as session:
        result = await session.execute(
            select(UserService).where(
                UserService.user_id == user_id,
                UserService.service_id == "core"
            )
        )
        user_service = result.scalar_one_or_none()
        
        if not user_service:
            from core.database.models import UserService as US
            user_service = US(
                user_id=user_id,
                service_id="core",
                state="topup_custom_amount",
                state_data={"asset": asset}
            )
            session.add(user_service)
        else:
            user_service.state = "topup_custom_amount"
            user_service.state_data = {"asset": asset}


async def handle_custom_amount_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Handle custom amount message from user.
    Returns True if message was handled, False otherwise.
    """
    from core.database.models import UserService
    from sqlalchemy import select
    
    telegram_user = update.effective_user
    user_id = await get_or_create_user(telegram_user.id, telegram_user)
    
    # Check if user is in custom amount state
    async with get_db() as session:
        result = await session.execute(
            select(UserService).where(
                UserService.user_id == user_id,
                UserService.service_id == "core",
                UserService.state == "topup_custom_amount"
            )
        )
        user_service = result.scalar_one_or_none()
        
        if not user_service:
            return False
        
        asset = user_service.state_data.get("asset", "TON") if user_service.state_data else "TON"
        
        # Clear state
        user_service.state = None
        user_service.state_data = None
    
    lang = await get_user_language(user_id)
    text = update.message.text.strip()
    
    # Parse amount
    try:
        # Replace comma with dot for decimal
        text = text.replace(",", ".")
        amount = Decimal(text)
        
        if amount <= 0:
            await update.message.reply_text(
                "❌ Сумма должна быть больше 0",
                parse_mode="HTML"
            )
            return True
        
        # Check limits
        amounts = CRYPTO_AMOUNTS.get(asset, [1, 5, 10, 25, 50, 100])
        min_amount = Decimal(str(min(amounts))) / 2
        max_amount = Decimal(str(max(amounts))) * 10
        
        if amount < min_amount:
            await update.message.reply_text(
                f"❌ Минимальная сумма: {min_amount} {asset}",
                parse_mode="HTML"
            )
            return True
        
        if amount > max_amount:
            await update.message.reply_text(
                f"❌ Максимальная сумма: {max_amount} {asset}",
                parse_mode="HTML"
            )
            return True
        
        # Create payment
        await create_custom_payment(update, user_id, lang, asset, amount)
        return True
        
    except (ValueError, InvalidOperation):
        await update.message.reply_text(
            "❌ Некорректная сумма. Введите число, например: 15 или 7.5",
            parse_mode="HTML"
        )
        return True


async def create_custom_payment(update: Update, user_id: int, lang: str, asset: str, amount: Decimal):
    """Create payment with custom amount"""
    # Convert crypto amount to GTON
    conv_result = await currency_converter.convert_to_gton(amount, asset)
    if not conv_result.success:
        await update.message.reply_text(
            f"❌ Ошибка конвертации: {conv_result.error}",
            parse_mode="HTML"
        )
        return
    
    gton_amount = conv_result.gton_amount
    
    # Show loading
    loading_msg = await update.message.reply_text(
        "⏳ Создаём платёж...",
        parse_mode="HTML"
    )
    
    # Create payment
    result = await payment_service.create_payment(
        user_id=user_id,
        amount_gton=gton_amount,
        provider="cryptobot",
        currency=asset
    )
    
    if not result.success:
        await loading_msg.edit_text(
            f"❌ <b>Ошибка создания платежа</b>\n\n{result.error}",
            parse_mode="HTML"
        )
        return
    
    # Success - show payment link
    info = CRYPTO_INFO.get(asset, {"icon": "💰", "name": asset})
    
    # Format amount nicely
    if amount == int(amount):
        amount_str = str(int(amount))
    else:
        amount_str = f"{amount:.8f}".rstrip('0').rstrip('.')
    
    text = f"✅ <b>Платёж создан!</b>\n\n"
    text += f"{info['icon']} Сумма: {amount_str} {asset}\n"
    text += f"💰 Получите: ~{format_gton(gton_amount)} GTON\n\n"
    text += f"Нажмите кнопку ниже для оплаты через @CryptoBot:"
    
    keyboard = [
        [{"text": f"💳 Оплатить {amount_str} {asset}", "url": result.payment_url}],
        [{"text": "🔄 Проверить оплату", "callback_data": f"top_up:check:{result.payment_uuid}"}],
        [{"text": t(lang, "COMMON.back"), "callback_data": f"top_up:crypto:{asset}"}]
    ]
    
    await loading_msg.edit_text(
        text,
        reply_markup=build_keyboard(keyboard),
        parse_mode="HTML"
    )
    
    logger.info(f"Custom payment created: {result.payment_uuid} for user {user_id}, {amount} {asset}")


# =============================================================================
# TELEGRAM STARS
# =============================================================================

# Predefined Stars amounts
STARS_AMOUNTS = [10, 25, 50, 100, 250, 500, 1000]


async def show_stars_menu(query, user_id: int, lang: str):
    """Show Telegram Stars payment menu"""
    from core.payments.providers.stars import stars_provider
    
    gton_balance, fiat_balance = await get_user_balance_with_fiat(user_id)
    
    # Get rates
    rub_rate = await stars_provider.get_stars_to_rub_rate()
    gton_rate = await stars_provider.get_stars_to_gton_rate()
    min_stars, max_stars = await stars_provider.get_limits()
    
    text = "⭐ <b>Пополнение через Telegram Stars</b>\n\n"
    text += f"💰 Баланс: {format_gton(gton_balance)} GTON\n"
    text += f"💱 Курс: 1 ⭐ = {rub_rate} ₽\n\n"
    text += "Выберите сумму пополнения:\n\n"
    
    # Show conversion examples
    for amount in [10, 50, 100]:
        gton = await stars_provider.stars_to_gton(amount)
        rub = rub_rate * amount
        text += f"• {amount} ⭐ = {rub:.0f} ₽ → {format_gton(gton)} GTON\n"
    
    # Amount buttons
    keyboard = []
    row = []
    for amount in STARS_AMOUNTS:
        if amount < min_stars or amount > max_stars:
            continue
        gton = await stars_provider.stars_to_gton(amount)
        row.append({
            "text": f"{amount} ⭐",
            "callback_data": f"top_up:stars_pay:{amount}"
        })
        if len(row) == 3:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    # Custom amount button
    keyboard.append([{"text": "✏️ Своя сумма", "callback_data": "top_up:stars_custom"}])
    keyboard.append([{"text": t(lang, "COMMON.back"), "callback_data": "top_up"}])
    
    await query.edit_message_text(
        text,
        reply_markup=build_keyboard(keyboard),
        parse_mode="HTML"
    )


async def create_stars_invoice(query, user_id: int, lang: str, stars_amount: int):
    """Create and send Stars invoice"""
    from telegram import LabeledPrice
    from core.payments.providers.stars import stars_provider
    
    # Validate
    is_valid, error = await stars_provider.validate_amount(stars_amount)
    if not is_valid:
        await query.answer(error, show_alert=True)
        return
    
    # Calculate GTON
    gton_amount = await stars_provider.stars_to_gton(stars_amount)
    
    # Create invoice payload (will be returned in successful_payment)
    payload = f"stars_topup:{user_id}:{stars_amount}"
    
    # Send invoice
    try:
        await query.message.reply_invoice(
            title="Пополнение баланса",
            description=f"Пополнение на {format_gton(gton_amount)} GTON",
            payload=payload,
            provider_token="",  # Empty for Stars
            currency="XTR",
            prices=[LabeledPrice(label="GTON", amount=stars_amount)],
        )
        
        # Delete the menu message
        await query.message.delete()
        
        logger.info(f"Stars invoice sent: user={user_id}, stars={stars_amount}, gton={gton_amount}")
        
    except Exception as e:
        logger.error(f"Failed to send Stars invoice: {e}")
        await query.answer(f"Ошибка: {e}", show_alert=True)


async def ask_stars_custom_amount(query, user_id: int, lang: str):
    """Ask user to enter custom Stars amount"""
    from core.plugins.core_api import CoreAPI
    from core.payments.providers.stars import stars_provider
    
    min_stars, max_stars = await stars_provider.get_limits()
    rub_rate = await stars_provider.get_stars_to_rub_rate()
    
    # Set state
    core_api = CoreAPI("core")
    await core_api.set_user_state(user_id, "stars_custom_amount", {})
    
    text = "✏️ <b>Введите количество Stars</b>\n\n"
    text += f"💱 Курс: 1 ⭐ = {rub_rate} ₽\n\n"
    text += f"Минимум: {min_stars} ⭐\n"
    text += f"Максимум: {max_stars} ⭐\n\n"
    text += "Введите число:"
    
    keyboard = [
        [{"text": "❌ Отмена", "callback_data": "top_up:stars"}]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=build_keyboard(keyboard),
        parse_mode="HTML"
    )


async def handle_stars_custom_input(update, context, user_id: int, lang: str):
    """Handle custom Stars amount input"""
    from telegram import LabeledPrice
    from core.plugins.core_api import CoreAPI
    from core.payments.providers.stars import stars_provider
    
    core_api = CoreAPI("core")
    text_input = update.message.text.strip()
    
    # Parse amount
    try:
        stars_amount = int(text_input)
    except ValueError:
        await update.message.reply_text("❌ Введите целое число")
        return
    
    # Validate
    is_valid, error = await stars_provider.validate_amount(stars_amount)
    if not is_valid:
        await update.message.reply_text(f"❌ {error}")
        return
    
    # Clear state
    await core_api.clear_user_state(user_id)
    
    # Calculate GTON
    gton_amount = await stars_provider.stars_to_gton(stars_amount)
    
    # Create invoice payload
    payload = f"stars_topup:{user_id}:{stars_amount}"
    
    # Send invoice
    try:
        await update.message.reply_invoice(
            title="Пополнение баланса",
            description=f"Пополнение на {format_gton(gton_amount)} GTON",
            payload=payload,
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="GTON", amount=stars_amount)],
        )
        
        logger.info(f"Stars custom invoice sent: user={user_id}, stars={stars_amount}, gton={gton_amount}")
        
    except Exception as e:
        logger.error(f"Failed to send Stars invoice: {e}")
        await update.message.reply_text(f"❌ Ошибка: {e}")
