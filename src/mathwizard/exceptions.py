class MathWizardError(Exception):
    """Base exception class for everything mathwizard."""


class AuthenticationError(MathWizardError):
    pass


class UserNotFoundError(MathWizardError):
    def __init__(self, user_id: int) -> None:
        super().__init__(f"User {user_id} not found")
        self.user_id = user_id


class QuestionNotFoundError(MathWizardError):
    def __init__(self, question_id: int) -> None:
        super().__init__(f"Question {question_id} not found")
        self.question_id = question_id
 