from tests.app_client import make_test_client
from tests.fakes import FakePasswordHasher, FakeUnitOfWorkFactory

from mathwizard.app.routes.figures import router as figures_router
from mathwizard.models.domain.figure import FigureDraft, FigureSpec, Viewport
from mathwizard.ports.unit_of_work import UnitOfWorkFactory

VALID_BODY = {
    "slug": "parabool",
    "title": "Parabool",
    "spec": {
        "viewport": {"x": [-5, 5]},
        "elements": [{"type": "functionGraph", "fn": "x^2"}],
    },
}


def authenticate(client, uow_factory: UnitOfWorkFactory) -> None:
    hasher = FakePasswordHasher()
    with uow_factory() as uow:
        user = uow.users.add(username="root", password_hash=hasher.hash("secret"))
        uow.roster.add_teacher(user.id)
        uow.commit()
    response = client.post(
        "/auth/login", json={"username": "root", "password": "secret"}
    )
    assert response.status_code == 200


def seed_figure(
    uow_factory: UnitOfWorkFactory,
    *,
    slug: str,
    title: str,
) -> int:
    with uow_factory() as uow:
        figure = uow.figures.add(
            FigureDraft(
                slug=slug,
                title=title,
                spec=FigureSpec(viewport=Viewport(x=(-5.0, 5.0))),
            )
        )
        uow.commit()
    return figure.id


def test_list_requires_authentication() -> None:
    client = make_test_client(FakeUnitOfWorkFactory(), figures_router)
    assert client.get("/api/v1/figures").status_code == 401


def test_post_then_list_and_get() -> None:
    uow_factory = FakeUnitOfWorkFactory()
    client = make_test_client(uow_factory, figures_router)
    authenticate(client, uow_factory)

    created = client.post("/api/v1/figures", json=VALID_BODY)
    assert created.status_code == 201
    figure_id = created.json()["id"]

    listing = client.get("/api/v1/figures")
    assert listing.status_code == 200
    assert [f["slug"] for f in listing.json()["figures"]] == ["parabool"]

    detail = client.get(f"/api/v1/figures/{figure_id}")
    assert detail.status_code == 200
    assert detail.json()["spec"]["elements"][0]["fn"] == "x^2"


def test_list_figures_omits_spec_and_description() -> None:
    uow_factory = FakeUnitOfWorkFactory()
    seed_figure(uow_factory, slug="parabola", title="Parabola")
    client = make_test_client(uow_factory, figures_router)
    authenticate(client, uow_factory)

    response = client.get("/api/v1/figures")

    summary = response.json()["figures"][0]
    assert summary == {
        "id": 1,
        "slug": "parabola",
        "title": "Parabola",
        "question_id": None,
        "part_id": None,
    }


def test_post_duplicate_slug_conflicts() -> None:
    uow_factory = FakeUnitOfWorkFactory()
    client = make_test_client(uow_factory, figures_router)
    authenticate(client, uow_factory)
    client.post("/api/v1/figures", json=VALID_BODY)
    assert client.post("/api/v1/figures", json=VALID_BODY).status_code == 409


def test_post_malformed_spec_is_422() -> None:
    uow_factory = FakeUnitOfWorkFactory()
    client = make_test_client(uow_factory, figures_router)
    authenticate(client, uow_factory)
    bad = {
        "slug": "x",
        "title": "x",
        "spec": {"viewport": {"x": [-5, 5]}, "elements": [{"type": "banana"}]},
    }
    assert client.post("/api/v1/figures", json=bad).status_code == 422


def test_get_missing_is_404() -> None:
    uow_factory = FakeUnitOfWorkFactory()
    client = make_test_client(uow_factory, figures_router)
    authenticate(client, uow_factory)
    assert client.get("/api/v1/figures/999").status_code == 404
