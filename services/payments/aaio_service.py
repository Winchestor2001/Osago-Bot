import httpx
import hashlib
from typing import Optional
from urllib.parse import urlencode

from data.config import AAIO_MERCHANT_ID, AAIO_SECRET_KEY1


class AaioService:
    BASE_URL = "https://aaio.so/merchant/get_pay_url"
    CURRENCY = "RUB"  # или RUB, UAH, EUR
    LANG = "ru"

    def __init__(self):
        self.merchant_id = AAIO_MERCHANT_ID
        self.secret_key1 = AAIO_SECRET_KEY1

    def _generate_signature(self, merchant_id: str, amount: str, currency: str, secret: str, order_id: str) -> str:
        raw = f"{merchant_id}:{amount}:{currency}:{secret}:{order_id}"
        print(f"[SIGN] Raw string: {raw}")
        return hashlib.sha256(raw.encode()).hexdigest()

    async def create_payment_url(
        self,
        order_id: str,
        amount: float,
        email: Optional[str] = None,
        desc: Optional[str] = None,
        method: Optional[str] = None,
        us_key: Optional[str] = None
    ) -> str:
        str_amount = f"{amount:.2f}"
        sign = self._generate_signature(self.merchant_id, str_amount, self.CURRENCY, self.secret_key1, order_id)

        payload = {
            "merchant_id": self.merchant_id,
            "amount": str_amount,
            "order_id": order_id,
            "currency": self.CURRENCY,
            "lang": self.LANG,
            "sign": sign,
            "us_key": us_key,
        }

        if desc:
            payload["desc"] = desc
        if email:
            payload["email"] = email
        if method:
            payload["method"] = method

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.BASE_URL, data=payload, headers=headers)
                print("[AAIO] Status:", response.status_code)
                print("[AAIO] Response Text:", response.text)  # <-- ВАЖНО
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as e:
            raise ValueError(f"AAIO Error: {e.response.text}")  # <-- Покажет ошибку из API

        if data.get("type") == "success":
            return data["url"]
        else:
            raise ValueError(f"AAIO Error: {data}")