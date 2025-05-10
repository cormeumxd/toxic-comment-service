from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AnalyzeRequest(BaseModel):
    texts: list[str]
    model_id: int

class HistoryItem(BaseModel):
    model_name: str
    start_at: datetime
    end_at: Optional[datetime]
    status: str
    cost: float

    class Config:
        from_attributes = True 