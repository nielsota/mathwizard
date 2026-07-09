from pathlib import Path

from sqlalchemy.engine import make_url
from sqlmodel import SQLModel, create_engine

from .mixins import UserMixin, QuestionsMixin


class DBClient(UserMixin, QuestionsMixin):
    def __init__(self, database_url: str, echo: bool = False):
        Path(make_url(database_url).database).parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(database_url, echo=echo)
        SQLModel.metadata.create_all(self.engine)
