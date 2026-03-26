from threading import RLock

from app.models import ShortLink


class InMemoryLinkRepository:
    def __init__(self) -> None:
        self._storage: dict[str, ShortLink] = {}
        self._lock = RLock()

    def add(self, link: ShortLink) -> None:
        with self._lock:
            self._storage[link.code] = link

    def add_if_absent(self, link: ShortLink) -> bool:
        with self._lock:
            if link.code in self._storage:
                return False
            self._storage[link.code] = link
            return True

    def get(self, code: str) -> ShortLink | None:
        with self._lock:
            return self._storage.get(code)

    def exists(self, code: str) -> bool:
        with self._lock:
            return code in self._storage

    def list_all(self) -> list[ShortLink]:
        with self._lock:
            return list(self._storage.values())
