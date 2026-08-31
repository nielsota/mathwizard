from abc import abstractmethod
from typing import Protocol

from mathwizard.models.domain.roster import Student, Teacher


class RosterRepository(Protocol):
    @abstractmethod
    def add_teacher(self, user_id: int) -> Teacher: ...

    @abstractmethod
    def add_student(self, user_id: int, teacher_id: int) -> Student: ...

    @abstractmethod
    def get_teacher(self, teacher_id: int) -> Teacher | None: ...

    @abstractmethod
    def get_teacher_by_user_id(self, user_id: int) -> Teacher | None: ...

    @abstractmethod
    def get_student_by_user_id(self, user_id: int) -> Student | None: ...

    @abstractmethod
    def list_students_for_teacher(self, teacher_id: int) -> list[Student]: ...
