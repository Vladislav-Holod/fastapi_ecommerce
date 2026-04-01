from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from datetime import datetime
# Строка подключения для SQLite
DATABASE_URL = "sqlite:///ecommerce.db"

# Создаём Engine
engine = create_engine(DATABASE_URL, echo=True)

# Настраиваем фабрику сеансов
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


