"""One-off: run the real AI pipeline for every demo image and save the
result as JSON under demo/ai_cache/, so seeall.demo_cache can seed the
in-memory cache instantly after a fresh deploy (e.g. Streamlit Cloud
restarts, which lose the in-memory cache)."""
import json
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent))
from seeall.ocr import analyze_text_boxes
from seeall.deterministic import to_issues
from seeall.link_purpose import vague_link_issues
from seeall.scale_detect import detect_scale
from seeall.ai import analyze_with_ai

load_dotenv()

DEMO_DIR = Path(__file__).parent.parent / "demo"
OUT_DIR = DEMO_DIR / "ai_cache"


def run():
    OUT_DIR.mkdir(exist_ok=True)
    for path in sorted(DEMO_DIR.glob("*")):
        if path.suffix.lower() not in (".png", ".jpg", ".jpeg"):
            continue
        out_path = OUT_DIR / f"{path.name}.json"
        image = Image.open(path).convert("RGB")
        scale = detect_scale(image.size[0]).scale
        findings = analyze_text_boxes(image, scale)
        det_issues = to_issues(findings, image.size) + vague_link_issues(findings, image.size)

        print(f"{path.name}: calling AI...")
        start = time.time()
        response, provider_name, elapsed, fallback_note = analyze_with_ai(image, det_issues)
        wall = time.time() - start
        print(f"{path.name}: provider={provider_name} elapsed={elapsed:.1f}s wall={wall:.1f}s "
              f"issues={len(response.issues)} fallback={fallback_note}")

        if provider_name.startswith("MOCK") or provider_name.startswith("Measured checks only"):
            print(f"{path.name}: SKIPPED saving — got a fallback response, not a real AI result.")
            continue

        out_path.write_text(json.dumps({
            "provider_name": provider_name,
            "elapsed": elapsed,
            "response": response.model_dump(),
        }, indent=2))
        print(f"{path.name}: saved -> {out_path}")


if __name__ == "__main__":
    run()
