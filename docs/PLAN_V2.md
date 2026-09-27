# SeeAll v2 - improvement plan

## Rules (read first, follow for every step)
- Do ONE step at a time, in order. Do not start the next step until the
  current step's "Done when" checks all pass.
- Test-first: write a failing test, then the code. Run the full test suite.
- After each step: verify in the running Streamlit app with
  eval/images/checkout.png, commit with message "v2 step N: <title>",
  tick the step in docs/TASKS.md, and write 2-3 lines in docs/PROGRESS.md
  (what changed, what you verified, before/after score for checkout.png).
- Never break a working app. If a step runs over its time box, ship the
  smallest working version, note what was cut in PROGRESS.md, and move on.
- Keep API usage low: use the image-hash cache; do not re-run the full eval
  after every step (only in steps A8 and C3).
- Deadline: submission 17:30, feature freeze 16:15. Stop at the PAUSE
  markers and wait for the human.

## Phase A - make the results correct, clear and useful

### A0. Baseline (10 min)
Run checkout.png through the app. Save the current score, issue count and
annotated image to docs/baseline/. Compare the issues against
eval/labels/checkout.md and list false positives and misses in PROGRESS.md.
Done when: baseline saved and the comparison is written.

### A1. Fix screenshot scale (20 min)
Auto-detect scale from image width: under 500 px wide = 1x; 700-1300 = 2x
or 3x (use common phone widths 750/828 = 2x, 1080/1125/1170/1179/1284/1290
= 3x); desktop widths over 1300 = 1x. Keep the manual selector as an
override, pre-filled with the detected value and a note "Detected: 1x
(phone, 383 px)". Show a warning when detection is uncertain.
Done when: tests cover each width band; checkout.png is detected as 1x and
the false small-text flags disappear.

### A2. New issue data model with WCAG tags and grouping (30 min)
Every issue gets: wcag_id (e.g. "1.4.3"), wcag_name ("Contrast
(Minimum)"), level (A/AA/AAA), principle (Perceivable/Operable/
Understandable/Robust), source ("measured" or "ai"), severity
(critical/serious/minor), plain_title (one short plain-English line),
who_is_affected, why_it_matters, fix, instances (list of boxes, each with
optional measured values).
Group findings with the same wcag_id and the same kind of fix into ONE
issue with several instances (e.g. "Placeholder text too light - 8 fields").
Add a WCAG catalog module (seeall/wcag.py) holding id, name, level,
principle and a one-line plain description for every criterion used.
Done when: checkout.png shows grouped issues (placeholders = 1 issue with
many instances) and every issue displays its WCAG id and level.

### A3. Fairer score (20 min)
Replace per-box deductions with per-issue deductions, weighted by severity
and capped: critical -15, serious -8, minor -3, a grouped issue adds at most
+50% of its base deduction for extra instances, AI issues with confidence
below 0.5 count half, floor at 0. Also show a pass/fail count per level
(e.g. "Level A: 1 issue, Level AA: 3 issues") and a grade label:
90+ Excellent, 75-89 Good, 50-74 Needs work, under 50 Poor.
Done when: unit tests pin the formula; checkout.png scores roughly 55-70;
a clean synthetic screen scores 90+; grey_on_white still scores low.

### A4. Clear annotations (30 min)
- Numbers on the image match the issue numbers in the list (one number per
  grouped issue, repeated on each instance).
- Colour = severity: critical red, serious orange, minor yellow. Solid
  outline = measured, dashed outline = AI finding.
- Number badges: bigger, white text on a solid colour circle, placed so they
  do not overlap text or each other.
- A legend above the image explaining colours, solid vs dashed, and numbers.
- Drop invalid AI boxes: outside the image, smaller than 8x8 px, or on a
  near-uniform area with no content (like the empty box 14 bottom-left).
- Each issue card shows a cropped thumbnail of its first instance.
- A filter: show all / critical only / measured only / AI only.
Done when: tests cover box validation; the checkout annotation is readable
without explanation (describe it in PROGRESS.md) and the empty box is gone.

### A5. Solutions everywhere (40 min)
- Contrast issues: exact fix colour, new ratio, and a CSS snippet, e.g.
  "color: #595959; /* 7.0:1 on #FFFFFF */".
- "Preview with fixes": a second image where failing text pixels (the text
  colour cluster found by OCR) are recoloured to the suggested colour, shown
  side by side with the original (before / after).
