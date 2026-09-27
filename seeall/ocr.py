"""Deterministic text checks: OCR text boxes, 2-means text/background color
split, WCAG contrast, and small-text flagging."""
import numpy as np
from .contrast import contrast_ratio, required_ratio, suggest_passing_color

_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        from rapidocr_onnxruntime import RapidOCR
        _engine = RapidOCR()
    return _engine


def _kmeans2(pixels, iters=10):
    """pixels: (N,3) float array. Returns (centers(2,3), labels(N,))."""
    rng = np.random.default_rng(0)
    lo, hi = pixels.min(0), pixels.max(0)
    centers = np.array([lo, hi], dtype=float)
    labels = np.zeros(len(pixels), dtype=int)
    for _ in range(iters):
        dists = ((pixels[:, None, :] - centers[None, :, :]) ** 2).sum(-1)
        labels = dists.argmin(1)
        for k in (0, 1):
            mask = labels == k
            if mask.any():
                centers[k] = pixels[mask].mean(0)
    return centers, labels


def _box_bounds(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)


def analyze_text_boxes(image, scale):
    """image: PIL.Image (RGB). scale: device pixel ratio (1, 2, or 3).
    Returns a list of finding dicts, one per OCR text box."""
    arr = np.array(image.convert("RGB"))
    engine = _get_engine()
    result, _ = engine(arr)
    findings = []
    if not result:
        return findings

    for points, text, score in result:
        x0, y0, x1, y1 = _box_bounds(points)
        x0i, y0i, x1i, y1i = int(x0), int(y0), int(x1), int(y1)
        crop = arr[max(y0i, 0):max(y1i, 1), max(x0i, 0):max(x1i, 1)]
        if crop.size == 0:
            continue
        pixels = crop.reshape(-1, 3).astype(float)
        centers, labels = _kmeans2(pixels)
        counts = np.bincount(labels, minlength=2)
        text_idx = counts.argmin()
        bg_idx = 1 - text_idx
        text_rgb = tuple(centers[text_idx])
        bg_rgb = tuple(centers[bg_idx])

        css_height = (y1i - y0i) / scale
        font_size_css = css_height * 0.75  # cap-height-to-font-size approximation
        ratio = contrast_ratio(text_rgb, bg_rgb)
        req = required_ratio(font_size_css)
        passes = ratio >= req

        finding = {
            "text": text,
            "box_px": (x0i, y0i, x1i, y1i),
            "font_size_css": round(font_size_css, 1),
            "text_rgb": tuple(round(c) for c in text_rgb),
            "bg_rgb": tuple(round(c) for c in bg_rgb),
            "contrast_ratio": round(ratio, 2),
            "required_ratio": req,
            "contrast_passes": passes,
            "small_text": font_size_css < 12,
        }
        if not passes:
            suggestion = suggest_passing_color(text_rgb, bg_rgb, req)
            if suggestion:
                finding["suggested_hex"], finding["suggested_ratio"] = suggestion
                finding["suggested_ratio"] = round(finding["suggested_ratio"], 2)
        findings.append(finding)
    return findings
