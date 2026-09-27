from seeall.ai import clean_json_response, needs_thinking_disabled


def test_plain_json_passes_through():
    raw = '{"issues": []}'
    assert clean_json_response(raw) == '{"issues": []}'


def test_strips_markdown_code_fence():
    raw = '```json\n{"issues": []}\n```'
    assert clean_json_response(raw) == '{"issues": []}'


def test_strips_plain_code_fence():
    raw = '```\n{"issues": []}\n```'
    assert clean_json_response(raw) == '{"issues": []}'


def test_strips_think_tags_before_json():
    raw = '<think>reasoning about the image here</think>\n{"issues": []}'
    assert clean_json_response(raw) == '{"issues": []}'


def test_strips_surrounding_whitespace():
    raw = '  \n {"issues": []} \n  '
    assert clean_json_response(raw) == '{"issues": []}'


def test_needs_thinking_disabled_for_nemotron_models():
    assert needs_thinking_disabled("nvidia/nemotron-3-nano-omni-30b-a3b-reasoning") is True
    assert needs_thinking_disabled("nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free") is True


def test_needs_thinking_disabled_false_for_other_models():
    assert needs_thinking_disabled("gemini-3.8-flash") is False
