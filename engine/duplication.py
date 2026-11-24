"""Duplication checking.

Sibling to the continuity checker, and concerned with a different
failure: a page that repeats earlier text verbatim. The continuity
checker verifies facts; it cannot see that two pages share whole
sentences. The first book this system produced made the failure
measurable: the sliding-window prompt handed the model the previous
pages in full, and the model treated that context as material to
re-emit, so the opening anchor paragraph restarted on page after
page (90 of 100 pages shared at least one full sentence verbatim
with the previous page).

This module measures the failure deterministically. Sentences are
normalized (case, whitespace, and edge punctuation folded) and a
sentence counts when it has at least MIN_SENTENCE_WORDS words, so
trivial fragments ("He died.") are not treated as duplication. The
headline metric matches the first book's measurement: the number of
pages sharing at least one full sentence with the immediately
previous page.
"""

from __future__ import annotations

import re
from collections import Counter

MIN_SENTENCE_WORDS = 4

_SENTENCE_RE = re.compile(r"[^.!?]+[.!?]+|[^.!?]+$")


def split_sentences(text: str) -> list[str]:
    """Return the text's normalized sentences of countable length."""
    out = []
    for raw in _SENTENCE_RE.findall(text):
        norm = " ".join(raw.lower().split()).strip(" \t\"'“”‘’")
        if len(norm.split()) >= MIN_SENTENCE_WORDS:
            out.append(norm)
    return out


def page_overlap(text: str, earlier_texts: list[str],
                 previous_text: str | None) -> dict:
    """Measure one page's verbatim sentence overlap with earlier text.

    Returns counts of the page's sentences that appear in the
    immediately previous page and in any earlier page, plus the list
    of shared sentences themselves (for retry prompts and reports).
    """
    sentences = split_sentences(text)
    earlier = set()
    for t in earlier_texts:
        earlier.update(split_sentences(t))
    previous = (set(split_sentences(previous_text))
                if previous_text else set())
    shared_any = [s for s in sentences if s in earlier]
    shared_prev = [s for s in sentences if s in previous]
    return {
        "sentences": len(sentences),
        "shared_with_previous": len(shared_prev),
        "shared_with_any_earlier": len(shared_any),
        "shared_sentences": sorted(set(shared_any)),
    }


def check_duplication(pages: list[dict]) -> dict:
    """Measure verbatim sentence duplication across a finished book.

    ``pages`` is an ordered list of dicts with ``index``,
    ``question_id`` and ``text``. Returns the headline count of pages
    sharing a full sentence with the previous page, the most repeated
    sentences in the book, and the per-page detail.
    """
    per_page = []
    sharing_with_previous = 0
    seen: list[str] = []
    previous_text: str | None = None
    counts: Counter = Counter()
    for page in pages:
        text = page["text"]
        counts.update(set(split_sentences(text)))
        overlap = page_overlap(text, seen, previous_text)
        if overlap["shared_with_previous"] > 0:
            sharing_with_previous += 1
        per_page.append({
            "page_index": page["index"],
            "question_id": page["question_id"],
            "sentences": overlap["sentences"],
            "shared_with_previous": overlap["shared_with_previous"],
            "shared_with_any_earlier":
                overlap["shared_with_any_earlier"],
        })
        seen.append(text)
        previous_text = text
    most_repeated = [
        {"sentence": sentence, "pages": n}
        for sentence, n in counts.most_common(10) if n > 1
    ]
    return {
        "pages_sharing_sentence_with_previous": sharing_with_previous,
        "total_pages": len(pages),
        "most_repeated_sentences": most_repeated,
        "per_page": per_page,
    }
