"""Biography pack tests: schema, structure, and answer alignment.

The memoir pack's first commit shipped with a defect this suite
exists to prevent from recurring: the pack's question ids and the
demo answers' ids did not intersect, so the pairing of pack and
answers was never actually exercised. These tests therefore prove,
before any generation is attempted, that the biography pack and its
demonstration answers align exactly: every question has exactly one
non-empty answer, no answer names an unknown question, and the
typed facts the pack declares are the values the bible extracts
from those answers.

The demonstration subject is the series' demonstration user, the
fictional persona Frozen In Flames. A canonical character record
(demo/frozen-in-flames-character.json) holds the invented facts of
the character's life exactly once; the demo answers were drawn from
it, and this suite proves the bible extracted from the answers is
internally the values the shipped book carries. The character is
living, so the pack's death_year slot is declared but deliberately
unestablished by the demo answers.

Canon supersession (2026-11-24): the biography build invented the
character's core facts because the survey never asked the author.
The author has since set the canon himself (born 2000 in Dallas;
mother Ruby Flames; father Onyx Frozen; partner Amber Flames),
and the canonical record now carries the corrected values. The
shipped biography book and its demo answers retain the earlier
invented values -- they are the book as published, and a corrected
edition is queued separately -- so the record-agreement test below
pins the supersession mechanically: the answers and the record
must diverge in exactly the author-corrected fields, no more and
no fewer.
"""

import json
import tempfile
import unittest
from pathlib import Path

from engine.bible import Bible
from engine.generate import BookBuilder
from engine.model import StubModel
from engine.pack import load_pack, validate_pack

ROOT = Path(__file__).resolve().parent.parent

EXPECTED_FACTS = {
    "subject_name": "Frozen In Flames",
    "birth_year": "1960",
    "birthplace": "Memphis",
    "mother_name": "Evelyn Flames",
    "father_name": "Harold Flames",
    "partner_name": "Alice Flames",
}

PACK_FACT_SLOTS = set(EXPECTED_FACTS) | {"death_year"}


class TestBiographyPack(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack = load_pack(ROOT / "packs" / "biography.json")
        with open(ROOT / "demo" / "biography-demo-answers.json",
                  encoding="utf-8") as fh:
            cls.demo = json.load(fh)
        cls.answers = cls.demo["answers"]
        with open(ROOT / "demo" / "frozen-in-flames-character.json",
                  encoding="utf-8") as fh:
            cls.character = json.load(fh)

    def test_pack_is_valid(self):
        self.assertEqual(validate_pack(self.pack), [])

    def test_genre_and_version(self):
        self.assertEqual(self.pack["genre"], "biography")
        self.assertEqual(self.pack["version"], "1.0.0")

    def test_third_person_framework(self):
        # The pack's defining difference from memoir is point of view.
        self.assertEqual(self.pack["framework"]["pov"], "third person")

    def test_refrain_default_off(self):
        # Biography is third-person and chronological; recurrence
        # reads as error rather than voice, so the pack's refrain
        # default is off.
        self.assertIs(self.pack["framework"]["refrain"], False)

    def test_one_hundred_questions(self):
        self.assertEqual(len(self.pack["questions"]), 100)

    def test_ten_questions_per_chapter(self):
        counts = {}
        for q in self.pack["questions"]:
            counts[q["chapter"]] = counts.get(q["chapter"], 0) + 1
        self.assertEqual(len(counts), 10)
        for chapter, count in counts.items():
            self.assertEqual(count, 10, chapter)

    def test_every_question_fully_specified(self):
        for q in self.pack["questions"]:
            for field in ("id", "chapter", "prompt", "narrative_job",
                          "position", "devices", "bible_keys"):
                self.assertIn(field, q, f"{q.get('id')} missing {field}")
                self.assertTrue(q[field], f"{q['id']} empty {field}")

    def test_fact_slots_present(self):
        slots = {q["fact"]["slot"] for q in self.pack["questions"]
                 if "fact" in q}
        self.assertEqual(slots, PACK_FACT_SLOTS)

    def test_demo_answers_labeled_fabricated(self):
        self.assertIn("Frozen In Flames", self.demo["persona"])
        self.assertIn("fictional", self.demo["persona"].lower())
        self.assertIn("fabricated", self.demo["provenance"].lower())

    def test_answers_align_with_questions(self):
        """The memoir defect, as a test: ids must intersect fully."""
        qids = [q["id"] for q in self.pack["questions"]]
        self.assertEqual(sorted(self.answers), sorted(qids))
        for qid in qids:
            self.assertTrue(self.answers[qid].strip(),
                            f"{qid} has an empty answer")

    def _extracted_facts(self):
        bible = Bible()
        for q in self.pack["questions"]:
            bible.update_from_answer(q, self.answers[q["id"]])
        return {slot: fact["value"] for slot, fact in bible.facts.items()}

    def test_facts_extract_expected_values(self):
        extracted = self._extracted_facts()
        self.assertEqual(extracted, EXPECTED_FACTS)
        # The character is living: no death fact may be established.
        self.assertNotIn("death_year", extracted)

    # The fields the author corrected on 2026-11-24. The shipped
    # book's answers carry the biography build's invented values;
    # the record carries the author's canon.
    CORRECTED_FIELDS = {"birth_year", "birthplace", "mother_name",
                        "father_name", "partner_name"}

    def test_character_record_agrees_with_answers(self):
        """Supersession, pinned: the bible extracted from the
        shipped book's demo answers and the corrected canonical
        record must diverge in exactly the author-corrected
        fields. Any other divergence means the record and the
        shipped book have drifted apart unrecorded."""
        record_facts = {k: str(v)
                        for k, v in self.character["facts"].items()}
        extracted = self._extracted_facts()
        self.assertEqual(set(extracted), set(record_facts))
        divergent = {k for k in extracted
                     if extracted[k] != record_facts[k]}
        self.assertEqual(divergent, self.CORRECTED_FIELDS)
        self.assertEqual(self.character["character"]["name"],
                         "Frozen In Flames")
        self.assertEqual(record_facts["birth_year"], "2000")
        self.assertEqual(record_facts["birthplace"], "Dallas")

    def test_stub_build_produces_full_book(self):
        """End-to-end plumbing: 100 answers in, 100 pages out."""
        with tempfile.TemporaryDirectory() as tmp:
            builder = BookBuilder(self.pack, self.answers, StubModel(),
                                  Path(tmp) / "state.json")
            report = builder.build()
        self.assertEqual(report["pages_built"], 100)
        self.assertEqual(report["skipped_empty"], [])
        self.assertEqual(report["continuity_issues"], [])
        self.assertIs(report["refrain"], False)
        self.assertEqual(
            report["duplication"]["pages_sharing_sentence_with_previous"],
            0)


if __name__ == "__main__":
    unittest.main()
