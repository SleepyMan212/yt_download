from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

yt_app = importlib.import_module("app")


@pytest.fixture()
def client():
    yt_app.app.config.update(TESTING=True)
    with yt_app.app.test_client() as client:
        yield client
