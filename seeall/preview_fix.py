"""'Preview with fixes': recolour failing text pixels to their suggested colour."""
import numpy as np
from PIL import Image


def recolor_text_pixels(image, findings):
    """findings: dicts with box_px, text_rgb, bg_rgb, suggested_rgb. Within
    each box, pixels closer to the text cluster than the background cluster
    are repainted to suggested_rgb; everything else is untouched."""
    arr = np.array(image.convert("RGB")).astype(float)

    for f in findings:
        x0, y0, x1, y1 = f["box_px"]
        region = arr[y0:y1, x0:x1]
        if region.size == 0:
            continue
        text_rgb = np.array(f["text_rgb"], dtype=float)
        bg_rgb = np.array(f["bg_rgb"], dtype=float)
        new_rgb = np.array(f["suggested_rgb"], dtype=float)

        dist_text = np.linalg.norm(region - text_rgb, axis=-1)
        dist_bg = np.linalg.norm(region - bg_rgb, axis=-1)
        mask = dist_text < dist_bg
        region[mask] = new_rgb
        arr[y0:y1, x0:x1] = region

    return Image.fromarray(arr.astype(np.uint8))
