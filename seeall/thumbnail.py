"""Crop a padded thumbnail of an issue's box, clamped to image bounds."""


def crop_thumbnail(image, box_px, padding=10):
    x0, y0, x1, y1 = box_px
    width, height = image.size
    x0 = max(0, x0 - padding)
    y0 = max(0, y0 - padding)
    x1 = min(width, x1 + padding)
    y1 = min(height, y1 + padding)
    return image.crop((x0, y0, x1, y1))
