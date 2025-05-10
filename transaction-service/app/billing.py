# billing_manager.py
from services.wallet_client import WalletClient
from services.ml_client import MlClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.models import MLModel, SessionLog
from fastapi import HTTPException
from datetime import datetime


class BillingManager:
    def __init__(self, db: AsyncSession, wallet_client: WalletClient, ml_client: MlClient):
        self.db = db
        self.wallet_client = wallet_client
        self.ml_client = ml_client

    async def log_session_start(self, user_id: int, model_id: int, word_count: int) -> int:
        session = SessionLog(
            user_id=user_id,
            model_id=model_id,
            start_at=datetime.utcnow(),
            status="started",
            total_words_for_classification=word_count
        )
        self.db.add(session)
        await self.db.flush()
        return session.id
    
    async def log_session_end(self, session_id: int, status: str):
        stmt = select(SessionLog).where(SessionLog.id == session_id)
        result = await self.db.execute(stmt)
        session = result.scalars().first()

        if session:
            session.end_at = datetime.utcnow()
            session.status = status
            await self.db.commit()

    async def calculate_cost(self, data: list[str], model_id: int) -> float:
        """
        Рассчитывает стоимость на основе количества символов и цены модели.
        """
        try:
            stmt = select(MLModel).where(MLModel.id == model_id)
            result = await self.db.execute(stmt)
            model = result.scalars().first()

            if not model:
                raise HTTPException(status_code=404, detail="Модель не найдена")

            total_chars = sum(len(text) for text in data)
            cost = total_chars * float(model.price_per_char)
            return round(cost, 4)

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка расчёта стоимости: {e}")

    async def make_payment(self, user_id: int, amount: float) -> None:
        """
        Проверяет баланс и списывает средства через topup с отрицательной суммой.
        """
        try:
            balance = await self.wallet_client.check_balance(user_id)
            if balance < amount:
                raise HTTPException(status_code=400, detail="Недостаточно средств")
            
            # Списываем через пополнение с отрицательной суммой
            await self.wallet_client.topup(user_id, -amount)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка при списании средств: {e}")

    async def refund(self, user_id: int, amount: float) -> None:
        """
        Возвращает деньги пользователю через пополнение.
        """
        try:
            await self.wallet_client.topup(user_id, amount)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка при возврате средств: {e}")