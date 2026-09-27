import io
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from PIL import Image

from seeall.ocr import analyze_text_boxes
from seeall.deterministic import to_issues
from seeall.annotate import draw_boxes
from seeall.scoring import compute_score, severity_breakdown, format_breakdown
from seeall.ai import analyze_with_ai, provider_status_label
from seeall.merge import ai_issues_to_schema, merge_and_rank
from seeall.simulate import simulate, SIMULATION_KINDS
from seeall.speech import script_to_speech
from seeall.report import build_report
from seeall.demo_picker import pick_example_image
from seeall.badges import confidence_badge
from seeall.scale_detect import detect_scale
from seeall.group_issues import group_issues

load_dotenv()

st.set_page_config(page_title="SeeAll - Accessibility Auditor", layout="wide")

st.title("SeeAll")
st.caption("AI accessibility auditor for designers")
st.caption(provider_status_label(os.environ))

with st.sidebar:
    st.header("How SeeAll works")
    st.markdown(
        "1. **Measured issues** — OCR finds text, a colour-clustering "
        "algorithm splits text vs. background colour, and exact WCAG 2.2 "
        "contrast math flags failures.\n"
        "2. **AI-found issues** — a vision model (NVIDIA / OpenRouter / "
        "Gemini, with automatic fallback) spots what code can't: unclear "
        "icons, colour-only meaning, missing labels, clutter.\n"
        "3. **Simulations** — see the screen the way colour-blind or "
        "low-vision users do.\n"
        "4. **Hear this screen** — a text-to-speech readout in the order "
        "a screen reader would announce it.\n\n"
        "A designer always makes the final call — AI suggestions can be wrong."
    )

with st.expander("About your data & AI limitations", expanded=False):
    st.write(
        "- Screenshots are processed in memory only and are never stored.\n"
        "- AI suggestions can be wrong. A designer decides; test with real users with disabilities.\n"
        "- Do not upload screens containing personal data."
    )

DEMO_DIR = Path(__file__).parent / "demo"
demo_images = sorted(
    p.name for pattern in ("*.png", "*.jpg", "*.jpeg") for p in DEMO_DIR.glob(pattern)
) if DEMO_DIR.exists() else []

if st.button("Try an example screen with known issues", help="Loads a sample screenshot and runs the audit for you"):
    example = pick_example_image(demo_images)
    if example:
        st.session_state["picked_demo_override"] = example
        st.session_state["auto_run"] = True
        st.rerun()

col1, col2 = st.columns([2, 1])
with col1:
    uploaded = st.file_uploader("Upload a screenshot", type=["png", "jpg", "jpeg"])
    picked_demo = None
    if not uploaded and demo_images:
        override = st.session_state.pop("picked_demo_override", None)
        options = ["(none)"] + demo_images
        default_index = options.index(override) if override in options else 0
        picked_demo = st.selectbox("...or pick a demo image", options, index=default_index)

image = None
if uploaded:
    image = Image.open(io.BytesIO(uploaded.read())).convert("RGB")
elif picked_demo and picked_demo != "(none)":
    image = Image.open(DEMO_DIR / picked_demo).convert("RGB")

with col2:
    scale_options = [1, 2, 3]
    default_scale_index = 0
    detection = None
    if image:
        detection = detect_scale(image.size[0])
        default_scale_index = scale_options.index(detection.scale)
    scale = st.selectbox(
        "Screenshot scale", scale_options, index=default_scale_index, format_func=lambda s: f"{s}x",
    )
    if detection:
        st.caption(f"Detected: {detection.scale}x ({detection.label})")
        if not detection.confident:
            st.warning("Scale detection is uncertain for this width — check the dropdown above.")
    language = st.selectbox("Language", ["English", "French", "Arabic"], index=0)

auto_run = st.session_state.pop("auto_run", False)
if image and (st.button("Audit", type="primary") or auto_run):
    with st.spinner("Running deterministic checks..."):
        findings = analyze_text_boxes(image, scale)
        deterministic_issues = to_issues(findings, image.size)

    with st.spinner("Asking the AI vision model..."):
        ai_response, provider_name, elapsed, fallback_note = analyze_with_ai(image, deterministic_issues)
        ai_issues = ai_issues_to_schema(ai_response, image.size)

    issues = merge_and_rank(deterministic_issues, ai_issues)
    score = compute_score(issues)

    st.session_state["last_result"] = {
        "image": image,
        "issues": issues,
        "score": score,
        "provider_name": provider_name,
        "elapsed": elapsed,
        "fallback_note": fallback_note,
        "screen_reader_script": ai_response.screen_reader_script,
    }

result = st.session_state.get("last_result")
if result:
    breakdown = format_breakdown(severity_breakdown(result["issues"]))
    st.metric("Accessibility score", f"{result['score']} / 100", help=breakdown)
    st.caption(breakdown)
    st.caption(f"AI provider: {result['provider_name']} ({result['elapsed']:.1f}s)")
    if result.get("fallback_note"):
        st.info(f"Fallback used: {result['fallback_note']}")
    annotated = draw_boxes(result["image"], result["issues"])
    st.image(annotated, caption="Numbered issues", use_container_width=True)

    tab_issues, tab_colorblind, tab_hear, tab_report = st.tabs(
        ["Issues", "Colour-blind views", "Hear this screen", "Report"]
    )

    with tab_issues:
        grouped = group_issues(result["issues"])
        if not grouped:
            st.success("No issues found.")
        for i, group in enumerate(grouped, start=1):
            min_confidence = min((inst.get("confidence", 1.0) for inst in group["instances"]), default=1.0)
            badge = confidence_badge(min_confidence)
            count = len(group["instances"])
            instance_note = f" ({count} instances)" if count > 1 else ""
            st.markdown(
                f"**{i}. [{group['severity'].upper()}] {group['plain_title']}{instance_note}** "
                f"— WCAG {group['wcag_id']} {group['wcag_name']} (Level {group['level']}) — {badge} \n"
                f"{group['why_it_matters']} \n"
                f"*Affects:* {group['who_is_affected']} \n"
                f"*Fix:* {group['fix']}"
            )

    with tab_colorblind:
        sim_cols = st.columns(3)
        for idx, kind in enumerate(SIMULATION_KINDS):
            with sim_cols[idx % 3]:
                try:
                    sim_img = simulate(result["image"], kind)
                    st.image(sim_img, caption=kind.replace("_", " ").title(), use_container_width=True)
                except Exception as e:
                    st.error(f"{kind}: {e}")

    with tab_hear:
        script = result["screen_reader_script"]
        if not script:
            st.info("No screen reader script available.")
        else:
            st.write("\n".join(f"- {line}" for line in script))
            if st.button("Generate speech"):
                audio = script_to_speech(script, language)
                st.audio(audio, format="audio/mp3")

    with tab_report:
        report_md = build_report(result["score"], result["issues"], result["provider_name"], result["elapsed"])
        st.markdown(report_md)
        st.download_button("Download report (Markdown)", report_md, file_name="seeall_report.md")

elif image:
    st.image(image, caption="Preview", use_container_width=True)
