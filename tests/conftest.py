from __future__ import annotations

import os
import sys
import time
from collections.abc import Iterator
from pathlib import Path

import pytest
from pytest import MonkeyPatch

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


def _test_delay_seconds() -> float:
    """Пауза после каждого теста. Отключить: PYTEST_TEST_DELAY_SEC=0"""
    raw = os.environ.get("PYTEST_TEST_DELAY_SEC", "0.1")
    try:
        return max(0.0, float(raw))
    except ValueError:
        return 0.1


@pytest.fixture(autouse=True)
def _pause_after_each_test() -> Iterator[None]:
    yield
    delay = _test_delay_seconds()
    if delay > 0:
        time.sleep(delay)


@pytest.fixture(scope="session", autouse=True)
def _noop_database_pool() -> Iterator[None]:
    import main  # noqa: F401  — полный граф импорта до патча (иначе цикл core.objects ↔ logger)

    from core.objects import database as db
    import core.methods.authentication as auth_mod

    mp = MonkeyPatch()

    async def _noop_connect() -> None:
        return None

    async def _noop_close() -> None:
        return None

    async def _no_session_row(_connection: object, _session_id: object) -> None:
        """Без обращения к пулу: валидный по форме Bearer даёт 403 SESSION_NOT_FOUND, как при отсутствии сессии."""
        return None

    mp.setattr(db, "connect", _noop_connect)
    mp.setattr(db, "close", _noop_close)
    mp.setattr(auth_mod, "_get_user_info_by_session_id", _no_session_row)
    yield
    mp.undo()


@pytest.fixture(scope="session")
def client() -> Iterator:
    from fastapi.testclient import TestClient

    from main import app

    with TestClient(app) as c:
        yield c


# Токен для заголовка Authorization в тестах «со вторым сценарием» (Bearer).
TEST_SESSION_BEARER = (
    "019dfc12-a070-7dbb-bbfc-3b6827fb2a4b."
    "a0f31c8c4fa628aa384f634f58431ae295dbab7f495f0a77e5cec5337466f754"
)


@pytest.fixture
def invalid_bearer() -> dict[str, str]:
    return {"Authorization": f"Bearer {TEST_SESSION_BEARER}"}
