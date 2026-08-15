"""
D1 — Token-sequence similarity ratio (drift proxy)

Implementation: difflib.SequenceMatcher (Ratcliff-Obershelp gestalt pattern
matching), NOT the Hunt-Szymanski LCS algorithm this module was previously
labelled with. SequenceMatcher.ratio() is 2*M/T over matching blocks, which is
not longest-common-subsequence length; the earlier citation to Hunt & Szymanski
(1977), CACM 20(5):350-353 was inaccurate and has been removed.

Role: Per-turn intent-preservation score against the anchored goal.

LIMITATION (VF-07 — construct validity): this ratio measures lexical overlap
with the anchor text, not task-relevant progress. It ranks echoing the prompt
verbatim (~1.0) above genuine on-task work — in review fixtures, running the
relevant tests scored ~0.29, BELOW an off-task CSS edit at ~0.30. Do not gate
drift decisions on this score alone; it needs replacing before it is relied on.
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
