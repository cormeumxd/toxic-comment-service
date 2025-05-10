from fastapi import HTTPException
from billing import BillingManager

class PredictionService:
    def __init__(self, db, wallet_client, ml_client):
        self.db = db
        self.billing = BillingManager(db, wallet_client, ml_client)
        self.ml_client = ml_client

    async def analyze_text(self, texts: list[str], model_id: int, user_id: int):
        char_count = sum(len(text) for text in texts)
        cost = await self.billing.calculate_cost(texts, model_id)
        session_id = await self.billing.log_session_start(user_id, model_id, char_count)

        try:
            await self.billing.make_payment(user_id, cost)
            result = await self.ml_client.predict(model_id, texts)
            await self.billing.log_session_end(session_id, "completed")
            return {"texts": texts, "result": result, "cost": cost}

        except Exception as e:
            await self.billing.log_session_end(session_id, "failed")
            raise HTTPException(status_code=500, detail=f"Ошибка анализа: {e}")