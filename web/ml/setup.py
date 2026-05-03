from setuptools import setup

setup(
    name="train",
    version="1.0.0",
    py_modules=["train", "inference"],  # ← explicitly expose train.py as a module
    install_requires=[  # ← dependencies from requirements.txt
        "sqlalchemy",
        "pymysql",
        "pandas",
        "xgboost",
        "scikit-learn",
        "joblib",
    ],
)
