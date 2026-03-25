from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

ALLOWED_CUSTOM_CODE_CHARS = set(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
)


class ErrorResponse(BaseModel):
    error: dict[str, Any]


class ValidationErrorItem(BaseModel):
    loc: list[str | int]
    msg: str
    type: str


class CreateLinkRequest(BaseModel):
    original_url: HttpUrl
    custom_code: str | None = Field(
        default=None,
        min_length=3,
        max_length=32,
        description="Опциональный custom_short-код.",
    )
    expires_in_seconds: int | None = Field(
        default=None,
        gt=0,
        description="Опциональный TTL в секундах.",
    )

    @field_validator("custom_code")
    @classmethod
    def validate_custom_code(cls, value: str | None) -> str | None:
        if value and any(
            char not in ALLOWED_CUSTOM_CODE_CHARS for char in value
        ):
            raise ValueError(
                "эт самое, custom_code может содержать только буквы, цифры, '-' и '_'"
            )
        return value


class LinkBase(BaseModel):
    original_url: str
    code: str
    created_at: datetime
    expires_at: datetime | None
    is_active: bool


class LinkWithStats(LinkBase):
    clicks: int
    is_deleted: bool


class CreateLinkResponse(LinkBase):
    short_url: str


class LinkStatsResponse(LinkWithStats):
    pass


class LinkListItemResponse(LinkWithStats):
    pass


class DeleteLinkResponse(BaseModel):
    message: str
    code: str
    is_active: bool


class HealthResponse(BaseModel):
    status: str = "ok"


class InternalLinkDTO(LinkWithStats):
    model_config = ConfigDict(from_attributes=True)
