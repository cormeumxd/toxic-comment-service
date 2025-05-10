from pydantic import BaseModel
from typing import List

class ModelResponse(BaseModel):
    id: int
    name: str
    type: str
    price_per_char: float

    class Config:
        from_attributes = True

class AddModelRequest(BaseModel):
    type: str
    name: str
    price_per_char: float

class PredictRequest(BaseModel):
    texts: List[str]


class PredictResponseItem(BaseModel):
    label: str
    score: float


class PredictResponse(BaseModel):
    result: List[PredictResponseItem]


class LoadModelsResponse(BaseModel):
    message: str
    loaded_model_ids: List[int]