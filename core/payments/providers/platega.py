"""
Platega Payment Provider

Integration with Platega.io for SBP (СБП) payments.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Optional, List

import aiohttp
from loguru import logger

from .base import BasePaymentProvider, ProviderPaymentResult, PaymentStatus, WebhookResult


PLATEGA_API_URL = "https://app.platega.io"


class PlategalProvider(BasePaymentProvider):
    PAYMENT_METHOD_SBP = 2

    @property
    def id(self) -> str:
        return "platega"

    @property
    def name(self) -> str:
        return "СБП (Platega)"

    @property
    def currencies(self) -> List[str]:
        return ["RUB"]

    @property
    def icon(self) -> str:
        return "🏦"

    @property
    def api_url(self) -> str:
        return PLATEGA_API_URL

    @property
    def merchant_id(self) -> str:
        return self.config.get("merchant_id", "")

    @property
    def api_key(self) -> str:
        return self.config.get("api_key", "")

    def validate_config(self) -> tuple[bool, Optional[str]]:
        if not self.merchant_id:
            return False, "Merchant ID is required"
        if not self.api_key:
            return False, "API Key is required"
        return True, None

    async def _request(self, method: str, endpoint: str, data: dict | None = None) -> dict:
        url = f"{self.api_url}/{endpoint}"
        headers = {
            "X-MerchantId": self.merchant_id,
            "X-Secret": self.api_key,
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession() as session:
            if method == "GET":
                async with session.get(url, headers=headers, params=data) as response:
                    if response.status != 200:
                        text = await response.text()
                        logger.error(f"Platega API error: {response.status} - {text}")
                        raise Exception(f"Platega API error: {response.status}")
                    return await response.json()

            async with session.post(url, headers=headers, json=data) as response:
                if response.status != 200:
                    text = await response.text()
                    logger.error(f"Platega API error: {response.status} - {text}")
                    raise Exception(f"Platega API error: {response.status}")
                return await response.json()

    async def create_payment(
        self,
        amount: Decimal,
        currency: str,
        user_id: int,
        payment_uuid: str,
        description: str | None = None,
        **kwargs,
    ) -> ProviderPaymentResult:
        try:
            if currency not in self.currencies:
                return ProviderPaymentResult(
                    success=False,
                    error=f"Unsupported currency: {currency}. Supported: {', '.join(self.currencies)}",
                )

            payment_data = {
                "paymentMethod": self.PAYMENT_METHOD_SBP,
                "paymentDetails": {
                    "amount": int(amount),
                    "currency": "RUB",
                },
                "description": description or f"Пополнение баланса #{payment_uuid[:8]}",
                "return": kwargs.get("return_url", "https://t.me"),
                "failedUrl": kwargs.get("failed_url", "https://t.me"),
                "payload": f"{payment_uuid}:{user_id}",
            }

            result = await self._request("POST", "transaction/process", payment_data)

            transaction_id = result.get("transactionId")
            redirect_url = result.get("redirect")

            logger.info(f"Platega payment created: {transaction_id} for {amount} RUB")

            return ProviderPaymentResult(
                success=True,
                payment_url=redirect_url,
                provider_payment_id=str(transaction_id) if transaction_id is not None else None,
                raw_response=result,
            )

        except Exception as e:
            logger.error(f"Platega create_payment error: {e}")
            return ProviderPaymentResult(success=False, error=str(e))

    async def check_payment(self, provider_payment_id: str) -> PaymentStatus:
        try:
            result = await self._request("GET", f"transaction/{provider_payment_id}")
            status = str(result.get("status", "")).upper()

            status_map = {
                "PENDING": PaymentStatus.PENDING,
                "CONFIRMED": PaymentStatus.COMPLETED,
                "COMPLETED": PaymentStatus.COMPLETED,
                "PAID": PaymentStatus.COMPLETED,
                "EXPIRED": PaymentStatus.EXPIRED,
                "FAILED": PaymentStatus.FAILED,
                "CANCELLED": PaymentStatus.FAILED,
            }

            mapped = status_map.get(status, PaymentStatus.PENDING)
            logger.info(f"Platega payment {provider_payment_id} status: {status} -> {mapped.value}")
            return mapped

        except Exception as e:
            logger.error(f"Platega check_payment error: {e}")
            return PaymentStatus.PENDING

    async def handle_webhook(self, data: dict, headers: dict | None = None) -> WebhookResult:
        try:
            if headers:
                merchant_id = headers.get("X-MerchantId", "")
                if merchant_id and merchant_id != self.merchant_id:
                    return WebhookResult(success=False, error="Invalid merchant ID")

            transaction_id = data.get("id")
            status = str(data.get("status", "")).upper()

            if status in {"CONFIRMED", "COMPLETED", "PAID"}:
                payment_status = PaymentStatus.COMPLETED
            elif status == "EXPIRED":
                payment_status = PaymentStatus.EXPIRED
            elif status in {"FAILED", "CANCELLED"}:
                payment_status = PaymentStatus.FAILED
            else:
                payment_status = PaymentStatus.PENDING

            return WebhookResult(
                success=True,
                payment_uuid=None,
                status=payment_status,
                provider_payment_id=str(transaction_id) if transaction_id is not None else None,
            )

        except Exception as e:
            logger.error(f"Platega webhook error: {e}")
            return WebhookResult(success=False, error=str(e))
