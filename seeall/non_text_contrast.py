"""WCAG 1.4.11 Non-text Contrast (estimated): sample a thin ring just
outside each OCR text box (a proxy for an input/button boundary) against a
further-out background ring, and flag boundaries under 3:1. This is a
rough estimate from a screenshot, not a real border detector — every
finding is labelled 'measured (estimated region)'."""
import numpy as np

from .contrast import contrast_ratio, required_ratio

_RING_WIDTH = 2
_RING_GAP = 3
_NON_TEXT_REQUIRED_RATIO = 3.0


def _ring_mean_color(image_array, box_px, inner_offset, outer_offset):
    x0, y0, x1, y1 = box_px
    height, width = image_array.shape[:2]
    ox0 = max(0, x0 - outer_offset)
    oy0 = max(0, y0 - outer_offset)
    ox1 = min(width, x1 + outer_offset)
    oy1 = min(height, y1 + outer_offset)
    ix0 = max(0, x0 - inner_offset)
    iy0 = max(0, y0 - inner_offset)
    ix1 = min(width, x1 + inner_offset)
    iy1 = min(height, y1 + inner_offset)

    outer = image_array[oy0:oy1, ox0:ox1]
    if outer.size == 0:
        return None
    mask = np.ones(outer.shape[:2], dtype=bool)
    iy0_rel, ix0_rel = iy0 - oy0, ix0 - ox0
    iy1_rel, ix1_rel = iy1 - oy0, ix1 - ox0
    mask[max(iy0_rel, 0):iy1_rel, max(ix0_rel, 0):ix1_rel] = False
    ring_pixels = outer[mask]
    if ring_pixels.size == 0:
        return None
    return ring_pixels.reshape(-1, outer.shape[-1]).mean(axis=0)


def check_non_text_contrast(image, findings):
    """findings: OCR raw findings with box_px. Returns a list of issue-shaped
    dicts for boundaries estimated under 3:1."""
    arr = np.array(image.convert("RGB"))
    results = []
    for f in findings:
        box_px = f.get("box_px")
        if not box_px:
            continue
        border_color = _ring_mean_color(arr, box_px, _RING_GAP, _RING_GAP + _RING_WIDTH)
        background_color = _ring_mean_color(arr, box_px, _RING_GAP + _RING_WIDTH, _RING_GAP + _RING_WIDTH * 4)
        if border_color is None or background_color is None:
            continue
        ratio = contrast_ratio(tuple(border_color), tuple(background_color))
        if ratio < _NON_TEXT_REQUIRED_RATIO:
            results.append({
                "type": "non_text_contrast",
                "severity": "minor",
                "box": None,
                "box_px": box_px,
                "description": (
                    f"The boundary around \"{f.get('text', 'this element')}\" is estimated at "
                    f"{ratio:.1f}:1 contrast, below the required {_NON_TEXT_REQUIRED_RATIO}:1 "
                    "(measured (estimated region))."
                ),
                "affected_users": "Users with low vision who rely on visible input/button boundaries.",
                "fix": "Increase the border or edge contrast to at least 3:1 against its surroundings.",
                "confidence": 1.0,
                "source": "measured",
            })
    return results
