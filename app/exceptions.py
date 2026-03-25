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
            message="Чета не нашлась короткая ссылка.",
            details={"code": code},
        )


class CodeAlreadyExistsError(AppError):
    def __init__(self, code: str) -> None:
        super().__init__(
            status_code=409,
            error_code="custom_code_already_exists",
            message="Указанный custom_code уже юзается.",
            details={"code": code},
        )


class LinkExpiredError(AppError):
    def __init__(self, code: str) -> None:
        super().__init__(
            status_code=410,
            error_code="link_expired",
            message="Короткая ссылка истекла, увы.",
            details={"code": code},
        )


class LinkInactiveError(AppError):
    def __init__(self, code: str) -> None:
        super().__init__(
            status_code=410,
            error_code="link_inactive",
            message="Короткая ссылка неактивна бро.",
            details={"code": code},
        )
