from mathwizard.db.client import DBClient
from mathwizard.enums import UserRole
from mathwizard.exceptions import AuthorizationError, RoleNotAssignedError
from mathwizard.models.auth import UserResponse
from mathwizard.models.db import User
from mathwizard.models.user import (
    MyTeacherResponse,
    StudentsResponse,
    StudentSummary,
    TeacherSummary,
)


class UserService:
    def __init__(self, db: DBClient) -> None:
        self.db = db

    def get_role(self, user: User) -> UserRole:
        assert user.id is not None
        if self.db.get_teacher_by_user_id(user.id) is not None:
            return UserRole.TEACHER
        if self.db.get_student_by_user_id(user.id) is not None:
            return UserRole.STUDENT
        raise RoleNotAssignedError(user.id)

    def to_response(self, user: User) -> UserResponse:
        assert user.id is not None
        return UserResponse(id=user.id, username=user.username, role=self.get_role(user))

    def list_students(self, user: User) -> StudentsResponse:
        assert user.id is not None
        teacher = self.db.get_teacher_by_user_id(user.id)
        if teacher is None:
            raise AuthorizationError("Teacher access required")
        assert teacher.id is not None
        students = self.db.list_student_users_for_teacher(teacher.id)
        return StudentsResponse(
            students=[
                StudentSummary(id=student.id, username=student.username)
                for student in students
                if student.id is not None
            ]
        )

    def get_my_teacher(self, user: User) -> MyTeacherResponse:
        assert user.id is not None
        student = self.db.get_student_by_user_id(user.id)
        if student is None:
            raise AuthorizationError("Student access required")
        teacher_user = self.db.get_teacher_user(student.teacher_id)
        if teacher_user is None or teacher_user.id is None:
            raise RoleNotAssignedError(user.id)
        return MyTeacherResponse(
            teacher=TeacherSummary(id=teacher_user.id, username=teacher_user.username)
        )
