from __future__ import annotations

from datetime import datetime
from pathlib import Path

from pydantic import BaseModel  # type: ignore

from exercise_finder.constants import pdf_acronym_to_level_mapping
from exercise_finder.enums import ExamLevel


class Exam(BaseModel):
    id: str
    year: int
    tijdvak: int
    level: ExamLevel

    @classmethod
    def from_file_path(cls, file_path: Path) -> "Exam":
        """Create an Exam from a file path."""
        parts = file_path.stem.split("-")
        return cls(
            id=file_path.stem,
            level=pdf_acronym_to_level_mapping[parts[0].lower()],
            year=datetime.strptime(parts[3], "%y").year,
            tijdvak=int(parts[4]),
        )

    def __str__(self) -> str:
        return f"exam_{self.level.value}_{self.year}_tijdvak_{self.tijdvak}.pdf"

