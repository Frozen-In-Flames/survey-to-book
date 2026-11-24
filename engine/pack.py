"""Genre pack loading and schema validation.

A genre pack is a JSON document with three parts:

* ``framework`` -- the control layer: voice, point of view, tense,
  page target, a library of named literary devices (each with an
  instruction string), and global instructions applied to every page.
* ``chapters`` -- the structural arc the questions are distributed over.
* ``questions`` -- the survey. Each question carries, beside the prompt
  shown to the respondent, its ``narrative_job`` (structural role),
  ``position`` (placement in the arc), ``devices`` (framework device
  ids applied when converting the answer to prose), ``bible_keys``
  (story-bible entries the answer creates or updates), and an optional
  ``fact`` declaration used by the continuity checker.
"""

from __future__ import annotations

import json
from pathlib import Path

REQUIRED_QUESTION_FIELDS = (
    "id",
    "chapter",
    "prompt",
    "narrative_job",
    "position",
    "devices",
    "bible_keys",
)

FACT_KINDS = ("person_name", "place_name", "year")


class PackError(ValueError):
    """Raised when a genre pack fails schema validation."""


def load_pack(path: str | Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        pack = json.load(fh)
    errors = validate_pack(pack)
    if errors:
        raise PackError("invalid genre pack:\n" + "\n".join(errors))
    return pack


def validate_pack(pack: dict) -> list[str]:
    """Return a list of schema errors; empty list means valid."""
    errors: list[str] = []

    for field in ("genre", "version", "framework", "chapters", "questions"):
        if field not in pack:
            errors.append(f"pack missing top-level field: {field}")

    framework = pack.get("framework", {})
    for field in ("voice", "pov", "tense", "page_target_words", "devices",
                  "global_instructions"):
        if field not in framework:
            errors.append(f"framework missing field: {field}")
    devices = framework.get("devices", {})
    for dev_id, dev in devices.items():
        if not isinstance(dev, dict) or "name" not in dev or "instruction" not in dev:
            errors.append(f"device {dev_id!r} must define name and instruction")
    refrain = framework.get("refrain")
    if refrain is not None and not isinstance(refrain, bool):
        errors.append("framework.refrain must be a boolean when present")

    chapter_ids = set()
    for chapter in pack.get("chapters", []):
        for field in ("id", "title"):
            if field not in chapter:
                errors.append(f"chapter missing field: {field} ({chapter!r})")
        chapter_ids.add(chapter.get("id"))

    seen_ids = set()
    for q in pack.get("questions", []):
        qid = q.get("id", "<no id>")
        for field in REQUIRED_QUESTION_FIELDS:
            if field not in q:
                errors.append(f"question {qid}: missing field {field}")
        if qid in seen_ids:
            errors.append(f"duplicate question id: {qid}")
        seen_ids.add(qid)
        if q.get("chapter") not in chapter_ids:
            errors.append(f"question {qid}: unknown chapter {q.get('chapter')!r}")
        for dev_id in q.get("devices", []):
            if dev_id not in devices:
                errors.append(f"question {qid}: unknown device {dev_id!r}")
        if not isinstance(q.get("bible_keys", []), list):
            errors.append(f"question {qid}: bible_keys must be a list")
        fact = q.get("fact")
        if fact is not None:
            for field in ("slot", "kind", "triggers"):
                if field not in fact:
                    errors.append(f"question {qid}: fact missing field {field}")
            if fact.get("kind") not in FACT_KINDS:
                errors.append(
                    f"question {qid}: fact kind must be one of {FACT_KINDS}")
    return errors


def questions_by_chapter(pack: dict) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {c["id"]: [] for c in pack["chapters"]}
    for q in pack["questions"]:
        grouped[q["chapter"]].append(q)
    return grouped
