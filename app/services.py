import secrets
import string
from datetime import timedelta

from app.exceptions import (
    CodeAlreadyExistsError,
    LinkExpiredError,
    LinkInactiveError,
    LinkNotFoundError,
)
from app.models import ShortLink, utc_now
from app.repository import InMemoryLinkRepository


class LinkService:
    _alphabet = string.ascii_letters + string.digits
    _default_code_length = 6

    def __init__(self, repository: InMemoryLinkRepository) -> None:
        self.repository = repository

    def create_link(
        self,
        *,
        original_url: str,
        custom_code: str | None,
        expires_in_seconds: int | None,
    ) -> ShortLink:
        expires_at = (
            utc_now() + timedelta(seconds=expires_in_seconds)
            if expires_in_seconds is not None
            else None
        )
        if custom_code is not None:
            link = ShortLink(
                original_url=original_url,
                code=custom_code,
                expires_at=expires_at,
            )

            if not self.repository.add_if_absent(link):
                raise CodeAlreadyExistsError(custom_code)

            return link
        while True:
            code = self._generate_code()
            link = ShortLink(
                original_url=original_url,
                code=code,
                expires_at=expires_at,
            )
            if self.repository.add_if_absent(link):
                return link

    def resolve_link(self, code: str) -> ShortLink:
        link = self._get_existing_link(code)

        if link.is_deleted:
            raise LinkInactiveError(code)
        if link.is_expired():
            raise LinkExpiredError(code)

        link.clicks += 1
        return link

    def get_link_stats(self, code: str) -> ShortLink:
        return self._get_existing_link(code)

    def deactivate_link(self, code: str) -> ShortLink:
        link = self._get_existing_link(code)
        link.is_deleted = True
        return link

    def list_links(self) -> list[ShortLink]:
        return sorted(
            self.repository.list_all(),
            key=lambda link: link.created_at,
            reverse=True,
        )

    def _get_existing_link(self, code: str) -> ShortLink:
        link = self.repository.get(code)
        if link is None:
            raise LinkNotFoundError(code)
        return link

    def _generate_code(self) -> str:
        return "".join(
            secrets.choice(self._alphabet)
            for _ in range(self._default_code_length)
        )
