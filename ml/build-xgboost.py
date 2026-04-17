import joblib
import pandas as pd

from os import system

from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import root_mean_squared_error
from sklearn.model_selection import train_test_split

from xgboost import XGBRegressor

system("cls")

INPUT_FILE_NAME = "Formatted Car Sales.csv"
MODEL_BUNDLE_FILE_NAME = "Formatted Car Sales.pkl"

TEST_SIZE = 0.2
DATE_COL = "date"
TARGET_COL = "count"


def get_label_encoders(df: pd.DataFrame) -> dict[str, LabelEncoder]:
    le_encoders = {}  # col_name: le_encoder

    for col in df.columns:
        if col.lower() == "date":
            continue

        le_encoder = LabelEncoder()
        le_encoder.fit(df[col])

        le_encoders[col] = le_encoder

    return le_encoders


def train_test_split(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    n = len(df)
    split_idx = int(n * (1 - TEST_SIZE))
    train_df, test_df = df.iloc[:split_idx].copy(), df.iloc[split_idx:].copy()

    return train_df, test_df


def pre_process(df: pd.DataFrame, le_encoders: dict[str, LabelEncoder]) -> None:
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
    for col_name, le_encoder in le_encoders.items():
        df[col_name] = le_encoder.transform(df[col_name])

    df[TARGET_COL] = df.pop(TARGET_COL)  # Move Count to Last Pos
    return df


def train_model(train_df: pd.DataFrame) -> XGBRegressor:
    x = train_df.drop(columns=[TARGET_COL])
    y = train_df[TARGET_COL]

    model = XGBRegressor()
    model.fit(x, y)

    return model


def test_model(model: XGBRegressor, test_df: pd.DataFrame) -> tuple[float, float]:
    x_test = test_df.drop(columns=[TARGET_COL])
    y_test = test_df[TARGET_COL]

    y_pred = model.predict(x_test)
    y_pred = list(map(round, y_pred))

    rmse = root_mean_squared_error(y_test, y_pred)
    acc = (y_pred == y_test).mean() * 100

    return rmse, acc


if __name__ == "__main__":
    df = pd.read_csv(INPUT_FILE_NAME)

    # Sort by Date
    df[DATE_COL] = pd.to_datetime(df[DATE_COL], format="%d-%m-%Y", errors="raise")
    df = df.sort_values("date")

    # Label Encoding for all Categorical Cols
    le_encoders = get_label_encoders(df)

    # Split First Pre-Process Later
    train_df, test_df = train_test_split(df)

    train_df = pre_process(train_df, le_encoders)
    test_df = pre_process(test_df, le_encoders)

    model = train_model(train_df)

    # Save Models, Encoders & Attributes
    model_bundle = {
        "model": model,
        "encoders": le_encoders,
        "attributes": list(le_encoders.keys()),
    }
    joblib.dump(model_bundle, MODEL_BUNDLE_FILE_NAME)

    rmse, acc = test_model(model, test_df)
    print(f"RMSE    : {rmse:.2f}")
    print(f"Accuracy: {acc:.2f} %")