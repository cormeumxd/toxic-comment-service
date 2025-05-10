from fastapi import FastAPI, Depends, HTTPException, APIRouter
import tempfile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from services.wallet_client import WalletClient
from services.ml_client import MlClient
from ml import PredictionService
from billing import BillingManager
import logging
from datetime import datetime
import os
from auth import get_current_user, oauth2_scheme
from db.database import get_db
from db.models import SessionLog, MLModel
from schemas import AnalyzeRequest, HistoryItem
from sqlalchemy import select
import pandas as pd


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/history", response_model=list[HistoryItem])
async def get_history(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_id = int(user.get("sub"))
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid user")

    try:
        stmt = (
            select(SessionLog, MLModel.name.label("model_name"), MLModel.price_per_char.label("price_per_char"))
            .join(MLModel, SessionLog.model_id == MLModel.id)
            .where(SessionLog.user_id == user_id)
            .order_by(SessionLog.start_at.desc())
        )

        result = await db.execute(stmt)
        rows = result.all()

        return [
            HistoryItem(
                model_name=model_name,
                start_at=session_log.start_at,
                end_at=session_log.end_at,
                status=session_log.status,
                cost=float(session_log.total_words_for_classification * price_per_char)
                if price_per_char else 0.0,
            )
            for (session_log, model_name, price_per_char) in rows
        ]
    except Exception as e:
        logger.error(f"Error fetching history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
async def analyze_text(
    request: AnalyzeRequest,
    user: dict = Depends(get_current_user),
    token = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    
    # Используем существующую логику анализа
    texts, model_id = request.texts, request.model_id
    user_id = int(user.get("sub"))
    
    wallet_client = WalletClient(token=token)
    ml_client = MlClient(token=token)
    prediction_service = PredictionService(db, wallet_client, ml_client)

    try:
        result = await prediction_service.analyze_text(texts, model_id, user_id)

        filtered_result = [
            {
                "texts": text,
                "label": prediction.get("label", "Unknown"),
                "score": prediction.get("score", 0.0)
            }
            for text, prediction in zip(texts, result["result"])
        ]
        
        df = pd.DataFrame(filtered_result)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            file_path = tmp.name
            df.to_csv(file_path, index=False)
            
            return FileResponse(
                file_path,
                media_type="text/csv",
                filename="analysis_results.csv",
                headers={"Content-Disposition": "attachment; filename=analysis_results.csv"}
            )

            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))