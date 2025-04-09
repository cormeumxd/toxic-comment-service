from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from db.models import Wallet
from schemas import WalletCreate, WalletResponse
from utils import get_wallet, create_wallet, update_balance
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/wallet", tags=["wallet"])

@router.post("/", response_model=WalletResponse)
async def create_wallet_endpoint(
    wallet_data: WalletCreate, 
    db: AsyncSession = Depends(get_db)
):
    if await get_wallet(db, wallet_data.user_id):
        raise HTTPException(status_code=400, detail="Wallet already exists")
    logger.info("Wallet created")
    return await create_wallet(db, wallet_data.user_id)

@router.get("/{user_id}", response_model=WalletResponse)
async def read_wallet(
    user_id: int, 
    db: AsyncSession = Depends(get_db)
):
    wallet = await get_wallet(db, user_id)
    logger.info("Wallet fetched")
    return wallet

@router.post("/{user_id}/topup", response_model=WalletResponse)
async def topup_wallet(
    user_id: int, 
    amount: float, 
    db: AsyncSession = Depends(get_db)
):
    wallet = await update_balance(db, user_id, amount)
    logger.info("Wallet topped up")
    return wallet
        