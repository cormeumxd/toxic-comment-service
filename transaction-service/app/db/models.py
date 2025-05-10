from sqlalchemy import Column, Integer, Float, ForeignKey, String, Numeric, TIMESTAMP
from db.database import Base, engine

class Wallet(Base):
    __tablename__ = "wallet"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True)
    balance = Column(Float, default=0.0)

class MLModel(Base):
    __tablename__ = "ml_models"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(100), nullable=False)
    name = Column(String(255), nullable=False)
    price_per_char = Column(Numeric(10, 4), nullable=False)

class SessionLog(Base):
    __tablename__ = 'session'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    model_id = Column(Integer, nullable=False)
    start_at = Column(TIMESTAMP, nullable=False)
    end_at = Column(TIMESTAMP)
    status = Column(String(50), nullable=False)
    total_words_for_classification = Column(Integer, nullable=False)