from mathwizard.exceptions import AuthorizationError, RoleNotAssignedError
from mathwizard.models.domain.user import User, UserRole, UserWithRole
from mathwizard.ports.unit_of_work import RosterUnitOfWork


class UserService:
    def with_role(self, uow: RosterUnitOfWork, user: User) -> UserWithRole:
        with uow:
            role = self._role(uow, user)
        return UserWithRole(id=user.id, username=user.username, role=role)

    def list_student_users(self, uow: RosterUnitOfWork, user: User) -> list[User]:
        with uow:
            teacher = uow.roster.get_teacher_by_user_id(user.id)
            if teacher is None:
                raise AuthorizationError("Teacher access required")
            students = uow.roster.list_students_for_teacher(teacher.id)
            users = uow.users.get_many([student.user_id for student in students])
        return sorted(users, key=lambda student: student.username)

    def get_teacher_user(self, uow: RosterUnitOfWork, user: User) -> User:
        with uow:
            student = uow.roster.get_student_by_user_id(user.id)
            if student is None:
                raise AuthorizationError("Student access required")
            teacher = uow.roster.get_teacher(student.teacher_id)
            if teacher is None:
                raise RoleNotAssignedError(user.id)
            return uow.users.get(teacher.user_id)

    # Called from inside another method's block, so it must not open one itself.
    def _role(self, uow: RosterUnitOfWork, user: User) -> UserRole:
        if uow.roster.get_teacher_by_user_id(user.id) is not None:
            return UserRole.TEACHER
        if uow.roster.get_student_by_user_id(user.id) is not None:
            return UserRole.STUDENT
        raise RoleNotAssignedError(user.id)
