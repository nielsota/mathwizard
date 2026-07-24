from fastapi import APIRouter, HTTPException, status

from mathwizard.app.auth import CurrentUserDep
from mathwizard.app.dependencies import FigureServiceDep
from mathwizard.exceptions import DuplicateFigureSlugError, FigureNotFoundError
from mathwizard.models.figure import (
    FigureCreateRequest,
    FigureListResponse,
    FigureResponse,
)

router = APIRouter(prefix="/api/v1/figures", tags=["figures"])


@router.get("")
def list_figures(
    figure_service: FigureServiceDep,
    current_user: CurrentUserDep,
) -> FigureListResponse:
    return figure_service.list_figures()


@router.get("/{figure_id}")
def get_figure(
    figure_id: int,
    figure_service: FigureServiceDep,
    current_user: CurrentUserDep,
) -> FigureResponse:
    try:
        return figure_service.get_figure(figure_id)
    except FigureNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post("", status_code=status.HTTP_201_CREATED)
def create_figure(
    body: FigureCreateRequest,
    figure_service: FigureServiceDep,
    current_user: CurrentUserDep,
) -> FigureResponse:
    try:
        return figure_service.create_figure(body)
    except DuplicateFigureSlugError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
