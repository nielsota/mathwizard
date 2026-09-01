import typer
from rich import print as rprint
from sqlalchemy import make_url

from mathwizard.db.engine import create_db_engine, create_session_factory
from mathwizard.db.migrations import upgrade_schema
from mathwizard.db.unit_of_work import SqlAlchemyUnitOfWorkFactory
from mathwizard.models.domain.question import QuestionSource
from mathwizard.services.bootstrap import BootstrapService
from mathwizard.settings import Settings, get_settings

app = typer.Typer(help="MathWizard content/admin CLI.", no_args_is_help=True)
db_app = typer.Typer(help="Database schema management.", no_args_is_help=True)
app.add_typer(db_app, name="db")


def _uow_factory(settings: Settings) -> SqlAlchemyUnitOfWorkFactory:
    engine = create_db_engine(settings.db.url)
    return SqlAlchemyUnitOfWorkFactory(create_session_factory(engine))


@app.callback()
def main() -> None:
    """MathWizard content/admin CLI."""


@db_app.command("upgrade")
def db_upgrade() -> None:
    """Apply all pending Alembic migrations."""
    settings = get_settings()
    upgrade_schema(settings)
    database_url = make_url(settings.db.url).render_as_string(hide_password=True)
    rprint(f"[green]Schema up to date.[/green] {database_url}")


@app.command()
def seed_practice() -> None:
    """Sync practice exercise YAMLs into the database (idempotent upsert)."""
    settings = get_settings()
    uow_factory = _uow_factory(settings)
    with uow_factory() as uow:
        before = len(uow.questions.list(source=QuestionSource.PRACTICE))
    BootstrapService(settings).seed_practice_questions(uow_factory())
    with uow_factory() as uow:
        after = len(uow.questions.list(source=QuestionSource.PRACTICE))
    rprint(
        f"[green]Practice sync complete.[/green] "
        f"{after} practice questions in DB (+{after - before} new)."
    )


@app.command()
def seed_figures() -> None:
    """Sync figure spec YAMLs into the database (idempotent upsert)."""
    settings = get_settings()
    uow_factory = _uow_factory(settings)
    with uow_factory() as uow:
        before = len(uow.figures.list())
    BootstrapService(settings).seed_figures(uow_factory())
    with uow_factory() as uow:
        after = len(uow.figures.list())
    rprint(
        f"[green]Figure sync complete.[/green] "
        f"{after} figures in DB (+{after - before} new)."
    )


if __name__ == "__main__":
    app()
