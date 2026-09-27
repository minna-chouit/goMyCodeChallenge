"""Pick which demo image the 'Try an example screen' button loads."""

_PREFERRED = "grey_on_white.png"


def pick_example_image(demo_image_names):
    if not demo_image_names:
        return None
    if _PREFERRED in demo_image_names:
        return _PREFERRED
    return demo_image_names[0]
