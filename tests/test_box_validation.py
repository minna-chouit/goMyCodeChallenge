import numpy as np
from PIL import Image

from seeall.box_validation import is_valid_box, is_low_content, drop_invalid_ai_boxes


def test_box_within_bounds_and_size_is_valid():
    assert is_valid_box((10, 10, 30, 30), (100, 100)) is True


def test_box_outside_image_bounds_is_invalid():
    assert is_valid_box((90, 90, 150, 150), (100, 100)) is False


def test_box_with_negative_coords_is_invalid():
    assert is_valid_box((-5, -5, 20, 20), (100, 100)) is False


def test_box_too_small_is_invalid():
    assert is_valid_box((10, 10, 15, 15), (100, 100)) is False  # 5x5 < 8x8


def test_box_exactly_8x8_is_valid():
    assert is_valid_box((10, 10, 18, 18), (100, 100)) is True


def test_uniform_flat_region_is_low_content():
    arr = np.full((50, 50, 3), 200, dtype=np.uint8)
    assert is_low_content(arr, (5, 5, 25, 25)) is True


def test_region_with_variation_is_not_low_content():
    arr = np.zeros((50, 50, 3), dtype=np.uint8)
    arr[10:20, 10:20] = 255  # a sharp block of contrast inside the region
    assert is_low_content(arr, (0, 0, 30, 30)) is False


def _flat_image_with_content_block():
    img = Image.new("RGB", (100, 100), (255, 255, 255))
    for x in range(10, 30):
        for y in range(10, 30):
            img.putpixel((x, y), (0, 0, 0))
    return img


def test_drop_invalid_ai_boxes_removes_out_of_bounds():
    img = _flat_image_with_content_block()
    issues = [{"box_px": (90, 90, 150, 150)}]
    assert drop_invalid_ai_boxes(issues, img) == []


def test_drop_invalid_ai_boxes_removes_tiny_box():
    img = _flat_image_with_content_block()
    issues = [{"box_px": (12, 12, 15, 15)}]
    assert drop_invalid_ai_boxes(issues, img) == []


def test_drop_invalid_ai_boxes_removes_empty_area():
    img = _flat_image_with_content_block()
    issues = [{"box_px": (50, 50, 70, 70)}]  # flat white area, no content
    assert drop_invalid_ai_boxes(issues, img) == []


def test_drop_invalid_ai_boxes_keeps_valid_content_box():
    img = _flat_image_with_content_block()
    issues = [{"box_px": (5, 5, 35, 35)}]  # spans both black block and white background
    assert len(drop_invalid_ai_boxes(issues, img)) == 1
