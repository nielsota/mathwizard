from sqlalchemy import select
from sqlalchemy.orm import Session

from mathwizard.db.mapping import student_to_domain, teacher_to_domain
from mathwizard.db.tables.roster import StudentSchema, TeacherSchema
from mathwizard.models.domain.roster import Student, Teacher
from mathwizard.ports.roster import RosterRepository


class SqlAlchemyRosterRepository(RosterRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add_teacher(self, user_id: int) -> Teacher:
        row = TeacherSchema(user_id=user_id)
        self._session.add(row)
        self._session.flush()
        return teacher_to_domain(row)

    def add_student(self, user_id: int, teacher_id: int) -> Student:
        row = StudentSchema(user_id=user_id, teacher_id=teacher_id)
        self._session.add(row)
        self._session.flush()
        return student_to_domain(row)

    def get_teacher(self, teacher_id: int) -> Teacher | None:
        row = self._session.get(TeacherSchema, teacher_id)
        return None if row is None else teacher_to_domain(row)

    def get_teacher_by_user_id(self, user_id: int) -> Teacher | None:
        statement = select(TeacherSchema).where(TeacherSchema.user_id == user_id)
        row = self._session.scalars(statement).first()
        return None if row is None else teacher_to_domain(row)

    def get_student_by_user_id(self, user_id: int) -> Student | None:
        statement = select(StudentSchema).where(StudentSchema.user_id == user_id)
        row = self._session.scalars(statement).first()
        return None if row is None else student_to_domain(row)

    def list_students_for_teacher(self, teacher_id: int) -> list[Student]:
        statement = (
            select(StudentSchema)
            .where(StudentSchema.teacher_id == teacher_id)
            .order_by(StudentSchema.id)
        )
        return [
            student_to_domain(row) for row in self._session.scalars(statement).all()
        ]
