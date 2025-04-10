import httpx
from typing import Optional

from data.config import CRYSTALPAY_LOGIN, CRYSTALPAY_SECRET, WEBHOOK_URL


class CrystalPayClient:
    BASE_URL = "https://api.crystalpay.io/v3/invoice/create/"

    def __init__(self):
        self.auth_login = CRYSTALPAY_LOGIN
        self.auth_secret = CRYSTALPAY_SECRET

    async def create_invoice(
            self,
            amount: float | int,
            lifetime: int = 15,
            invoice_type: str = "purchase",
            amount_currency: Optional[str] = None,
            required_method: Optional[str] = None,
            payer_details: Optional[str] = None,
            description: Optional[str] = None,
            extra: Optional[str] = None,
            redirect_url: Optional[str] = None,
            callback_url: Optional[str] = WEBHOOK_URL + '/payments/crystalpay/',
    ) -> dict:
        payload = {
            "auth_login": self.auth_login,
            "auth_secret": self.auth_secret,
            "amount": amount,
            "type": invoice_type,
            "lifetime": lifetime,
        }

        optional_fields = {
            "amount_currency": amount_currency,
            "required_method": required_method,
            "payer_details": payer_details,
            "description": description,
            "extra": extra,
            "redirect_url": redirect_url,
            "callback_url": callback_url,
        }

        payload.update({k: v for k, v in optional_fields.items() if v is not None})

        async with httpx.AsyncClient() as client:
            response = await client.post(self.BASE_URL, json=payload)
            response.raise_for_status()
            data = response.json()

        if data.get("error"):
            raise Exception(f"CrystalPay error: {data.get('errors')}")

        return data
