from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    password: str


class Question(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    exam_id: str | None = None
    title: str
    stem: str
    calculator_allowed: bool | None = None
    difficulty: int | None = None

    parts: list["QuestionPart"] = Relationship(
        back_populates="question",
        cascade_delete=True,
    )


class QuestionPart(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    question_id: int = Field(foreign_key="question.id")
    label: str
    text: str
    points: int = 0

    question: Question = Relationship(back_populates="parts")