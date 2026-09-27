# SeeAll — remaining work before 17:30

Feature freeze: 16:15. Nothing new after that — only bug fixes.

## PLAN_V2 progress (docs/PLAN_V2.md)

### Phase A
- [x] A0. Baseline
- [x] A1. Fix screenshot scale
- [ ] A2. New issue data model with WCAG tags and grouping
- [ ] A3. Fairer score
- [ ] A4. Clear annotations
- [ ] A5. Solutions everywhere
- [ ] A6. Readable report
- [ ] A7. New checks
- [ ] A8. Re-evaluate
- PAUSE for human approval before Phase B
### Phase B (plan pending human confirmation)
- [ ] B1/B2/B3
- PAUSE for human approval before Phase C
### Phase C
- [ ] C1-C4

## Must do before freeze

- [x] **Real-model test: NVIDIA Build.** NVIDIA is now the primary provider.
      Validated live with `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`:
      5/5 real audits succeeded (UI + eval), 1-8s latency, no JSON
      validation failures, no daily-quota issue observed. Thinking mode is
      disabled via `chat_template_kwargs.enable_thinking=false` and any
      leftover `<think>` tags/code fences are stripped before parsing
      (`seeall/ai.py: clean_json_response`, `needs_thinking_disabled`).
- [x] **Real-model test: Gemini (secondary).** Validated live too:
      `gemini-2.0-flash` was retired (fixed, now `gemini-3.8-flash`).
      Findings were high-quality with no prompt tuning needed. Free tier's
      20 req/day cap was hit twice during our own testing — a real demo
      risk if Gemini becomes primary again on a day it's already used.
- [ ] **Real-model test: OpenRouter.** Not yet validated live — only NVIDIA
      and Gemini have real API calls behind them so far. Order is NVIDIA ->
      OpenRouter -> Gemini -> mock; if NVIDIA's key is ever removed,
      confirm OpenRouter's free Nemotron model actually gets used and
      returns valid JSON before relying on it.
- [ ] **Real screenshots in `eval/images/`.** Still only the 5 synthetic
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
- [x] **README AI disclosure.** Updated: "Models used" now documents the
      thinking-mode fix, per-provider live-validation results, the 20
      req/day Gemini quota risk (hit twice during testing), and the
      in-memory AI result cache. "Responsible AI" section unchanged and
      still accurate (in-memory processing, AI-can-be-wrong warning,
      personal-data warning) — also surfaced live in-app (sidebar +
      expander + always-visible provider status + fallback-note banner).

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

## Reliability work done since the initial build

- [x] **Silent exception swallowing fixed.** Every provider failure is now
      logged (`seeall.ai` logger, `%s failed (%s): %s`) with a short
      classified reason (`short_error_reason`: rate-limited / model
      unavailable / authentication failed / unavailable), and the UI shows
      an `st.info` banner naming which provider failed and why when a
      fallback happens.
- [x] **AI result caching.** In-memory cache keyed by image + deterministic-
      findings hash (`seeall/ai_cache.py`) avoids re-spending quota on
      repeat audits of the same screenshot within a server process's
      lifetime. Verified live: a second UI request for the same demo image
      returned the identical cached latency instead of a new API call.

## Known issues / risks for the demo

- **Gemini free tier: 20 requests/day per model.** Confirmed exhausted
  twice during validation testing today. NVIDIA is primary now, so this
  mostly matters only if NVIDIA's key becomes unavailable mid-demo.
- **OpenRouter path is unvalidated.** If both NVIDIA and Gemini fail during
  the demo, the third hop (OpenRouter's free Nemotron model) has not been
  exercised against the real API yet — unknown whether its JSON output
  needs the same thinking-mode fix (it should, same model family) or has
  its own quirks.
- **Cache is process-local and unbounded.** Fine for a single demo session;
  would need an eviction policy or persistence if this ran as a long-lived
  multi-user service.
