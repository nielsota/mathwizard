import typer
from alembic import command
from rich import print as rprint

from mathwizard.db.client import DBClient
from mathwizard.db.migrations import alembic_config
from mathwizard.enums import QuestionSource
from mathwizard.services.bootstrap import BootstrapService
from mathwizard.settings import get_settings

app = typer.Typer(help="MathWizard content/admin CLI.", no_args_is_help=True)


@app.callback()
def main() -> None:
    """MathWizard content/admin CLI."""


db_app = typer.Typer(help="Database schema management.", no_args_is_help=True)
app.add_typer(db_app, name="db")


@db_app.command("upgrade")
def db_upgrade() -> None:
    """Apply all pending Alembic migrations."""
    settings = get_settings()
    command.upgrade(alembic_config(settings), "head")
    rprint(f"[green]Schema up to date.[/green] {settings.database_url}")


@app.command()
def seed_practice() -> None:
    """Sync practice exercise YAMLs into the database (idempotent upsert)."""
    settings = get_settings()
    db = DBClient(settings.database_url)
    before = len(db.list_questions(source=QuestionSource.PRACTICE))
    BootstrapService(db, settings).seed_practice_questions()
    after = len(db.list_questions(source=QuestionSource.PRACTICE))
    db.engine.dispose()
    rprint(
        f"[green]Practice sync complete.[/green] "
        f"{after} practice questions in DB (+{after - before} new)."
    )


@app.command()
def seed_figures() -> None:
    """Sync figure spec YAMLs into the database (idempotent upsert)."""
    settings = get_settings()
    db = DBClient(settings.database_url)
    before = len(db.list_figures())
    BootstrapService(db, settings).seed_figures()
    after = len(db.list_figures())
    db.engine.dispose()
    rprint(
        f"[green]Figure sync complete.[/green] "
        f"{after} figures in DB (+{after - before} new)."
    )


if __name__ == "__main__":
    app()
