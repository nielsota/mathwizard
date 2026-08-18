from datetime import datetime, timedelta

from sqlalchemy.orm import Session, sessionmaker

from mathwizard.db.repositories.session import SqlAlchemySessionRepository
from mathwizard.db.repositories.user import SqlAlchemyUserRepository
from mathwizard.ports.session import SessionRepository

NOW = datetime(2026, 8, 17, 12, 0, 0)


def _seed_user(session: Session) -> int:
    user = SqlAlchemyUserRepository(session).add(
        username="root", password_hash="hash"
    )
    session.commit()
    return user.id


def test_repository_satisfies_the_session_repository_protocol(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        repository: SessionRepository = SqlAlchemySessionRepository(session)

    assert repository is not None


def test_add_persists_a_session(session_factory: sessionmaker[Session]) -> None:
    with session_factory() as session:
        user_id = _seed_user(session)
        SqlAlchemySessionRepository(session).add(
            token="tok",
            user_id=user_id,
            created_at=NOW,
            expires_at=NOW + timedelta(days=7),
        )
        session.commit()

    with session_factory() as session:
        stored = SqlAlchemySessionRepository(session).get("tok")

    assert stored is not None
    assert stored.user_id == user_id
    assert stored.expires_at == NOW + timedelta(days=7)
    assert stored.revoked_at is None


def test_get_returns_none_for_unknown_token(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        assert SqlAlchemySessionRepository(session).get("nope") is None


def test_get_returns_expired_sessions_so_the_domain_can_judge_them(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        user_id = _seed_user(session)
        SqlAlchemySessionRepository(session).add(
            token="tok",
            user_id=user_id,
            created_at=NOW - timedelta(days=8),
            expires_at=NOW - timedelta(days=1),
        )
        session.commit()

    with session_factory() as session:
        stored = SqlAlchemySessionRepository(session).get("tok")

    assert stored is not None
    assert stored.is_active(NOW) is False


def test_revoke_stamps_the_given_timestamp(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        user_id = _seed_user(session)
        SqlAlchemySessionRepository(session).add(
            token="tok",
            user_id=user_id,
            created_at=NOW,
            expires_at=NOW + timedelta(days=7),
        )
        session.commit()

    with session_factory() as session:
        SqlAlchemySessionRepository(session).revoke("tok", NOW)
        session.commit()

    with session_factory() as session:
        stored = SqlAlchemySessionRepository(session).get("tok")

    assert stored is not None
    assert stored.revoked_at == NOW


def test_revoke_is_a_no_op_for_unknown_token(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        SqlAlchemySessionRepository(session).revoke("nope", NOW)
        session.commit()

    with session_factory() as session:
        assert SqlAlchemySessionRepository(session).get("nope") is None
