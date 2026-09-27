from seeall.ai import provider_status_label


def test_no_providers_configured():
    assert provider_status_label({}) == "No AI provider configured — will use offline mock"


def test_one_provider_configured():
    label = provider_status_label({"GEMINI_API_KEY": "gk"})
    assert label == "AI provider ready: Google Gemini"


def test_multiple_providers_lists_in_fallback_order():
    env = {"GEMINI_API_KEY": "gk", "NVIDIA_API_KEY": "nk"}
    label = provider_status_label(env)
    assert label == "AI provider ready: NVIDIA Build (+1 fallback configured)"
