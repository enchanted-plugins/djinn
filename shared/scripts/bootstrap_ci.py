"""
bootstrap_ci.py — non-parametric bootstrap 95% confidence interval.

Honest-numbers contract: every Djinn advisory carries (value, ci_low, ci_high, N).
Any advisory emitted without these four is rejected by the Haiku validator.

Stdlib only. Uses `random.choices` for resampling.
"""
from __future__ import annotations

import random
import statistics
from typing import Sequence, Tuple

_ITERATIONS = 1000
_ALPHA = 0.05  # 95% CI


def bootstrap_ci(
    samples: Sequence[float],
    iterations: int = _ITERATIONS,
    alpha: float = _ALPHA,
) -> Tuple[float, float, float, int]:
    """Return (point_estimate, ci_low, ci_high, N).

    Point estimate is the sample mean. CI bounds are the percentile interval of
    the resampled means. N is len(samples).

    For N <= 1, returns (sample, sample, sample, N) — CI is undefined but the
    contract requires the tuple shape, so we collapse the band to a point.
    """
    n = len(samples)
    if n == 0:
        return 0.0, 0.0, 0.0, 0
    if n == 1:
        v = float(samples[0])
        return v, v, v, 1

    point = float(statistics.fmean(samples))
    resampled_means: list[float] = []
    for _ in range(iterations):
        resample = random.choices(samples, k=n)
        resampled_means.append(statistics.fmean(resample))
    resampled_means.sort()
    lo_idx = int((alpha / 2) * iterations)
    hi_idx = int((1 - alpha / 2) * iterations) - 1
    hi_idx = max(hi_idx, lo_idx)
    return (
        point,
        float(resampled_means[lo_idx]),
        float(resampled_means[hi_idx]),
        n,
    )
