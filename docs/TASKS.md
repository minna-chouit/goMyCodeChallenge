# SeeAll — remaining work before 17:30

Feature freeze: 16:15. Nothing new after that — only bug fixes.

## Must do before freeze

- [ ] **Real-model test: NVIDIA Build and/or OpenRouter.** Only Gemini has
      been validated against a live API so far (see below). If an
      `NVIDIA_API_KEY` or `OPENROUTER_API_KEY` becomes available, run the
      same check: one real audit through the UI, one through
      `eval/run_eval.py`, confirm no JSON validation failures, confirm the
      fallback order (NVIDIA -> OpenRouter -> Gemini -> mock) picks the
      right provider.
- [ ] **Real screenshots in `eval/images/`.** Currently only the 5 synthetic
      images (grey-on-white, tiny text, red/green status, 2 clean) have
      been run through eval. Add 5-7 real app/web screenshots with real
      accessibility issues, add matching entries to `eval/expected.json`,
      and re-run `eval/run_eval.py`.
- [ ] **Hugging Face Spaces deploy.** README has the Spaces front matter
      ready (`sdk: streamlit`, `app_file: app.py`). Needs a Space created
      under your HF account, secrets set (`NVIDIA_API_KEY` /
      `OPENROUTER_API_KEY` / `GEMINI_API_KEY`), and `git push` to the Space
      remote. This needs your HF credentials — not something automatable
      here.
- [x] **README AI disclosure.** Present: "Models used" section names every
      provider and fallback order, "Responsible AI" section covers
      in-memory processing, AI-can-be-wrong warning, and the personal-data
      warning. Also surfaced live in-app (sidebar + expander). Worth a
      final read-through before the demo, not a rewrite.

## Brainstormed additions (all approved, all built and committed)

- [x] "Try an example screen with known issues" button — one click loads a
      demo image and runs the audit automatically.
- [x] Visible confidence badge ("Needs human check" below 50%) per issue,
      in both the Issues tab and the Markdown report.
- [x] Severity breakdown next to the score (e.g. "82/100 — 1 critical, 1
      minor").
- [x] Regression test locking in mock fallback when no API keys are set
      (`tests/test_ai_fallback.py`).
- [x] Sidebar "How SeeAll works" walkthrough + always-visible AI provider
      status line (not just after running an audit).

## Known issues / risks for the demo

- **Gemini free tier: 20 requests/day per model.** Already exhausted once
  during validation testing today. If it's exhausted again during judging,
  the app will silently fall back to mock (clearly labelled in the UI, but
  judges won't see real AI output). Mitigate by not over-testing right
  before the demo, and/or having NVIDIA/OpenRouter keys as backup.
- **Provider failures are swallowed silently** (`except Exception: continue`
  in `seeall/ai.py`) — there's no server-log trace of *why* a provider
  failed, only that it fell back. Fine for the hackathon; would need a
  logged reason before this goes further.
