from PIL import Image

from seeall import ai
from seeall.ai_cache import compute_cache_key, AICache


def test_same_image_and_findings_give_same_key():
    img1 = Image.new("RGB", (10, 10), "white")
    img2 = Image.new("RGB", (10, 10), "white")
    findings = [{"type": "contrast"}]
    assert compute_cache_key(img1, findings) == compute_cache_key(img2, findings)


def test_different_image_gives_different_key():
    img1 = Image.new("RGB", (10, 10), "white")
    img2 = Image.new("RGB", (10, 10), "black")
    assert compute_cache_key(img1, []) != compute_cache_key(img2, [])


def test_different_findings_give_different_key():
    img = Image.new("RGB", (10, 10), "white")
    key1 = compute_cache_key(img, [{"type": "contrast"}])
    key2 = compute_cache_key(img, [{"type": "small_target"}])
    assert key1 != key2


def test_cache_get_set_roundtrip():
    cache = AICache()
    assert cache.get("key1") is None
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"


def test_cache_clear():
    cache = AICache()
    cache.set("key1", "value1")
    cache.clear()
    assert cache.get("key1") is None


def test_analyze_with_ai_second_call_is_cached(monkeypatch):
    monkeypatch.setattr(ai, "build_providers", lambda env: [("NVIDIA Build", "url1", "k1", "m1")])

    calls = {"n": 0}

    def fake_call_provider(base_url, key, model, image, det):
        calls["n"] += 1
        return "FAKE_RESPONSE"

    monkeypatch.setattr(ai, "_call_provider", fake_call_provider)

    image = Image.new("RGB", (5, 5), "white")
    first = ai.analyze_with_ai(image, [])
    second = ai.analyze_with_ai(image, [])

    assert calls["n"] == 1
    assert first == second
