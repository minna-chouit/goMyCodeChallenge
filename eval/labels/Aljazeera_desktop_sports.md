# Aljazeera_desktop_sports.png
Source: Al Jazeera Arabic, sports section (articles + newsletter box). Device: desktop, 1x (1660 px).
Expected score: 80-95 (mostly clean; good Arabic control screen).

## Real issues
- 3.3.8 Accessible Authentication, AA - minor - AI (needs human check): newsletter form is protected by reCAPTCHA; fine if invisible, a problem if it shows an image puzzle.
- Small text - minor - measured: "محمي بخدمة reCAPTCHA" is very small.
- 1.1.1 Non-text Content, A - minor - AI: news photos need descriptive alt text (cannot verify markup; suggest alt text).

## Should NOT be flagged
- Email field has a visible label ("البريد الإلكتروني"): pass.
- "اشترك الآن" white on black: pass.
- Privacy policy link is underlined: pass.
- Headlines black on white, summaries dark grey on white: pass.
- Blue bar above the newsletter card: decorative.
