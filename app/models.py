from dataclasses import dataclass, field
from datetime import UTC, datetime


def utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass(slots=True)
class ShortLink:
    original_url: str
    code: str
    created_at: datetime = field(default_factory=utc_now)
    expires_at: datetime | None = None
    clicks: int = 0
    is_deleted: bool = False

    def is_expired(self, now: datetime | None = None) -> bool:
        return (
            self.expires_at is not None
            and (now or utc_now()) >= self.expires_at
        )

    def is_active(self, now: datetime | None = None) -> bool:
        return not self.is_deleted and not self.is_expired(now)
