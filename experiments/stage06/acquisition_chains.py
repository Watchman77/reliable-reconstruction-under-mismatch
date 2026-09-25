"""Frozen-candidate acquisition chains for Stage 06 development.

All arrays use float RGB in [0, 1]. The alternate chain applies blur and noise
in linear light before the sRGB camera-response/tone map and JPEG encoding.
"""

from __future__ import annotations

import io
from dataclasses import asdict, dataclass

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter


@dataclass(frozen=True)
class ChainConfig:
    chain_id: str
    operator_domain: str
    blur_sigma: float
    noise_std: float
    jpeg_quality: int
    jpeg_subsampling: int = 0

    def validate(self) -> None:
        if self.operator_domain not in {"srgb", "linear_rgb"}:
            raise ValueError(f"Unsupported operator domain: {self.operator_domain}")
        if self.blur_sigma < 0 or self.noise_std < 0:
            raise ValueError("blur_sigma and noise_std must be non-negative")
        if not 1 <= self.jpeg_quality <= 100:
            raise ValueError("jpeg_quality must lie in [1, 100]")
        if self.jpeg_subsampling not in {0, 1, 2}:
            raise ValueError("jpeg_subsampling must be 0, 1, or 2")


def _validate_image(image: np.ndarray) -> np.ndarray:
    array = np.asarray(image, dtype=np.float64)
    if array.ndim != 3 or array.shape[2] != 3:
        raise ValueError(f"Expected HxWx3 RGB array, got {array.shape}")
    if not np.isfinite(array).all() or array.min() < 0 or array.max() > 1:
        raise ValueError("RGB values must be finite and lie in [0, 1]")
    return array


def srgb_to_linear(image: np.ndarray) -> np.ndarray:
    image = _validate_image(image)
    return np.where(image <= 0.04045, image / 12.92, ((image + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(image: np.ndarray) -> np.ndarray:
    image = np.clip(np.asarray(image, dtype=np.float64), 0.0, 1.0)
    return np.where(image <= 0.0031308, 12.92 * image, 1.055 * image ** (1 / 2.4) - 0.055)


def blur_rgb(image: np.ndarray, sigma: float) -> np.ndarray:
    image = _validate_image(image)
    if sigma == 0:
        return image.copy()
    return gaussian_filter(image, sigma=(sigma, sigma, 0), mode="reflect")


def jpeg_roundtrip(image: np.ndarray, quality: int, subsampling: int) -> np.ndarray:
    image = _validate_image(image)
    encoded = Image.fromarray(np.rint(image * 255).astype(np.uint8), mode="RGB")
    payload = io.BytesIO()
    encoded.save(payload, format="JPEG", quality=quality, subsampling=subsampling, optimize=False)
    payload.seek(0)
    with Image.open(payload) as decoded:
        decoded.load()
        return np.asarray(decoded.convert("RGB"), dtype=np.float64) / 255.0


def simulate_observation(reference_srgb: np.ndarray, config: ChainConfig, seed: int) -> tuple[np.ndarray, dict[str, object]]:
    """Apply one chain with deterministic noise and return observation + receipt."""
    config.validate()
    reference_srgb = _validate_image(reference_srgb)
    rng = np.random.default_rng(seed)
    if config.operator_domain == "linear_rgb":
        working = srgb_to_linear(reference_srgb)
        working = blur_rgb(working, config.blur_sigma)
        working = np.clip(working + config.noise_std * rng.standard_normal(working.shape), 0.0, 1.0)
        pre_codec = linear_to_srgb(working)
    else:
        working = blur_rgb(reference_srgb, config.blur_sigma)
        pre_codec = np.clip(working + config.noise_std * rng.standard_normal(working.shape), 0.0, 1.0)
    observation = jpeg_roundtrip(pre_codec, config.jpeg_quality, config.jpeg_subsampling)
    receipt = {
        **asdict(config),
        "seed": int(seed),
        "input_shape": list(reference_srgb.shape),
        "input_dtype": str(reference_srgb.dtype),
        "output_dtype": str(observation.dtype),
        "stage_order": (
            ["srgb_to_linear", "gaussian_blur", "linear_gaussian_noise", "linear_to_srgb", "jpeg"]
            if config.operator_domain == "linear_rgb"
            else ["gaussian_blur", "srgb_gaussian_noise", "jpeg"]
        ),
    }
    return observation, receipt


STAGE06_DEVELOPMENT_CHAINS = {
    "srgb_j75_b16_n2": ChainConfig(
        chain_id="srgb_j75_b16_n2",
        operator_domain="srgb",
        blur_sigma=1.6,
        noise_std=2 / 255,
        jpeg_quality=75,
    ),
    "linear_j75_b16_n2": ChainConfig(
        chain_id="linear_j75_b16_n2",
        operator_domain="linear_rgb",
        blur_sigma=1.6,
        noise_std=2 / 255,
        jpeg_quality=75,
    ),
}

