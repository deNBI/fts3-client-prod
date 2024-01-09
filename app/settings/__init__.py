from pydantic_settings import BaseSettings
from pydantic import SecretStr


class Settings(BaseSettings):
    DEBUG: bool
    LOG_LEVEL: str = "INFO"
    API_KEY: SecretStr
    S3_URL: str
    S3_BUCKET: str
    S3_ACCESS_KEY: SecretStr
    S3_SECRET_KEY: SecretStr
    FTS3_URL: str
    FTS3_CA: str = "/code/keys/CA.pem"
    FTS3_CERT: str = "/code/keys/fts3.cert.pem"
    FTS3_KEY: str = "/code/keys/fts3.key.pem"

    class Config:
        case_sensitive = True
        secrets_dir = "/run/secrets"


settings = Settings()
