from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]
from pydantic import BaseModel  # type: ignore

from .exam import Exam
from .ocr import FigureInfo


class QuestionRecord(BaseModel):
    """
    A normalized, question-sized record suitable for indexing.
    """

    id: str
    exam: Exam
    title: str
    question_number: str
    question_text: str
    figure: FigureInfo
    source_images: list[str]
    page_images: list[str] | None = None
    figure_images: list[str] | None = None

    @classmethod
    def from_yaml(cls, yaml_path: Path) -> list["QuestionRecord"]:
        """
        Load question records from a YAML file.

        YAML file should contain a list of QuestionRecord objects.

        Validates:
        - File exists and is a .yaml file
        - Filename matches exam naming convention
        - All records belong to the same exam

        Example:
            records = QuestionRecord.from_yaml(Path("data/questions/exams/processed/VW-1025-a-18-1-o.yaml"))
        """
        # Validate file exists
        if not yaml_path.exists():
            raise FileNotFoundError(f"YAML file not found: {yaml_path}")

        if not yaml_path.is_file():
            raise ValueError(f"Path is not a file: {yaml_path}")

        # Validate extension
        if yaml_path.suffix != ".yaml":
            raise ValueError(f"File must have .yaml extension, got: {yaml_path.suffix}")

        # Validate filename pattern matches exam naming
        exam = Exam.from_file_path(yaml_path)

        # Load and validate records
        with open(yaml_path) as f:
            data = yaml.safe_load(f)

        if not data:
            raise ValueError(f"YAML file is empty: {yaml_path}")

        if not isinstance(data, list):
            raise ValueError(f"YAML file must contain a list of records, got: {type(data)}")

        # Parse all records
        records = []
        for i, item in enumerate(data):
            try:
                records.append(cls.model_validate(item))
            except Exception as e:
                raise ValueError(f"Invalid record at index {i}: {e}")

        # Validate all records belong to same exam
        exam_ids = {record.exam.id for record in records}
        if len(exam_ids) > 1:
            raise ValueError(f"All records must belong to same exam. Found: {exam_ids}")

        expected_exam_id = exam.id
        if records[0].exam.id != expected_exam_id:
            raise ValueError(
                f"Exam ID mismatch. Filename suggests '{expected_exam_id}', "
                f"but records have '{records[0].exam.id}'"
            )

        return records

    @classmethod
    def from_exam_dir(cls, exam_dir: Path) -> list["QuestionRecord"]:
        """
        Load question records from an exam directory containing individual YAML files.

        Each YAML file contains a single QuestionRecord object (e.g., q1.yaml, q2.yaml).

        Validates:
        - Directory exists and contains .yaml files
        - Directory name matches exam naming convention
        - All records belong to the same exam

        Example:
            records = QuestionRecord.from_exam_dir(Path("data/questions/exams/processed/VW-1025-a-18-1-o/"))
        """
        # Validate directory exists
        if not exam_dir.exists():
            raise FileNotFoundError(f"Exam directory not found: {exam_dir}")

        if not exam_dir.is_dir():
            raise ValueError(f"Path is not a directory: {exam_dir}")

        # Validate directory name matches exam naming
        exam = Exam.from_file_path(exam_dir)

        # Load all YAML files in the directory
        yaml_files = sorted(exam_dir.glob("*.yaml"))
        if not yaml_files:
            raise ValueError(f"No YAML files found in {exam_dir}")

        # Parse all records
        records = []
        for yaml_file in yaml_files:
            with yaml_file.open("r") as f:
                data = yaml.safe_load(f)
                try:
                    record = cls.model_validate(data)
                    records.append(record)
                except Exception as e:
                    raise ValueError(f"Invalid record in {yaml_file.name}: {e}")

        # Validate all records belong to same exam
        exam_ids = {record.exam.id for record in records}
        if len(exam_ids) > 1:
            raise ValueError(f"All records must belong to same exam. Found: {exam_ids}")

        expected_exam_id = exam.id
        if records[0].exam.id != expected_exam_id:
            raise ValueError(
                f"Exam ID mismatch. Directory suggests '{expected_exam_id}', "
                f"but records have '{records[0].exam.id}'"
            )

        return records

    def to_text(self) -> str:
        """Convert a question record to a text string for vector store indexing."""
        parts = [self.title.strip(), self.question_text.strip()]
        if self.figure and self.figure.description:
            parts.append("\n\n[FIGURE]\n" + self.figure.description.strip())
        return "\n".join(parts).strip() + "\n"

    def attributes_for_vector_store(self) -> dict[str, Any]:
        """Convert a question record to a dictionary of attributes for the vector store."""
        return {
            "record_id": self.id,
            "exam_id": self.exam.id,
            "exam_level": self.exam.level.value,
            "exam_year": str(self.exam.year),
            "exam_tijdvak": str(self.exam.tijdvak),
            "question_number": str(self.question_number),
            "page_images": json.dumps(self.page_images or [], ensure_ascii=False),
            "figure_images": json.dumps(self.figure_images or [], ensure_ascii=False),
            "source_images": json.dumps(self.source_images or [], ensure_ascii=False),
            "figure_present": str(bool(self.figure.present)),
            "figure_missing": str(bool(self.figure.missing)),
        }


class QuestionRecordVectorStoreAttributes(BaseModel):
    """
    Validated attributes from a vector store result.

    These are the metadata fields stored alongside each question in the vector store.
    """

    record_id: str
    exam_id: str
    exam_level: str
    exam_year: str
    exam_tijdvak: str
    question_number: str
    page_images: str  # JSON string
    figure_images: str  # JSON string
    source_images: str  # JSON string
    figure_present: str
    figure_missing: str

    def get_page_images(self) -> list[str]:
        """Parse page_images JSON string to list."""
        return json.loads(self.page_images)

    def get_figure_images(self) -> list[str]:
        """Parse figure_images JSON string to list."""
        return json.loads(self.figure_images)

    def get_source_images(self) -> list[str]:
        """Parse source_images JSON string to list."""
        return json.loads(self.source_images)

