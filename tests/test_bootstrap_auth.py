from pathlib import Path

from mathwizard.db.client import DBClient
from mathwizard.services.auth import verify_password
from mathwizard.services.bootstrap import BootstrapService
from mathwizard.settings import Settings


def make_db(tmp_path: Path) -> DBClient:
    return DBClient(f"sqlite:///{tmp_path / 'bootstrap.db'}")


def make_service(tmp_path: Path, *, username: str, password: str) -> BootstrapService:
    db = make_db(tmp_path)
    settings = Settings(
        database_url=f"sqlite:///{tmp_path / 'bootstrap.db'}",
        repo_root=tmp_path,
        bootstrap_username=username,
        bootstrap_password=password,
    )
    return BootstrapService(db, settings)


def test_seed_root_user_hashes_configured_password(tmp_path: Path) -> None:
    svc = make_service(tmp_path, username="teacher", password="s3cret")

    svc.seed_root_user()

    user = svc.db.get_user_by_username("teacher")
    assert user is not None
    assert user.password_hash != "s3cret"
    assert verify_password("s3cret", user.password_hash)


def test_seed_root_user_is_idempotent(tmp_path: Path) -> None:
    svc = make_service(tmp_path, username="teacher", password="s3cret")

    svc.seed_root_user()

    svc2 = BootstrapService(
        svc.db,
        Settings(
            database_url=f"sqlite:///{tmp_path / 'bootstrap.db'}",
            repo_root=tmp_path,
            bootstrap_username="teacher",
            bootstrap_password="changed",
        ),
    )
    svc2.seed_root_user()

    user = svc.db.get_user_by_username("teacher")
    assert user is not None
    assert verify_password("s3cret", user.password_hash)
    assert not verify_password("changed", user.password_hash)
