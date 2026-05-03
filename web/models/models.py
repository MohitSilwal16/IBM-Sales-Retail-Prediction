from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, Column, Integer, Float, String, ForeignKey

from config import config

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(25), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)


class ModelMetaData(Base):
    __tablename__ = "model_metadata"

    model_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    data_file_name = Column(String(255), nullable=False)
    model_job_name = Column(String(255), nullable=False)


class DataAttributes(Base):
    __tablename__ = "data_attributes"

    attr_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    category_name = Column(String(255), nullable=False)
    category_val = Column(String(255), nullable=False)


class ModelEval(Base):
    __tablename__ = "model_eval"

    model_eval_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    job_name = Column(String(255), nullable=False)
    file_name = Column(String(255), nullable=False)
    rmse = Column(Float, nullable=False)
    accuracy = Column(Float, nullable=False)


engine = create_engine(
    config.settings.DATABASE_URL,
    connect_args=(
        {"check_same_thread": False} if "sqlite" in config.settings.DATABASE_URL else {}
    ),
)

Base.metadata.create_all(bind=engine)
