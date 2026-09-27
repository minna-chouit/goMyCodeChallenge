"""Vision-model issue detection with provider fallback:
NVIDIA Build -> OpenRouter -> Gemini -> offline mock."""
import base64
import io
import json
import logging
import os
import re
import time

from pydantic import ValidationError

from .ai_cache import compute_cache_key, AICache
from .ai_schema import AIResponse

logger = logging.getLogger("seeall.ai")
_AI_CACHE = AICache()

_THINK_TAG_RE = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)
_CODE_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)

SYSTEM_PROMPT = (
    "You are an accessibility auditor. Given a UI screenshot, find issues a "
    "deterministic tool cannot. Types: color_only (meaning by colour alone), "
    "icon_unclear, missing_label (also: '*' required fields with no legend, "
    "or placeholder used as the only label), small_target (<24x24px), "
    "layout (clutter), alt_text, image_of_text (text baked into an image), "
    "error_handling (errors shown only by colour or with no fix suggestion), "
    "captcha_or_memory_test (login puzzle, no alternative), drag_only (no "
    "tap/click alternative), sticky_obscures_focus (sticky bar hiding focus), "
    "orientation_lock ('rotate your device'), visual_presentation (justified "
    "text/long lines), other.\n"
    "Do not repeat the issues already listed as 'known deterministic findings' "
    "below. Respond with STRICT JSON ONLY, no markdown fences, matching exactly "
    "this schema:\n"
    '{"issues":[{"type":"color_only|icon_unclear|missing_label|small_target|layout|'
    'alt_text|image_of_text|error_handling|captcha_or_memory_test|drag_only|'
    'sticky_obscures_focus|orientation_lock|visual_presentation|other",'
    '"severity":"critical|serious|minor","box":[x0,y0,x1,y1],"description":"...",'
    '"affected_users":"...","fix":"...","confidence":0.0}],'
    '"alt_texts":[{"box":[x0,y0,x1,y1],"alt":"..."}],'
    '"screen_reader_script":["Heading, ...","Button, ..."]}\n'
    "box coordinates are relative (0-1) [x0,y0,x1,y1]."
)


_MAX_IMAGE_SIDE = 1280
_AI_TIMEOUT_SECONDS = 40
_AI_MAX_TOKENS = 1500


def resize_for_ai(image, max_side=_MAX_IMAGE_SIDE):
    """Downscale before sending to the vision model — smaller image, fewer
    tokens, faster response. No-op if already within the limit."""
    width, height = image.size
    longest = max(width, height)
    if longest <= max_side:
        return image
    scale = max_side / longest
    return image.resize((round(width * scale), round(height * scale)))


def _image_to_data_url(image):
    buf = io.BytesIO()
    resize_for_ai(image).save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{b64}"


def _build_messages(image, deterministic_findings):
    known = json.dumps(deterministic_findings)
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": f"Known deterministic findings (do not repeat): {known}"},
                {"type": "image_url", "image_url": {"url": _image_to_data_url(image)}},
            ],
        },
    ]


def needs_thinking_disabled(model):
    """Nemotron reasoning models wrap JSON output in <think> chain-of-thought
    unless thinking is explicitly turned off."""
    return "nemotron" in model.lower()


def clean_json_response(raw):
    """Strip <think>...</think> blocks and markdown code fences a model may
    wrap strict JSON output in, so json.loads sees only the JSON."""
    text = _THINK_TAG_RE.sub("", raw)
    text = _CODE_FENCE_RE.sub("", text)
    return text.strip()


def _call_provider(base_url, api_key, model, image, deterministic_findings):
    from openai import OpenAI

    client = OpenAI(base_url=base_url, api_key=api_key, timeout=_AI_TIMEOUT_SECONDS, max_retries=0)
    messages = _build_messages(image, deterministic_findings)
    extra_body = {"chat_template_kwargs": {"enable_thinking": False}} if needs_thinking_disabled(model) else {}

    last_error = None
    for attempt in range(2):
        response = client.chat.completions.create(
            model=model, messages=messages, temperature=0, max_tokens=_AI_MAX_TOKENS, extra_body=extra_body,
        )
        raw = response.choices[0].message.content
        cleaned = clean_json_response(raw)
        try:
            data = json.loads(cleaned)
            return AIResponse.model_validate(data)
        except (json.JSONDecodeError, ValidationError) as e:
            last_error = e
            messages.append({"role": "assistant", "content": raw})
            messages.append({
                "role": "user",
                "content": f"That response was invalid: {e}. Reply with corrected STRICT JSON only.",
            })
    raise last_error


