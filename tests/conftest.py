import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repository import InMemoryLinkRepository
from app.services import LinkService


@pytest.fixture()
def client() -> TestClient:
    app.state.link_service = LinkService(InMemoryLinkRepository())
    with TestClient(app) as test_client:
        yield test_client
