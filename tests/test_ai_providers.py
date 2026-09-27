from seeall.ai import build_providers


def test_provider_order_all_keys_present():
    env = {
        "NVIDIA_API_KEY": "nk",
        "OPENROUTER_API_KEY": "ok",
        "GEMINI_API_KEY": "gk",
    }
    names = [p[0] for p in build_providers(env)]
    assert names == ["NVIDIA Build", "OpenRouter", "Google Gemini"]


def test_provider_skipped_when_key_missing():
    env = {"GEMINI_API_KEY": "gk"}
    names = [p[0] for p in build_providers(env)]
    assert names == ["Google Gemini"]


def test_no_keys_gives_empty_list():
    assert build_providers({}) == []


def test_openrouter_default_model_is_free_nemotron_vision():
    env = {"OPENROUTER_API_KEY": "ok"}
    providers = build_providers(env)
    name, base_url, key, model = providers[0]
    assert base_url == "https://openrouter.ai/api/v1"
    assert model == "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"


def test_openrouter_model_configurable_via_env():
    env = {"OPENROUTER_API_KEY": "ok", "OPENROUTER_VLM_MODEL": "some/other-model"}
    _, _, _, model = build_providers(env)[0]
    assert model == "some/other-model"
