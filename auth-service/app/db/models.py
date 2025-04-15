from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from db.database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    login = Column(String, unique=True)
    phone = Column(String)
    #is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    modified_at = Column(DateTime, onupdate=datetime.datetime.utcnow)

class Credential(Base):
    __tablename__ = "credentials"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    password_hash = Column(String)