#!/usr/bin/env python3
"""Reproducible Phase-0 canary for compound forward-model mismatch.

The script intentionally uses only NumPy, SciPy, Pillow and pandas so the
acquisition and evaluation plumbing can be validated before GPU baselines are
introduced. It is not the proposed journal method.
"""

from __future__ import annotations

import argparse
import io
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw
from scipy import ndimage, signal, stats


@dataclass(frozen=True)
class Acquisition:
    blur_type: str
    blur_length: int
    blur_angle_deg: float
    gaussian_sigma: float
    photons: float
    read_noise_std: float
    downsample_factor: int
    jpeg_quality: int


@dataclass(frozen=True)
class AssumedOperator:
    label: str
    blur_type: str
    blur_length: int
    blur_angle_deg: float
    gaussian_sigma: float
    wiener_balance: float


TRUE_ACQUISITIONS = {
    "blur_only": Acquisition(
        blur_type="motion",
        blur_length=15,
        blur_angle_deg=24.0,
        gaussian_sigma=0.0,
        photons=0.0,
        read_noise_std=0.0,
        downsample_factor=1,
        jpeg_quality=100,
    ),
    "compound": Acquisition(
        blur_type="motion",
        blur_length=15,
        blur_angle_deg=24.0,
        gaussian_sigma=0.0,
        photons=45.0,
        read_noise_std=0.012,
        downsample_factor=2,
        jpeg_quality=32,
    ),
}


ASSUMPTIONS = (
    AssumedOperator("blur_matched", "motion", 15, 24.0, 0.0, 0.006),
    AssumedOperator("mild", "motion", 13, 18.0, 0.0, 0.006),
    AssumedOperator("moderate", "motion", 9, 5.0, 0.0, 0.006),
    AssumedOperator("severe", "gaussian", 0, 0.0, 2.2, 0.006),
)


