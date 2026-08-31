from typing import Any

from fastapi import APIRouter, HTTPException, status

from mathwizard.app.auth import CurrentUserDep
from mathwizard.app.dependencies import FigureServiceDep, UnitOfWorkDep
from mathwizard.exceptions import DuplicateFigureSlugError, FigureNotFoundError
from mathwizard.models.api.figure import (
    FigureCreateRequest,
    FigureListResponse,
    FigureResponse,
)
from mathwizard.models.domain.figure import Figure, FigureDraft

router = APIRouter(prefix="/api/v1/figures", tags=["figures"])


@router.get("", response_model=FigureListResponse)
def list_figures(
    uow: UnitOfWorkDep,
    figure_service: FigureServiceDep,
    current_user: CurrentUserDep,
) -> dict[str, Any]:
    return {"figures": figure_service.list_figures(uow)}


@router.get("/{figure_id}", response_model=FigureResponse)
def get_figure(
    figure_id: int,
    uow: UnitOfWorkDep,
    figure_service: FigureServiceDep,
    current_user: CurrentUserDep,
) -> Figure:
    try:
        return figure_service.get_figure(uow, figure_id)
    except FigureNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post("", status_code=status.HTTP_201_CREATED, response_model=FigureResponse)
def create_figure(
    body: FigureCreateRequest,
    uow: UnitOfWorkDep,
    figure_service: FigureServiceDep,
    current_user: CurrentUserDep,
) -> Figure:
    try:
        return figure_service.create_figure(
            uow,
            FigureDraft(
                slug=body.slug,
                title=body.title,
                spec=body.spec,
                description=body.description,
            ),
        )
    except DuplicateFigureSlugError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
