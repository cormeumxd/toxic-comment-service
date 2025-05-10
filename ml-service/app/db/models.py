from sqlalchemy import Column, Integer, String, Numeric
from db.database import Base

class MLModel(Base):
    __tablename__ = "ml_models"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(100), nullable=False)
    name = Column(String(255), nullable=False)
    price_per_char = Column(Numeric(10, 4), nullable=False)