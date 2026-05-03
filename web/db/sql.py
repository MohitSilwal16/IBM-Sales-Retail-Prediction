from sqlalchemy import exists
from sqlalchemy.orm import sessionmaker

from models.models import engine, User, DataAttributes, ModelEval, ModelMetaData

# Init
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
db = SessionLocal()


# Users
def create_user(user: User) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_user_by_user_id(user_id: int) -> User | None:
    user = db.query(User).filter(User.user_id == user_id).first()
    return user


def get_user_by_user_name(username: str) -> User | None:
    user = db.query(User).filter(User.username == username).first()
    return user


# Data Attributes
def get_attrs_of_data_file(user_id: int, data_file_name: str) -> list[DataAttributes]:
    data_attrs = (
        db.query(DataAttributes)
        .filter(
            DataAttributes.user_id == user_id,
            DataAttributes.file_name == data_file_name,
        )
        .all()
    )

    return data_attrs


# Model Eval Stats
def get_model_eval_stats(user_id: int, data_file_name: str) -> ModelEval:
    model_stats = (
        db.query(ModelEval)
        .filter(ModelEval.user_id == user_id, ModelEval.file_name == data_file_name)
        .first()
    )

    return model_stats


# Model Meta Data
def create_model_metadata(
    user_id: int, data_file_name: str, model_job_name: str
) -> None:
    new_entry = ModelMetaData(
        user_id=user_id, data_file_name=data_file_name, model_job_name=model_job_name
    )

    db.add(new_entry)
    db.commit()


def get_model_by_user_and_file(
    user_id: int, data_file_name: str
) -> ModelMetaData | None:
    return (
        db.query(ModelMetaData)
        .filter(
            ModelMetaData.user_id == user_id,
            ModelMetaData.data_file_name == data_file_name,
        )
        .first()
    )


def get_models_by_user_id(user_id: int) -> list[ModelMetaData]:
    return (
        db.query(ModelMetaData)
        .filter(
            ModelMetaData.user_id == user_id,
        )
        .all()
    )
