from PIL import Image

from seeall import ai
from seeall.ai import resize_for_ai, short_error_reason, analyze_with_ai


def test_resize_shrinks_large_image_preserving_aspect():
    img = Image.new("RGB", (2560, 1280), "white")  # 2:1
    out = resize_for_ai(img, max_side=1280)
    assert max(out.size) == 1280
    assert out.size[0] / out.size[1] == 2.0


def test_resize_leaves_small_image_unchanged():
    img = Image.new("RGB", (383, 1023), "white")
    out = resize_for_ai(img, max_side=1280)
    assert out.size == (383, 1023)


def test_resize_handles_tall_image():
    img = Image.new("RGB", (600, 3000), "white")
    out = resize_for_ai(img, max_side=1280)
    assert max(out.size) == 1280
    assert out.size[0] < out.size[1]


def test_short_error_reason_recognizes_timeout():
    class FakeTimeout(Exception):
        pass
    err = FakeTimeout("Request timed out.")
    assert short_error_reason(err) == "timed out"


def test_all_providers_timing_out_gives_measured_only_not_fake_mock(monkeypatch):
    class FakeTimeout(Exception):
        pass

    monkeypatch.setattr(ai, "build_providers", lambda env: [
        ("NVIDIA Build", "url1", "k1", "m1"), ("Google Gemini", "url2", "k2", "m2"),
    ])
    monkeypatch.setattr(ai, "_call_provider", lambda *a: (_ for _ in ()).throw(FakeTimeout("Request timed out.")))

    image = Image.new("RGB", (5, 5), "white")
    response, provider_name, elapsed, fallback_note = analyze_with_ai(image, [])

    assert response.issues == []
    assert "too long" in fallback_note.lower()
    assert "timed out" in provider_name.lower()


def test_one_timeout_then_success_is_not_measured_only(monkeypatch):
    class FakeTimeout(Exception):
        pass

    monkeypatch.setattr(ai, "build_providers", lambda env: [
        ("NVIDIA Build", "url1", "k1", "m1"), ("Google Gemini", "url2", "k2", "m2"),
    ])
    calls = {"n": 0}

    def fake_call(base_url, key, model, image, det):
        calls["n"] += 1
        if calls["n"] == 1:
            raise FakeTimeout("Request timed out.")
        return "FAKE_RESPONSE"

    monkeypatch.setattr(ai, "_call_provider", fake_call)

    image = Image.new("RGB", (5, 5), "white")
    response, provider_name, elapsed, fallback_note = analyze_with_ai(image, [])

    assert response == "FAKE_RESPONSE"
    assert provider_name == "Google Gemini"
