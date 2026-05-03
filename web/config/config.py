from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str
    DATABASE_URL: str

    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str

    AWS_REGION: str
    S3_BUCKET_NAME: str
    S3_ENDPOINT_URL: str

    SAGEMAKER_ROLE_ARN: str
    SAGEMAKER_LOCAL_MODE: str

    class Config:
        env_file = ".env"


settings = Settings()
