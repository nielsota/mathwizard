from datetime import timedelta
from pathlib import Path

from mathwizard.db.client import DBClient
from mathwizard.models.db import _utcnow


def make_db(tmp_path: Path) -> DBClient:
    return DBClient(f"sqlite:///{tmp_path / 'auth.db'}")


def test_create_user_stores_password_hash(tmp_path: Path) -> None:
    db = make_db(tmp_path)

    user = db.create_user("root", "hashed-password")

    assert user.id is not None
    assert user.username == "root"
    assert user.password_hash == "hashed-password"


def test_session_lifecycle(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    user = db.create_user("root", "hashed-password")
    assert user.id is not None

    session = db.create_session(user.id, timedelta(days=7))

    assert session.id
    assert session.user_id == user.id
    assert session.expires_at > _utcnow()
    assert db.get_session(session.id) is not None

    db.revoke_session(session.id)

    assert db.get_session(session.id) is None


def test_expired_session_is_not_returned(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    user = db.create_user("root", "hashed-password")
    assert user.id is not None

    session = db.create_session(user.id, timedelta(seconds=-1))

    assert db.get_session(session.id) is None
