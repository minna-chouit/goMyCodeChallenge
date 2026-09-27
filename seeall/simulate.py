"""Colour-blindness and low-vision simulation views.

Uses daltonlens when available; falls back to a Machado 2009 matrix
transform (same math daltonlens uses under the hood) if the import fails.
"""
import numpy as np
from PIL import Image, ImageFilter

_MACHADO_MATRICES = {
    "deuteranopia": np.array([
        [0.367, 0.861, -0.228],
        [0.280, 0.673, 0.047],
        [-0.012, 0.043, 0.969],
    ]),
    "protanopia": np.array([
        [0.152, 1.053, -0.205],
        [0.115, 0.786, 0.099],
        [-0.004, -0.048, 1.052],
    ]),
    "tritanopia": np.array([
        [1.256, -0.077, -0.179],
        [-0.078, 0.931, 0.148],
        [0.005, 0.691, 0.304],
    ]),
}


def _simulate_matrix(image, kind):
    arr = np.array(image.convert("RGB"), dtype=float) / 255.0
    matrix = _MACHADO_MATRICES[kind]
    simulated = arr @ matrix.T
    simulated = np.clip(simulated, 0, 1) * 255
    return Image.fromarray(simulated.astype(np.uint8))


def _achromatopsia(image):
    grey = image.convert("L").convert("RGB")
    return grey


def _low_vision(image):
    blurred = image.filter(ImageFilter.GaussianBlur(radius=3))
    arr = np.array(blurred, dtype=float)
    mean = arr.mean()
    arr = mean + (arr - mean) * 0.5  # reduce contrast
    arr = np.clip(arr, 0, 255)
    return Image.fromarray(arr.astype(np.uint8))


def simulate(image, kind):
    try:
        if kind in ("deuteranopia", "protanopia", "tritanopia"):
            from daltonlens import simulate as dl_simulate, convert
            simulator = dl_simulate.Simulator_Machado2009()
            deficiency = {
                "deuteranopia": dl_simulate.Deficiency.DEUTAN,
                "protanopia": dl_simulate.Deficiency.PROTAN,
                "tritanopia": dl_simulate.Deficiency.TRITAN,
            }[kind]
            arr = np.array(image.convert("RGB"))
            simulated = simulator.simulate_cvd(arr, deficiency, severity=1.0)
            return Image.fromarray(simulated)
    except Exception:
        pass

    if kind in _MACHADO_MATRICES:
        return _simulate_matrix(image, kind)
    if kind == "achromatopsia":
        return _achromatopsia(image)
    if kind == "low_vision":
        return _low_vision(image)
    raise ValueError(f"Unknown simulation kind: {kind}")


SIMULATION_KINDS = ["deuteranopia", "protanopia", "tritanopia", "achromatopsia", "low_vision"]
