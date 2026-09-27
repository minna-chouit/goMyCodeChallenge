"""Draw numbered severity boxes on a copy of the screenshot, one number per
grouped issue, repeated on every instance."""
from PIL import Image, ImageDraw, ImageFont

_SEVERITY_COLOR = {
    "critical": (220, 38, 38),   # red
    "serious": (217, 119, 6),    # orange
    "minor": (202, 138, 4),      # yellow (darkened for legibility)
}


def _dashed_rectangle(draw, box, color, width=3, dash=6, gap=4):
    x0, y0, x1, y1 = box
    edges = [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))]
    for (sx, sy), (ex, ey) in edges:
        length = max(abs(ex - sx), abs(ey - sy))
        steps = max(1, int(length / (dash + gap)))
        for i in range(steps + 1):
            t0 = i * (dash + gap) / max(length, 1)
            t1 = min(1.0, t0 + dash / max(length, 1))
            px0 = sx + (ex - sx) * t0
            py0 = sy + (ey - sy) * t0
            px1 = sx + (ex - sx) * t1
            py1 = sy + (ey - sy) * t1
            draw.line([(px0, py0), (px1, py1)], fill=color, width=width)


def draw_boxes(image, grouped_issues):
    """grouped_issues: list of groups (see group_issues.group_issues), each
    with 'severity', 'source', and 'instances' (each with 'box_px')."""
    img = image.convert("RGB").copy()
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except OSError:
        font = ImageFont.load_default()

    for i, group in enumerate(grouped_issues, start=1):
        color = _SEVERITY_COLOR.get(group.get("severity", "minor"), (37, 99, 235))
        is_measured = group.get("source", "") == "measured" or "measured" in group.get("source", "")
        for instance in group["instances"]:
            box_px = instance.get("box_px")
            if not box_px:
                continue
            x0, y0, x1, y1 = box_px
            if is_measured:
                draw.rectangle([x0, y0, x1, y1], outline=color, width=3)
            else:
                _dashed_rectangle(draw, (x0, y0, x1, y1), color, width=3)

            label = str(i)
            text_bbox = draw.textbbox((0, 0), label, font=font)
            badge_w = max(24, text_bbox[2] - text_bbox[0] + 12)
            badge_h = max(24, text_bbox[3] - text_bbox[1] + 10)
            badge_x0, badge_y0 = x0, max(y0 - badge_h - 2, 0)
            draw.ellipse(
                [badge_x0, badge_y0, badge_x0 + badge_h, badge_y0 + badge_h],
                fill=color,
            )
            draw.text(
                (badge_x0 + badge_h / 2, badge_y0 + badge_h / 2), label,
                fill=(255, 255, 255), font=font, anchor="mm",
            )
    return img
