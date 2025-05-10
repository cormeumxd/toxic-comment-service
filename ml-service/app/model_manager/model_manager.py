from model_manager.models import ModelManagerABC
from db.models import MLModel
from typing import List
from sqlalchemy import select
from transformers import pipeline
from sqlalchemy.ext.asyncio import AsyncSession
import torch
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelManager(ModelManagerABC):
    def __init__(self, device="cpu"):
        self._model_pool = {}
        self.device = device
        if device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    async def get_available_models(self, db) -> List[MLModel]:
        """
        Retrieves a list of available machine learning models from the database.

        Args:
            db (AsyncSession): The asynchronous database session.

        Returns:
            List[MLModel]: A list of MLModel instances representing the available models.

        Raises:
            Exception: If there is an error while fetching models from the database.
        """

        try:
            result = await db.execute(select(MLModel))
            models = result.scalars().all()
            return models
        except Exception as e:
            logger.error(f"Ошибка при получении моделей из БД: {e}")
            raise

    async def download_models(self, db: AsyncSession):
        """
        Downloads and loads all available models from the database into memory.

        Args:
            db (AsyncSession): The asynchronous database session.

        Raises:
            Exception: If there is an error while fetching models from the database or loading models into memory.
        """
        try:
            stmt = select(MLModel.id, MLModel.name, MLModel.type)
            result = await db.execute(stmt)
            rows = result.all() 

            for row in rows:
                model_id, model_name, model_type = row
                try:
                    logger.info(f"Loading model {model_name} (ID: {model_id}) for task '{model_type}' on device '{self.device}'")
                    self._model_pool[model_id] = pipeline(
                        task=model_type,
                        model=model_name,
                        device=self.device
                    )
                except Exception as e:
                    logger.error(f"Failed to load model {model_name}: {e}")
        except Exception as e:
            logger.error(f"Database error while downloading models: {e}")
            raise

    async def predict(self, model_id: int, data: List[str]):
        """
        Makes a prediction using the specified model and input data.

        Args:
            model_id (int): The ID of the model to use for prediction.
            data (List[str]): The input data to predict.

        Returns:
            The prediction result.

        Raises:
            Exception: If the model is not available or there is an error while making the prediction.
        """
        try:
            model = self._model_pool[model_id]
            return model(data)
        except Exception as e:
            logger.error(f"Failed to predict with model {model_id}: {e}")
            raise
        