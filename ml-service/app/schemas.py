from pydantic import BaseModel
from typing import List

class ModelResponse(BaseModel):
    id: int
    name: str
    type: str
    price_for_one_word: float

    class Config:
        from_attributes = True


class PredictRequest(BaseModel):
    texts: List[str]


class PredictResponseItem(BaseModel):
    label: str
    score: float


class PredictResponse(PredictRequest):
    result: List[List[PredictResponseItem]]


class LoadModelsResponse(BaseModel):
    message: str
    loaded_model_ids: List[int]