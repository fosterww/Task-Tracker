from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


class DBSettings(BaseSettings):
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str
    DATABASE_HOST: str
    DATABASE_PORT: str
    DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


class ServiceSettings(BaseSettings):
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    S3_ENDPOINT: str
    S3_REGION: str
    S3_BUCKET: str
    REDIS_URL: str
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool
    USE_CREDENTIALS: bool
    VALIDATE_CERTS: bool

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
dbsettings = DBSettings()
srcsettings = ServiceSettings()
