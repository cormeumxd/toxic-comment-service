from sqlalchemy import Column, Integer, Float, ForeignKey
from db.database import Base, engine

class Wallet(Base):
    __tablename__ = "wallet"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True)
    balance = Column(Float, default=0.0)