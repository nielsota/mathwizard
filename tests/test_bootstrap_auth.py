from pathlib import Path

from mathwizard.db.unit_of_work import SqlAlchemyUnitOfWorkFactory
from mathwizard.services.auth import verify_password
from mathwizard.services.bootstrap import BootstrapService
from mathwizard.settings import Settings


def _settings(tmp_path: Path, *, username: str, password: str) -> Settings:
    return Settings(
        database_url="sqlite:///unused.db",
        repo_root=tmp_path,
        bootstrap_username=username,
        bootstrap_password=password,
    )


def test_seed_root_user_hashes_configured_password(
    tmp_path: Path,
    uow_factory: SqlAlchemyUnitOfWorkFactory,
) -> None:
    settings = _settings(tmp_path, username="teacher", password="s3cret")

    BootstrapService(settings).seed_root_user(uow_factory())

    with uow_factory() as uow:
        user = uow.users.get_by_username("teacher")
    assert user is not None
    assert user.password_hash != "s3cret"
    assert verify_password("s3cret", user.password_hash)


def test_seed_root_user_is_idempotent(
    tmp_path: Path,
    uow_factory: SqlAlchemyUnitOfWorkFactory,
) -> None:
    BootstrapService(
        _settings(tmp_path, username="teacher", password="s3cret")
    ).seed_root_user(uow_factory())

    BootstrapService(
        _settings(tmp_path, username="teacher", password="changed")
    ).seed_root_user(uow_factory())

    with uow_factory() as uow:
        user = uow.users.get_by_username("teacher")
    assert user is not None
    assert verify_password("s3cret", user.password_hash)
    assert not verify_password("changed", user.password_hash)
