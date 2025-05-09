from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from db.models import User, Credential
from schemas import UserCreate
from utils import verify_password, get_password_hash, decode_access_token
from db.database import get_db
from datetime import datetime, timedelta

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

async def register_user(user_create: UserCreate, db: AsyncSession):
    # Check if login or email already exists
    result = await db.execute(select(User).where((User.login == user_create.login)))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Login already registered")

    new_user = User(
        email=user_create.email,
        name=user_create.name,
        login=user_create.login,
        phone=user_create.phone,
        created_at=datetime.utcnow(),
        modified_at=datetime.utcnow()
    )
    db.add(new_user)
    await db.flush()  # To get new_user.user_id

    password_hash = get_password_hash(user_create.password)
    new_cred = Credential(
        user_id=new_user.user_id,
        password_hash=password_hash
    )
    db.add(new_cred)
    await db.commit()
    await db.refresh(new_user)

    return new_user

async def authenticate_user(login: str, password: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.login == login))
    user = result.scalars().first()
    if not user:
        return None

    result = await db.execute(select(Credential).where(Credential.user_id == user.user_id))
    cred = result.scalars().first()
    if not cred or not verify_password(password, cred.password_hash):
        return None

    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    result = await db.execute(select(User).where(User.user_id == int(user_id)))
    user = result.scalars().first()
    if user is None:
        raise credentials_exception
    return user