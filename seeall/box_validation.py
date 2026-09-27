"""Validate AI-returned boxes before they become issues: drop boxes outside
the image, too small to be a real UI element, or over near-uniform content
(the model hallucinating a box on empty space)."""
import numpy as np

MIN_BOX_SIZE = 8
_LOW_CONTENT_STD_THRESHOLD = 10.0


def is_valid_box(box_px, image_size):
    x0, y0, x1, y1 = box_px
    width_img, height_img = image_size
    if x0 < 0 or y0 < 0 or x1 > width_img or y1 > height_img:
        return False
    if (x1 - x0) < MIN_BOX_SIZE or (y1 - y0) < MIN_BOX_SIZE:
        return False
    return True


def is_low_content(image_array, box_px):
    """True if the region has near-zero variance (empty/flat area)."""
    x0, y0, x1, y1 = box_px
    region = image_array[max(y0, 0):max(y1, 1), max(x0, 0):max(x1, 1)]
    if region.size == 0:
        return True
    return float(np.std(region)) < _LOW_CONTENT_STD_THRESHOLD


def drop_invalid_ai_boxes(ai_issues, image):
    """Filters out AI issues whose box is outside the image, too small, or
    over a near-uniform/empty area (the model hallucinating a finding)."""
    image_array = np.array(image)
    image_size = image.size
    kept = []
    for issue in ai_issues:
        box_px = issue.get("box_px")
        if not box_px:
            continue
        if not is_valid_box(box_px, image_size):
            continue
        if is_low_content(image_array, box_px):
            continue
        kept.append(issue)
    return kept
