import typer
from rich import print as rprint

from mathwizard.db.client import DBClient
from mathwizard.enums import QuestionSource
from mathwizard.services.bootstrap import BootstrapService
from mathwizard.settings import get_settings

app = typer.Typer(help="MathWizard content/admin CLI.", no_args_is_help=True)


@app.callback()
def main() -> None:
    """MathWizard content/admin CLI."""


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


if __name__ == "__main__":
    app()
