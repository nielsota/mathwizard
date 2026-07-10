from sqlmodel import Session as DBSession
from sqlmodel import select

from mathwizard.db.mixins.base import NeedsEngine
from mathwizard.enums import QuestionSource
from mathwizard.exceptions import QuestionNotFoundError
from mathwizard.models.db import Question, QuestionPart


class QuestionsMixin(NeedsEngine):

    def create_question(
        self,
        title: str,
        stem: str,
        parts: list[dict],
        *,
        topic: str,
        source: QuestionSource = QuestionSource.PRACTICE,
        tags: list[str] | None = None,
        exam_id: str | None = None,
        calculator_allowed: bool | None = None,
        difficulty: int | None = None,
    ) -> Question:
        question = Question(
            topic=topic,
            source=source,
            tags=tags or [],
            title=title,
            stem=stem,
            exam_id=exam_id,
            calculator_allowed=calculator_allowed,
            difficulty=difficulty,
        )
        with DBSession(self.engine) as session:
            session.add(question)
            session.flush()
            for i, part in enumerate(parts):
                session.add(QuestionPart(
                    question_id=question.id,
                    label=part.get("label", chr(ord("a") + i)),
                    text=part["text"],
                    points=part.get("points", 0),
                ))
            session.commit()
            session.refresh(question)
            _ = question.parts
        return question

    def get_question(self, question_id: int) -> Question:
        with DBSession(self.engine) as session:
            question = session.get(Question, question_id)
            if question is None:
                raise QuestionNotFoundError(question_id)
            _ = question.parts
            return question

    def list_questions(
        self,
        *,
        topic: str | None = None,
        source: QuestionSource | None = None,
    ) -> list[Question]:
        statement = select(Question).order_by(Question.id)
        if topic is not None:
            statement = statement.where(Question.topic == topic)
        if source is not None:
            statement = statement.where(Question.source == source)

        with DBSession(self.engine) as session:
            questions = session.exec(statement).all()
            for question in questions:
                _ = question.parts
            return list(questions)

    def update_question(
        self,
        question_id: int,
        *,
        title: str | None = None,
        stem: str | None = None,
        topic: str | None = None,
        source: QuestionSource | None = None,
        tags: list[str] | None = None,
        exam_id: str | None = None,
        calculator_allowed: bool | None = None,
        difficulty: int | None = None,
        parts: list[dict] | None = None,
    ) -> Question:
        with DBSession(self.engine) as session:
            question = session.get(Question, question_id)
            if question is None:
                raise QuestionNotFoundError(question_id)

            if title is not None:
                question.title = title
            if stem is not None:
                question.stem = stem
            if topic is not None:
                question.topic = topic
            if source is not None:
                question.source = source
            if tags is not None:
                question.tags = tags
            if exam_id is not None:
                question.exam_id = exam_id
            if calculator_allowed is not None:
                question.calculator_allowed = calculator_allowed
            if difficulty is not None:
                question.difficulty = difficulty

            if parts is not None:
                for existing in question.parts:
                    session.delete(existing)
                session.flush()
                for i, part in enumerate(parts):
                    session.add(QuestionPart(
                        question_id=question_id,
                        label=part.get("label", chr(ord("a") + i)),
                        text=part["text"],
                        points=part.get("points", 0),
                    ))

            session.commit()
            session.refresh(question)
            _ = question.parts
            return question

    def delete_question(self, question_id: int) -> None:
        with DBSession(self.engine) as session:
            question = session.get(Question, question_id)
            if question is None:
                raise QuestionNotFoundError(question_id)
            session.delete(question)
            session.commit()
