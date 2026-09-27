# oudknisProductDetails2Desktop.png
Source: Ouedkniss car ad details table, Arabic RTL, dark theme. Device: desktop, 1x (1890 px).
Expected score: 80-95 (mostly clean; useful as an Arabic control screen).

## Real issues
- 1.4.3 Contrast (Minimum), AA - minor - measured: the small grey "وصف" (Description) label on dark grey (estimated borderline).
- Readability - minor - AI (advisory, not a strict WCAG failure): labels on the right and values in the middle are ~800 px apart; low-vision users with magnification lose track of which value belongs to which label. Suggest placing values closer.

## Should NOT be flagged
- All label/value rows (white on dark grey): pass.
- Faint row dividers: decorative, no contrast requirement.

## Notes
- Cannot verify from screenshot: whether this is marked up as a real table (1.3.1) and the language of mixed Arabic / Latin / Darija text ("Voiture jdida") (3.1.2).
- OCR test: Arabic text and mixed direction values like "1700كم".
