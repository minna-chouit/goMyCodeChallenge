# random_form_ui_mobile.jpg
Source: Maze sign-up form (design shot). Device: phone, likely 2x (736 px).
PRIVACY: a real-looking email address is visible in the field. Blur it before committing publicly.
Expected score: 60-75.

## Real issues
- 1.4.13 Content on Hover or Focus, AA / 2.4.11 Focus Not Obscured, AA - serious - AI: the password-rules tooltip covers the newsletter checkbox label and the main submit button's text. Users cannot see the primary action.
- 1.4.3 Contrast (Minimum), AA - serious - measured: green "Strong" text on white (estimated about 2.5:1).
- 1.4.11 Non-text Contrast, AA - minor - measured/AI: light green check icons in the tooltip are faint.
- 1.4.1 Use of Color, A - minor - AI: "Terms of Service" and "Log in" links are marked by blue colour only, no underline, inside dark text.

## Should NOT be flagged
- Visible labels above both fields (Email, Password): pass.
- Blue focus border on the password field: good visible focus.
- Password strength shown by word + bar (not colour alone): pass.
- "SIGN UP WITH GOOGLE" (blue on white, with text): pass.
