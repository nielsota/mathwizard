class MathWizardError(Exception):
    """Base exception class for everything mathwizard."""


class AuthenticationError(MathWizardError):
    pass


class AuthorizationError(MathWizardError):
    pass


class RoleNotAssignedError(MathWizardError):
    def __init__(self, user_id: int) -> None:
        super().__init__(f"User {user_id} has no teacher or student role")
        self.user_id = user_id


class UserNotFoundError(MathWizardError):
    def __init__(self, identifier: int | str) -> None:
        super().__init__(f"User {identifier} not found")
        self.identifier = identifier


class QuestionNotFoundError(MathWizardError):
    def __init__(self, question_id: int) -> None:
        super().__init__(f"Question {question_id} not found")
        self.question_id = question_id


class FigureNotFoundError(MathWizardError):
    def __init__(self, figure_id: int) -> None:
        super().__init__(f"Figure {figure_id} not found")
        self.figure_id = figure_id


class DuplicateFigureSlugError(MathWizardError):
    def __init__(self, slug: str) -> None:
        super().__init__(f"Figure with slug '{slug}' already exists")
        self.slug = slug
