import httpx
from fastapi import HTTPException
from typing import Dict, Any

WALLET_SERVICE_URL = "http://wallet-service:8002/wallet"

class WalletClient:
    def __init__(self, token: str):
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}"}

    async def create_wallet(self, user_id: int) -> dict:
        """
        Создает новый кошелек для указанного пользователя.

        :param user_id: ID пользователя, для которого создается кошелек
        :return: словарь с данными созданного кошелька
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.post(
                WALLET_SERVICE_URL,
                headers=self.headers,
                json={"user_id": user_id}
            )
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Ошибка создания кошелька")
            return response.json()