from PIL import Image

from seeall.thumbnail import crop_thumbnail


def test_crop_returns_image_of_expected_region():
    img = Image.new("RGB", (100, 100), "white")
    thumb = crop_thumbnail(img, (10, 10, 30, 30), padding=5)
    assert thumb.size == (30, 30)  # (30-10)+2*5 each side


def test_crop_clamps_to_image_bounds():
    img = Image.new("RGB", (50, 50), "white")
    thumb = crop_thumbnail(img, (0, 0, 10, 10), padding=20)
    assert thumb.size[0] <= 50 and thumb.size[1] <= 50


def test_crop_handles_box_at_edge():
    img = Image.new("RGB", (100, 100), "white")
    thumb = crop_thumbnail(img, (90, 90, 100, 100), padding=5)
    assert thumb.size[0] > 0 and thumb.size[1] > 0
