from sqlmodel import Session as DBSession
from sqlmodel import select

from mathwizard.db.mixins.base import NeedsEngine
from mathwizard.models.db import Question, QuestionPart
from mathwizard.exceptions import QuestionNotFoundError


class QuestionsMixin(NeedsEngine):

    def create_question(
        self,
        title: str,
        stem: str,
        parts: list[dict],
        *,
        exam_id: str | None = None,
        calculator_allowed: bool | None = None,
        difficulty: int | None = None,
    ) -> Question:
        question = Question(
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
        return question

    def get_question(self, question_id: int) -> Question:
        with DBSession(self.engine) as session:
            question = session.get(Question, question_id)
            if question is None:
                raise QuestionNotFoundError(question_id)
            _ = question.parts
            return question

    def list_questions(self) -> list[Question]:
        with DBSession(self.engine) as session:
            questions = session.exec(select(Question)).all()
            for q in questions:
                _ = q.parts
            return list(questions)

    def update_question(
        self,
        question_id: int,
        *,
        title: str | None = None,
        stem: str | None = None,
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
