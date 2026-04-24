"""
D3 — Vitter Reservoir Sampling (Algorithm R)
Reference: Vitter J.S. (1985), "Random sampling with a reservoir", ACM Transactions on Mathematical Software 11(1):37-57.
Role: Bounded-memory uniform sampling of k=32 intent-anchor turns across arbitrary-length sessions.
"""
from __future__ import annotations
import random


def update_reservoir(reservoir: list, turn: dict, n_seen: int, k: int = 32) -> list:
    """Apply Algorithm R in place-style: returns a possibly mutated new reservoir.

    n_seen is the 1-based count of turns observed *including* the current `turn`.
    For n_seen <= k the turn is appended. Otherwise it replaces a random slot with
    probability k / n_seen — the canonical Vitter-R uniform-sample invariant.
    """
    r = list(reservoir)
    if n_seen <= k:
        r.append(turn)
        return r
    j = random.randint(0, n_seen - 1)  # inclusive on both ends
    if j < k:
        r[j] = turn
    return r
