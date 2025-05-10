from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.endpoints.users import router as wallet_router
from db.database import engine, Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

app.include_router(wallet_router)

@app.get("/")
async def root():
    return {"message": "Auth Service"}