from fastapi import FastAPI
from api.endpoints.wallet import router as wallet_router
from db.database import engine, Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database connected")

app.include_router(wallet_router)

@app.get("/")
async def root():
    return {"message": "Async Wallet Service"}