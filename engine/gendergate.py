"""Generation-time subject-gender gate.

Sibling to the duplication guard, and concerned with a different
failure: a page that genders the book's subject female. The
canonical character record (demo/frozen-in-flames-character.json,
v2.0.0) is unambiguous that the series' demonstration subject,
Frozen In Flames, is male, but the continuity checker constrains
typed facts and kinship triggers only; it has no subject-gender
check. The failure shipped once: in The Keeping Book (family
history, v0.3.0), page 79 reads "In my lifetime, it falls to my
mother and I—two women who have embraced the same task", the
narrator counting himself among two women (see DEFECTS.md, F4,
for the full classification of that book: 394 sentences carry a
female pronoun or role word, 391 of them correctly attached to
the book's mostly female cast, exactly 1 attached to the
subject). The same class was measured in The Day Book (short
story collection, v0.5.0; DEFECTS.md, S7).

This module is the generation-time half of the S7 failsafe. It
is a referent screen, not a ban on female pronouns: the cast of
these books is mostly women (the mother Ruby, the sister Opal,
the partner Amber, the matriarchs Jet, Pearl, Coral, Topaz), and
their pronouns are correct and must remain. The screen flags
only definite-pattern constructions in which a female pronoun
or role word attaches to the subject/narrator himself:

- GROUP: a female group noun ("two women") in a sentence that
  also carries a first-person reference, with no determiner
  construction that places the women outside the narrator's
  group ("the women of the line").
- APPOSITIVE: a female role word inside the comma-bounded
  appositive chain attached to "I" ("I, Ruby's son and Onyx's
  daughter, arrived"), or predicated of "I" directly ("I am a
  daughter of..."), or held "as a daughter" in a first-person
  sentence.
- HERSELF: "herself" in a sentence with "I" and no female cast
  name to attach it to ("I sat at my father's bench..., a piano
  teacher and church organist herself").
- UNRESOLVED SHE: a nominative "she" in a sentence that also
  carries a first-person reference, names no female cast
  member, and holds no kinship possessive ("my mother", "her
  sister") to anchor the pronoun. This rule is a screen, not a
  verdict: it can flag a sentence whose "she" belongs to a
  woman named only in a neighbouring sentence. A flag costs a
  bounded regeneration whose retry prompt asks the model to
  name the woman meant; it never edits text, and the arbiter
  for the finished book is the post-build S7 audit
  (extraction plus sentence-by-sentence classification), not
  this screen's raw count.

Sentences are split exactly as the S7 audit extractor splits
them, so the gate and the audit see the same sentences.
"""

from __future__ import annotations

import re

FEMALE_CAST_NAMES = (
    "Ruby", "Opal", "Amber", "Jet", "Pearl", "Coral", "Jade",
    "Topaz",
)

_ROLE = r"(?:daughter|sister|wife|mother|woman|girl|lady|heroine|actress)"
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
_FIRST_PERSON = re.compile(r"\b(?:I|me|my|mine|we|us|our|ours)\b")
_FIRST_PERSON_I = re.compile(r"\bI\b")

_GROUP_RE = re.compile(
    r"\b(?:women|ladies)\b", re.IGNORECASE)
_GROUP_EXCLUDE = re.compile(
    r"\b(?:the|these|those|such|other|many|few|all) (?:women|ladies)\b",
    re.IGNORECASE)
_ROLE_RE = re.compile(r"\b" + _ROLE + r"\b", re.IGNORECASE)
_I_COMMA_RE = re.compile(r"\bI\s*,")
_I_PREDICATE_RE = re.compile(r"\bI (?:am|was|'m|became)\b",
                             re.IGNORECASE)
_AS_ROLE_RE = re.compile(
    r"\bas (?:a|an|the) " + _ROLE + r"\b", re.IGNORECASE)
_HERSELF_RE = re.compile(r"\bherself\b", re.IGNORECASE)
_SHE_RE = re.compile(r"\bshe\b", re.IGNORECASE)
_KINSHIP_POSSESSIVE = re.compile(
    r"\b(?:my|her|his|their|our) (?:mother|sister|wife|daughter|"
    r"grandmother|aunt|granddaughter|niece)\b", re.IGNORECASE)


def _cast_named(sentence: str) -> bool:
    return any(re.search(rf"\b{name}\b", sentence)
               for name in FEMALE_CAST_NAMES)


def _bare_token(word: str) -> str:
    token = word.strip(",.;:!?\"'“”‘’").lower()
    if token.endswith("'s"):
        token = token[:-2]
    return token


def _predicate_ascription(sentence: str) -> bool:
    """A female role word predicated of "I": within a short
    window after "I am / I was", and not immediately preceded
    by "my" — "my mother", "my sister" name the narrator's
    relatives, not the narrator. A name's possessive does not
    exempt the word: "I am my mother's daughter" ascribes the
    role to the narrator through the second role word."""
    for match in _I_PREDICATE_RE.finditer(sentence):
        words = sentence[match.end():].split()
        for j, word in enumerate(words[:7]):
            if _ROLE_RE.fullmatch(_bare_token(word)):
                prev = words[j - 1].lower() if j > 0 else ""
                if prev != "my":
                    return True
    return False


def _self_ascription(sentence: str) -> bool:
    comma = _I_COMMA_RE.search(sentence)
    if comma:
        # Only the comma-bounded appositive chain attached to
        # "I" is the narrator's self-description; a role word
        # later in the sentence belongs to someone else.
        end = sentence.find(",", comma.end())
        segment = sentence[comma.end():
                           end if end != -1 else len(sentence)]
        match = _ROLE_RE.search(segment)
        if match and not segment[:match.start()].rstrip().lower() \
                .endswith(" my"):
            return True
    return _predicate_ascription(sentence)


def sentence_flags(sentence: str) -> list[str]:
    """Return the gate rules a single sentence trips (may be
    empty). Rule names are stable strings for reports."""
    rules = []
    has_i = bool(_FIRST_PERSON_I.search(sentence))
    has_fp = bool(_FIRST_PERSON.search(sentence))
    if (_GROUP_RE.search(sentence) and has_fp
            and not _GROUP_EXCLUDE.search(sentence)):
        rules.append("group_inclusion")
    if _self_ascription(sentence):
        rules.append("self_ascription")
    if has_fp and _AS_ROLE_RE.search(sentence):
        rules.append("self_ascription")
    if (has_i and _HERSELF_RE.search(sentence)
            and not _cast_named(sentence)):
        rules.append("herself_appositive")
    if (has_fp and _SHE_RE.search(sentence)
            and not _cast_named(sentence)
            and not _KINSHIP_POSSESSIVE.search(sentence)):
        rules.append("unresolved_she")
    return rules


def subject_gender_flags(text: str) -> list[dict]:
    """Screen one page's text. Returns one entry per flagged
    sentence: {"sentence": ..., "rules": [...]}."""
    normalized = re.sub(r"\s+", " ", text)
    out = []
    for sentence in _SENTENCE_SPLIT.split(normalized):
        sentence = sentence.strip()
        if not sentence:
            continue
        rules = sentence_flags(sentence)
        if rules:
            out.append({"sentence": sentence,
                        "rules": sorted(set(rules))})
    return out
