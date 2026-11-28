"""Generation-time screen for meta-narrative leakage.

A third sibling gate, concerned with a failure neither the
duplication guard nor the gender screens can see: the
generation machinery's own vocabulary appearing in the prose
as the prose's subject. In The Kept Hours (devotional,
v0.6.0; see DEFECTS.md, V6) the pages talk about their
mechanism -- "anchor sentence" named on 60 pages, "anchor
theme" on 7, "the theme returns" on 5, "refrain" on 3, the
formula "As I write today's entry, carrying the newer
facts..." on 19 pages, and prompt instruction language
reproduced outright on page 9 ("Carry this theme changed:").
The sentences are frequently new -- the duplication guard has
nothing to measure -- while their subject is the bookkeeping.

The root cause is the prompt surface: the refrain block named
the apparatus ("anchor theme", "restate it as developed"),
the device instruction told the model to "carry the newer
facts into it", and the duplication retry note repeated the
same formulas, so the model's most available phrasing for a
return was the instruction's own. The prompt-level half of
the fix lives where the prompts are built (engine/generate.py
and the pack's device instructions): instructions now direct
the return without naming the apparatus or supplying a
quotable formula. This module is the output half: a screen
for the apparatus phrases themselves, enforced with the same
bounded regeneration as the other gates, so leakage that
survives the prompt fix costs a retry rather than shipping.

The phrase list is deliberately narrow. It names the
machinery -- the anchor apparatus as a compound ("anchor
sentence", "anchor theme"), the return described as an event
of the text ("the theme returns", "carry this theme
changed"), the retry formula ("carrying the newer facts",
"newer facts"), the prompt's own section names ("story
bible", "fixed facts", "rolling synopsis", "source answer",
"narrative job", "question id"), and "refrain", the device
name the measured book used as apparatus. The bare word
"anchor" is not screened: it is also the respondent's own
word for his family's saying, elicited by the survey as
content. A flag costs a bounded regeneration whose retry note
asks for the entry itself; the screen never edits text.
"""

from __future__ import annotations

import re

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")

META_PHRASES = (
    "anchor sentence",
    "anchor theme",
    "the theme returns",
    "theme returns",
    "carry this theme changed",
    "carrying the newer facts",
    "newer facts",
    "story bible",
    "fixed facts",
    "rolling synopsis",
    "source answer",
    "narrative job",
    "question_id",
    "question id",
    "refrain",
    # The refrain block's own instruction formula, quoted back
    # as narration by The Kept Hours corrected edition
    # (v0.6.1, DEFECTS V17: pages 50, 53, 94 verbatim, echoes
    # on 90 and 95). The block has been reworded; these phrases
    # screen any recurrence of the old wording or an echo of
    # the new one.
    "runs through this book",
    "first said on its first page",
    "comes back to that sentence",
    "let it arrive changed",
    "arrive changed by the days since",
    "must live inside it",
    "must live inside them",
)

_PATTERNS = tuple(
    (phrase, re.compile(rf"\b{re.escape(phrase)}\b", re.IGNORECASE))
    for phrase in META_PHRASES)


def meta_sentence_phrases(sentence: str) -> list[str]:
    """Return the apparatus phrases a single sentence holds."""
    return [phrase for phrase, pattern in _PATTERNS
            if pattern.search(sentence)]


def meta_flags(text: str) -> list[dict]:
    """Screen one page's text. Returns one entry per flagged
    sentence: {"sentence": ..., "rules": ["meta_term"],
    "phrases": [...]}. Sentences are split exactly as the
    other gates split them."""
    normalized = re.sub(r"\s+", " ", text)
    out = []
    for sentence in _SENTENCE_SPLIT.split(normalized):
        sentence = sentence.strip()
        if not sentence:
            continue
        phrases = meta_sentence_phrases(sentence)
        if phrases:
            out.append({"sentence": sentence,
                        "rules": ["meta_term"],
                        "phrases": phrases})
    return out


def audit_meta_terms(pages: list[dict]) -> dict:
    """Count apparatus-phrase leakage across a finished book,
    by phrase and by page, with the same list the generation
    screen enforces."""
    by_phrase: dict[str, int] = {}
    pages_with = set()
    for page in pages:
        normalized = re.sub(r"\s+", " ", page["text"])
        for sentence in _SENTENCE_SPLIT.split(normalized):
            for phrase in meta_sentence_phrases(sentence.strip()):
                by_phrase[phrase] = by_phrase.get(phrase, 0) + 1
                pages_with.add(page["index"])
    return {
        "flagged_sentences": sum(by_phrase.values()),
        "pages_with_meta_terms": len(pages_with),
        "by_phrase": by_phrase,
    }
