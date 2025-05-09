from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from model_manager.model_manager import ModelManager
from db.models import MLModel
from schemas import ModelResponse, LoadModelsResponse, PredictResponse, PredictRequest
from typing import List

router = APIRouter()
model_manager = ModelManager(device="auto")  # Можно настроить через config


@router.get("/models", response_model=List[ModelResponse])
async def list_models(db: AsyncSession = Depends(get_db)):
    """Получить список всех моделей"""
    try:
        models = await model_manager.get_available_models(db)
        return models
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения моделей: {e}")


@router.post("/load-models", response_model=LoadModelsResponse)
async def load_all_models(db: AsyncSession = Depends(get_db)):
    """Загрузить все модели из БД в память"""
    try:
        await model_manager.download_models(db)
        cached_models = list(model_manager._model_pool.keys())
        return {
            "message": f"Успешно загружено {len(cached_models)} моделей",
            "loaded_model_ids": cached_models
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки моделей: {e}")


@router.post("/predict/{model_id}", response_model=PredictResponse)
async def predict(model_id: int, texts: PredictRequest, db: AsyncSession = Depends(get_db)):
    """Выполнить предикт с помощью указанной модели"""
    if model_id not in model_manager._model_pool:
        raise HTTPException(status_code=404, detail="Модель не загружена")

    try:
        result = await model_manager.predict(model_id, texts)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка предикта: {e}")