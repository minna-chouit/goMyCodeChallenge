# mobile_UI.jpg
Source: Dribbble-style concept, two phone screens (productivity app) on a grey background with a watermark. Device: phone mockups inside a 1080 px image.
Expected score: 30-50.

## Real issues
- 1.4.3 Contrast (Minimum), AA - critical - measured: white "View Task" and "Set Reminder" on orange buttons (estimated about 2:1, fails even the 3:1 large-text rule).
- 1.4.3 Contrast (Minimum), AA - serious - measured: orange "Productive" on white (estimated about 2:1; large text still needs 3:1).
- 1.4.3 Contrast (Minimum), AA - serious - measured: light grey times on white/peach cards (07:00 - 08:00, 09:00 - 10:00, 11:00 - 12:00, 08:00 - 10:00). Group as one issue.
- 1.1.1 Non-text Content, A - serious - AI: bottom navigation is icon-only (home, calendar, add, stats, profile) with no text labels.
- 1.4.11 Non-text Contrast, AA - serious - measured/AI: inactive bottom-bar icons are very light grey on white (below 3:1).
- 2.4.4 Link Purpose, A - minor - AI: "Click to view more" card: vague wording ("+5 schedule" helps a little).
- 1.1.1 Non-text Content, A - minor - AI: attendee avatars have no names; progress ring "80%" relies on the ring graphic plus a number (number present: OK), grey track is faint.
- 1.4.11 Non-text Contrast, AA - minor - AI: thin orange current-time line and the ring's grey remainder track are faint.

## Should NOT be flagged
- Dark teal headings on white: pass.
- White text on dark teal cards ("Great, your today's plan almost done", "February", dates): pass.
- The background watermark: decoration, not content.

## Notes
- "Scedule" is a spelling mistake: a content-quality note, not a WCAG failure.
