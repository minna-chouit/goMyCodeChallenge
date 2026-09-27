"""In-memory cache for AI results, keyed by image content + deterministic
findings, so repeated audits of the same screenshot don't spend AI quota."""
import hashlib
import io
import json


def compute_cache_key(image, deterministic_findings):
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    image_hash = hashlib.sha256(buf.getvalue()).hexdigest()
    findings_hash = hashlib.sha256(json.dumps(deterministic_findings, sort_keys=True, default=str).encode()).hexdigest()
    return f"{image_hash}:{findings_hash}"


class AICache:
    def __init__(self):
        self._store = {}

    def get(self, key):
        return self._store.get(key)

    def set(self, key, value):
        self._store[key] = value

    def clear(self):
        self._store.clear()
