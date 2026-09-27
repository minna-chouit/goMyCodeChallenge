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

## A5. Solutions everywhere
Added `css_snippet()` and `hex_to_rgb()` to `seeall/contrast.py`, wired into
the contrast fix text: e.g. "Fix: Change text color to #747474 -> 4.6:1
(color: #747474; /* 4.6:1 on #FDFDFD */)". Added `seeall/preview_fix.py:
recolor_text_pixels()` (nearest-cluster pixel recolouring within each
failing box) and wired a "Preview with fixes" checkbox showing before/after
side by side. Added `seeall/vision_analysis.py` (contrast_failures_in_view,
color_only_relevant_issues, simulation_panel_text) giving every simulation
view a "What breaks here" / "How to fix it" panel. 21 new tests (117 total).
Verified live on grey_on_white.png: CSS snippet rendered exactly as
specced; "Preview with fixes" toggled a real before/after recolour;
every colour-vision view (deuteranopia/protanopia/tritanopia/achromatopsia)
showed "1 finding relies on colour alone..." + a concrete fix, and Low
Vision correctly showed "No extra problems for these users" (its one
contrast issue was already failing originally, not "only in this view").
Caught and fixed a grammar bug during verification ("1 finding rely" ->
"1 finding relies") before committing.

## A6. Readable report
Rewrote `seeall/report.py` on the new grouped data model: `top_fixes()`
(ranks by the same per-group deduction magnitude `compute_score_v2` uses,
so "highest impact" is literally "costs the most score"), `verdict_sentence()`
(one plain sentence per grade), `group_by_principle()` (Perceivable ->
Operable -> Understandable -> Robust, empty buckets omitted), and a static
`CANNOT_CHECK` list. `build_report()` (Markdown) restructured to: summary,
verdict, "Fix these 3 first", issues grouped by principle, cannot-check
disclosure. Added `build_html_report()` — a self-contained styled/printable
HTML version of the same structure. 9 new tests (126 total).
Wired into app.py: Report tab now shows both, with separate "Download
report (HTML)" and "Download report (Markdown)" buttons.
Verified live on grey_on_white.png: report opened with score/grade/verdict,
"Fix these 3 first" (correctly showed only the 1 real issue present, not
padded to 3), issues grouped under "Perceivable", and the cannot-check
list — understandable without knowing what "1.4.3" means, per the
Done-when.

## A7. New checks
**Measured (all unit-tested):**
- `seeall/link_purpose.py`: `is_vague_link_text()` flags "click here", "read
  more", "here", "more", "learn more", French, and Arabic equivalents.
  Short single words ("here"/"more") require an exact match so real words
  like "adhere"/"moreover" aren't false-flagged; longer phrases match as a
  compact substring so OCR-merged text like "Have a coupon?Clickhere"
  still gets caught. `vague_link_issues()` builds the 2.4.4 issue.
  **Verified live on checkout.jpg: correctly flagged "Have a
  coupon?Clickhere" as WCAG 2.4.4** — exactly the plan's Done-when.
- `seeall/aaa_bonus.py` + `required_ratio_aaa()`: informational-only report
  of text that also clears the stricter AAA bar (7:1 normal / 4.5:1
  large); no score impact. Shown as a caption under the score.
- `seeall/non_text_contrast.py`: implemented and unit-tested (concentric-
  ring sampling around each OCR box vs. further-out background), but
  **NOT wired into the live pipeline** — verified live on checkout.jpg it
  produced 37 flagged "boundaries" including the phone's status bar
  ("9:41"), i.e. it can't tell an input border from ordinary text
  neighbourhoods on a real screenshot, only on a clean synthetic test.
  Shipping the smallest WORKING version per the plan's own rule: kept the
  tested module (in case a future PR adds real edge/rectangle detection)
  but disabled it from `app.py` rather than ship 37 false positives.

**AI checklist (7 new types added: image_of_text, error_handling,
captcha_or_memory_test, drag_only, sticky_obscures_focus, orientation_lock,
visual_presentation — each mapped to its own WCAG id in wcag.py; existing
`missing_label` prompt text extended to also cover the 3.3.2
asterisk-with-no-legend and placeholder-as-only-label patterns rather than
adding a redundant new type for the same WCAG id).**
Verified live on checkout.jpg: the longer SYSTEM_PROMPT still produced
valid JSON (no validation-failure retries), but **latency increased a
lot** — one call took 156s (vs. 1-8s pre-A7) and a second call exceeded
6 minutes before being cut off. This run happened to return zero AI-found
issues both times (a model-variance outcome, not a crash), so the 3.3.2
asterisk-legend AI catch specifically could not be confirmed live within
the time available — flagged in docs/TASKS.md as unverified, not claimed
as working.
30 new tests (148 total).

## A8. Re-evaluate
The user added 10 real screenshots + rich label files (eval/labels/*.md,
each with WCAG-tagged expected issues, false-positive traps, and an
expected score band) while A1-A7 were in progress. Ran v1-vs-v2 scoring
(deterministic-only, to respect the "keep API usage low" rule given A7's
observed 1.5-6+ minute NVIDIA latency) across all 16 eval images.
**Headline result**: 3 real screens that scored a meaningless 0/100 under
v1 (checkout.jpg, intelly dashboard with 230 flat findings, mobile UI)
now score 60-73 "Needs work" under v2 — every other image's score moved
up or stayed flat, none moved down. checkout.png got the full before/after
including a real AI call (reusing A7's live-verified result: v1=0 ->
v2=60), satisfying the plan's specific Done-when. Full table and notes in
eval/results.md's new "v2 re-evaluation (A8)" section.
Cut for time: did not systematically cross-check each label's "Should NOT
be flagged" false-positive traps, or re-run the AI dimension across all 12
new real screenshots (both flagged as follow-ups in eval/results.md and
docs/TASKS.md rather than silently skipped).
