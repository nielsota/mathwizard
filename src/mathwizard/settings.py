# mypy: ignore-errors
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


class PathSettings(BaseModel):
    repo_root: Path = Field(default_factory=_repo_root)

    @property
    def data_dir(self) -> Path:
        return self.repo_root / "data"

    @property
    def practice_dir(self) -> Path:
        return self.data_dir / "questions" / "practice"

    @property
    def figures_dir(self) -> Path:
        return self.data_dir / "questions" / "figures"

    @property
    def frontend_dist_dir(self) -> Path:
        return self.repo_root / "frontend" / "dist"


class DatabaseSettings(BaseModel):
    url: str = "sqlite:///data/db/mathwizard.db"


class WebSettings(BaseModel):
    session_ttl_days: int = 7
    session_cookie_name: str = "mw_session"
    cookie_secure: bool = False


class BootstrapSettings(BaseModel):
    username: str = "root"
    password: str = "root"
    student_usernames: list[str] = ["student1", "student2"]
    student_password: str = "student"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
        env_nested_delimiter="__",
    )

    paths: PathSettings = Field(default_factory=PathSettings)
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    web: WebSettings = Field(default_factory=WebSettings)
    bootstrap: BootstrapSettings = Field(default_factory=BootstrapSettings)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
