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

Matching rules keep the scans from producing false positives.
Trigger phrases are matched at word boundaries, so a trigger such as
"Father" does not match inside "grandfather" and "Mother" does not
match inside "grandmother": a name attached to a grandparent is a
claim about the grandparent, not about the parent. A token that is an
established name plus a plural "s" (the family name "Calloways"
against the established "Calloway") is the same name in plural form,
not a misspelling, and the reverse also holds: the singular form of
a plural established name ("Flame" against "Flames", used as an
attributive noun) is the same name. And a capitalized token is only
treated as a near-miss spelling of an established name when it
shares the name's first letter or appears capitalized somewhere
other than the start of a sentence: an ordinary English word such
as "Yet" is capitalized only because it opens a sentence, and it
sits one edit from a short established name such as "Jet" by
coincidence, not by misspelling.

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


def _trigger_pattern(trigger: str) -> "re.Pattern[str]":
    """Compile a trigger phrase to match at word boundaries.

    A bare substring search matches "Mother" inside "grandmother" and
    "Father" inside "grandfather", which turns a correctly named
    grandparent into a spurious contradiction of the parent's name.
    Boundaries are added only where the trigger's edge is a word
    character, so phrases and punctuation-ended triggers still match.
    """
    prefix = r"\b" if trigger[0].isalnum() or trigger[0] == "_" else ""
    suffix = r"\b" if trigger[-1].isalnum() or trigger[-1] == "_" else ""
    return re.compile(prefix + re.escape(trigger) + suffix, re.IGNORECASE)


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
                for m in _trigger_pattern(trigger).finditer(text):
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
            text = page["text"]
            occurrences: dict[str, list["re.Match[str]"]] = {}
            for m in _NAME_TOKEN_RE.finditer(text):
                occurrences.setdefault(m.group(0), []).append(m)
            for token, matches in occurrences.items():
                # A plural of an established name ("Calloways" for
                # "Calloway") is the same name, not a misspelling;
                # so is the singular of a plural established name
                # ("Flame" for "Flames").
                if any(token.lower() == ref.lower() + "s"
                       or ref.lower() == token.lower() + "s"
                       for ref in established):
                    continue
                # A token counts as name-capitalized only if it
                # appears somewhere other than a sentence start: a
                # common word is capitalized at a sentence start by
                # position, not because it is a name.
                mid_sentence = any(
                    _is_mid_sentence(text, m.start())
                    for m in matches)
                for ref in established:
                    if token != ref and _levenshtein(token.lower(),
                                                     ref.lower()) == 1 \
                            and (token[0].lower() == ref[0].lower()
                                 or mid_sentence):
                        first = matches[0]
                        issues.append({
                            "type": "name_drift",
                            "fact_slot": None,
                            "expected": ref,
                            "found": token,
                            "page_index": page["index"],
                            "question_id": page["question_id"],
                            "excerpt": text[max(0, first.start() - 60):
                                            first.end() + 60].strip(),
                        })
    return _dedup_issues(issues)


def _is_mid_sentence(text: str, start: int) -> bool:
    """True if the token at ``start`` is capitalized mid-sentence.

    Walk back over whitespace and closing punctuation; a token is
    sentence-initial when nothing precedes it, or when the preceding
    substantive character ends a sentence (``.``, ``!``, ``?``).
    """
    i = start - 1
    while i >= 0 and text[i] in " \t\n\"'`)]}":
        i -= 1
    if i < 0:
        return False
    return text[i] not in ".!?"


def _dedup_issues(issues: list[dict]) -> list[dict]:
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
