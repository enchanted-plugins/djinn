"""
D1 — Hunt-Szymanski Longest Common Subsequence Alignment
Reference: Hunt J.W. and Szymanski T.G. (1977), "A fast algorithm for computing longest common subsequences", Communications of the ACM 20(5):350-353.
Role: Per-turn intent-preservation score against the anchored goal.
"""
from __future__ import annotations
import difflib, re
_TOKEN_RE = re.compile(r"\w+")
_STOPWORDS = frozenset({"a","an","the","and","or","of","to","in","on","for","with","is","are","be"})


def normalize(text: str) -> list[str]:
    return [t for t in _TOKEN_RE.findall(text.lower()) if t not in _STOPWORDS]


def preservation_ratio(anchor_tokens: list[str], current_tokens: list[str]) -> float:
    """Return LCS-based similarity ratio in [0,1] of current vs anchor token lists."""
    if not anchor_tokens:
        return 1.0
    return difflib.SequenceMatcher(None, anchor_tokens, current_tokens, autojunk=False).ratio()
