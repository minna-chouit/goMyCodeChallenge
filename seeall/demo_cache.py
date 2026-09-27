"""Seed the in-memory AI cache from precomputed JSON for bundled demo
images, so 'Try an example screen' is instant even right after a fresh
deploy (Streamlit Cloud restarts lose the in-memory cache)."""
import json
from pathlib import Path

from .ai_cache import compute_cache_key
from .ai_schema import AIResponse


def precomputed_json_path(demo_dir, image_name):
    return Path(demo_dir) / "ai_cache" / f"{image_name}.json"


def load_precomputed(demo_dir, image_name):
    path = precomputed_json_path(demo_dir, image_name)
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    response = AIResponse.model_validate(data["response"])
    return response, data["provider_name"], data.get("elapsed", 0.0)


def seed_ai_cache(demo_dir, ai_cache, image_name, image, deterministic_findings):
    """Returns True if a precomputed result was found and seeded."""
    precomputed = load_precomputed(demo_dir, image_name)
    if precomputed is None:
        return False
    response, provider_name, elapsed = precomputed
    cache_key = compute_cache_key(image, deterministic_findings)
    ai_cache.set(cache_key, (response, provider_name, elapsed, None))
    return True
