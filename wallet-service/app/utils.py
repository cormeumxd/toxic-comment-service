from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Wallet
from fastapi import HTTPException

async def get_wallet(db: AsyncSession, user_id: int) -> Wallet:
    result = await db.execute(select(Wallet).where(Wallet.user_id == user_id))
    return result.scalars().first()

async def create_wallet(db: AsyncSession, user_id: int) -> Wallet:
    try:
        wallet = Wallet(user_id=user_id)
        db.add(wallet)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await db.commit()
    return wallet

async def update_balance(db: AsyncSession, user_id: int, amount: float) -> Wallet:
    wallet = await get_wallet(db, user_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    try:
        wallet.balance += amount
        db.add(wallet)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await db.commit()
    return wallet