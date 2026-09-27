from PIL import Image

from seeall.annotate import draw_boxes


def _group(severity="critical", source="measured", boxes=((10, 10, 40, 40),)):
    return {
        "severity": severity, "source": source,
        "instances": [{"box_px": b} for b in boxes],
    }


def test_draw_boxes_returns_same_size_image():
    img = Image.new("RGB", (100, 100), "white")
    out = draw_boxes(img, [_group()])
    assert out.size == (100, 100)


def test_draw_boxes_handles_multiple_instances_same_number():
    img = Image.new("RGB", (200, 200), "white")
    group = _group(boxes=((10, 10, 40, 40), (60, 60, 90, 90)))
    out = draw_boxes(img, [group])
    assert out.size == (200, 200)


def test_draw_boxes_handles_ai_source_dashed():
    img = Image.new("RGB", (100, 100), "white")
    out = draw_boxes(img, [_group(source="ai")])
    assert out.size == (100, 100)


def test_draw_boxes_empty_groups_no_crash():
    img = Image.new("RGB", (50, 50), "white")
    out = draw_boxes(img, [])
    assert out.size == (50, 50)


def test_draw_boxes_skips_instance_without_box():
    img = Image.new("RGB", (50, 50), "white")
    group = {"severity": "minor", "source": "measured", "instances": [{"box_px": None}]}
    out = draw_boxes(img, [group])
    assert out.size == (50, 50)
