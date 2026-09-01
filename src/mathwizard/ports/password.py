from abc import abstractmethod
from typing import Protocol


class PasswordHasher(Protocol):
    dummy_hash: str

    @abstractmethod
    def hash(self, plain: str) -> str: ...

    @abstractmethod
    def verify(self, plain: str, hashed: str) -> bool: ...
