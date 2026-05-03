import os
import joblib
import numpy as np
import pandas as pd

from xgboost import XGBRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error

from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy import create_engine, Column, Integer, Float, String, ForeignKey

# ── Constants ────────────────────────────────────────────
DATE_COL = "date"
TARGET_COL = "count"
TEST_SIZE = 0.2

# ── Env vars injected by SageMaker ─────────
INPUT_DIR = os.environ["SM_CHANNEL_TRAIN"]
OUTPUT_DIR = os.environ["SM_MODEL_DIR"]

DB_URL = os.environ["DATABASE_URL"]
USER_ID = int(os.environ["USER_ID"])
FILE_NAME = os.environ["FILE_NAME"]


# ── DB Model ─────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(25), nullable=False)
    hashed_password = Column(String(255), nullable=False)


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
    file_name = Column(String(255), nullable=False)
    rmse = Column(Float, nullable=False)
    accuracy = Column(Float, nullable=False)


# ── Helpers ───────────────────────────────────────────────
def get_label_encoders(df: pd.DataFrame) -> dict[str, LabelEncoder]:
    le_encoders = {}  # col_name: le_encoder

    for col in df.columns:
        if col.lower() == "date":
            continue

        le_encoder = LabelEncoder()
        le_encoder.fit(df[col])

        le_encoders[col] = le_encoder

    return le_encoders


def split_df(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    split_idx = int(len(df) * (1 - TEST_SIZE))
    return df.iloc[:split_idx].copy(), df.iloc[split_idx:].copy()


def pre_process(df: pd.DataFrame, le_encoders: dict[str, LabelEncoder]) -> pd.DataFrame:
    df = df.groupby(list(df.columns)).size().reset_index(name=TARGET_COL)

    # Feature Engineering
    df["day"] = df[DATE_COL].dt.day
    df["month"] = df[DATE_COL].dt.month
    df["year"] = df[DATE_COL].dt.year

    df["day_of_week"] = df[DATE_COL].dt.day_of_week
    df["day_of_year"] = df[DATE_COL].dt.day_of_year
    df["quarter"] = df[DATE_COL].dt.quarter

    df.drop(columns=[DATE_COL], inplace=True)

    # Label Encoding
    for col, le in le_encoders.items():
        df[col] = le.transform(df[col])

    df[TARGET_COL] = df.pop(TARGET_COL)  # move target to last column
    return df


def save_attributes_to_db(engine: Engine, le_encoders: dict[str, LabelEncoder]) -> None:
    rows = []
    for col, le in le_encoders.items():
        for cls in le.classes_:  # unique values for this column
            rows.append(
                DataAttributes(
                    user_id=USER_ID,
                    file_name=FILE_NAME,
                    category_name=col,
                    category_val=str(cls),
                )
            )

    with Session(engine) as session:
        # wipe existing entries for this user+file before inserting fresh
        session.query(DataAttributes).filter_by(
            user_id=USER_ID, file_name=FILE_NAME
        ).delete()
        session.add_all(rows)
        session.commit()

    print(f"Saved {len(rows)} category values to DB")


def save_model_eval_to_db(engine: Engine, rmse: float, accuracy: float) -> None:
    row = ModelEval(
        user_id=USER_ID,
        file_name=FILE_NAME,
        rmse=rmse,
        accuracy=accuracy,
    )

    with Session(engine) as session:
        # optionally remove previous evaluation for same user + file
        session.query(ModelEval).filter_by(
            user_id=USER_ID, file_name=FILE_NAME
        ).delete()

        session.add(row)
        session.commit()

    print(f"Saved model eval -> RMSE: {rmse}, Accuracy: {accuracy}")


# ── Main ──────────────────────────────────────────────────
if __name__ == "__main__":
    # 1. Load — SageMaker already downloaded the S3 file to INPUT_DIR
    csv_path = os.path.join(INPUT_DIR, FILE_NAME)

    df = pd.read_csv(csv_path)
    df[DATE_COL] = pd.to_datetime(df[DATE_COL], format="%d-%m-%Y", errors="raise")
    df = df.sort_values(DATE_COL)

    # 2. Fit encoders on full data before split
    le_encoders = get_label_encoders(df)

    # 3. Split → preprocess each separately
    train_df, test_df = split_df(df)

    train_df = pre_process(train_df, le_encoders)
    test_df = pre_process(test_df, le_encoders)

    # 4. Train
    x = train_df.drop(columns=[TARGET_COL])
    y = train_df[TARGET_COL]

    model = XGBRegressor()
    model.fit(x, y)

    # 5. Evaluate
    x_test = test_df.drop(columns=[TARGET_COL])
    y_test = test_df[TARGET_COL]

    y_pred = model.predict(x_test)
    y_pred = list(map(round, y_pred))

    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    acc = (pd.Series(y_pred) == y_test.reset_index(drop=True)).mean() * 100

    print(f"RMSE    : {rmse:.2f}")
    print(f"Accuracy: {acc:.2f}%")

    # 6. Save bundle → SageMaker picks this up from SM_MODEL_DIR
    bundle = {
        "model": model,
        "encoders": le_encoders,
        "feature_order": list(train_df.drop(columns=[TARGET_COL]).columns),
    }
    joblib.dump(bundle, os.path.join(OUTPUT_DIR, "model.joblib"))
    print("Model bundle saved")

    # 7. Write unique Classes & Eval Stats to RDS
    engine = create_engine(DB_URL)  # SQL Engine

    save_model_eval_to_db(engine, rmse, acc)
    save_attributes_to_db(engine, le_encoders)
