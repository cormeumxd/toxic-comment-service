from pydantic import BaseModel

class WalletCreate(BaseModel):
    user_id: int

class TopUpRequest(BaseModel):
    amount: float

class WalletResponse(BaseModel):
    id: int
    user_id: int
    balance: float

    class Config:
        from_attributes = True