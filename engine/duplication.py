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


# ---------------------------------------------------------------------
# Refrain development
#
# The refrain parameter selects recurrence as a device, but the
# device is recurrence with development: the anchor theme returns
# changed by what the story has established since its last
# appearance. Identical restatement is the first book's defect, not
# the device. This check separates the two quantities the build
# report must state: verbatim copying (the loop detector, measured
# by check_duplication and by the anchor-copy count here) and
# refrain development (whether each thematic recurrence of the
# anchor demonstrably differs and carries newer material).

_STOPWORDS = frozenset({
    "the", "a", "an", "and", "or", "but", "of", "to", "in", "on",
    "at", "by", "for", "with", "from", "as", "was", "were", "is",
    "are", "had", "has", "have", "he", "she", "it", "its", "his",
    "her", "they", "their", "that", "this", "when", "than", "then",
    "into", "over", "after", "before", "not", "no", "so", "if",
})

ANCHOR_JACCARD = 0.5


def _content_words(sentence: str) -> set[str]:
    return {w for w in re.findall(r"[a-z']+", sentence)
            if w not in _STOPWORDS and len(w) > 2}


def check_refrain(pages: list[dict]) -> dict:
    """Measure refrain development against the book's anchor.

    The anchor is the first page's countable sentences -- the
    material the first book looped. Each later sentence is
    classified against the anchor sentence it most resembles:

    * a **verbatim anchor copy** if it is identical to an anchor
      sentence (a loop, and a development failure);
    * a **thematic recurrence** if its content words overlap an
      anchor sentence's content words (Jaccard >= ANCHOR_JACCARD)
      without being identical;
    * a **developed recurrence** if, in addition, it carries at
      least one content word drawn from the story's material
      outside itself -- the pages since the anchor, or elsewhere
      on its own page -- i.e. the theme has absorbed newer facts.

    Development passes only when there are no verbatim anchor
    copies and every thematic recurrence is developed.
    """
    if not pages:
        return {"anchor_sentences": [], "recurrences": [],
                "thematic_recurrences": 0, "developed_recurrences": 0,
                "verbatim_anchor_copies": 0, "failing_pages": [],
                "development_pass": True}
    anchor = split_sentences(pages[0]["text"])
    anchor_words = [_content_words(s) for s in anchor]
    recurrences = []
    story_words: set[str] = set()  # content words of pages[1..i-1]
    for page in pages[1:]:
        page_sentences = split_sentences(page["text"])
        sentence_words = [_content_words(s) for s in page_sentences]
        page_words = set().union(*sentence_words) if sentence_words \
            else set()
        for si, sentence in enumerate(page_sentences):
            words = sentence_words[si]
            best_j, best_anchor = 0.0, -1
            for ai, aw in enumerate(anchor_words):
                if not aw or not words:
                    continue
                j = len(words & aw) / len(words | aw)
                if j > best_j:
                    best_j, best_anchor = j, ai
            if best_anchor < 0:
                continue
            if sentence == anchor[best_anchor]:
                recurrences.append({
                    "page_index": page["index"],
                    "question_id": page["question_id"],
                    "kind": "verbatim_copy", "developed": False})
            elif best_j >= ANCHOR_JACCARD:
                new_words = words - anchor_words[best_anchor]
                others = set().union(
                    *(w for j, w in enumerate(sentence_words)
                      if j != si)) if len(sentence_words) > 1 else set()
                pool = story_words | others
                developed = bool(new_words & pool)
                recurrences.append({
                    "page_index": page["index"],
                    "question_id": page["question_id"],
                    "kind": "thematic",
                    "developed": developed})
        story_words |= page_words
    thematic = [r for r in recurrences if r["kind"] == "thematic"]
    verbatim = [r for r in recurrences if r["kind"] == "verbatim_copy"]
    failing = sorted({r["page_index"] for r in verbatim}
                     | {r["page_index"] for r in thematic
                        if not r["developed"]})
    return {
        "anchor_sentences": anchor[:3],
        "recurrences": recurrences,
        "thematic_recurrences": len(thematic),
        "developed_recurrences":
            sum(1 for r in thematic if r["developed"]),
        "verbatim_anchor_copies": len(verbatim),
        "failing_pages": failing,
        "development_pass": not failing,
    }
