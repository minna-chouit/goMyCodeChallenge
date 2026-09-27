import logging

from PIL import Image

from seeall import ai
from seeall.ai import analyze_with_ai, short_error_reason


class _FakeRateLimitError(Exception):
    pass


class _FakeNotFoundError(Exception):
    pass


def test_short_error_reason_recognizes_rate_limit():
    err = _FakeRateLimitError("Error code: 429 - quota exceeded")
    assert short_error_reason(err) == "rate-limited"


def test_short_error_reason_recognizes_not_found():
    err = _FakeNotFoundError("Error code: 404 - model not found")
    assert short_error_reason(err) == "model unavailable"


def test_short_error_reason_generic_fallback():
    assert short_error_reason(ValueError("boom")) == "unavailable"


def test_fallback_note_set_when_first_provider_fails(monkeypatch):
    monkeypatch.setattr(ai, "build_providers", lambda env: [
        ("NVIDIA Build", "url1", "k1", "m1"),
        ("Google Gemini", "url2", "k2", "m2"),
    ])

    calls = {"n": 0}

    def fake_call_provider(base_url, key, model, image, det):
        calls["n"] += 1
        if calls["n"] == 1:
            raise _FakeRateLimitError("429")
        return "FAKE_RESPONSE"

    monkeypatch.setattr(ai, "_call_provider", fake_call_provider)

    image = Image.new("RGB", (5, 5), "white")
    response, provider_name, elapsed, fallback_note = analyze_with_ai(image, [])

    assert response == "FAKE_RESPONSE"
    assert provider_name == "Google Gemini"
    assert fallback_note == "NVIDIA Build rate-limited, used Google Gemini"


def test_no_fallback_note_when_first_provider_succeeds(monkeypatch):
    monkeypatch.setattr(ai, "build_providers", lambda env: [("NVIDIA Build", "url1", "k1", "m1")])
    monkeypatch.setattr(ai, "_call_provider", lambda *a: "FAKE_RESPONSE")

    image = Image.new("RGB", (5, 5), "white")
    response, provider_name, elapsed, fallback_note = analyze_with_ai(image, [])

    assert fallback_note is None
    assert provider_name == "NVIDIA Build"


def test_provider_failure_is_logged(monkeypatch, caplog):
    monkeypatch.setattr(ai, "build_providers", lambda env: [("NVIDIA Build", "url1", "k1", "m1")])

    def always_fails(*a):
        raise _FakeRateLimitError("429")

    monkeypatch.setattr(ai, "_call_provider", always_fails)

    image = Image.new("RGB", (5, 5), "white")
    with caplog.at_level(logging.WARNING, logger="seeall.ai"):
        analyze_with_ai(image, [])

    assert any("NVIDIA Build" in record.message and "429" in record.message for record in caplog.records)
