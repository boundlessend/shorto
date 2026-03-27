import inspect

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repository import InMemoryLinkRepository
from app.services import LinkService


@pytest.fixture()
def client() -> TestClient:
    """Поднимает изолированный TestClient с чистым in-memory хранилищем."""
    app.state.link_service = LinkService(InMemoryLinkRepository())
    with TestClient(app) as test_client:
        yield test_client


def pytest_runtest_setup(item: pytest.Item) -> None:
    """Печатает краткое описание теста перед запуском.

    За счёт этого при обычном запуске pytest видно, какую именно
    пользовательскую историю или контракт API проверяет тест.
    """
    terminal_reporter = item.config.pluginmanager.get_plugin(
        "terminalreporter"
    )
    test_obj = getattr(item, "obj", None)
    description = inspect.getdoc(test_obj) if test_obj else None

    if terminal_reporter and description:
        terminal_reporter.write_line(f"→ {item.name}: {description}")
