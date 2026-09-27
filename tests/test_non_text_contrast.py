import numpy as np
from PIL import Image

from seeall.non_text_contrast import check_non_text_contrast

# Ring geometry must match seeall.non_text_contrast's constants:
# border ring = box expanded by 3..5px, background ring = box expanded by 5..11px.
_BOX = (30, 30, 90, 50)


def _image_with_box_border(border_rgb, outside_rgb):
    arr = np.full((80, 120, 3), outside_rgb, dtype=np.uint8)
    arr[25:55, 25:95] = border_rgb          # sits in the 3..5px ring around _BOX
    arr[27:53, 27:93] = (255, 255, 255)     # input interior, inside _BOX
    return Image.fromarray(arr)


def test_low_contrast_border_is_flagged():
    img = _image_with_box_border((235, 235, 235), (255, 255, 255))
    findings = [{"box_px": _BOX, "text": "Enter name"}]
    result = check_non_text_contrast(img, findings)
    assert len(result) == 1
    assert result[0]["type"] == "non_text_contrast"


def test_high_contrast_border_is_not_flagged():
    img = _image_with_box_border((0, 0, 0), (255, 255, 255))
    findings = [{"box_px": _BOX, "text": "Enter name"}]
    result = check_non_text_contrast(img, findings)
    assert result == []


def test_marks_estimated_region():
    img = _image_with_box_border((235, 235, 235), (255, 255, 255))
    findings = [{"box_px": _BOX, "text": "Enter name"}]
    result = check_non_text_contrast(img, findings)
    assert "estimated region" in result[0]["description"].lower()
