import json
from pathlib import Path
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict
from sqlalchemy import URL

# NoDecode: let `_split` parse the raw .env string instead of pydantic-settings
# forcing JSON on list fields
EnvList = Annotated[list[str], NoDecode]


class Settings(BaseSettings):
    app_name: str = "izero-print-module"
    database_hostname: str
    database_port: int
    database_password: str
    database_name: str
    database_username: str
    cors_allow_origins: EnvList
    cors_allow_methods: EnvList
    cors_allow_headers: EnvList
    sentry_dsn: str | None = None
    sentry_environment: str = "development"
    sentry_traces_sample_rate: float = 0.0
    sentry_send_default_pii: bool = False
    http_audit_sensitive_headers: EnvList = [
        "authorization",
        "cookie",
        "set-cookie",
        "x-api-key",
        "proxy-authorization",
    ]
    http_audit_sensitive_body_fields: EnvList = [
        "password",
        "new_password",
        "old_password",
        "current_password",
        "password_confirmation",
        "token",
        "access_token",
        "refresh_token",
        "id_token",
        "jwt_token",
        "client_secret",
        "secret",
        "csrf_token",
        "api_key",
        "authorization",
    ]
    http_audit_max_body_length: int = 10_000
    # Directory holding the document templates; a relative path is
    # taken from the working directory of the service
    templates_dir: Path = Path("app/infrastructure/templates")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator(
        "cors_allow_origins",
        "cors_allow_methods",
        "cors_allow_headers",
        "http_audit_sensitive_headers",
        "http_audit_sensitive_body_fields",
        mode="before",
    )
    @classmethod
    def _split(cls, value: str | list[str]) -> list[str]:
        """
        Parses a .env value written either comma-separated (a,b) or as
        a JSON list (["a","b"]) into trimmed, non-empty items.
        """
        if isinstance(value, str):
            if value.strip().startswith("["):
                value = json.loads(value)
            else:
                value = value.split(",")
        return [item.strip() for item in value if item.strip()]

    @property
    def database_url(self) -> URL:
        """Postgres DSN with credentials escaped (safe for special chars)."""
        return URL.create(
            drivername="postgresql",
            username=self.database_username,
            password=self.database_password,
            host=self.database_hostname,
            port=self.database_port,
            database=self.database_name,
        )


settings = Settings()
