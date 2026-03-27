from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse

from app.exceptions import AppError
from app.models import ShortLink
from app.schemas import (
    CreateLinkRequest,
    CreateLinkResponse,
    DeleteLinkResponse,
    HealthResponse,
    LinkListItemResponse,
    LinkStatsResponse,
)
from app.services import LinkService

router = APIRouter()


def get_service(request: Request) -> LinkService:
    """Возвращает сервис ссылок, сохранённый в `app.state`."""
    return request.app.state.link_service


ServiceDep = Annotated[LinkService, Depends(get_service)]


def error_response(
    *,
    status_code: int,
    code: str,
    message: str,
    details: Any,
) -> JSONResponse:
    """Собирает единый формат ошибок для всех API-ответов.

    Фронтенд может стабильно ориентироваться на поля:
    `error.code`, `error.message` и `error.details`.
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details,
            }
        },
    )


def base_link_data(link: ShortLink) -> dict[str, Any]:
    """Преобразует модель ссылки в базовый JSON-пэйлоад ответа."""
    return {
        "original_url": link.original_url,
        "code": link.code,
        "created_at": link.created_at,
        "expires_at": link.expires_at,
        "is_active": link.is_active(),
    }


def detailed_link_data(link: ShortLink) -> dict[str, Any]:
    """Добавляет к базовым полям служебную статистику по ссылке."""
    return {
        **base_link_data(link),
        "clicks": link.clicks,
        "is_deleted": link.is_deleted,
    }


async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
    """Преобразует доменные ошибки приложения в единый JSON-ответ."""
    return error_response(
        status_code=exc.status_code,
        code=exc.error_code,
        message=exc.message,
        details=exc.details,
    )


async def handle_validation_error(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    """Возвращает ошибки валидации FastAPI в общем формате API."""
    return error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        code="validation_error",
        message="Валидация запроса не удалась.",
        details=exc.errors(),
    )


@router.get("/health", response_model=HealthResponse, tags=["system"])
def healthcheck() -> HealthResponse:
    """Проверка доступности сервиса.

    Используется фронтендом и инфраструктурой для quick health-check.
    """
    return HealthResponse()


@router.post(
    "/links",
    response_model=CreateLinkResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["links"],
)
def create_short_link(
    payload: CreateLinkRequest,
    request: Request,
    service: ServiceDep,
) -> CreateLinkResponse:
    """Создаёт короткую ссылку.

    Возвращает код, итоговый short URL и признаки активности ссылки.
    """
    link = service.create_link(
        original_url=str(payload.original_url),
        custom_code=payload.custom_code,
        expires_in_seconds=payload.expires_in_seconds,
    )
    return CreateLinkResponse(
        **base_link_data(link),
        short_url=str(request.url_for("redirect_to_original", code=link.code)),
    )


@router.get(
    "/links", response_model=list[LinkListItemResponse], tags=["links"]
)
def list_links(service: ServiceDep) -> list[LinkListItemResponse]:
    """Возвращает список созданных коротких ссылок со статистикой."""
    return [
        LinkListItemResponse(**detailed_link_data(link))
        for link in service.list_links()
    ]


@router.get("/links/{code}", response_model=LinkStatsResponse, tags=["links"])
def get_link_stats(code: str, service: ServiceDep) -> LinkStatsResponse:
    """Возвращает подробную статистику по конкретной короткой ссылке."""
    return LinkStatsResponse(
        **detailed_link_data(service.get_link_stats(code))
    )


@router.delete(
    "/links/{code}",
    response_model=DeleteLinkResponse,
    tags=["links"],
)
def deactivate_link(code: str, service: ServiceDep) -> DeleteLinkResponse:
    """Деактивирует ссылку без физического удаления из хранилища."""
    link = service.deactivate_link(code)
    return DeleteLinkResponse(
        message="Ссылка деактивирована.",
        code=link.code,
        is_active=link.is_active(),
    )


@router.get("/{code}", name="redirect_to_original", tags=["redirect"])
def redirect_to_original(code: str, service: ServiceDep) -> RedirectResponse:
    """Редиректит на исходный URL и увеличивает счётчик переходов."""
    link = service.resolve_link(code)
    return RedirectResponse(
        url=link.original_url,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    )
