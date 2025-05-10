# ml_client_service.py
import httpx
from fastapi import HTTPException
from typing import List, Dict, Any

ML_SERVICE_URL = "http://ml-service:8001"

class MlClient:
    def __init__(self, token: str):
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}"}

    async def get_models(self) -> List[Dict[str, Any]]:
        """Получить список доступных моделей"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{ML_SERVICE_URL}/models", headers=self.headers)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Ошибка при получении списка моделей")
            return response.json()

    async def predict(self, model_id: int, texts: List[str]) -> List[Dict]:
        """Выполнить предикт через указанную модель"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{ML_SERVICE_URL}/predict/{model_id}",
                json={"texts": texts},
                headers=self.headers
            )
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Ошибка при выполнении предикта")
            return response.json()["result"]