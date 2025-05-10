from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from schemas import ModelResponse, LoadModelsResponse, PredictResponse, PredictRequest, AddModelRequest
from typing import List
from auth import get_current_user
from db.models import MLModel

router = APIRouter()

@router.get("/models", response_model=List[ModelResponse])
async def list_models(
    request: Request,
    current_user = Depends(get_current_user),  # Proper user object
    db: AsyncSession = Depends(get_db)
):
    """
    Returns a list of models available for analysis.

    Requires authentication to view models.
    """
    try:
        model_manager = request.app.state.model_manager
        models = await model_manager.get_available_models(db)
        return models
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении моделей: {e}")

@router.post("/load-models", response_model=LoadModelsResponse)
async def load_all_models(
    request: Request,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
    
):  
    """
    Downloads and loads all available models from the database.

    Returns a JSON with a message and a list of loaded model IDs.
    Requires authentication to view models.
    """
    try:
        model_manager = request.app.state.model_manager
        await model_manager.download_models(db)
        cached_models = list(model_manager._model_pool.keys())
        return {
            "message": f"Успешно загружено {len(cached_models)} моделей",
            "loaded_model_ids": cached_models
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при загрузке моделей: {e}")
    
@router.post("/add-model", response_model=dict)
async def add_model(
    request: AddModelRequest,
    db: AsyncSession = Depends(get_db),
    request_state: Request = None
):
    """
    Creates a new model and saves it to the database.

    Returns a JSON with a success message.
    Requires authentication to add models.
    """
    new_model = MLModel(
        type=request.type,
        name=request.name,
        price_per_char=request.price_per_char
    )
    db.add(new_model)
    await db.commit()
    await db.refresh(new_model)

    try:
        model_manager = request_state.app.state.model_manager
        await model_manager.download_models(db)  # Refresh the cache
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при загрузке моделей: {e}")

    return {"message": "Модель успешно добавлена"} 

@router.post("/predict/{model_id}", response_model=PredictResponse)
async def predict(
    request: Request,
    model_id: int, 
    texts: PredictRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Makes a prediction using the specified model and input texts.

    Returns a JSON with the prediction result.
    Requires authentication to make predictions.
    """
    model_manager = request.app.state.model_manager
    
    if model_id not in model_manager._model_pool:
        raise HTTPException(status_code=404, detail="Model not loaded")

    try:
        result = await model_manager.predict(model_id, texts.texts)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {e}")