import httpx
from fastapi import HTTPException
from typing import Dict, Any

WALLET_SERVICE_URL = "http://wallet-service:8002/wallet"

class WalletClient:
    def __init__(self, token: str):
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}"}

    async def check_balance(self, user_id: int) -> float:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{WALLET_SERVICE_URL}/{user_id}", headers=self.headers)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Ошибка кошелька")
            return response.json()["balance"]

    async def topup(self, user_id: int, amount: float) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{WALLET_SERVICE_URL}/{user_id}/topup",
                json={"amount": amount},
                headers=self.headers
            )
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Ошибка списания")
            return response.json()