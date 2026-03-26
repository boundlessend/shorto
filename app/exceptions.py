from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AppError(Exception):
    status_code: int
    error_code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)


class LinkNotFoundError(AppError):
    def __init__(self, code: str) -> None:
        super().__init__(
            status_code=404,
            error_code="link_not_found",
            message="Не нашли короткую ссылку.",
            details={"code": code},
        )


class CodeAlreadyExistsError(AppError):
    def __init__(self, code: str) -> None:
        super().__init__(
            status_code=409,
            error_code="custom_code_already_exists",
            message="Указанный custom_code уже используется.",
            details={"code": code},
        )


class LinkExpiredError(AppError):
    def __init__(self, code: str) -> None:
        super().__init__(
            status_code=410,
            error_code="link_expired",
            message="Короткая ссылка истекла.",
            details={"code": code},
        )


class LinkInactiveError(AppError):
    def __init__(self, code: str) -> None:
        super().__init__(
            status_code=410,
            error_code="link_inactive",
            message="Короткая ссылка неактивна.",
            details={"code": code},
        )
