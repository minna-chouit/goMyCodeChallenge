"""WCAG 2.2 contrast math: relative luminance, contrast ratio, and a
nearest-passing-color suggestion via HSL lightness search."""
import colorsys


def _channel_luminance(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(rgb):
    r, g, b = rgb
    return 0.2126 * _channel_luminance(r) + 0.7152 * _channel_luminance(g) + 0.0722 * _channel_luminance(b)


def contrast_ratio(rgb1, rgb2):
    l1, l2 = relative_luminance(rgb1), relative_luminance(rgb2)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def required_ratio(font_size_px, bold=False):
    is_large = font_size_px >= 24 or (bold and font_size_px >= 18.66)
    return 3.0 if is_large else 4.5


def suggest_passing_color(text_rgb, bg_rgb, target_ratio):
    """Darken or lighten text_rgb (in HSL lightness) until it passes target_ratio
    against bg_rgb. Returns (hex, new_ratio) or None if no direction reaches it."""
    r, g, b = [c / 255.0 for c in text_rgb]
    h, l, s = colorsys.rgb_to_hls(r, g, b)[1], None, None
    h, orig_l, s = colorsys.rgb_to_hls(r, g, b)

    def ratio_at(lightness):
        rr, gg, bb = colorsys.hls_to_rgb(h, lightness, s)
        rgb = (rr * 255, gg * 255, bb * 255)
        return rgb, contrast_ratio(rgb, bg_rgb)

    bg_lum = relative_luminance(bg_rgb)
    directions = [-1, 1] if bg_lum > 0.5 else [1, -1]

    for direction in directions:
        lightness = orig_l
        for _ in range(100):
            lightness = max(0.0, min(1.0, lightness + direction * 0.01))
            rgb, ratio = ratio_at(lightness)
            if ratio >= target_ratio:
                hexcode = "#%02X%02X%02X" % tuple(round(c) for c in rgb)
                return hexcode, ratio
            if lightness in (0.0, 1.0):
                break
    return None


def css_snippet(text_hex, ratio, bg_rgb):
    bg_hex = "#%02X%02X%02X" % tuple(round(c) for c in bg_rgb)
    return f"color: {text_hex}; /* {ratio:.1f}:1 on {bg_hex} */"


def hex_to_rgb(hexcode):
    hexcode = hexcode.lstrip("#")
    return tuple(int(hexcode[i:i + 2], 16) for i in (0, 2, 4))


def required_ratio_aaa(font_size_px, bold=False):
    """WCAG 1.4.6 Contrast (Enhanced): 4.5:1 for large text, 7:1 otherwise."""
    is_large = font_size_px >= 24 or (bold and font_size_px >= 18.66)
    return 4.5 if is_large else 7.0
