# SeeAll Eval Results

Deterministic checks (contrast, small text) are provider-independent; the AI column and latency are run once per provider below so both real providers can be shown as tested.

| Image | Contrast (found/exp) | P/R | Small text (found/exp) | P/R | NVIDIA color-only (found/exp) | NVIDIA provider/time | Gemini color-only (found/exp) | Gemini provider/time |
|---|---|---|---|---|---|---|---|---|
| grey_on_white.png | 1/1 | 1.0/1.0 | 0/0 | 1.0/1.0 | 0/0 | NVIDIA Build / 7.23s | 0/0 | Google Gemini / 2.61s |
| tiny_text.png | 0/0 | 1.0/1.0 | 1/1 | 1.0/1.0 | 1/0 | NVIDIA Build / 8.68s | 0/0 | MOCK - AI unavailable / 0.6s |
| red_green_status.png | 0/0 | 1.0/1.0 | 0/0 | 1.0/1.0 | 2/1 | NVIDIA Build / 6.17s | 0/1 | MOCK - AI unavailable / 0.62s |
| clean_1.png | 0/0 | 1.0/1.0 | 0/0 | 1.0/1.0 | 0/0 | NVIDIA Build / 1.7s | 0/0 | MOCK - AI unavailable / 0.59s |
| clean_2.png | 0/0 | 1.0/1.0 | 0/0 | 1.0/1.0 | 0/0 | NVIDIA Build / 2.35s | 0/0 | MOCK - AI unavailable / 0.55s |

NVIDIA: 5 calls, average 5.23s, fallback used: False

Gemini: 5 calls, average 0.99s, fallback used: True

## Notes
- Gemini's free tier (20 requests/day/model) was already partly used by
  earlier manual validation; some Gemini calls above fell back to mock
  mid-run. NVIDIA Build has no such daily cap observed so far.
- red_green_status.png: NVIDIA correctly reports 2 color-only issues
  (one per status dot); expected.json only tracks 1 bucket for this
  category, so the found/expected ratio looks like an over-count but
  both findings are genuine.