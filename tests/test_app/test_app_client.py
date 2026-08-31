from fastapi.testclient import TestClient
from tests.app_client import make_settings, make_test_client
from tests.fakes import FakePasswordHasher, FakeUnitOfWorkFactory

from mathwizard.ports.unit_of_work import UnitOfWorkFactory


def test_make_test_client_logins_against_the_fake_unit_of_work() -> None:
    factory: UnitOfWorkFactory = FakeUnitOfWorkFactory()
    hasher = FakePasswordHasher()
    with factory() as uow:
        user = uow.users.add(username="root", password_hash=hasher.hash("secret"))
        uow.roster.add_teacher(user.id)
        uow.commit()
    client = make_test_client(factory, settings=make_settings())

    response = client.post(
        "/auth/login", json={"username": "root", "password": "secret"}
    )

    assert isinstance(client, TestClient)
    assert response.status_code == 200
    assert response.json()["username"] == "root"