def synthetic_image(size: int = 256) -> np.ndarray:
    """Create a deterministic image containing edges and smooth structure."""
    yy, xx = np.mgrid[0:size, 0:size]
    base = np.zeros((size, size, 3), dtype=np.float32)
    base[..., 0] = 0.12 + 0.72 * (xx / (size - 1))
    base[..., 1] = 0.10 + 0.68 * (yy / (size - 1))
    base[..., 2] = 0.18 + 0.32 * np.sin(xx / 13.0) * np.cos(yy / 17.0)
    image = Image.fromarray(np.uint8(np.clip(base, 0, 1) * 255), "RGB")
    draw = ImageDraw.Draw(image)
    draw.rectangle((24, 30, 108, 112), outline=(250, 250, 250), width=5)
    draw.ellipse((142, 34, 226, 118), fill=(225, 55, 35), outline=(255, 245, 210), width=4)
    draw.polygon([(50, 210), (100, 132), (150, 210)], fill=(25, 210, 115))
    draw.line((15, 235, 240, 140), fill=(250, 235, 30), width=5)
    for i in range(8):
        x0 = 166 + (i % 4) * 18
        y0 = 150 + (i // 4) * 25
        draw.rectangle((x0, y0, x0 + 9, y0 + 9), fill=(20, 20, 20) if i % 2 else (245, 245, 245))
    return np.asarray(image, dtype=np.float32) / 255.0


def load_images(input_dir: Path | None, size: int = 256) -> list[tuple[str, np.ndarray]]:
    if input_dir is None:
        return [("synthetic_000", synthetic_image(size))]
    records: list[tuple[str, np.ndarray]] = []
    for path in sorted(input_dir.iterdir()):
        if path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}:
            continue
        image = Image.open(path).convert("RGB")
        image.thumbnail((size, size), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (size, size), (0, 0, 0))
        canvas.paste(image, ((size - image.width) // 2, (size - image.height) // 2))
        records.append((path.stem, np.asarray(canvas, dtype=np.float32) / 255.0))
    if not records:
        raise ValueError(f"No supported images found in {input_dir}")
    return records


def motion_kernel(length: int, angle_deg: float) -> np.ndarray:
    size = max(3, int(length) | 1)
    kernel = np.zeros((size, size), dtype=np.float32)
    centre = (size - 1) / 2.0
    angle = math.radians(angle_deg)
    half = (length - 1) / 2.0
    samples = max(4 * length, 16)
    for t in np.linspace(-half, half, samples):
        x = centre + t * math.cos(angle)
        y = centre + t * math.sin(angle)
        x0, y0 = int(math.floor(x)), int(math.floor(y))
        dx, dy = x - x0, y - y0
        for ix, wx in ((x0, 1 - dx), (x0 + 1, dx)):
            for iy, wy in ((y0, 1 - dy), (y0 + 1, dy)):
                if 0 <= ix < size and 0 <= iy < size:
                    kernel[iy, ix] += wx * wy
    kernel /= kernel.sum()
    return kernel


def gaussian_kernel(sigma: float) -> np.ndarray:
    radius = max(2, int(math.ceil(3 * sigma)))
    axis = np.arange(-radius, radius + 1, dtype=np.float32)
    kernel = np.exp(-(axis[:, None] ** 2 + axis[None, :] ** 2) / (2 * sigma**2))
    return kernel / kernel.sum()


def kernel_from_spec(blur_type: str, length: int, angle: float, sigma: float) -> np.ndarray:
    if blur_type == "motion":
        return motion_kernel(length, angle)
    if blur_type == "gaussian":
        return gaussian_kernel(sigma)
    raise ValueError(f"Unsupported blur type: {blur_type}")


def convolve_rgb(image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    return np.stack(
        [signal.fftconvolve(image[..., c], kernel, mode="same") for c in range(3)], axis=-1
    ).astype(np.float32)


def jpeg_roundtrip(image: np.ndarray, quality: int) -> np.ndarray:
    buffer = io.BytesIO()
    Image.fromarray(np.uint8(np.clip(image, 0, 1) * 255), "RGB").save(
        buffer, format="JPEG", quality=quality, subsampling=2
    )
    buffer.seek(0)
    return np.asarray(Image.open(buffer).convert("RGB"), dtype=np.float32) / 255.0


def degrade(image: np.ndarray, cfg: Acquisition, rng: np.random.Generator) -> np.ndarray:
    kernel = kernel_from_spec(cfg.blur_type, cfg.blur_length, cfg.blur_angle_deg, cfg.gaussian_sigma)
    observed = np.clip(convolve_rgb(image, kernel), 0, 1)
    if cfg.photons > 0:
        observed = rng.poisson(observed * cfg.photons).astype(np.float32) / cfg.photons
    if cfg.read_noise_std > 0:
        observed += rng.normal(0.0, cfg.read_noise_std, observed.shape).astype(np.float32)
    observed = np.clip(observed, 0, 1)
    if cfg.downsample_factor > 1:
        height, width = observed.shape[:2]
        small = Image.fromarray(np.uint8(observed * 255), "RGB").resize(
            (width // cfg.downsample_factor, height // cfg.downsample_factor), Image.Resampling.BICUBIC
        )
        observed = np.asarray(
            small.resize((width, height), Image.Resampling.BICUBIC), dtype=np.float32
        ) / 255.0
    return jpeg_roundtrip(observed, cfg.jpeg_quality) if cfg.jpeg_quality < 100 else observed


def pad_and_shift_kernel(kernel: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    padded = np.zeros(shape, dtype=np.float32)
    kh, kw = kernel.shape
    padded[:kh, :kw] = kernel
    return np.roll(padded, shift=(-(kh // 2), -(kw // 2)), axis=(0, 1))


def wiener_deconvolution(observed: np.ndarray, kernel: np.ndarray, balance: float) -> np.ndarray:
    transfer = np.fft.fft2(pad_and_shift_kernel(kernel, observed.shape[:2]))
    denominator = np.abs(transfer) ** 2 + balance
    channels = []
    for c in range(3):
        spectrum = np.fft.fft2(observed[..., c])
        restored = np.fft.ifft2(np.conj(transfer) * spectrum / denominator).real
        channels.append(restored)
    return np.clip(np.stack(channels, axis=-1), 0, 1).astype(np.float32)


def psnr(reference: np.ndarray, estimate: np.ndarray) -> float:
    mse = float(np.mean((reference - estimate) ** 2))
    return float("inf") if mse == 0 else 10.0 * math.log10(1.0 / mse)


def ssim(reference: np.ndarray, estimate: np.ndarray) -> float:
    """Mean channel SSIM using a Gaussian local window."""
    values = []
    c1, c2 = 0.01**2, 0.03**2
    for channel in range(3):
        x, y = reference[..., channel], estimate[..., channel]
        mux = ndimage.gaussian_filter(x, 1.5)
        muy = ndimage.gaussian_filter(y, 1.5)
        sigx = ndimage.gaussian_filter(x * x, 1.5) - mux * mux
        sigy = ndimage.gaussian_filter(y * y, 1.5) - muy * muy
        sigxy = ndimage.gaussian_filter(x * y, 1.5) - mux * muy
        score = ((2 * mux * muy + c1) * (2 * sigxy + c2)) / (
            (mux * mux + muy * muy + c1) * (sigx + sigy + c2)
        )
        values.append(float(np.mean(score)))
    return float(np.mean(values))


def normalized_residual(observed: np.ndarray, estimate: np.ndarray, assumed_kernel: np.ndarray) -> float:
    predicted = np.clip(convolve_rgb(estimate, assumed_kernel), 0, 1)
    numerator = np.linalg.norm(predicted - observed)
    denominator = np.linalg.norm(observed) + 1e-12
    return float(numerator / denominator)


def edge_error(reference: np.ndarray, estimate: np.ndarray) -> float:
    ref_gray = reference.mean(axis=2)
    est_gray = estimate.mean(axis=2)
    ref_edge = np.hypot(ndimage.sobel(ref_gray, 0), ndimage.sobel(ref_gray, 1))
    est_edge = np.hypot(ndimage.sobel(est_gray, 0), ndimage.sobel(est_gray, 1))
    return float(np.mean(np.abs(ref_edge - est_edge)))


def comparison_panel(reference: np.ndarray, observed: np.ndarray, reconstructions: list[np.ndarray]) -> Image.Image:
    images = [reference, observed, *reconstructions]
    labels = ["Reference", "Observed", *[s.label.title() for s in ASSUMPTIONS]]
    tile_size = reference.shape[0]
    panel = Image.new("RGB", (tile_size * len(images), tile_size + 28), "white")
    draw = ImageDraw.Draw(panel)
    for index, (array, label) in enumerate(zip(images, labels)):
        tile = Image.fromarray(np.uint8(np.clip(array, 0, 1) * 255), "RGB")
        panel.paste(tile, (index * tile_size, 28))
        draw.text((index * tile_size + 6, 7), label, fill="black")
    return panel


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/canary"))
    parser.add_argument("--seed", type=int, default=20260915)
    parser.add_argument("--size", type=int, default=256)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, object]] = []
    manifest: dict[str, object] = {
        "seed": args.seed,
        "true_acquisitions": {name: asdict(cfg) for name, cfg in TRUE_ACQUISITIONS.items()},
        "assumed_operators": [asdict(item) for item in ASSUMPTIONS],
        "sources": [],
    }

    for image_index, (source_id, reference) in enumerate(load_images(args.input_dir, args.size)):
        image_seed = args.seed + image_index
        manifest["sources"].append({"source_id": source_id, "seed": image_seed})
        for condition, acquisition in TRUE_ACQUISITIONS.items():
            observed = degrade(reference, acquisition, np.random.default_rng(image_seed))
            reconstructions: list[np.ndarray] = []
            for assumed in ASSUMPTIONS:
                kernel = kernel_from_spec(
                    assumed.blur_type,
                    assumed.blur_length,
                    assumed.blur_angle_deg,
                    assumed.gaussian_sigma,
                )
                reconstruction = wiener_deconvolution(observed, kernel, assumed.wiener_balance)
                reconstructions.append(reconstruction)
                rows.append(
                    {
                        "source_id": source_id,
                        "seed": image_seed,
                        "acquisition_condition": condition,
                        "mismatch_level": assumed.label,
                        "psnr_db": psnr(reference, reconstruction),
                        "ssim": ssim(reference, reconstruction),
                        "edge_mae": edge_error(reference, reconstruction),
                        "normalized_measurement_residual": normalized_residual(observed, reconstruction, kernel),
                        "true_blur_type": acquisition.blur_type,
                        "true_blur_length": acquisition.blur_length,
                        "true_blur_angle_deg": acquisition.blur_angle_deg,
                        "assumed_blur_type": assumed.blur_type,
                        "assumed_blur_length": assumed.blur_length,
                        "assumed_blur_angle_deg": assumed.blur_angle_deg,
                        "assumed_gaussian_sigma": assumed.gaussian_sigma,
                    }
                )
            comparison_panel(reference, observed, reconstructions).save(
                args.output_dir / f"{source_id}_{condition}_comparison.png"
            )

    metrics = pd.DataFrame(rows)
    metrics.to_csv(args.output_dir / "metrics.csv", index=False)
    with (args.output_dir / "manifest.json").open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)

    summary = metrics.groupby(["acquisition_condition", "mismatch_level"], sort=False)[
        ["psnr_db", "ssim", "edge_mae", "normalized_measurement_residual"]
    ].mean()
    print(summary.round(4).to_string())
    for condition, group in metrics.groupby("acquisition_condition", sort=False):
        corr = stats.spearmanr(
            group["normalized_measurement_residual"], -group["psnr_db"]
        ).statistic
        print(f"\n{condition}: Spearman(residual, reconstruction error proxy) = {corr:.4f}")
    print(f"\nOutputs written to: {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
