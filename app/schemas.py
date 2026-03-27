from datetime import datetime


from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

ALLOWED_CUSTOM_CODE_CHARS = set(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
)


class CreateLinkRequest(BaseModel):
    """Тело запроса на создание короткой ссылки."""

    original_url: HttpUrl
    custom_code: str | None = Field(
        default=None,
        min_length=3,
        max_length=32,
        description="Опциональный custom short-code длиной от 3 до 32 символов.",
    )
    expires_in_seconds: int | None = Field(
        default=None,
        gt=0,
        description="Опциональный TTL в секундах. После истечения ссылка вернёт 410.",
    )

    @field_validator("custom_code")
    @classmethod
    def validate_custom_code(cls, value: str | None) -> str | None:
        if value and any(
            char not in ALLOWED_CUSTOM_CODE_CHARS for char in value
        ):
            raise ValueError(
                "custom_code может содержать только буквы, цифры, '-' и '_'"
            )
        return value


class LinkBase(BaseModel):
    """Базовые поля короткой ссылки, используемые в большинстве ответов."""

    original_url: str
    code: str
    created_at: datetime
    expires_at: datetime | None
    is_active: bool


class LinkWithStats(LinkBase):
    """Расширенная версия ссылки со статистикой и флагом удаления."""

    clicks: int
    is_deleted: bool


class CreateLinkResponse(LinkBase):
    """Ответ после создания короткой ссылки."""

    short_url: str


class LinkStatsResponse(LinkWithStats):
    """Подробный ответ по одной короткой ссылке."""

    pass


class LinkListItemResponse(LinkWithStats):
    """Элемент ответа списка ссылок."""

    pass


class DeleteLinkResponse(BaseModel):
    """Ответ после деактивации ссылки."""

    message: str
    code: str
    is_active: bool


class HealthResponse(BaseModel):
    """Ответ health-check эндпоинта."""

    status: str = "ok"