- Each simulation view (deuteranopia, protanopia, tritanopia, achromatopsia,
  low vision) gets a short panel: "What breaks for these users here" and
  "How to fix it". Compute it: re-run the contrast check on the simulated
  image and list elements that fail only in that view; add colour-only issues
  (1.4.1) relevant to that view. Always end with concrete fixes (add an icon
  or text label, underline links, increase contrast, don't rely on red/green).
Done when: tests cover the recolour function and simulated-view contrast;
every view shows at least one sentence of analysis and one fix, or "No
extra problems for these users".

### A6. Readable report (30 min)
Restructure the on-screen results and the downloadable report:
1. Summary card: score, grade, one sentence verdict, counts by severity.
2. "Fix these 3 first": the three highest-impact issues, plain language.
3. Issues grouped by principle (Perceivable, Operable, Understandable), each
   as a card: number, plain_title, WCAG badge (id + level), who is affected,
   why it matters (one line), fix (with CSS when possible), thumbnail.
4. "What SeeAll cannot check from a screenshot" (short list, see A7 notes).
Write for designers, not auditors: short sentences, no jargon without a
plain explanation. Offer the download as HTML (styled, readable, printable)
and keep Markdown as a second option.
Done when: the report opens with the summary and top 3; a person can
understand each issue without knowing WCAG.

### A7. New checks (45 min)
Measured (exact, unit-tested):
- 2.4.4 Link purpose: flag vague link text in OCR output (click here, read
  more, here, more, learn more, en savoir plus, cliquez ici, and Arabic
  equivalents such as "اضغط هنا" and "اقرأ المزيد").
- 1.4.11 Non-text contrast: 3:1 for input borders, button edges and icons
  where a clear boundary is detectable; mark as "measured (estimated
  region)".
- 1.4.6 AAA bonus: report which text also passes 7:1 (informational, no
  deduction).
AI (added to the prompt checklist, each with its wcag_id):
- 3.3.2 Required fields marked only with * and no legend; placeholders used
  as the only label or hint.
- 1.4.5 Images of text. 3.3.1/3.3.3 Errors shown only by colour or without a
  suggestion. 3.3.8 CAPTCHA or memory tests on login screens. 2.5.7 Drag-only
  controls. 2.4.11 Sticky bars that may hide focused items. 1.3.4 "Rotate
  your device" messages. 1.4.8 Justified text or very long lines.
Done when: tests cover every measured check; checkout.png flags "Have a
coupon? Click here" (2.4.4) and the asterisk legend issue (3.3.2).

### A8. Re-evaluate (15 min)
Run the eval on all labelled screens in eval/images with eval/labels.
Update eval/results.md: per screen, found vs expected, false positives,
score before v2 vs after v2.
Done when: results.md shows before/after for checkout.png.

## PAUSE - stop here. Summarise Phase A for the human and wait for
## approval before Phase B.

## Phase B - UI polish (plan will be confirmed by the human)
- B1. Layout: results page reads top to bottom: summary, top 3, annotated
  image with legend, grouped issues, simulations with fixes, report download.
- B2. Visual design: consistent colours for severity, WCAG badges, cards,
  generous spacing; the app itself must pass its own checks (run SeeAll on a
  screenshot of SeeAll and fix what it finds - use this in the demo).
- B3. Language: UI labels available in English and French at minimum.
Done when: the human approves the look.

## PAUSE - wait for approval before Phase C.

## Phase C - better NVIDIA outputs (no training)
- C1. Prompt: include the WCAG checklist from seeall/wcag.py (ids, names,
  plain descriptions) and require every issue to cite a wcag_id from it,
  quote the visible text it refers to as evidence, and give a box.
- C2. Few-shot: add 1-2 labelled screens from eval/labels as worked
  examples of a good answer (keep the prompt within the model's limits;
  downscale example images if needed).
- C3. Guardrails: temperature 0.2 or lower; reject issues without evidence
  or with invalid boxes; merge AI issues that duplicate measured ones;
  optional second call that asks the model to verify its own findings
  against the image and drop unsupported ones (only if latency stays
  under ~15 s).
- C4. Re-run the eval and compare precision/recall before and after C1-C3.
Done when: results.md shows the AI precision improved or stayed equal with
fewer false positives, and latency is reported.