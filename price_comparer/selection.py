"""Parse checklist answers like ``1,3,5-7``, ``all`` or ``none``."""
from __future__ import annotations


def parse_selection(answer: str, count: int) -> list[int]:
    """Return sorted zero-based indices. Raises ValueError on bad input."""
    answer = (answer or "").strip().lower()
    if answer in ("", "none", "n", "0"):
        return []
    if answer in ("all", "a", "*"):
        return list(range(count))
    chosen: set[int] = set()
    for part in answer.replace(" ", ",").split(","):
        if not part:
            continue
        if "-" in part:
            lo, _, hi = part.partition("-")
            start, end = int(lo), int(hi)
            if start > end:
                start, end = end, start
            rng = range(start, end + 1)
        else:
            rng = [int(part)]
        for n in rng:
            if not 1 <= n <= count:
                raise ValueError(f"{n} is out of range 1-{count}")
            chosen.add(n - 1)
    return sorted(chosen)
