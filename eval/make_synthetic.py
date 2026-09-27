"""Generate synthetic screenshots with known accessibility issues for eval."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).parent / "images"
OUT.mkdir(exist_ok=True)


def _font(size):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


def make_grey_on_white():
    img = Image.new("RGB", (400, 200), "white")
    d = ImageDraw.Draw(img)
    d.text((20, 80), "Low contrast text", font=_font(28), fill=(0x9E, 0x9E, 0x9E))
    img.save(OUT / "grey_on_white.png")


def make_tiny_text():
    img = Image.new("RGB", (400, 200), "white")
    d = ImageDraw.Draw(img)
    d.text((20, 90), "Tiny label text here", font=_font(10), fill=(0, 0, 0))
    img.save(OUT / "tiny_text.png")


def make_red_green_status():
    img = Image.new("RGB", (400, 200), "white")
    d = ImageDraw.Draw(img)
    d.ellipse((30, 80, 60, 110), fill=(200, 0, 0))
    d.ellipse((100, 80, 130, 110), fill=(0, 160, 0))
    d.text((20, 130), "Status", font=_font(20), fill=(0, 0, 0))
    img.save(OUT / "red_green_status.png")


def make_clean_screen(name, bg=(255, 255, 255), fg=(20, 20, 20)):
    img = Image.new("RGB", (400, 200), bg)
    d = ImageDraw.Draw(img)
    d.text((20, 80), "Clean readable text", font=_font(26), fill=fg)
    img.save(OUT / name)


if __name__ == "__main__":
    make_grey_on_white()
    make_tiny_text()
    make_red_green_status()
    make_clean_screen("clean_1.png")
    make_clean_screen("clean_2.png", bg=(15, 15, 20), fg=(240, 240, 240))

    expected = {
        "grey_on_white.png": {"contrast_issues": 1, "small_text_issues": 0},
        "tiny_text.png": {"contrast_issues": 0, "small_text_issues": 1},
        "red_green_status.png": {"contrast_issues": 0, "small_text_issues": 0, "color_only_issues": 1},
        "clean_1.png": {"contrast_issues": 0, "small_text_issues": 0},
        "clean_2.png": {"contrast_issues": 0, "small_text_issues": 0},
    }
    with open(Path(__file__).parent / "expected.json", "w") as f:
        json.dump(expected, f, indent=2)
    print("Synthetic images + expected.json written.")
