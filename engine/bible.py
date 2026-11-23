"""The story bible: structured state accumulated during generation.

The bible is the engine's compressed representation of everything the
book has established so far. It is updated deterministically from each
answer, keyed by the question's ``bible_keys`` declarations, and it
carries typed ``facts`` (declared by a question's ``fact`` field) that
the continuity checker enforces against later pages.

Rendering is budgeted: when the bible is placed into a generation
prompt, entries relevant to the current question are rendered first,
then core entries (people, places, motifs), up to a word budget. This
is what allows a book of arbitrary length to be generated with a
bounded context window: the bible plus the rolling synopsis stand in
for the full text of all earlier pages.
"""

from __future__ import annotations

import re

CORE_PREFIXES = ("people.", "places.", "motifs.")
_NAME_RE = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\b")
_YEAR_RE = re.compile(r"\b(1[89]\d\d|20\d\d)\b")


def _words(text: str) -> int:
    return len(text.split())


class Bible:
    def __init__(self) -> None:
        # key -> {"key", "text", "source_question", "chapter"}
        self.entries: dict[str, dict] = {}
        # slot -> {"slot", "kind", "value", "triggers", "source_question"}
        self.facts: dict[str, dict] = {}

    # -- updates ---------------------------------------------------------

    def update_from_answer(self, question: dict, answer: str) -> None:
        """Fold one answer into the bible per the question's declarations."""
        for key in question.get("bible_keys", []):
            self.entries[key] = {
                "key": key,
                "text": answer.strip(),
                "source_question": question["id"],
                "chapter": question["chapter"],
            }
        fact = question.get("fact")
        if fact:
            value = self._extract_fact_value(fact["kind"], answer)
            if value:
                self.facts[fact["slot"]] = {
                    "slot": fact["slot"],
                    "kind": fact["kind"],
                    "value": value,
                    "triggers": fact["triggers"],
                    "source_question": question["id"],
                }

    @staticmethod
    def _extract_fact_value(kind: str, answer: str) -> str | None:
        text = answer.strip()
        if kind in ("person_name", "place_name"):
            # Short answers to name questions are the value itself.
            if _words(text) <= 6:
                return text.strip(" .")
            match = _NAME_RE.search(text)
            return match.group(1) if match else None
        if kind == "year":
            match = _YEAR_RE.search(text)
            return match.group(1) if match else None
        return None

    # -- rendering -------------------------------------------------------

    def render(self, relevant_keys: list[str], word_budget: int = 700) -> str:
        """Render bible entries for a prompt, most relevant first."""
        ordered: list[dict] = []
        seen: set[str] = set()
        for key in relevant_keys:
            if key in self.entries and key not in seen:
                ordered.append(self.entries[key])
                seen.add(key)
        for key, entry in self.entries.items():
            if key not in seen and key.startswith(CORE_PREFIXES):
                ordered.append(entry)
                seen.add(key)
        for key, entry in self.entries.items():
            if key not in seen:
                ordered.append(entry)
                seen.add(key)

        lines: list[str] = []
        used = 0
        for entry in ordered:
            text = entry["text"]
            if _words(text) > 120:
                text = " ".join(text.split()[:120]) + " ..."
            line = f"- {entry['key']}: {text}"
            used += _words(line)
            if used > word_budget and lines:
                lines.append("- (further bible entries omitted for length)")
                break
            lines.append(line)
        return "\n".join(lines) if lines else "(nothing established yet)"

    def render_facts(self) -> str:
        if not self.facts:
            return "(no fixed facts established yet)"
        return "\n".join(
            f"- {f['slot']}: {f['value']}" for f in self.facts.values())

    # -- serialization ---------------------------------------------------

    def to_dict(self) -> dict:
        return {"entries": self.entries, "facts": self.facts}

    @classmethod
    def from_dict(cls, data: dict) -> "Bible":
        bible = cls()
        bible.entries = data.get("entries", {})
        bible.facts = data.get("facts", {})
        return bible
