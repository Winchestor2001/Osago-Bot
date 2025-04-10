import httpx
from typing import Optional

from data.config import NICEPAY_MERCHANT_ID, NICEPAY_SECRET_KEY


class NicepayInvoiceCreator:
    BASE_URL = "https://nicepay.io/public/api/payment"

    def __init__(self):
        self.merchant_id = NICEPAY_MERCHANT_ID
        self.secret = NICEPAY_SECRET_KEY

    async def create_invoice(
        self,
        order_id: str,
        customer: str,
        amount: float,
        currency: str = "RUB",
        description: Optional[str] = None,
        method: Optional[str] = None,
        success_url: Optional[str] = None,
        fail_url: Optional[str] = None,
    ) -> dict:
        payload = {
            "merchant_id": self.merchant_id,
            "secret": self.secret,
            "order_id": order_id,
            "customer": customer,
            "amount": int(amount * 100),
            "currency": currency,
        }

        if description:
            payload["description"] = description
        if method:
            payload["method"] = method
        if success_url:
            payload["success_url"] = success_url
        if fail_url:
            payload["fail_url"] = fail_url
        async with httpx.AsyncClient() as client:
            response = await client.post(self.BASE_URL, json=payload)
            data = response.json()

        if data["status"] != "success":
            raise Exception(f"Payment creation failed: {data['data'].get('message')}")

        return data["data"]
