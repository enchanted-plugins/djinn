"""
D2 — Baum-Welch HMM Task-Boundary Inference
Reference: Baum L.E. and Welch L. (1970), "An inequality and associated maximization technique in statistical estimation for probabilistic functions of Markov processes".
Role: Infer per-turn task state (ON_TASK | SIDEQUEST | LOST) from tool-pattern + topic-tag observation pairs.

Pure Python stdlib only. No numpy. 3-state HMM; forward-backward + single-pass Baum-Welch
re-estimation on the submitted observation sequence, then Viterbi-style argmax of the
posterior per timestep to emit the state label sequence.
"""
from __future__ import annotations
from math import log, exp

STATES = ["ON_TASK", "SIDEQUEST", "LOST"]
_N = 3


def _normalize(row: list[float]) -> list[float]:
    s = sum(row)
    if s <= 0:
        return [1.0 / len(row)] * len(row)
    return [x / s for x in row]


def _encode_observations(observations: list[tuple[str, str]]) -> tuple[list[int], list[tuple[str, str]]]:
    vocab: dict[tuple[str, str], int] = {}
    seq: list[int] = []
    for obs in observations:
        if obs not in vocab:
            vocab[obs] = len(vocab)
        seq.append(vocab[obs])
    idx_to_obs = sorted(vocab, key=vocab.get)
    return seq, idx_to_obs


def _forward_backward(obs_seq: list[int], A: list[list[float]], B: list[list[float]], pi: list[float]):
    T = len(obs_seq)
    M = len(B[0])
    alpha = [[0.0] * _N for _ in range(T)]
    beta = [[0.0] * _N for _ in range(T)]

    # Forward
    for i in range(_N):
        alpha[0][i] = pi[i] * B[i][obs_seq[0]]
    alpha[0] = _normalize(alpha[0])
    for t in range(1, T):
        for j in range(_N):
            s = 0.0
            for i in range(_N):
                s += alpha[t - 1][i] * A[i][j]
            alpha[t][j] = s * B[j][obs_seq[t]]
        alpha[t] = _normalize(alpha[t])

    # Backward
    for i in range(_N):
        beta[T - 1][i] = 1.0
    beta[T - 1] = _normalize(beta[T - 1])
    for t in range(T - 2, -1, -1):
        for i in range(_N):
            s = 0.0
            for j in range(_N):
                s += A[i][j] * B[j][obs_seq[t + 1]] * beta[t + 1][j]
            beta[t][i] = s
        beta[t] = _normalize(beta[t])

    return alpha, beta


def infer_states(observations: list[tuple[str, str]]) -> list[str]:
    """Return a list of state labels (one per observation) from {ON_TASK, SIDEQUEST, LOST}.

    Runs one pass of forward-backward with sensible priors; we do not iterate the full
    Baum-Welch EM because per-turn we only need posterior state labels, not the ML model.
    """
    if not observations:
        return []

    obs_seq, vocab = _encode_observations(observations)
    M = max(1, len(vocab))

    # Priors: start ON_TASK; self-transition favored; emissions uniform then re-estimated.
    pi = [0.8, 0.15, 0.05]
    A = [
        [0.80, 0.15, 0.05],  # ON_TASK
        [0.30, 0.60, 0.10],  # SIDEQUEST
        [0.10, 0.20, 0.70],  # LOST
    ]
    B = [[1.0 / M] * M for _ in range(_N)]

    # Single re-estimation step (cheap, stdlib-only)
    alpha, beta = _forward_backward(obs_seq, A, B, pi)
    T = len(obs_seq)
    gamma = [[alpha[t][i] * beta[t][i] for i in range(_N)] for t in range(T)]
    gamma = [_normalize(row) for row in gamma]

    # Re-estimate B
    B_new = [[1e-6] * M for _ in range(_N)]
    denom = [1e-9] * _N
    for t in range(T):
        for i in range(_N):
            B_new[i][obs_seq[t]] += gamma[t][i]
            denom[i] += gamma[t][i]
    for i in range(_N):
        B_new[i] = [v / denom[i] for v in B_new[i]]

    # Re-run forward-backward with refined B
    alpha, beta = _forward_backward(obs_seq, A, B_new, pi)
    gamma = [_normalize([alpha[t][i] * beta[t][i] for i in range(_N)]) for t in range(T)]

    return [STATES[max(range(_N), key=lambda i: row[i])] for row in gamma]
