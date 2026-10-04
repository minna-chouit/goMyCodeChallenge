from PIL import Image

from seeall import ai
from seeall.ai import analyze_with_ai, short_error_reason


class Fake503(Exception):
    pass


_PROVIDERS = [("NVIDIA Build", "u1", "k1", "m1"), ("Google Gemini", "u2", "k2", "m2")]


def _img(color="white"):
    return Image.new("RGB", (6, 6), color)


def test_503_is_classified_overloaded():
    err = Fake503("Error code: 503 - ResourceExhausted: Worker local total request limit reached (16/16)")
    assert short_error_reason(err) == "overloaded"


def test_high_demand_503_is_overloaded():
    err = Fake503("Error code: 503 - This model is currently experiencing high demand.")
    assert short_error_reason(err) == "overloaded"


def test_overloaded_provider_is_retried_once_then_succeeds(monkeypatch):
    monkeypatch.setattr(ai, "_OVERLOAD_RETRY_DELAY", 0)
    monkeypatch.setattr(ai, "build_providers", lambda env: _PROVIDERS[:1])
    calls = {"n": 0}

    def flaky(*a):
        calls["n"] += 1
        if calls["n"] == 1:
            raise Fake503("Error code: 503 - Service Unavailable")
        return "REAL"

    monkeypatch.setattr(ai, "_call_provider", flaky)
    response, provider, _, note = analyze_with_ai(_img(), [])
    assert response == "REAL"
    assert provider == "NVIDIA Build"
    assert calls["n"] == 2


def test_all_providers_failing_gives_measured_only_not_mock(monkeypatch):
    monkeypatch.setattr(ai, "_OVERLOAD_RETRY_DELAY", 0)
    monkeypatch.setattr(ai, "build_providers", lambda env: _PROVIDERS)
    monkeypatch.setattr(ai, "_call_provider", lambda *a: (_ for _ in ()).throw(Fake503("503 Service Unavailable")))
    response, provider, _, note = analyze_with_ai(_img(), [])
    assert response.issues == []
    assert "MOCK" not in provider
    assert "measured checks only" in note.lower()
    assert "NVIDIA Build" in note and "Google Gemini" in note


def test_no_providers_configured_still_uses_mock(monkeypatch):
    monkeypatch.setattr(ai, "build_providers", lambda env: [])
    response, provider, _, note = analyze_with_ai(_img(), [])
    assert provider.startswith("MOCK")
    assert note is None


def test_failed_result_is_not_cached(monkeypatch):
    monkeypatch.setattr(ai, "_OVERLOAD_RETRY_DELAY", 0)
    monkeypatch.setattr(ai, "build_providers", lambda env: _PROVIDERS[:1])
    state = {"fail": True}

    def provider(*a):
        if state["fail"]:
            raise Fake503("503 Service Unavailable")
        return "REAL"

    monkeypatch.setattr(ai, "_call_provider", provider)
    image = _img("black")
    first = analyze_with_ai(image, [])
    assert first[0].issues == []
    state["fail"] = False
    second = analyze_with_ai(image, [])
    assert second[0] == "REAL"
