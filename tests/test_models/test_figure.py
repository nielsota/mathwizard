import pytest
from pydantic import ValidationError

from mathwizard.models.figure import FigureSpec


def test_valid_function_graph_spec_parses() -> None:
    spec = FigureSpec.model_validate(
        {
            "viewport": {"x": [-5, 5]},
            "elements": [{"type": "functionGraph", "fn": "x^2"}],
        }
    )
    assert spec.show_grid is True
    assert spec.viewport.y is None
    assert spec.elements[0].fn == "x^2"
    assert spec.elements[0].type == "functionGraph"


def test_unknown_element_type_is_rejected() -> None:
    with pytest.raises(ValidationError):
        FigureSpec.model_validate(
            {
                "viewport": {"x": [-5, 5]},
                "elements": [{"type": "banana", "fn": "x^2"}],
            }
        )


def test_missing_fn_is_rejected() -> None:
    with pytest.raises(ValidationError):
        FigureSpec.model_validate(
            {"viewport": {"x": [-5, 5]}, "elements": [{"type": "functionGraph"}]}
        )
