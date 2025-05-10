from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from db.database import get_db
from schemas import UserCreate, UserResponse, Token
from auth import register_user, authenticate_user, get_current_user
from utils import create_access_token
from services.wallet import WalletClient

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(user_create: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user.

    Create a new user and its wallet.

    Args:
        user_create (UserCreate): User registration data.

    Returns:
        UserResponse: Created user.

    Raises:
        HTTPException: If user with given login already exists.
    """
    user = await register_user(user_create, db)
    try:
        access_token = create_access_token(
            data={"sub": str(user.user_id)},
            expires_delta=timedelta(minutes=1)
        )
        
        wclient = WalletClient(token=access_token)
        wallet = await wclient.create_wallet(
            user_id=str(user.user_id)
        )
        logger.info(f"Создан кошелек для пользователя {user.user_id}: {wallet}")
    except Exception as e:
        logger.error(f"Ошибка при создании кошелька для пользователя {user.user_id}: {str(e)}")
    return user

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    Login user.

    Authenticate a user and issue an access token.

    Args:
        form_data (OAuth2PasswordRequestForm): User authentication data.

    Returns:
        Token: Access token.

    Raises:
        HTTPException: If user with given login and password does not exist.
    """
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=400, detail="Неправильный логин или пароль")

    access_token = create_access_token(
        data={"sub": str(user.user_id)},
        expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user