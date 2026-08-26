from collections.abc import Iterator
from pathlib import Path

import pytest
from litestar import Litestar
from litestar.testing import TestClient
from openhost_test_harness import OpenhostStack

from server.app import create_app
from server.brave.client import API_BASE_URL_ENV_VAR
from server.config import Config
from server.database import Database
from server.settings_store import SettingsStore
from tests.brave_stub import VALID_KEY
from tests.brave_stub import run_brave_stub


@pytest.fixture(scope="session")
def stack() -> Iterator[OpenhostStack]:
    """Build the app's Dockerfile, run it under podman per openhost.toml, and front it with the real OpenHost router.

    - stack.url                    — through the router; requires owner auth
    - stack.owner_session          — a requests.Session authenticated as the zone owner
    - stack.playwright_login(page) — log a playwright page in as the owner for browser tests
    - stack.app_url                — direct to the container (control your own headers; eg the health probe)
    """
    with OpenhostStack() as s:
        yield s


@pytest.fixture
def database_path(tmp_path: Path) -> Path:
    return tmp_path / "main.db"


@pytest.fixture
def store(database_path: Path) -> SettingsStore:
    database = Database(path=database_path)
    database.initialize()
    return SettingsStore(database=database)


@pytest.fixture
def app(database_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Litestar]:
    """The app running in-process, with the Brave API replaced by a local fixture-serving stub."""
    with run_brave_stub() as stub:
        monkeypatch.setenv(API_BASE_URL_ENV_VAR, stub.base_url)
        yield create_app(Config(database_path=database_path))


@pytest.fixture
def client(app: Litestar) -> Iterator[TestClient[Litestar]]:
    with TestClient(app=app) as test_client:
        yield test_client


@pytest.fixture
def configured_client(client: TestClient[Litestar], store: SettingsStore) -> TestClient[Litestar]:
    store.save_api_key(VALID_KEY)
    return client
