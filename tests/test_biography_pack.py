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
    "subject_name": "Walter Elias Brandt",
    "birth_year": "1911",
    "birthplace": "Pittsburgh",
    "mother_name": "Anna Brandt",
    "father_name": "Josef Brandt",
    "partner_name": "Clara Brandt",
    "death_year": "1989",
}


class TestBiographyPack(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack = load_pack(ROOT / "packs" / "biography.json")
        with open(ROOT / "demo" / "biography-demo-answers.json",
                  encoding="utf-8") as fh:
            cls.demo = json.load(fh)
        cls.answers = cls.demo["answers"]

    def test_pack_is_valid(self):
        self.assertEqual(validate_pack(self.pack), [])

    def test_genre_and_version(self):
        self.assertEqual(self.pack["genre"], "biography")
        self.assertEqual(self.pack["version"], "1.0.0")

    def test_third_person_framework(self):
        # The pack's defining difference from memoir is point of view.
        self.assertEqual(self.pack["framework"]["pov"], "third person")

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
        self.assertEqual(slots, set(EXPECTED_FACTS))

    def test_demo_answers_labeled_fabricated(self):
        self.assertIn("fictional", self.demo["persona"].lower())
        self.assertIn("fabricated", self.demo["note"].lower())

    def test_answers_align_with_questions(self):
        """The memoir defect, as a test: ids must intersect fully."""
        qids = [q["id"] for q in self.pack["questions"]]
        self.assertEqual(sorted(self.answers), sorted(qids))
        for qid in qids:
            self.assertTrue(self.answers[qid].strip(),
                            f"{qid} has an empty answer")

    def test_facts_extract_expected_values(self):
        bible = Bible()
        for q in self.pack["questions"]:
            bible.update_from_answer(q, self.answers[q["id"]])
        extracted = {slot: fact["value"]
                     for slot, fact in bible.facts.items()}
        self.assertEqual(extracted, EXPECTED_FACTS)

    def test_stub_build_produces_full_book(self):
        """End-to-end plumbing: 100 answers in, 100 pages out."""
        with tempfile.TemporaryDirectory() as tmp:
            builder = BookBuilder(self.pack, self.answers, StubModel(),
                                  Path(tmp) / "state.json")
            report = builder.build()
        self.assertEqual(report["pages_built"], 100)
        self.assertEqual(report["skipped_empty"], [])
        self.assertEqual(report["continuity_issues"], [])


if __name__ == "__main__":
    unittest.main()
