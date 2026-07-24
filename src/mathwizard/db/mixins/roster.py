from sqlmodel import Session as DBSession
from sqlmodel import select

from mathwizard.db.mixins.base import NeedsEngine
from mathwizard.models.db import Student, Teacher, User


class RosterMixin(NeedsEngine):

    def create_teacher(self, user_id: int) -> Teacher:
        with DBSession(self.engine) as session:
            teacher = Teacher(user_id=user_id)
            session.add(teacher)
            session.commit()
            session.refresh(teacher)
            return teacher

    def create_student(self, user_id: int, teacher_id: int) -> Student:
        with DBSession(self.engine) as session:
            student = Student(user_id=user_id, teacher_id=teacher_id)
            session.add(student)
            session.commit()
            session.refresh(student)
            return student

    def get_teacher_by_user_id(self, user_id: int) -> Teacher | None:
        with DBSession(self.engine) as session:
            return session.exec(
                select(Teacher).where(Teacher.user_id == user_id)
            ).first()

    def get_student_by_user_id(self, user_id: int) -> Student | None:
        with DBSession(self.engine) as session:
            return session.exec(
                select(Student).where(Student.user_id == user_id)
            ).first()

    def list_student_users_for_teacher(self, teacher_id: int) -> list[User]:
        with DBSession(self.engine) as session:
            return list(
                session.exec(
                    select(User)
                    .join(Student, Student.user_id == User.id)
                    .where(Student.teacher_id == teacher_id)
                    .order_by(User.username)
                ).all()
            )

    def get_teacher_user(self, teacher_id: int) -> User | None:
        with DBSession(self.engine) as session:
            teacher = session.get(Teacher, teacher_id)
            if teacher is None:
                return None
            return session.get(User, teacher.user_id)
