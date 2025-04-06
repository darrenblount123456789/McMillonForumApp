import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Create async database engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create session factory
SessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, autocommit=False, autoflush=False
)

# Base class for models
Base = declarative_base()

# Dependency to get a database session
async def get_db():
    async with SessionLocal() as session:
        yield session
