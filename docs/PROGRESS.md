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
