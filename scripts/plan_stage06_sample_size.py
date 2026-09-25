#!/usr/bin/env python3
"""Plan Stage 06 independent source count from precision and event support.

This is a design utility, not an outcome-analysis script. Inputs must be chosen
from development/external-pilot evidence before the independent cohort is opened.
"""

from __future__ import annotations

import argparse
import json
import math


def probability_at_least(n: int, minimum: int, probability: float) -> float:
    return sum(
        math.comb(n, k) * probability**k * (1.0 - probability) ** (n - k)
        for k in range(minimum, n + 1)
    )


def event_support_n(probability: float, minimum: int, assurance: float, maximum: int) -> int:
    for n in range(minimum, maximum + 1):
        if probability_at_least(n, minimum, probability) >= assurance:
            return n
    raise ValueError("No event-support solution within --maximum-sources")


def precision_n(source_sd: float, half_width: float, z_value: float = 1.96) -> int:
    return math.ceil((z_value * source_sd / half_width) ** 2)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-positive-probability", type=float, required=True)
    parser.add_argument("--minimum-positive-sources", type=int, default=10)
    parser.add_argument("--assurance", type=float, default=0.95)
    parser.add_argument("--paired-effect-source-sd", type=float, required=True)
    parser.add_argument("--target-ci-half-width", type=float, required=True)
    parser.add_argument("--maximum-sources", type=int, default=1000)
    args = parser.parse_args()

    if not 0 < args.source_positive_probability < 1:
        parser.error("--source-positive-probability must lie strictly between 0 and 1")
    if not 0 < args.assurance < 1:
        parser.error("--assurance must lie strictly between 0 and 1")
    if args.minimum_positive_sources < 1:
        parser.error("--minimum-positive-sources must be positive")
    if args.paired_effect_source_sd <= 0 or args.target_ci_half_width <= 0:
        parser.error("precision inputs must be positive")

    n_event = event_support_n(
        args.source_positive_probability,
        args.minimum_positive_sources,
        args.assurance,
        args.maximum_sources,
    )
    n_precision = precision_n(args.paired_effect_source_sd, args.target_ci_half_width)
    selected = max(n_event, n_precision)
    result = {
        "source_positive_probability": args.source_positive_probability,
        "minimum_positive_sources": args.minimum_positive_sources,
        "event_support_assurance": args.assurance,
        "event_support_source_count": n_event,
        "paired_effect_source_sd": args.paired_effect_source_sd,
        "target_95pct_ci_half_width": args.target_ci_half_width,
        "precision_source_count_normal_approximation": n_precision,
        "selected_minimum_independent_sources": selected,
        "event_support_probability_at_selected_n": probability_at_least(
            selected, args.minimum_positive_sources, args.source_positive_probability
        ),
        "warning": "Freeze conservative inputs and the selected count before opening independent outcomes.",
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

