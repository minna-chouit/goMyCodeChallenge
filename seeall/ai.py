"""Vision-model issue detection with provider fallback: NVIDIA Build -> Gemini -> offline mock."""
import base64
import io
import json
import os
import time

from pydantic import ValidationError

from .ai_schema import AIResponse

SYSTEM_PROMPT = (
    "You are an accessibility auditor. Given a UI screenshot, find issues a "
    "deterministic tool cannot: meaning shown by color only, unclear icons, "
    "missing or vague labels, tap targets under 24x24 px, cluttered layout, "
    "and images needing alt text. Do not repeat the issues already listed as "
    "'known deterministic findings' below. Respond with STRICT JSON ONLY, no "
    "markdown fences, matching exactly this schema:\n"
    '{"issues":[{"type":"color_only|icon_unclear|missing_label|small_target|layout|alt_text|other",'
    '"severity":"critical|serious|minor","box":[x0,y0,x1,y1],"description":"...",'
    '"affected_users":"...","fix":"...","confidence":0.0}],'
    '"alt_texts":[{"box":[x0,y0,x1,y1],"alt":"..."}],'
    '"screen_reader_script":["Heading, ...","Button, ..."]}\n'
    "box coordinates are relative (0-1) [x0,y0,x1,y1]."
)


def _image_to_data_url(image):
    buf = io.BytesIO()
    image.save(buf, format="PNG")
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


def _call_provider(base_url, api_key, model, image, deterministic_findings):
    from openai import OpenAI

    client = OpenAI(base_url=base_url, api_key=api_key)
    messages = _build_messages(image, deterministic_findings)

    last_error = None
    for attempt in range(2):
        response = client.chat.completions.create(
            model=model, messages=messages, temperature=0, max_tokens=2000,
        )
        raw = response.choices[0].message.content
        try:
            data = json.loads(raw)
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


def analyze_with_ai(image, deterministic_findings):
    """Returns (AIResponse, provider_name, seconds_elapsed)."""
    nvidia_key = os.environ.get("NVIDIA_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")

    providers = []
    if nvidia_key:
        model = os.environ.get("VLM_MODEL", "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning")
        providers.append(("NVIDIA Build", "https://integrate.api.nvidia.com/v1", nvidia_key, model))
    if gemini_key:
        providers.append((
            "Google Gemini", "https://generativelanguage.googleapis.com/v1beta/openai/",
            gemini_key, "gemini-2.0-flash",
        ))

    for name, base_url, key, model in providers:
        start = time.time()
        try:
            result = _call_provider(base_url, key, model, image, deterministic_findings)
            return result, name, time.time() - start
        except Exception:
            continue

    start = time.time()
    return _mock_response(image), "MOCK - AI unavailable", time.time() - start
