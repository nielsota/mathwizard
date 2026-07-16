from pydantic import BaseModel


class StudentSummary(BaseModel):
    id: int
    username: str


class TeacherSummary(BaseModel):
    id: int
    username: str


class StudentsResponse(BaseModel):
    students: list[StudentSummary]


class MyTeacherResponse(BaseModel):
    teacher: TeacherSummary
