from mathwizard.db.tables.figure import FigureSchema
from mathwizard.db.tables.question import QuestionPartSchema, QuestionSchema
from mathwizard.db.tables.roster import StudentSchema, TeacherSchema
from mathwizard.db.tables.session import SessionSchema
from mathwizard.db.tables.user import UserSchema
from mathwizard.models.domain.figure import Figure, FigureDraft, FigureSpec
from mathwizard.models.domain.question import Question, QuestionDraft, QuestionPart
from mathwizard.models.domain.roster import Student, Teacher
from mathwizard.models.domain.session import AuthSession
from mathwizard.models.domain.user import User


def user_to_domain(row: UserSchema) -> User:
    return User(id=row.id, username=row.username, password_hash=row.password_hash)


def session_to_domain(row: SessionSchema) -> AuthSession:
    return AuthSession(
        token=row.token,
        user_id=row.user_id,
        created_at=row.created_at,
        expires_at=row.expires_at,
        revoked_at=row.revoked_at,
    )


def teacher_to_domain(row: TeacherSchema) -> Teacher:
    return Teacher(id=row.id, user_id=row.user_id)


def student_to_domain(row: StudentSchema) -> Student:
    return Student(id=row.id, user_id=row.user_id, teacher_id=row.teacher_id)


def question_to_domain(row: QuestionSchema) -> Question:
    return Question(
        id=row.id,
        topic=row.topic,
        title=row.title,
        stem=row.stem,
        source=row.source,
        tags=list(row.tags),
        exam_id=row.exam_id,
        calculator_allowed=row.calculator_allowed,
        difficulty=row.difficulty,
        parts=[
            QuestionPart(
                id=part.id,
                label=part.label,
                text=part.text,
                points=part.points,
            )
            for part in row.parts
        ],
    )


def figure_to_domain(row: FigureSchema) -> Figure:
    return Figure(
        id=row.id,
        slug=row.slug,
        title=row.title,
        spec=FigureSpec.model_validate(row.spec),
        description=row.description,
        question_id=row.question_id,
        part_id=row.part_id,
    )


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
