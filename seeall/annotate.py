"""Draw numbered severity boxes on a copy of the screenshot."""
from PIL import Image, ImageDraw, ImageFont

_SEVERITY_COLOR = {
    "critical": (220, 38, 38),
    "serious": (217, 119, 6),
    "minor": (37, 99, 235),
}


def draw_boxes(image, issues):
    """issues: list of dicts with 'box_px' (x0,y0,x1,y1) and 'severity'."""
    img = image.convert("RGB").copy()
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 18)
    except OSError:
        font = ImageFont.load_default()

    for i, issue in enumerate(issues, start=1):
        x0, y0, x1, y1 = issue["box_px"]
        color = _SEVERITY_COLOR.get(issue.get("severity", "minor"), (37, 99, 235))
        draw.rectangle([x0, y0, x1, y1], outline=color, width=3)
        label = str(i)
        text_pos = (x0, max(y0 - 22, 0))
        text_bbox = draw.textbbox(text_pos, label, font=font)
        draw.rectangle(text_bbox, fill=color)
        draw.text(text_pos, label, fill=(255, 255, 255), font=font)
    return img
