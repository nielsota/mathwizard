# mypy: ignore-errors
from functools import lru_cache
from pathlib import Path

from pydantic import Field  # type: ignore[import-untyped]
from pydantic_settings import BaseSettings, SettingsConfigDict  # type: ignore[import-untyped]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    openai_api_key: str
    session_secret_key: str
    database_url: str = "sqlite:///data/mathwizard.db"
    repo_root: Path = Field(default_factory=_repo_root)
    session_ttl_days: int = 7
    cookie_secure: bool = False
    bootstrap_username: str = "root"
    bootstrap_password: str = "root"

    cognito_domain: str
    cognito_client_id: str
    cognito_client_secret: str
    cognito_user_pool_id: str
    cognito_region: str = "us-east-1"
    cognito_redirect_uri: str = "http://localhost:8000/callback"

    @property
    def data_dir(self) -> Path:
        return self.repo_root / "data"

    @property
    def practice_dir(self) -> Path:
        return self.data_dir / "questions" / "practice"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
