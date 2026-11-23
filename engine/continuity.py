"""Continuity checking.

Verifies finished pages against the typed facts in the story bible.
Two deterministic checks are applied:

1. **Fact-contradiction scan.** For each fact (for example a person's
   name, established by a specific survey answer), later pages are
   scanned around the fact's trigger phrases ("my mother", "born in",
   ...). If a different value appears in the value position next to a
   trigger, the page is flagged as contradicting the bible.
2. **Name-drift scan.** Capitalized names in the pages that differ
   from a bible name by a small edit distance (a misspelling or a
   silently altered name) are flagged for review.

The checker is deliberately conservative: it flags candidate problems
with page references and excerpts rather than asserting certainty.
An empty result means no candidate contradiction was found.
"""

from __future__ import annotations

import re

_NAME = r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})"
_YEAR = r"\b(1[89]\d\d|20\d\d)\b"
_NAME_TOKEN_RE = re.compile(r"\b[A-Z][a-z]{2,}\b")


def _levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1,
                           prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def _name_matches(candidate: str, value: str) -> bool:
    cand = candidate.strip(" ,.").lower()
    val = value.strip(" ,.").lower()
    if cand == val:
        return True
    # First-name-only or surname-only references are acceptable.
    if cand in val.split() or val in cand:
        return True
    if cand.split()[0] == val.split()[0]:
        return True
    return False


def _is_contradiction(candidate: str, value: str) -> bool:
    """Decide whether a differing candidate is a genuine contradiction.

    A full multi-word name that differs from the established value is a
    contradiction. A single differing word is treated as a possible
    nickname or form of address and is only flagged when it is not
    plausibly derived from any part of the established value.
    """
    cand_tokens = candidate.strip(" ,.").lower().split()
    val_tokens = value.strip(" ,.").lower().split()
    if len(cand_tokens) >= 2:
        return True
    token = cand_tokens[0]
    for ref in val_tokens:
        if token.startswith(ref) or ref.startswith(token):
            return False
        if _levenshtein(token, ref) <= 2:
            return False
    return True


def check_continuity(pages: list[dict], facts: dict[str, dict]) -> list[dict]:
    """Return a list of candidate continuity issues (possibly empty).

    ``pages`` is an ordered list of dicts with ``index``,
    ``question_id`` and ``text``. ``facts`` is the bible's fact table.
    """
    issues: list[dict] = []
    order = {p["question_id"]: p["index"] for p in pages}

    for slot, fact in facts.items():
        source_idx = order.get(fact["source_question"], -1)
        value = fact["value"]
        for page in pages:
            if page["index"] <= source_idx:
                continue
            text = page["text"]
            for trigger in fact["triggers"]:
                for m in re.finditer(re.escape(trigger), text, re.IGNORECASE):
                    window = text[m.end():m.end() + 48]
                    if fact["kind"] in ("person_name", "place_name"):
                        cand = re.match(
                            r"[\s,]*(?:named\s+|called\s+)?" + _NAME, window)
                        if cand and not _name_matches(cand.group(1), value) \
                                and _is_contradiction(cand.group(1), value):
                            issues.append({
                                "type": "fact_contradiction",
                                "fact_slot": slot,
                                "expected": value,
                                "found": cand.group(1),
                                "page_index": page["index"],
                                "question_id": page["question_id"],
                                "excerpt": text[max(0, m.start() - 30):
                                                m.end() + 60].strip(),
                            })
                    elif fact["kind"] == "year":
                        cand = re.search(_YEAR, window)
                        if cand and cand.group(1) != value:
                            issues.append({
                                "type": "fact_contradiction",
                                "fact_slot": slot,
                                "expected": value,
                                "found": cand.group(1),
                                "page_index": page["index"],
                                "question_id": page["question_id"],
                                "excerpt": text[max(0, m.start() - 30):
                                                m.end() + 60].strip(),
                            })

    # Name drift: near-miss spellings of established names.
    established: list[str] = []
    for fact in facts.values():
        if fact["kind"] in ("person_name", "place_name"):
            established.extend(fact["value"].split())
    established = [t for t in established if len(t) > 2]
    if established:
        for page in pages:
            seen_tokens = set(_NAME_TOKEN_RE.findall(page["text"]))
            for token in seen_tokens:
                for ref in established:
                    if token != ref and _levenshtein(token.lower(),
                                                     ref.lower()) == 1:
                        issues.append({
                            "type": "name_drift",
                            "fact_slot": None,
                            "expected": ref,
                            "found": token,
                            "page_index": page["index"],
                            "question_id": page["question_id"],
                            "excerpt": page["text"][:120],
                        })

    # Several triggers can match the same sentence; report each
    # distinct problem once.
    deduped: list[dict] = []
    seen_keys: set[tuple] = set()
    for issue in issues:
        key = (issue["type"], issue.get("fact_slot"),
               issue["page_index"], issue.get("found"))
        if key not in seen_keys:
            seen_keys.add(key)
            deduped.append(issue)
    return deduped
