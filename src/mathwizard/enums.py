from enum import StrEnum


class QuestionSource(StrEnum):
    PRACTICE = "practice"
    EXAM = "exam"
    GENERATED = "generated"


class UserRole(StrEnum):
    TEACHER = "teacher"
    STUDENT = "student"
