# Eval labels

One file per screenshot in eval/images, same file name with .md.
Each file lists:
- Real issues SeeAll should find (with WCAG id, level, severity, and whether a
  measured check or the AI should find it).
- Traps: things that look suspicious but should NOT be flagged (to measure
  false positives).
- An expected score band.

Contrast judgements marked "estimated" were made by eye from the screenshot.
Where SeeAll's measured ratio disagrees, trust the measurement and update the
label. Issues marked "cannot verify from screenshot" are listed for the
limitations slide and must not be counted as misses.
