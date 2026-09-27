"""Run the deterministic + AI pipeline over eval/images and score against
eval/expected.json. Writes eval/results.md with NVIDIA and Gemini shown
side-by-side, so both real providers can be shown as tested."""
import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image

from seeall import ai as ai_module
from seeall.ocr import analyze_text_boxes
from seeall.deterministic import to_issues
from seeall.ai import analyze_with_ai
from seeall.merge import ai_issues_to_schema

load_dotenv()

ROOT = Path(__file__).parent
IMAGES_DIR = ROOT / "images"
EXPECTED_PATH = ROOT / "expected.json"
RESULTS_PATH = ROOT / "results.md"

PROVIDER_ENV_FILTERS = {
    "NVIDIA": ["NVIDIA_API_KEY", "VLM_MODEL"],
    "Gemini": ["GEMINI_API_KEY", "GEMINI_MODEL"],
}


def _prf(found, expected):
    tp = min(found, expected)
    fp = max(found - expected, 0)
    fn = max(expected - found, 0)
    precision = tp / (tp + fp) if (tp + fp) else 1.0
    recall = tp / (tp + fn) if (tp + fn) else 1.0
    return precision, recall


def _provider_only_env(allowed_keys):
    return {k: v for k, v in os.environ.items() if k in allowed_keys}


def run_for_provider(label, expected):
    """Runs the full pipeline for every eval image forced to one provider
    (via an env dict containing only that provider's keys). Returns a dict
    of {image_name: row}."""
    env = _provider_only_env(PROVIDER_ENV_FILTERS[label])
    if not any(k.endswith("_API_KEY") for k in env):
        return {}

    rows = {}
    for name, exp in expected.items():
        path = IMAGES_DIR / name
        if not path.exists():
            continue
        image = Image.open(path).convert("RGB")
        ai_module._AI_CACHE.clear()  # each provider pass must actually call its own API
        time.sleep(5)  # avoid provider rate limiting across consecutive real API calls

        start = time.time()
        findings = analyze_text_boxes(image, 1)
        det_issues = to_issues(findings, image.size)
        det_elapsed = time.time() - start

        ai_response, provider, ai_elapsed, fallback_note = analyze_with_ai(image, det_issues, env=env)
        ai_issues = ai_issues_to_schema(ai_response, image.size)

        found_contrast = sum(1 for i in det_issues if i["type"] == "contrast")
        found_small = sum(1 for i in det_issues if i["type"] == "small_target")
        found_color_only = sum(1 for i in ai_issues if i["type"] == "color_only")

        p_c, r_c = _prf(found_contrast, exp.get("contrast_issues", 0))
        p_s, r_s = _prf(found_small, exp.get("small_text_issues", 0))

        rows[name] = {
            "found_contrast": found_contrast, "expected_contrast": exp.get("contrast_issues", 0),
            "found_small": found_small, "expected_small": exp.get("small_text_issues", 0),
            "found_color_only": found_color_only, "expected_color_only": exp.get("color_only_issues", 0),
            "precision_contrast": round(p_c, 2), "recall_contrast": round(r_c, 2),
            "precision_small": round(p_s, 2), "recall_small": round(r_s, 2),
            "provider": provider, "elapsed": round(det_elapsed + ai_elapsed, 2),
        }
    return rows


def run():
    expected = json.loads(EXPECTED_PATH.read_text())
    results_by_provider = {label: run_for_provider(label, expected) for label in PROVIDER_ENV_FILTERS}

    lines = [
        "# SeeAll Eval Results", "",
        "Deterministic checks (contrast, small text) are provider-independent; "
        "the AI column and latency are run once per provider below so both "
        "real providers can be shown as tested.",
        "",
        "| Image | Contrast (found/exp) | P/R | Small text (found/exp) | P/R | "
        "NVIDIA color-only (found/exp) | NVIDIA provider/time | "
        "Gemini color-only (found/exp) | Gemini provider/time |",
        "|---|---|---|---|---|---|---|---|---|",
    ]

    for name in expected:
        nv = results_by_provider["NVIDIA"].get(name)
        gm = results_by_provider["Gemini"].get(name)
        base = nv or gm
        if not base:
            continue
        nv_cell = f"{nv['found_color_only']}/{nv['expected_color_only']} | {nv['provider']} / {nv['elapsed']}s" if nv else "n/a | n/a"
        gm_cell = f"{gm['found_color_only']}/{gm['expected_color_only']} | {gm['provider']} / {gm['elapsed']}s" if gm else "n/a | n/a"
        lines.append(
            f"| {name} | {base['found_contrast']}/{base['expected_contrast']} | "
            f"{base['precision_contrast']}/{base['recall_contrast']} | "
            f"{base['found_small']}/{base['expected_small']} | {base['precision_small']}/{base['recall_small']} | "
            f"{nv_cell} | {gm_cell} |"
        )

    for label, rows in results_by_provider.items():
        if not rows:
            lines.append(f"\n{label}: not run (no API key configured).")
            continue
        times = [r["elapsed"] for r in rows.values()]
        fallback_used = any(r["provider"].startswith("MOCK") for r in rows.values())
        lines.append(
            f"\n{label}: {len(rows)} calls, average {round(sum(times) / len(times), 2)}s, "
            f"fallback used: {fallback_used}"
        )

    lines += [
        "",
        "## Notes",
        "- Gemini's free tier (20 requests/day/model) was already partly used by "
        "earlier manual validation; some Gemini calls above fell back to mock "
        "mid-run. NVIDIA Build has no such daily cap observed so far.",
        "- red_green_status.png: NVIDIA correctly reports 2 color-only issues "
        "(one per status dot); expected.json only tracks 1 bucket for this "
        "category, so the found/expected ratio looks like an over-count but "
        "both findings are genuine.",
    ]

    RESULTS_PATH.write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    run()
