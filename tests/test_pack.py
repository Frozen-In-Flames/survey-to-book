"""Pack schema tests: the shipped memoir pack and the validator."""

import copy
import json
import unittest
from pathlib import Path

from engine.bible import Bible
from engine.pack import load_pack, validate_pack

ROOT = Path(__file__).resolve().parent.parent

EXPECTED_MEMOIR_FACTS = {
    "subject_name": "June Calloway",
    "birth_year": "1962",
    "hometown": "Saltmarsh",
    "mother_name": "Rosa Calloway",
    "father_name": "Henry Calloway",
    "partner_name": "Daniel Reyes",
}


class TestMemoirPack(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack = load_pack(ROOT / "packs" / "memoir.json")
        with open(ROOT / "demo" / "memoir-demo-answers.json",
                  encoding="utf-8") as fh:
            cls.answers = json.load(fh)["answers"]

    def test_pack_is_valid(self):
        self.assertEqual(validate_pack(self.pack), [])

    def test_genre_and_version(self):
        # v1.1.0 added the identity question (q000); the original
        # 100 questions are unchanged from v1.0.0.
        self.assertEqual(self.pack["genre"], "memoir")
        self.assertEqual(self.pack["version"], "1.1.0")

    def test_question_count(self):
        # The original 100 questions plus the identity question
        # added by the clean-proof audit in v1.1.0.
        self.assertEqual(len(self.pack["questions"]), 101)

    def test_every_question_fully_specified(self):
        for q in self.pack["questions"]:
            for field in ("id", "chapter", "prompt", "narrative_job",
                          "position", "devices", "bible_keys"):
                self.assertIn(field, q, f"{q.get('id')} missing {field}")
                self.assertTrue(q[field], f"{q['id']} empty {field}")

    def test_ten_questions_per_chapter(self):
        counts = {}
        for q in self.pack["questions"]:
            counts[q["chapter"]] = counts.get(q["chapter"], 0) + 1
        self.assertEqual(len(counts), 10)
        for chapter, count in counts.items():
            # Chapter 1 carries the added identity question.
            expected = 11 if chapter == "ch01" else 10
            self.assertEqual(count, expected, chapter)

    def test_fact_questions_present(self):
        slots = {q["fact"]["slot"] for q in self.pack["questions"]
                 if "fact" in q}
        self.assertEqual(slots, set(EXPECTED_MEMOIR_FACTS))

    def test_identity_question_asks_for_main_character(self):
        """Clean-proof corollary: who the main character is is
        respondent data, elicited by an explicit identity question
        early in the survey -- never a fact the build supplies.
        Before pack v1.1.0 the memoir survey never asked: the
        narrator's name existed only as the demo answers file's
        persona metadata. The question declaring the subject_name
        fact must sit in the first chapter, stand first in the
        question list, and ask, in terms, who the book's main
        character is."""
        identity = [q for q in self.pack["questions"]
                    if q.get("fact", {}).get("slot") == "subject_name"]
        self.assertEqual(len(identity), 1)
        question = identity[0]
        self.assertEqual(question["id"],
                         self.pack["questions"][0]["id"])
        self.assertEqual(question["chapter"],
                         self.pack["questions"][0]["chapter"])
        self.assertIn("main character", question["prompt"].lower())
        self.assertTrue(
            self.answers[question["id"]].startswith("June Calloway"))

    def test_original_questions_unchanged(self):
        """The v1.1.0 audit added one question and moved none: the
        original ids q001-q100 are all present, in order, after
        the added q000."""
        ids = [q["id"] for q in self.pack["questions"]]
        self.assertEqual(ids[0], "q000")
        self.assertEqual(ids[1:],
                         [f"q{n:03d}" for n in range(1, 101)])

    def test_answers_align_with_questions(self):
        qids = [q["id"] for q in self.pack["questions"]]
        self.assertEqual(sorted(self.answers), sorted(qids))
        for qid in qids:
            self.assertTrue(self.answers[qid].strip(),
                            f"{qid} has an empty answer")

    def test_fact_traceability_coverage(self):
        """Completeness gate: every bible fact traces to a survey
        answer, and the extracted facts are the demonstration
        persona's recorded values."""
        bible = Bible()
        for q in self.pack["questions"]:
            bible.update_from_answer(q, self.answers[q["id"]])
        extracted = {slot: fact["value"]
                     for slot, fact in bible.facts.items()}
        self.assertEqual(extracted, EXPECTED_MEMOIR_FACTS)
        questions = {q["id"]: q for q in self.pack["questions"]}
        traced = 0
        for slot, fact in bible.facts.items():
            qid = fact["source_question"]
            self.assertIn(qid, questions,
                          f"{slot}: source question {qid} not in pack")
            self.assertEqual(questions[qid]["fact"]["slot"], slot)
            self.assertTrue(self.answers[qid].strip(),
                            f"{slot}: {qid} has an empty answer")
            traced += 1
        self.assertEqual(traced / len(bible.facts), 1.0)


class TestValidatorControls(unittest.TestCase):
    """Negative controls: broken packs must be rejected."""

    @classmethod
    def setUpClass(cls):
        cls.pack = load_pack(ROOT / "packs" / "memoir.json")

    def test_missing_field_rejected(self):
        broken = copy.deepcopy(self.pack)
        del broken["questions"][0]["narrative_job"]
        errors = validate_pack(broken)
        self.assertTrue(any("narrative_job" in e for e in errors))

    def test_unknown_device_rejected(self):
        broken = copy.deepcopy(self.pack)
        broken["questions"][0]["devices"] = ["no_such_device"]
        errors = validate_pack(broken)
        self.assertTrue(any("no_such_device" in e for e in errors))

    def test_duplicate_id_rejected(self):
        broken = copy.deepcopy(self.pack)
        broken["questions"][1]["id"] = broken["questions"][0]["id"]
        errors = validate_pack(broken)
        self.assertTrue(any("duplicate" in e for e in errors))

    def test_memoir_refrain_default_on(self):
        # The memoir book was generated with recurrence in effect;
        # its pack records that setting explicitly.
        self.assertIs(self.pack["framework"]["refrain"], True)

    def test_nonboolean_refrain_rejected(self):
        broken = copy.deepcopy(self.pack)
        broken["framework"]["refrain"] = "yes"
        errors = validate_pack(broken)
        self.assertTrue(any("refrain" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
