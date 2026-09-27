"""Run the deterministic + AI pipeline over eval/images and score against
eval/expected.json. Writes eval/results.md."""
import json
import time
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image

from seeall.ocr import analyze_text_boxes
from seeall.deterministic import to_issues
from seeall.ai import analyze_with_ai
from seeall.merge import ai_issues_to_schema

load_dotenv()

ROOT = Path(__file__).parent
IMAGES_DIR = ROOT / "images"
EXPECTED_PATH = ROOT / "expected.json"
RESULTS_PATH = ROOT / "results.md"


def _prf(found, expected):
    tp = min(found, expected)
    fp = max(found - expected, 0)
    fn = max(expected - found, 0)
    precision = tp / (tp + fp) if (tp + fp) else 1.0
    recall = tp / (tp + fn) if (tp + fn) else 1.0
    return precision, recall


def run():
    expected = json.loads(EXPECTED_PATH.read_text())
    rows = []
    total_time = 0.0
    total_calls = 0
    fallback_used = False

    for name, exp in expected.items():
        path = IMAGES_DIR / name
        if not path.exists():
            continue
        image = Image.open(path).convert("RGB")
        time.sleep(5)  # avoid provider rate limiting across consecutive real API calls

        start = time.time()
        findings = analyze_text_boxes(image, 1)
        det_issues = to_issues(findings, image.size)
        det_elapsed = time.time() - start

        ai_response, provider, ai_elapsed = analyze_with_ai(image, det_issues)
        total_calls += 1
        if provider.startswith("MOCK"):
            fallback_used = True
        ai_issues = ai_issues_to_schema(ai_response, image.size)

        found_contrast = sum(1 for i in det_issues if i["type"] == "contrast")
        found_small = sum(1 for i in det_issues if i["type"] == "small_target")
        found_color_only = sum(1 for i in ai_issues if i["type"] == "color_only")

        p_c, r_c = _prf(found_contrast, exp.get("contrast_issues", 0))
        p_s, r_s = _prf(found_small, exp.get("small_text_issues", 0))

        elapsed = det_elapsed + ai_elapsed
        total_time += elapsed

        rows.append({
            "image": name,
            "found_contrast": found_contrast, "expected_contrast": exp.get("contrast_issues", 0),
            "found_small": found_small, "expected_small": exp.get("small_text_issues", 0),
            "found_color_only": found_color_only, "expected_color_only": exp.get("color_only_issues", 0),
            "precision_contrast": round(p_c, 2), "recall_contrast": round(r_c, 2),
            "precision_small": round(p_s, 2), "recall_small": round(r_s, 2),
            "provider": provider, "elapsed": round(elapsed, 2),
        })

    lines = [
        "# SeeAll Eval Results", "",
        "| Image | Contrast (found/exp) | P/R | Small text (found/exp) | P/R | Color-only AI (found/exp) | Provider | Time (s) |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['image']} | {r['found_contrast']}/{r['expected_contrast']} | "
            f"{r['precision_contrast']}/{r['recall_contrast']} | "
            f"{r['found_small']}/{r['expected_small']} | {r['precision_small']}/{r['recall_small']} | "
            f"{r['found_color_only']}/{r['expected_color_only']} | {r['provider']} | {r['elapsed']} |"
        )
    lines += [
        "",
        f"Average runtime per image: {round(total_time / len(rows), 2) if rows else 0}s",
        f"Total API calls: {total_calls}",
        f"Fallback (mock) used: {fallback_used}",
    ]
    RESULTS_PATH.write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    run()
