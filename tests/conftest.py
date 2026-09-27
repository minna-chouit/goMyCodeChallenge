import pytest

from seeall import ai


@pytest.fixture(autouse=True)
def _clear_ai_cache():
    ai._AI_CACHE.clear()
    yield
    ai._AI_CACHE.clear()
