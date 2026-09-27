import numpy as np
from PIL import Image

from seeall.preview_fix import recolor_text_pixels


def test_recolor_changes_text_pixels_not_background():
    img = Image.new("RGB", (20, 20), (255, 255, 255))
    arr = np.array(img)
    arr[5:15, 5:15] = (200, 200, 200)  # a grey "text" block on white bg
    img = Image.fromarray(arr)

    finding = {
        "box_px": (0, 0, 20, 20),
        "text_rgb": (200, 200, 200),
        "bg_rgb": (255, 255, 255),
        "suggested_rgb": (0, 0, 0),
    }
    out = recolor_text_pixels(img, [finding])
    out_arr = np.array(out)
    assert tuple(out_arr[10, 10]) == (0, 0, 0)  # was grey text -> now black
    assert tuple(out_arr[1, 1]) == (255, 255, 255)  # background unchanged


def test_recolor_leaves_image_unchanged_with_no_findings():
    img = Image.new("RGB", (10, 10), "white")
    out = recolor_text_pixels(img, [])
    assert np.array_equal(np.array(img), np.array(out))


def test_recolor_only_affects_box_region():
    img = Image.new("RGB", (20, 20), (255, 255, 255))
    arr = np.array(img)
    arr[2:8, 2:8] = (200, 200, 200)
    img = Image.fromarray(arr)
    finding = {
        "box_px": (0, 0, 10, 10), "text_rgb": (200, 200, 200),
        "bg_rgb": (255, 255, 255), "suggested_rgb": (0, 0, 0),
    }
    out = recolor_text_pixels(img, [finding])
    out_arr = np.array(out)
    assert tuple(out_arr[15, 15]) == (255, 255, 255)  # outside box untouched
