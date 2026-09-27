---
title: SeeAll
emoji: 👁️
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: "1.38.0"
app_file: app.py
pinned: false
---

# SeeAll

AI accessibility auditor for designers. Upload a screenshot, get measured
WCAG contrast/text-size issues, AI-found issues (unclear icons, color-only
meaning, missing labels, small tap targets, cluttered layout, alt text),
colour-blindness/low-vision simulations, a "Hear this screen" screen-reader
readout (English/French/Arabic), and a downloadable Markdown report.

## What it does

1. **Measured issues** (deterministic): OCR finds text boxes, a 2-means
   colour split estimates text vs. background colour, and WCAG 2.2 contrast
   ratios are computed exactly. Small text (<12px) is flagged.
2. **AI-found issues** (vision model): meaning shown by colour only, unclear
   icons, missing/vague labels, small tap targets, cluttered layout, and
   missing alt text — returned as strict JSON, validated with pydantic.
3. **Simulated views**: deuteranopia, protanopia, tritanopia, achromatopsia,
   and low vision (blur + reduced contrast).
4. **Ranked issue list** with severity, location (numbered boxes on the
   image), why it matters, and a concrete fix.
5. **Hear this screen**: AI writes the screen-reader announcement order,
   played back with gTTS in English, French, or Arabic.
6. **Score out of 100** and a downloadable Markdown report.

## How to run

```bash
python -m venv .venv
.venv/Scripts/activate   # or source .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
cp .env.example .env     # fill in NVIDIA_API_KEY and/or GEMINI_API_KEY
streamlit run app.py
```

Without any API key configured, the app falls back to a clearly labelled
"MOCK - AI unavailable" response so the demo still runs offline.

## Models used

Fallback order: NVIDIA Build -> OpenRouter -> Google Gemini -> offline mock.

- NVIDIA Build (`nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` by default,
  configurable via `VLM_MODEL`), OpenAI-compatible endpoint.
- OpenRouter (`nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` by default,
  configurable via `OPENROUTER_VLM_MODEL`) — a free-tier NVIDIA Nemotron
  vision model, useful when the direct NVIDIA Build key isn't available.
- Google Gemini (`gemini-3.8-flash` by default, configurable via
  `GEMINI_MODEL`; `gemini-2.0-flash` was retired) via its OpenAI-compatible
  endpoint. Free tier is capped at 20 requests/day per model — expect
  fallback to mock if that's exhausted during a demo.
- Offline mock fallback if no provider is reachable.

## Evaluation

`eval/make_synthetic.py` generates 5 synthetic screenshots with known issues
(grey-on-white text, tiny text, red/green-only status, 2 clean screens).
`eval/run_eval.py` runs the full pipeline against `eval/images/` and scores
precision/recall for deterministic checks against `eval/expected.json`,
writing `eval/results.md`. `tests/test_contrast.py` unit-tests the WCAG
contrast formula and the colour-suggestion function.

## Limitations & responsible AI

- Screenshots are processed in memory only; nothing is stored.
- AI suggestions can be wrong — a human designer should decide, and the app
  should be validated with real users with disabilities.
- Do not upload screenshots containing personal data.
- AI-found issues with confidence below 0.5 are labelled "Needs human check".

## Out of scope

Live website crawling, Figma plugins, user accounts, databases, training
custom models.
