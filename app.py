import io
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from PIL import Image

from seeall.ocr import analyze_text_boxes
from seeall.deterministic import to_issues
from seeall.annotate import draw_boxes
from seeall.scoring import compute_score
from seeall.ai import analyze_with_ai
from seeall.merge import ai_issues_to_schema, merge_and_rank
from seeall.simulate import simulate, SIMULATION_KINDS
from seeall.speech import script_to_speech
from seeall.report import build_report
from seeall.demo_picker import pick_example_image
from seeall.badges import confidence_badge

load_dotenv()

st.set_page_config(page_title="SeeAll - Accessibility Auditor", layout="wide")

st.title("SeeAll")
st.caption("AI accessibility auditor for designers")

with st.expander("About your data & AI limitations", expanded=False):
    st.write(
        "- Screenshots are processed in memory only and are never stored.\n"
        "- AI suggestions can be wrong. A designer decides; test with real users with disabilities.\n"
        "- Do not upload screens containing personal data."
    )

DEMO_DIR = Path(__file__).parent / "demo"
demo_images = sorted(p.name for p in DEMO_DIR.glob("*.png")) if DEMO_DIR.exists() else []

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

with col2:
    scale = st.selectbox("Screenshot scale", [1, 2, 3], index=0, format_func=lambda s: f"{s}x")
    language = st.selectbox("Language", ["English", "French", "Arabic"], index=0)

image = None
if uploaded:
    image = Image.open(io.BytesIO(uploaded.read())).convert("RGB")
elif picked_demo and picked_demo != "(none)":
    image = Image.open(DEMO_DIR / picked_demo).convert("RGB")

auto_run = st.session_state.pop("auto_run", False)
if image and (st.button("Audit", type="primary") or auto_run):
    with st.spinner("Running deterministic checks..."):
        findings = analyze_text_boxes(image, scale)
        deterministic_issues = to_issues(findings, image.size)

    with st.spinner("Asking the AI vision model..."):
        ai_response, provider_name, elapsed = analyze_with_ai(image, deterministic_issues)
        ai_issues = ai_issues_to_schema(ai_response, image.size)

    issues = merge_and_rank(deterministic_issues, ai_issues)
    score = compute_score(issues)

    st.session_state["last_result"] = {
        "image": image,
        "issues": issues,
        "score": score,
        "provider_name": provider_name,
        "elapsed": elapsed,
        "screen_reader_script": ai_response.screen_reader_script,
    }

result = st.session_state.get("last_result")
if result:
    st.metric("Accessibility score", f"{result['score']} / 100")
    st.caption(f"AI provider: {result['provider_name']} ({result['elapsed']:.1f}s)")
    annotated = draw_boxes(result["image"], result["issues"])
    st.image(annotated, caption="Numbered issues", use_container_width=True)

    tab_issues, tab_colorblind, tab_hear, tab_report = st.tabs(
        ["Issues", "Colour-blind views", "Hear this screen", "Report"]
    )

    with tab_issues:
        if not result["issues"]:
            st.success("No issues found.")
        for i, issue in enumerate(result["issues"], start=1):
            badge = confidence_badge(issue.get("confidence", 1.0))
            st.markdown(
                f"**{i}. [{issue['severity'].upper()}] {issue['type']}** — {badge} \n"
                f"{issue['description']} \n"
                f"*Affects:* {issue['affected_users']} \n"
                f"*Fix:* {issue['fix']}"
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
