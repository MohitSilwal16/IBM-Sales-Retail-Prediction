from sklearn.preprocessing import LabelEncoder

from db import sql
from models.models import ModelEval, DataAttributes


def get_attrs(user_id: int, data_file_name: str) -> list[DataAttributes]:
    return sql.get_attrs_of_data_file(user_id, data_file_name)


def model_eval_stats(user_id: int, data_file_name: str) -> ModelEval:
    return sql.get_model_eval_stats(user_id, data_file_name)
