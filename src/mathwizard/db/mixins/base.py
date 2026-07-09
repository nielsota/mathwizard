from typing import Protocol

from sqlalchemy import Engine

class NeedsEngine(Protocol):
    engine: Engine