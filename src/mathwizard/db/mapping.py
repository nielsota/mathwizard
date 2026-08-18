from mathwizard.db.tables.figure import FigureSchema
from mathwizard.db.tables.question import QuestionPartSchema, QuestionSchema
from mathwizard.db.tables.roster import StudentSchema, TeacherSchema
from mathwizard.db.tables.session import SessionSchema
from mathwizard.db.tables.user import UserSchema
from mathwizard.models.domain.figure import Figure, FigureDraft
from mathwizard.models.domain.question import Question, QuestionDraft
from mathwizard.models.domain.roster import Student, Teacher
from mathwizard.models.domain.session import AuthSession
from mathwizard.models.domain.user import User

# from_attributes is passed per call rather than configured on the domain models,
# which keeps the domain free of any hint that it is ever loaded from a database.
# A column renamed out from under an entity fails here as a ValidationError.


def user_to_domain(row: UserSchema) -> User:
    return User.model_validate(row, from_attributes=True)


def session_to_domain(row: SessionSchema) -> AuthSession:
    return AuthSession.model_validate(row, from_attributes=True)


def teacher_to_domain(row: TeacherSchema) -> Teacher:
    return Teacher.model_validate(row, from_attributes=True)


def student_to_domain(row: StudentSchema) -> Student:
    return Student.model_validate(row, from_attributes=True)


def question_to_domain(row: QuestionSchema) -> Question:
    return Question.model_validate(row, from_attributes=True)


def figure_to_domain(row: FigureSchema) -> Figure:
    return Figure.model_validate(row, from_attributes=True)


# The write direction stays spelled out. Copying draft fields onto a row in a loop
# would work today, but setting an attribute a table does not have is silently
# accepted by SQLAlchemy, so a future rename would drop data instead of failing.


def apply_question_draft(row: QuestionSchema, draft: QuestionDraft) -> None:
    row.topic = draft.topic
    row.title = draft.title
    row.stem = draft.stem
    row.source = draft.source
    row.tags = list(draft.tags)
    row.exam_id = draft.exam_id
    row.calculator_allowed = draft.calculator_allowed
    row.difficulty = draft.difficulty
    # Reassigning the collection lets the delete-orphan cascade drop the old parts.
    row.parts = [
        QuestionPartSchema(label=part.label, text=part.text, points=part.points)
        for part in draft.parts
    ]


def apply_figure_draft(row: FigureSchema, draft: FigureDraft) -> None:
    row.slug = draft.slug
    row.title = draft.title
    row.spec = draft.spec.model_dump()
    row.description = draft.description
    row.question_id = draft.question_id
    row.part_id = draft.part_id
