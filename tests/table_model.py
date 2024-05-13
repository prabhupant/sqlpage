from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlmodel import SQLModel, Field

Base = declarative_base()

class TestTableSqlModel(SQLModel, table=True):
    __tablename__ = 'test_table'

    id: int = Field(primary_key=True)
    username: str = Field(default=None)
    email: str = Field(default=None)


class TestTableSqlAlchemy(Base):
    __tablename__ = 'test_table'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)