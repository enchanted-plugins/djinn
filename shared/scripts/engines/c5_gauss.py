"""
D5 — Gauss Accumulation (Intent-Type Drift Signature)
Reference: Gauss C.F. (1809), "Theoria motus corporum coelestium" — least-squares foundation for recursive EMA-with-posterior updates.
Role: Per-(intent-type, developer) drift-threshold posterior with 30-day EMA half-life.

Stdlib only. Atomic write-tmp-rename persistence is handled by callers; this module is
pure math.
"""
from __future__ import annotations
from math import sqrt


def update_posterior(prior: dict, observation: dict, alpha: float = 0.3) -> dict:
    """EMA-style posterior update over a drift-signature record.

    prior keys expected: {intent_type, developer, median_preservation, sigma,
                         p10_threshold, session_length_median, n_sessions}
    observation keys: {preservation_score, session_length}

    Returns a fresh dict with the updated fields. Missing prior fields initialize.
    """
    p = dict(prior) if prior else {}
    obs_score = float(observation.get("preservation_score", 0.0))
    obs_len = float(observation.get("session_length", 0))

    n_prev = int(p.get("n_sessions", 0))
    mean_prev = float(p.get("median_preservation", obs_score))
    var_prev = float(p.get("sigma", 0.0)) ** 2
    len_prev = float(p.get("session_length_median", obs_len))

    # EMA on the mean
    mean_new = (1 - alpha) * mean_prev + alpha * obs_score
    # EMA on variance (Welford-like, weighted by alpha)
    var_new = (1 - alpha) * var_prev + alpha * (obs_score - mean_new) ** 2
    sigma_new = sqrt(max(var_new, 0.0))
    len_new = (1 - alpha) * len_prev + alpha * obs_len

    # p10 threshold: mean - 1.2816 * sigma  (standard-normal 10th percentile)
    p10 = mean_new - 1.2816 * sigma_new

    p.update({
        "intent_type": p.get("intent_type") or observation.get("intent_type"),
        "developer": p.get("developer") or observation.get("developer"),
        "median_preservation": mean_new,
        "sigma": sigma_new,
        "p10_threshold": p10,
        "session_length_median": len_new,
        "n_sessions": n_prev + 1,
    })
    return p
