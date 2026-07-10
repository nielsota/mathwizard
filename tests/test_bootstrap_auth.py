from pathlib import Path

from mathwizard.db.client import DBClient
from mathwizard.services.auth import verify_password
from mathwizard.services.bootstrap import seed_root_user


def make_db(tmp_path: Path) -> DBClient:
    return DBClient(f"sqlite:///{tmp_path / 'bootstrap.db'}")


def test_seed_root_user_hashes_configured_password(tmp_path: Path) -> None:
    db = make_db(tmp_path)

    seed_root_user(db, username="teacher", password="s3cret")

    user = db.get_user_by_username("teacher")
    assert user is not None
    assert user.password_hash != "s3cret"
    assert verify_password("s3cret", user.password_hash)


def test_seed_root_user_is_idempotent(tmp_path: Path) -> None:
    db = make_db(tmp_path)

    seed_root_user(db, username="teacher", password="s3cret")
    seed_root_user(db, username="teacher", password="changed")

    user = db.get_user_by_username("teacher")
    assert user is not None
    assert verify_password("s3cret", user.password_hash)
    assert not verify_password("changed", user.password_hash)
