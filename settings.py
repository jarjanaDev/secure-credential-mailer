from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    smtp_host: str = Field(default="smtp.office365.com")
    smtp_port: int = Field(default=587)
    smtp_user: str = Field(default="")
    smtp_password: str = Field(default="")
    sender_name: str = Field(default="IT Operations")

    split_delay_seconds: int = Field(default=30)
    credential_expiry_days: int = Field(default=7)

    audit_db: str = Field(default="audit/audit.db")
    fernet_key: str = Field(default="")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
