"""Generation-time and audit-time spouse-term screen.

Sibling to the subject-gender gate (engine/gendergate.py), and
concerned with the one construction that gate cannot see. The
gender gate screens female pronouns and female role words
attached to the subject; but a first-person narrator can be
miscast with no female marker at all, by being given the wrong
spouse. In The Kept Hours (devotional, v0.6.0; see DEFECTS.md,
V2--V3) the respondent of record is a man with a wife, and the
generated narrator opens the book with "The family name of my
husband's line is Flames" and goes on to possess a husband on
62 of 100 pages (about 109 instances of "my husband"), while
the gate fired 23 retries on other constructions and the
post-build pronoun audit classified 218 female-marker sentences
with zero definite and zero probable instances. "Husband" is a
male role word; it is the narrator's possession of one that
miscasts him. A first-person narrator's spouse term is a
narrator-gender signal of the same definite class the gender
gate already screens, and this module is the screen V3
prescribed.

The screen is keyed to the subject's recorded gender, which the
pack elicits as a typed fact (``subject_gender``) from the
identity answer, exactly as the subject's name is elicited.
For a male subject, the partner is a wife, and a first-person
"my husband" (or "my husband's") is a definite flag; for a
female subject the terms reverse. The screen matches only the
first-person possessive construction: a cast member's spouse
("Ruby's husband", "her husband", "my mother's husband") is
not the narrator's and is never flagged. Like the gender gate,
this is a screen enforced with bounded regeneration at
generation time, never an edit; and it is also the post-build
audit's spouse-term half, so a book's gender result is never
again reported clean on the pronoun audit alone: the audit
counts spouse-term instances with the same code that screened
them at generation.

When no subject gender is recorded (a pack that does not
elicit the fact), the screen is inert.
"""

from __future__ import annotations

import re

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")

# For a subject of the recorded gender, the spouse term that
# miscasts the subject when the narrator possesses it in the
# first person, and the term that belongs to the subject's
# partner.
_WRONG_TERM = {"male": "husband", "female": "wife"}
_PARTNER_TERM = {"male": "wife", "female": "husband"}


def wrong_spouse_term(subject_gender: str | None) -> str | None:
    if subject_gender is None:
        return None
    return _WRONG_TERM.get(subject_gender.lower())


def partner_term(subject_gender: str | None) -> str | None:
    if subject_gender is None:
        return None
    return _PARTNER_TERM.get(subject_gender.lower())


def _pattern(subject_gender: str | None) -> "re.Pattern[str] | None":
    term = wrong_spouse_term(subject_gender)
    if term is None:
        return None
    return re.compile(rf"\bmy {term}(?:['’]s)?\b", re.IGNORECASE)


def spouse_sentence_flags(sentence: str,
                          subject_gender: str | None) -> list[str]:
    """Return the screen rules a single sentence trips (may be
    empty). The one rule is ``spouse_term_mismatch``: a
    first-person possessive spouse term that contradicts the
    subject's recorded gender."""
    pattern = _pattern(subject_gender)
    if pattern is not None and pattern.search(sentence):
        return ["spouse_term_mismatch"]
    return []


def spouse_flags(text: str,
                 subject_gender: str | None) -> list[dict]:
    """Screen one page's text. Returns one entry per flagged
    sentence: {"sentence": ..., "rules": [...]}. Sentences are
    split exactly as the gender gate splits them, so the two
    screens and the audit see the same sentences."""
    if _pattern(subject_gender) is None:
        return []
    normalized = re.sub(r"\s+", " ", text)
    out = []
    for sentence in _SENTENCE_SPLIT.split(normalized):
        sentence = sentence.strip()
        if not sentence:
            continue
        rules = spouse_sentence_flags(sentence, subject_gender)
        if rules:
            out.append({"sentence": sentence, "rules": rules})
    return out


def count_spouse_instances(text: str,
                           subject_gender: str | None) -> int:
    """Count individual wrong-spouse-term occurrences in a text
    (a sentence may hold more than one)."""
    pattern = _pattern(subject_gender)
    if pattern is None:
        return 0
    return len(pattern.findall(text))


def audit_spouse_terms(pages: list[dict],
                       subject_gender: str | None) -> dict:
    """The post-build audit's spouse-term half.

    ``pages`` is an ordered list of dicts with ``index``,
    ``question_id`` and ``text``, as in the duplication check.
    Every first-person wrong-spouse-term instance is a definite
    subject-gender instance by the rule this module states, so
    the audit reports the instance count and the page count
    directly; a book's gender result is clean only when this
    count is zero alongside the pronoun audit's.
    """
    per_page = []
    instances = 0
    pages_with = 0
    for page in pages:
        n = count_spouse_instances(page["text"], subject_gender)
        if n:
            pages_with += 1
            instances += n
            per_page.append({
                "page_index": page["index"],
                "question_id": page["question_id"],
                "instances": n,
            })
    return {
        "subject_gender": subject_gender,
        "wrong_term": wrong_spouse_term(subject_gender),
        "instances": instances,
        "pages_with_instances": pages_with,
        "per_page": per_page,
    }
