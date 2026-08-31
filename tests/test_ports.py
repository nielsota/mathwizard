import pytest

from mathwizard.ports.figure import FigureRepository
from mathwizard.ports.question import QuestionRepository
from mathwizard.ports.roster import RosterRepository
from mathwizard.ports.session import SessionRepository
from mathwizard.ports.unit_of_work import UnitOfWork, UnitOfWorkFactory
from mathwizard.ports.user import UserRepository

PORTS = [
    UserRepository,
    SessionRepository,
    RosterRepository,
    QuestionRepository,
    FigureRepository,
    UnitOfWork,
    UnitOfWorkFactory,
]


@pytest.mark.parametrize("port", PORTS, ids=lambda port: port.__name__)
def test_inheriting_a_port_without_implementing_it_fails_at_construction(
    port: type,
) -> None:
    incomplete = type("Incomplete", (port,), {})

    with pytest.raises(TypeError, match="abstract"):
        incomplete()
