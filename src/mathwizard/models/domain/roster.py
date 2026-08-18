from pydantic import BaseModel


class Teacher(BaseModel):
    id: int
    user_id: int


class Student(BaseModel):
    id: int
    user_id: int
    teacher_id: int