def _mock_response(image):
    return AIResponse(
        issues=[{
            "type": "other",
            "severity": "minor",
            "box": [0.05, 0.05, 0.5, 0.15],
            "description": "AI unavailable - showing a MOCK placeholder finding for the demo.",
            "affected_users": "N/A (mock data)",
            "fix": "N/A (mock data)",
            "confidence": 0.5,
        }],
        alt_texts=[],
        screen_reader_script=["MOCK - AI unavailable. This is placeholder screen reader text."],
    )


def _measured_only_response():
    """Every configured provider timed out: don't show a fake mock finding,
    just say so plainly and return no AI issues."""
    return AIResponse(
        issues=[],
        alt_texts=[],
        screen_reader_script=["AI took too long; showing measured checks only."],
    )


def build_providers(env):
    """Pure function: env dict -> ordered list of (name, base_url, key, model).
    Order: NVIDIA Build -> OpenRouter -> Gemini. Providers without an API key
    in env are skipped."""
    providers = []
    if env.get("NVIDIA_API_KEY"):
        model = env.get("VLM_MODEL", "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning")
        providers.append(("NVIDIA Build", "https://integrate.api.nvidia.com/v1", env["NVIDIA_API_KEY"], model))
    if env.get("OPENROUTER_API_KEY"):
        model = env.get("OPENROUTER_VLM_MODEL", "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free")
        providers.append(("OpenRouter", "https://openrouter.ai/api/v1", env["OPENROUTER_API_KEY"], model))
    if env.get("GEMINI_API_KEY"):
        model = env.get("GEMINI_MODEL", "gemini-3.8-flash")
        providers.append((
            "Google Gemini", "https://generativelanguage.googleapis.com/v1beta/openai/",
            env["GEMINI_API_KEY"], model,
        ))
    return providers


def provider_status_label(env):
    """Human-readable summary of which AI providers are configured, shown
    always (not just after an audit) for transparency."""
    providers = build_providers(env)
    if not providers:
        return "No AI provider configured — will use offline mock"
    label = f"AI provider ready: {providers[0][0]}"
    if len(providers) > 1:
        label += f" (+{len(providers) - 1} fallback configured)"
    return label


def short_error_reason(exc):
    """Map an exception to a short, judge-readable reason for a fallback note."""
    text = f"{type(exc).__name__} {exc}".lower()
    if "timeout" in text or "timed out" in text:
        return "timed out"
    if "429" in text or "rate" in text or "quota" in text:
        return "rate-limited"
    if "404" in text or "not found" in text or "not_found" in text:
        return "model unavailable"
    if "401" in text or "403" in text or "auth" in text:
        return "authentication failed"
    return "unavailable"


def analyze_with_ai(image, deterministic_findings, env=None):
    """Returns (AIResponse, provider_name, seconds_elapsed, fallback_note).
    fallback_note is None when the first configured provider succeeds, else a
    short judge-readable string like 'NVIDIA Build rate-limited, used Gemini'.
    env defaults to os.environ; pass an explicit dict to force a specific
    provider (e.g. for side-by-side eval runs)."""
    if env is None:
        env = os.environ

    cache_key = compute_cache_key(image, deterministic_findings)
    cached = _AI_CACHE.get(cache_key)
    if cached is not None:
        return cached

    providers = build_providers(env)
    failures = []

    for name, base_url, key, model in providers:
        start = time.time()
        try:
            result = _call_provider(base_url, key, model, image, deterministic_findings)
            fallback_note = None
            if failures:
                first_name, first_reason = failures[0]
                fallback_note = f"{first_name} {first_reason}, used {name}"
            outcome = (result, name, time.time() - start, fallback_note)
            _AI_CACHE.set(cache_key, outcome)
            return outcome
        except Exception as e:
            reason = short_error_reason(e)
            logger.warning("%s failed (%s): %s", name, reason, e)
            failures.append((name, reason))
            continue

    start = time.time()
    all_timed_out = bool(failures) and all(reason == "timed out" for _, reason in failures)
    if all_timed_out:
        fallback_note = "AI took too long; showing measured checks only"
        outcome = (_measured_only_response(), "Measured checks only (AI timed out)", time.time() - start, fallback_note)
    else:
        fallback_note = None
        if failures:
            first_name, first_reason = failures[0]
            fallback_note = f"{first_name} {first_reason}, used offline mock"
        outcome = (_mock_response(image), "MOCK - AI unavailable", time.time() - start, fallback_note)
    _AI_CACHE.set(cache_key, outcome)
    return outcome
