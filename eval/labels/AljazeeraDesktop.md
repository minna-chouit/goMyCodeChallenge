# AljazeeraDesktop.png
Source: Al Jazeera Arabic homepage with live video and cookie banner. Device: desktop, 1x (1917 px).
Expected score: 60-75.

## Real issues
- 2.4.11 Focus Not Obscured, AA - serious - AI: the cookie banner covers the bottom of the page; items focused behind it would be hidden.
- 1.4.2 Audio Control / 2.2.2 Pause, Stop, Hide, A - minor - AI (needs human check): a live video plays with a moving news ticker; a pause button and volume icon are visible, which is good. Confirm it does not autoplay with sound.
- 1.4.3 Contrast (Minimum), AA - minor - measured: grey section headings (اختيارات المحررين, مقالات, مراسلو الجزيرة) on white (estimated borderline around 4.5:1).
- 1.1.1 Non-text Content / 4.1.2, A - minor - AI: search icon is icon-only; video controls (share, clock, fullscreen) are icon-only.
- Small text - minor - measured: small overlay text inside the video player ("More videos", timestamp).

## Should NOT be flagged
- Main nav items (black on white) with dropdown chevrons: pass.
- "تسجيل" white on black: pass.
- Cookie banner text (white on dark navy) and its underlined links: pass.
- "الآن" active tab uses an underline: not colour-only.
- Grey empty ad placeholder at the top: layout, not a WCAG failure.
