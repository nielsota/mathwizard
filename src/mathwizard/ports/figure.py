from abc import abstractmethod
from typing import Protocol

from mathwizard.models.domain.figure import Figure, FigureDraft


class FigureRepository(Protocol):
    @abstractmethod
    def add(self, draft: FigureDraft) -> Figure: ...

    @abstractmethod
    def get(self, figure_id: int) -> Figure: ...

    @abstractmethod
    def get_by_slug(self, slug: str) -> Figure | None: ...

    @abstractmethod
    def upsert(self, draft: FigureDraft) -> Figure: ...

    @abstractmethod
    def list(self) -> list[Figure]: ...
