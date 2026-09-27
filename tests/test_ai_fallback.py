from PIL import Image

from seeall.ai import analyze_with_ai


def test_no_keys_falls_back_to_mock(monkeypatch):
    for key in ("NVIDIA_API_KEY", "OPENROUTER_API_KEY", "GEMINI_API_KEY"):
        monkeypatch.delenv(key, raising=False)

    image = Image.new("RGB", (10, 10), "white")
    response, provider_name, elapsed = analyze_with_ai(image, [])

    assert provider_name.startswith("MOCK")
    assert "MOCK" in response.screen_reader_script[0]
    assert elapsed >= 0
