# intelly_desktop_dashboard.jpg
Source: Dribbble-style concept, medical dashboard. Device: desktop mockup inside a frame (1200 px), UI is shown smaller than real size.
Expected score: 40-60.

## Real issues
- 1.4.3 Contrast (Minimum), AA - serious - measured: faded timeline cards ("Emergency visit", "Diagnostic test", 07:00-07:30) are very light grey on beige; they carry information, so they must pass.
- 1.4.3 Contrast (Minimum), AA - serious - measured: small grey captions on coloured cards (22-32 Y.O, AVERAGE, MINIMUM, STABLE, FAIR, CRITICAL, IN CLINIC, chart time labels) (estimated fail).
- 1.4.3 Contrast (Minimum), AA - minor - measured: greyed calendar days (5, 12, 19, 26) and week labels (W23-W27).
- Small text - minor - measured: many labels well under 12 px (card captions, calendar weeks, patient subtitles).
- 1.4.1 Use of Color, A - serious - AI: bar chart uses solid vs dashed bars with no legend; line chart has no y-axis values; meaning depends on visuals only.
- 1.1.1 Non-text Content, A - serious - AI: top-right icon-only buttons (profile, notifications, settings) and calendar icon buttons (refresh, download) have no visible labels.
- 2.5.8 Target Size (Minimum), AA - minor - AI: sidebar collapse button (small pink circle) is below 24x24 px.
- 1.4.11 Non-text Contrast, AA - minor - measured/AI: search field border (light pink) and dashed filter chips on beige are faint.
- 1.4.3 Contrast (Minimum), AA - minor - AI: decorative shapes (star, heart, triangle) sit behind text in cards and lower its contrast (e.g. "00:24 min IN CHAT").

## Should NOT be flagged
- "Good morning, Dr.Olivia" black on beige: pass.
- White sidebar text on black: pass.
- "Add event" and "View all details" (white on black): pass.
- Patient list items have text labels (Emergency Visit, Routine Check-Up): colour is not the only cue there.

## Notes
- Scale detection edge case: the screenshot is a presentation frame, not a real screen, so measured text sizes are smaller than in the real product.
