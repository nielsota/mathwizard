from __future__ import annotations

from pydantic import BaseModel  # type: ignore


class FigureInfo(BaseModel):
    """Figure information extracted from a question."""

    present: bool
    missing: bool = False
    description: str | None = None


class QuestionFromImagesOutput(BaseModel):
    """
    Output contract for the image -> question transcription agent.
    """

    question_text: str
    title: str
    figure: FigureInfo

