import json

from PIL import Image

from seeall.ai_cache import AICache, compute_cache_key
from seeall.demo_cache import precomputed_json_path, load_precomputed, seed_ai_cache


def test_precomputed_json_path(tmp_path):
    path = precomputed_json_path(tmp_path, "checkout.jpg")
    assert path == tmp_path / "ai_cache" / "checkout.jpg.json"


def test_load_precomputed_returns_none_when_missing(tmp_path):
    assert load_precomputed(tmp_path, "missing.png") is None


def test_load_precomputed_reads_saved_response(tmp_path):
    ai_dir = tmp_path / "ai_cache"
    ai_dir.mkdir()
    payload = {
        "provider_name": "NVIDIA Build (precomputed)",
        "elapsed": 3.2,
        "response": {"issues": [], "alt_texts": [], "screen_reader_script": ["Heading, Test"]},
    }
    (ai_dir / "checkout.jpg.json").write_text(json.dumps(payload))

    result = load_precomputed(tmp_path, "checkout.jpg")
    assert result is not None
    response, provider_name, elapsed = result
    assert provider_name == "NVIDIA Build (precomputed)"
    assert elapsed == 3.2
    assert response.screen_reader_script == ["Heading, Test"]


def test_seed_ai_cache_populates_cache_for_matching_key(tmp_path):
    ai_dir = tmp_path / "ai_cache"
    ai_dir.mkdir()
    payload = {
        "provider_name": "NVIDIA Build (precomputed)", "elapsed": 1.0,
        "response": {"issues": [], "alt_texts": [], "screen_reader_script": []},
    }
    (ai_dir / "demo.png.json").write_text(json.dumps(payload))

    cache = AICache()
    image = Image.new("RGB", (10, 10), "white")
    findings = [{"type": "contrast"}]

    seeded = seed_ai_cache(tmp_path, cache, "demo.png", image, findings)
    assert seeded is True

    cache_key = compute_cache_key(image, findings)
    cached = cache.get(cache_key)
    assert cached is not None
    response, provider_name, elapsed, fallback_note = cached
    assert provider_name == "NVIDIA Build (precomputed)"
    assert fallback_note is None


def test_seed_ai_cache_returns_false_when_no_precomputed_file(tmp_path):
    cache = AICache()
    image = Image.new("RGB", (10, 10), "white")
    assert seed_ai_cache(tmp_path, cache, "nope.png", image, []) is False
