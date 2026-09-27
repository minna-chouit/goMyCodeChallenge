# Baseline: checkout.jpg on v1 (pre-PLAN_V2)

- Image: 383x1023px, scale used: 1x (correct per A1's own rule: <500px = 1x)
- Provider: NVIDIA Build, 26.3s, no fallback
- **Score: 0 / 100**
- Issues: 31 total — 13 critical, 1 serious, 17 minor
- Breakdown: 13 contrast (all placeholder/label text, ~2.0-2.9:1 ratio),
  1 icon_unclear (back arrow, AI), 17 small_target (10 measured + 7 AI,
  duplicating the same elements the measured check already flagged)

## Comparison against eval/labels/checkout.md

Expected: "light placeholder text (1.4.3), placeholders used instead of
help text, asterisks with no '* required' note (3.3.2), vague link 'Have a
coupon? Click here' (2.4.4), small checkbox and small links close together
(2.5.8), white text on the red button near the contrast limit (1.4.3). A
fair score for this screen is roughly 40-60, not 0."

| Expected issue | Found? |
|---|---|
| Light placeholder text (1.4.3) | Yes — 13 contrast issues (all placeholders) |
| Placeholders used instead of help text | No — no such check exists yet |
| Asterisk with no "* required" legend (3.3.2) | No — no such check exists yet |
| Vague link "Have a coupon? Click here" (2.4.4) | No — flagged only for contrast/size, not vagueness |
| Small checkbox + links too close (2.5.8) | No — no target-spacing check exists |
| Red button text near contrast limit (1.4.3) | Yes — "PLACEORDER" flagged (2.86:1) |

**Misses**: link-purpose (2.4.4), placeholder-as-label (3.3.2 family),
target-spacing (2.5.8) — all require new checks, planned for A7.

**False positives / noise**:
- Score of 0 vs. a fair 40-60: current per-box flat deduction (critical
  -15 x 13 = -195 alone) has no cap and no grouping, so one root cause
  (light placeholder grey on every field) is counted as 13 separate
  critical deductions instead of one issue with many instances.
- AI re-flags small text (7 of 17 small_target issues) that the
  deterministic OCR check already flagged — duplicate issues under a
  different source, inflating both the issue count and the score penalty.
- No WCAG id/level/grouping on any issue, so a human has to read 31 lines
  to find 6 real underlying problems.

These map directly to Phase A's plan: A1 (scale — already correct here,
confirms no scale bug for this image), A2 (grouping + WCAG tags), A3
(fairer scoring), A7 (missing checks for 2.4.4, 3.3.2, 2.5.8).
