from PIL import Image

from seeall import ai
from seeall.ai import analyze_with_ai


def test_explicit_env_overrides_os_environ(monkeypatch):
    monkeypatch.setattr(ai, "build_providers", lambda env: [(f"provider-for-{env.get('X')}", "url", "k", "m")])
    monkeypatch.setattr(ai, "_call_provider", lambda *a: "FAKE_RESPONSE")

    image = Image.new("RGB", (5, 5), "white")
    _, provider_name, _, _ = analyze_with_ai(image, [], env={"X": "custom"})

    assert provider_name == "provider-for-custom"


def test_env_defaults_to_os_environ_when_not_passed(monkeypatch):
    monkeypatch.setenv("X", "from-os-environ")
    monkeypatch.setattr(ai, "build_providers", lambda env: [(f"provider-for-{env.get('X')}", "url", "k", "m")])
    monkeypatch.setattr(ai, "_call_provider", lambda *a: "FAKE_RESPONSE")

    image = Image.new("RGB", (5, 5), "black")
    _, provider_name, _, _ = analyze_with_ai(image, [])

    assert provider_name == "provider-for-from-os-environ"
