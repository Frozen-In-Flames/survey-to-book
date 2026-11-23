"""Pack schema tests: the shipped memoir pack and the validator."""

import copy
import unittest
from pathlib import Path

from engine.pack import load_pack, validate_pack

ROOT = Path(__file__).resolve().parent.parent


class TestMemoirPack(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack = load_pack(ROOT / "packs" / "memoir.json")

    def test_pack_is_valid(self):
        self.assertEqual(validate_pack(self.pack), [])

    def test_one_hundred_questions(self):
        self.assertEqual(len(self.pack["questions"]), 100)

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
            self.assertEqual(count, 10, chapter)

    def test_fact_questions_present(self):
        slots = {q["fact"]["slot"] for q in self.pack["questions"]
                 if "fact" in q}
        self.assertEqual(
            slots, {"birth_year", "mother_name", "father_name",
                    "hometown", "partner_name"})


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


if __name__ == "__main__":
    unittest.main()
