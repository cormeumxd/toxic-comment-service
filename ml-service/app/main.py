from fastapi import FastAPI
from contextlib import asynccontextmanager
from typing import AsyncIterator
from api.endpoints.routers import router as ml_router
from db.database import engine, Base
from model_manager.model_manager import ModelManager
from db.database import get_db
from db.database import AsyncSessionLocal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.model_manager = ModelManager(device="auto")
    logger.info("ModelManager initialized")

    async with AsyncSessionLocal() as session:
        try:
            await app.state.model_manager.download_models(session)
        except Exception as e:
            logger.error(f"Model pre-loading failed: {e}")
    
    yield 
    #await app.state.model_manager.cleanup()  # Assuming you have a cleanup method
    logger.info("ModelManager cleaned up")

app = FastAPI(lifespan=lifespan)
app.include_router(ml_router)

@app.get("/")
async def root():
    return {"message": "Async Wallet Service"}