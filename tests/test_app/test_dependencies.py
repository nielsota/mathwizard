from fastapi import FastAPI
from fastapi.testclient import TestClient

from mathwizard.app.dependencies import UnitOfWorkDep
from mathwizard.db.unit_of_work import SqlAlchemyUnitOfWorkFactory
from mathwizard.ports.unit_of_work import UnitOfWork


def make_client(
    uow_factory: SqlAlchemyUnitOfWorkFactory,
    seen: list[UnitOfWork],
) -> TestClient:
    app = FastAPI()
    app.state.uow_factory = uow_factory

    @app.get("/probe")
    def probe(uow: UnitOfWorkDep) -> dict[str, bool]:
        seen.append(uow)
        return {"entered": hasattr(uow, "users")}

    return TestClient(app)


def test_the_dependency_builds_a_fresh_unit_of_work_per_request(
    uow_factory: SqlAlchemyUnitOfWorkFactory,
) -> None:
    seen: list[UnitOfWork] = []
    client = make_client(uow_factory, seen)

    client.get("/probe")
    client.get("/probe")

    assert len(seen) == 2
    assert seen[0] is not seen[1]


def test_the_dependency_hands_over_an_unopened_unit_of_work(
    uow_factory: SqlAlchemyUnitOfWorkFactory,
) -> None:
    seen: list[UnitOfWork] = []
    client = make_client(uow_factory, seen)

    response = client.get("/probe")

    assert response.json() == {"entered": False}
