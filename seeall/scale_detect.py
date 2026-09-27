"""Auto-detect a screenshot's CSS-px scale (1x/2x/3x) from its pixel width."""
from dataclasses import dataclass

_2X_WIDTHS = {750, 828}
_3X_WIDTHS = {1080, 1125, 1170, 1179, 1284, 1290}


@dataclass
class ScaleDetection:
    scale: int
    label: str
    confident: bool


def detect_scale(width_px):
    if width_px < 500:
        return ScaleDetection(1, f"phone, {width_px} px", True)
    if width_px > 1300:
        return ScaleDetection(1, f"desktop, {width_px} px", True)
    if width_px in _2X_WIDTHS:
        return ScaleDetection(2, f"phone, {width_px} px", True)
    if width_px in _3X_WIDTHS:
        return ScaleDetection(3, f"phone, {width_px} px", True)
    return ScaleDetection(2, f"uncertain, {width_px} px", False)
