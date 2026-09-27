# SeeAll v2 progress log

## A0. Baseline
checkout.jpg (383x1023, correctly scale=1x) scores 0/100 on v1 vs. a fair
40-60 per the label. 31 issues found (13 critical/1 serious/17 minor);
6 real problems in the label, only 2 caught (placeholder contrast, red
button contrast) — link-purpose, placeholder-as-label, and target-spacing
checks don't exist yet. Full comparison in docs/baseline/checkout_v1_summary.md,
annotated image at docs/baseline/checkout_v1_annotated.jpg.

## A1. Fix screenshot scale
Added `seeall/scale_detect.py: detect_scale(width_px)` (11 tests, all width
bands: <500=1x, known 2x/3x phone widths, >1300=1x desktop, unknown
mid-range=uncertain). Wired into app.py: image loads before the scale
selectbox, pre-fills it with the detected value, shows "Detected: Nx
(label)", and warns when uncertain. Verified live in the running app:
checkout.jpg (383px) shows "Detected: 1x (phone, 383 px)" exactly as
specced. Score before/after: 0/100 -> 0/100 (unchanged) — v1's default was
already 1x for this image (selectbox index=0), so the false small-text
flags do NOT disappear here; they're a font-size-estimation issue, not a
scale bug, and will need A2/A3 (grouping) or a later OCR calibration fix,
not A1. Noting this now rather than overclaiming.
Also widened the demo picker to include jpg/jpeg (was png-only) so
checkout.jpg is selectable for manual verification going forward.

## A2. New issue data model with WCAG tags and grouping
Added `seeall/wcag.py` (catalog of 7 criteria used: 1.4.3, 1.1.1, 1.4.1,
1.3.1, 3.3.2, 2.5.8, 4.1.2, each with id/name/level/principle/description,
mapped from issue `type`) and `seeall/group_issues.py: group_issues()`
(groups by wcag_id + type into one issue with an `instances` list; merges
`source` when both measured and ai contributed; severity = most severe in
the group). 12 new tests, all passing (68 total).
Wired into the Issues tab (kept the flat list for scoring/annotation,
per A3/A4 being separate steps). Verified live on checkout.jpg: 30 flat
issues collapsed to 5 groups, e.g. "Text is hard to read (13 instances) —
WCAG 1.4.3 Contrast (Minimum) (Level AA)" and "Tap target or text is too
small (11 instances) — WCAG 2.5.8" — exactly the "placeholders = 1 issue
with many instances" target. Score before/after A2: 0/100 -> 0/100
(scoring untouched until A3, as planned).
Observed AI-quality nuance (not a bug in this step): one NVIDIA finding
was typed "alt_text" but its description is actually about contrast on
"Return to cart" — a model mislabel that will need C1's stricter WCAG-id
prompt to fix, not something A2's grouping can correct.

## A3. Fairer score
Added `compute_score_v2(grouped_issues)`, `level_counts()`, `grade_label()`
to `seeall/scoring.py`: per-GROUP deduction (critical -15, serious -8,
minor -3), +10%/extra instance capped at +50% of base, halved if the
group is purely AI-sourced with average confidence <0.5, floored at 0.
10 new tests pin the formula exactly (78 total, all passing).
Wired into app.py: score/grade/level-counts now come from grouped issues,
not the old flat per-box `compute_score`.
Verified live on checkout.jpg (NVIDIA failed this run, fell back to
Gemini — visibly shown, itself a nice validation of earlier reliability
work): **score 63/100 — Needs work**, squarely in the plan's 55-70 target.
"Level A: 1 issue, Level AA: 2 issues" shown correctly. 3 groups total
(13 contrast, 3 missing_label, 11 small_target).
Offline check (deterministic-only, no API call, to save quota):
clean_1.png / clean_2.png -> 100 "Excellent" (matches >=90 target).
grey_on_white.png -> 85 "Good" — NOT literally "low" as the plan's
Done-when phrasing suggests, but this is a single, real, isolated
contrast failure on an otherwise clean image; scoring it at 85 rather
than near-0 is the intended fairness improvement, not a bug. Flagging
this honestly rather than tuning the formula to force a lower number for
one specific test image.

## A4. Clear annotations
Added `seeall/box_validation.py` (is_valid_box, is_low_content,
drop_invalid_ai_boxes — drops AI boxes outside the image, <8x8px, or over
near-uniform/empty regions), `seeall/thumbnail.py` (crop_thumbnail),
`seeall/filter_issues.py` (all/critical/measured/ai), and rewrote
`seeall/annotate.py` to draw per-GROUP numbers (repeated on every
instance), severity colour (red/orange/dark-yellow — pure yellow (255,255,0)
is nearly invisible on white, so used a darkened gold instead for the
annotation's own legibility), solid outline for measured, dashed for AI
(hand-rolled dashed-rectangle since PIL has no native dashed stroke).
27 new tests (102 total).
Wired into app.py: `drop_invalid_ai_boxes` runs right after the AI call,
before merging; a legend line above the image explains colour/outline/
numbering; a "Show: All/Critical/Measured/AI" radio filters the issue
list (image numbering stays fixed to the full set so filtering doesn't
renumber); each issue card shows a cropped thumbnail of its first
instance.
**Bug found and fixed during verification**: deterministic issues were
tagged `source: "deterministic"` (from before A2 existed), but A2/A4's
data model and every new test assumed `"measured"` per the plan's own
wording. This silently made every measured (OCR/contrast) box render
DASHED instead of solid — caught by rendering the annotated checkout.jpg
locally and visually inspecting it. Fixed by renaming the source string
in `seeall/deterministic.py` (2 lines); no test had to change since they
all already expected "measured". Before/after annotated images saved at
docs/baseline/checkout_v1_annotated.jpg (old flat/unlabelled boxes) vs
docs/baseline/checkout_v2_annotated.jpg (grouped numbers, solid outlines,
readable without explanation — describing it here per the Done-when: two
big red "1" circles over the placeholder fields sharing one number, one
gold "2" circle repeated over each small-text field, no overlapping
badges, no stray empty box).
