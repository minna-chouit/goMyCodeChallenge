# bookingDotCom_desktop_sign_up_error.png
Source: Booking.com sign-in with an invalid email ("hhhh"). Device: desktop, 1x (1892 px).
Expected score: 75-90 (should be about the same as the no-error version; a well-built error must not lower the score).

## Real issues
- Same as bookingDotCom_desktop_sign_up.md: logo-only social buttons (serious), faint social button borders (minor), icon-only flag and help icons (minor).
- 3.3.3 Error Suggestion, AA - minor - AI (advisory): message "Make sure the email address you entered is correct" is generic; better: "Email address needs an @, e.g. name@example.com".

## Should NOT be flagged
- The error itself: shown with red border + icon + text, so NOT colour-only (1.4.1 pass) and identified in text (3.3.1 pass).
- Red error text on white: likely passes 4.5:1.
- "hhhh" typed value: user input, not a design issue.
