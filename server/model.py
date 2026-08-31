from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column
from sqlalchemy import String
from config import settings

engine = create_async_engine(settings.database_url, echo=False)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
class Base(DeclarativeBase):
    @classmethod
    @declared_attr.directive
    def __tablename__(cls):
        return cls.__name__.lower()

class User(Base):
    id:Mapped[int] = mapped_column(primary_key = True)
    nickname:Mapped[str] = mapped_column(String(30),nullable=False)
    email:Mapped[str]=mapped_column(String(255),nullable=False)
    password:Mapped[str]=mapped_column(String(255),nullable=False)


