from contextlib import asynccontextmanager
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse

from app.exceptions import AppError
from app.repository import InMemoryLinkRepository
from app.schemas import (
    CreateLinkRequest,
    CreateLinkResponse,
    DeleteLinkResponse,
    HealthResponse,
    LinkListItemResponse,
    LinkStatsResponse,
)
from app.services import LinkService


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.link_service = LinkService(InMemoryLinkRepository())
    yield


app = FastAPI(
    title="Мини сокращалка URL",
    version="1.0.0",
    description="Простая in-memory сокращалка URL.",
    lifespan=lifespan,
)


def get_service(request: Request) -> LinkService:
    return request.app.state.link_service


ServiceDep = Annotated[LinkService, Depends(get_service)]


def error_response(
    *,
    status_code: int,
    code: str,
    message: str,
    details: Any,
) -> JSONResponse:
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


def base_link_data(link) -> dict[str, Any]:
    return {
        "original_url": link.original_url,
        "code": link.code,
        "created_at": link.created_at,
        "expires_at": link.expires_at,
        "is_active": link.is_active(),
    }


def detailed_link_data(link) -> dict[str, Any]:
    return {
        **base_link_data(link),
        "clicks": link.clicks,
        "is_deleted": link.is_deleted,
    }


@app.exception_handler(AppError)
async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
    return error_response(
        status_code=exc.status_code,
        code=exc.error_code,
        message=exc.message,
        details=exc.details,
    )


@app.exception_handler(RequestValidationError)
async def handle_validation_error(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    return error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        code="validation_error",
        message="Request validation failed.",
        details=exc.errors(),
    )


@app.get("/health", response_model=HealthResponse, tags=["system"])
def healthcheck() -> HealthResponse:
    return HealthResponse()


@app.post(
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
    link = service.create_link(
        original_url=str(payload.original_url),
        custom_code=payload.custom_code,
        expires_in_seconds=payload.expires_in_seconds,
    )
    return CreateLinkResponse(
        **base_link_data(link),
        short_url=str(request.url_for("redirect_to_original", code=link.code)),
    )


@app.get("/links", response_model=list[LinkListItemResponse], tags=["links"])
def list_links(service: ServiceDep) -> list[LinkListItemResponse]:
    return [
        LinkListItemResponse(**detailed_link_data(link))
        for link in service.list_links()
    ]


@app.get("/links/{code}", response_model=LinkStatsResponse, tags=["links"])
def get_link_stats(code: str, service: ServiceDep) -> LinkStatsResponse:
    return LinkStatsResponse(
        **detailed_link_data(service.get_link_stats(code))
    )


@app.delete("/links/{code}", response_model=DeleteLinkResponse, tags=["links"])
def deactivate_link(code: str, service: ServiceDep) -> DeleteLinkResponse:
    link = service.deactivate_link(code)
    return DeleteLinkResponse(
        message="Ссылку деактивировали, всё ок.",
        code=link.code,
        is_active=link.is_active(),
    )


@app.get("/{code}", name="redirect_to_original", tags=["redirect"])
def redirect_to_original(code: str, service: ServiceDep) -> RedirectResponse:
    link = service.resolve_link(code)
    return RedirectResponse(
        url=link.original_url,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    )
