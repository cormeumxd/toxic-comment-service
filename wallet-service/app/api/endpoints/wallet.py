from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from db.models import Wallet
from schemas import WalletCreate, WalletResponse, TopUpRequest
from utils import get_wallet, create_wallet, update_balance
from auth import get_current_user
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/wallet", tags=["wallet"])

@router.post("/", response_model=WalletResponse)
async def create_wallet_endpoint(
    wallet_data: WalletCreate, 
    token: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if await get_wallet(db, wallet_data.user_id):
        raise HTTPException(status_code=400, detail="Wallet already exists")
    logger.info("Wallet created")
    return await create_wallet(db, wallet_data.user_id)

@router.get("/{user_id}", response_model=WalletResponse)
async def read_wallet(
    user_id: int,
    token: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    wallet = await get_wallet(db, user_id)
    logger.info("Wallet fetched")
    return wallet

@router.post("/{user_id}/topup", response_model=WalletResponse)
async def topup_wallet(
    user_id: int, 
    request: TopUpRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    amount = request.amount
    if user_id != int(current_user["sub"]):
        raise HTTPException(status_code=401, detail="Unauthorized")
    wallet = await update_balance(db, user_id, amount)
    logger.info("Wallet topped up")
    return wallet
        