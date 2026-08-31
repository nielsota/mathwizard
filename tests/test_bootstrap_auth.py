from pathlib import Path

from mathwizard.db.unit_of_work import SqlAlchemyUnitOfWorkFactory
from mathwizard.services.bootstrap import BootstrapService
from mathwizard.settings import (
    BootstrapSettings,
    DatabaseSettings,
    PathSettings,
    Settings,
)
from tests.fakes import FakePasswordHasher


def _settings(tmp_path: Path, *, username: str, password: str) -> Settings:
    return Settings(
        db=DatabaseSettings(url="sqlite:///unused.db"),
        paths=PathSettings(repo_root=tmp_path),
        bootstrap=BootstrapSettings(username=username, password=password),
    )


def test_seed_root_user_hashes_configured_password(
    tmp_path: Path,
    uow_factory: SqlAlchemyUnitOfWorkFactory,
) -> None:
    settings = _settings(tmp_path, username="teacher", password="s3cret")
    hasher = FakePasswordHasher()

    BootstrapService(settings, hasher=hasher).seed_root_user(uow_factory())

    with uow_factory() as uow:
        user = uow.users.get_by_username("teacher")
    assert user is not None
    assert user.password_hash != "s3cret"
    assert hasher.verify("s3cret", user.password_hash)


def test_seed_root_user_is_idempotent(
    tmp_path: Path,
    uow_factory: SqlAlchemyUnitOfWorkFactory,
) -> None:
    hasher = FakePasswordHasher()
    BootstrapService(
        _settings(tmp_path, username="teacher", password="s3cret"),
        hasher=hasher,
    ).seed_root_user(uow_factory())

    BootstrapService(
        _settings(tmp_path, username="teacher", password="changed"),
        hasher=hasher,
    ).seed_root_user(uow_factory())

    with uow_factory() as uow:
        user = uow.users.get_by_username("teacher")
    assert user is not None
    assert hasher.verify("s3cret", user.password_hash)
    assert not hasher.verify("changed", user.password_hash)
