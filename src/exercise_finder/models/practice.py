from __future__ import annotations

from pathlib import Path

import yaml  # type: ignore[import-untyped]
from pydantic import BaseModel  # type: ignore

from .multipart import MultipartQuestionOutput


class PracticeExerciseMetadata(BaseModel):
    """Metadata for a practice exercise set."""

    title: str
    subtitle: str

    @classmethod
    def load_from_yaml(cls, yaml_path: Path) -> "PracticeExerciseMetadata":
        """Load metadata from _meta.yaml file."""
        if not yaml_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {yaml_path}")

        with yaml_path.open("r") as f:
            data = yaml.safe_load(f)

        return cls.model_validate(data)


class PracticeExerciseSet(BaseModel):
    """Collection of practice exercises for a topic."""

    topic: str
    title: str
    subtitle: str
    exercises: list[MultipartQuestionOutput]

    def __add__(self, other: "PracticeExerciseSet") -> "PracticeExerciseSet":
        """
        Combine two PracticeExerciseSets.

        Validates that topic, title, and subtitle match before combining.
        Returns a new PracticeExerciseSet with combined exercises.
        """
        if not isinstance(other, PracticeExerciseSet):
            raise TypeError(f"Cannot add PracticeExerciseSet with {type(other)}")

        if self.topic != other.topic:
            raise ValueError(f"Cannot combine different topics: {self.topic} != {other.topic}")

        if self.title != other.title:
            raise ValueError(f"Cannot combine different titles: {self.title} != {other.title}")

        if self.subtitle != other.subtitle:
            raise ValueError(
                f"Cannot combine different subtitles: {self.subtitle} != {other.subtitle}"
            )

        return PracticeExerciseSet(
            topic=self.topic,
            title=self.title,
            subtitle=self.subtitle,
            exercises=self.exercises + other.exercises,
        )

    @classmethod
    def load_from_yaml(cls, yaml_path: Path) -> "PracticeExerciseSet":
        """Load exercise set from YAML file with validation."""
        with open(yaml_path) as f:
            data = yaml.safe_load(f)
        return cls.model_validate(data)

    @classmethod
    def load_from_directory(cls, topic_dir: Path) -> "PracticeExerciseSet":
        """
        Load practice exercises from a directory of individual YAML files.

        Directory structure:
            data/questions/practice/curated/unitcircle/
              |- p1.yaml
              |- p2.yaml
              |- ...

        Each file contains a single MultipartQuestionOutput.
        The directory name is used as the topic slug.

        Returns a PracticeExerciseSet with exercises loaded in sorted order.

        Example:
            exercise_set = PracticeExerciseSet.load_from_directory(
                Path("data/questions/practice/curated/unitcircle/")
            )
        """
        # Validate directory exists
        if not topic_dir.exists():
            raise FileNotFoundError(f"Topic directory not found: {topic_dir}")

        if not topic_dir.is_dir():
            raise ValueError(f"Path is not a directory: {topic_dir}")

        # Use directory name as topic
        topic = topic_dir.name

        # Load metadata
        metadata = PracticeExerciseMetadata.load_from_yaml(topic_dir / "_meta.yaml")

        # Load all practice YAML files (p*.yaml) and combine them
        yaml_files = sorted(topic_dir.glob("p*.yaml"))
        if not yaml_files:
            raise ValueError(f"No practice exercise files found in {topic_dir}")

        # Load each file and add to the result
        exercises = []
        for yaml_file in yaml_files:
            try:
                # Load each file as a single-exercise set (each file contains one MultipartQuestionOutput)
                with yaml_file.open("r") as f:
                    data = yaml.safe_load(f)
                    exercises.append(MultipartQuestionOutput.model_validate(data))
            except Exception as e:
                raise ValueError(f"Invalid exercise in {yaml_file.name}: {e}")

        return cls(
            topic=topic,
            title=metadata.title,
            subtitle=metadata.subtitle,
            exercises=exercises,
        )

