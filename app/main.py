from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.exceptions import AppError
from app.handlers import (
    handle_app_error,
    handle_validation_error,
    router,
)
from app.repository import InMemoryLinkRepository
from app.services import LinkService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Инициализирует in-memory зависимости на время жизни приложения."""
    app.state.link_service = LinkService(InMemoryLinkRepository())
    yield


app = FastAPI(
    title="Мини сокращалка URL",
    version="1.0.0",
    description="Простая in-memory сокращалка URL.",
    lifespan=lifespan,
)

app.add_exception_handler(AppError, handle_app_error)
app.add_exception_handler(RequestValidationError, handle_validation_error)
app.include_router(router)
