from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, JSON
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

class Scan(Base):
    __tablename__ = "scans"
    id = Column(String, primary_key=True, index=True)
    status = Column(String)
    repository = Column(String)
    pr_number = Column(Integer)
    created_at = Column(DateTime)
    result = Column(JSON)

class Finding(Base):
    __tablename__ = "findings"
    id = Column(String, primary_key=True, index=True)
    scan_id = Column(String, index=True)
    rule_id = Column(String)
    severity = Column(String)
    data = Column(JSON)

class Repository(Base):
    __tablename__ = "repositories"
    id = Column(String, primary_key=True, index=True)
    full_name = Column(String, unique=True, index=True)
    installation_id = Column(Integer)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
