from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum
from db.database import Base
import enum
import datetime

class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True)
    balance = Column(Numeric(10, 2), default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.datetime.utcnow)