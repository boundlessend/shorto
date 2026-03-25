from threading import RLock

from app.models import ShortLink


class InMemoryLinkRepository:
    def __init__(self) -> None:
        self._links: dict[str, ShortLink] = {}
        self._lock = RLock()

    def add(self, link: ShortLink) -> None:
        with self._lock:
            self._links[link.code] = link

    def get(self, code: str) -> ShortLink | None:
        with self._lock:
            return self._links.get(code)

    def exists(self, code: str) -> bool:
        with self._lock:
            return code in self._links

    def list_all(self) -> list[ShortLink]:
        with self._lock:
            return list(self._links.values())
