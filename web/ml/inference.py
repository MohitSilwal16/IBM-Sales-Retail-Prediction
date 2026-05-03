import os
import json
import joblib
import itertools
import pandas as pd

DATE_COL = "date"


def model_fn(model_dir: str) -> dict:
    bundle = joblib.load(os.path.join(model_dir, "model.joblib"))
    return bundle


def input_fn(request_body: str, content_type: str) -> pd.DataFrame:
    if content_type != "application/json":
        raise ValueError(f"Unsupported content type: {content_type}")
    data = json.loads(request_body)
    return pd.DataFrame(data["instances"])


def predict_fn(df: pd.DataFrame, bundle: dict) -> list:
    model = bundle["model"]
    encoders = bundle["encoders"]
    feature_order = bundle["feature_order"]  # ← use this

    row = df.iloc[0].copy()

    # ── Find empty cols & fixed cols ─────────────────────
    empty_cols = {
        col
        for col in encoders
        if col in row.index and (row[col] is None or str(row[col]).strip() == "")
    }
    fixed_cols = {col: row[col] for col in encoders if col not in empty_cols}

    # ── Build cartesian product of all empty cols ─────────
    # e.g. empty_cols = {Animal, Color}
    # → [("cat", "red"), ("cat", "blue"), ("dog", "red"), ("dog", "blue")]
    empty_col_names = list(empty_cols)
    empty_col_values = [list(encoders[col].classes_) for col in empty_col_names]
    combinations = list(itertools.product(*empty_col_values))  # cartesian product

    # ── Date range from input date (full month) ───────────
    input_date = pd.to_datetime(row[DATE_COL])
    dates = pd.date_range(
        start=input_date.replace(day=1),
        end=input_date + pd.offsets.MonthEnd(0),
        freq="D",
    )

    results = []

    for combo in combinations:
        # build label for this combination
        combo_dict = dict(zip(empty_col_names, combo))

        # expand across full month
        expanded = pd.DataFrame([{**fixed_cols, **combo_dict}] * len(dates))
        expanded.insert(0, DATE_COL, dates)
        expanded[DATE_COL] = pd.to_datetime(expanded[DATE_COL])

        # feature engineering
        expanded["day"] = expanded[DATE_COL].dt.day
        expanded["month"] = expanded[DATE_COL].dt.month
        expanded["year"] = expanded[DATE_COL].dt.year
        expanded["day_of_week"] = expanded[DATE_COL].dt.day_of_week
        expanded["day_of_year"] = expanded[DATE_COL].dt.day_of_year
        expanded["quarter"] = expanded[DATE_COL].dt.quarter
        expanded.drop(columns=[DATE_COL], inplace=True)

        # label encode all cols
        for col, le in encoders.items():
            if col in expanded.columns:
                expanded[col] = le.transform(expanded[col])

        # reorder columns to match training exactly ← add this
        expanded = expanded[feature_order]

        preds = model.predict(expanded)
        monthly_sum = int(sum(map(round, preds)))

        results.append(
            {
                **combo_dict,  # which classes were used
                "predicted_count": monthly_sum,
            }
        )

    return results


def output_fn(predictions: list, accept: str) -> tuple:
    return json.dumps({"predictions": predictions}), "application/json"
