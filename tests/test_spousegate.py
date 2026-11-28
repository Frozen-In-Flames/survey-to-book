"""Tests for the spouse-term screen (engine/spousegate.py).

The positive controls are the measured instances from The
Kept Hours v0.6.0 (DEFECTS.md, V2): the book's narrator, a man
of record with a wife, possesses a husband from page 1. The
negative controls are that same book's correct "my wife"
sentences (pages 9, 17, 54) and sentences about cast members'
spouses: the screen matches only the first-person possessive
construction, keyed to the subject's recorded gender.
Calibration against the full v0.6.0 text is pinned at the end:
the screen, keyed male, finds exactly the 109 instances on 62
pages that DEFECTS V2 records.
"""

import json
import unittest
from pathlib import Path

from engine.spousegate import audit_spouse_terms, \
    count_spouse_instances, spouse_flags, spouse_sentence_flags

ROOT = Path(__file__).resolve().parent.parent


class TestDefiniteInstancesFlag(unittest.TestCase):
    def test_page_one_opening(self):
        sentence = ("The family name of my husband's line is "
                    "Flames.")
        self.assertEqual(spouse_sentence_flags(sentence, "male"),
                         ["spouse_term_mismatch"])

    def test_curly_apostrophe(self):
        sentence = ("The family name of my husband’s line is "
                    "Flames.")
        self.assertEqual(spouse_sentence_flags(sentence, "male"),
                         ["spouse_term_mismatch"])

    def test_bare_my_husband(self):
        sentence = "I set a place for my husband at the table."
        self.assertEqual(spouse_sentence_flags(sentence, "male"),
                         ["spouse_term_mismatch"])

    def test_symmetric_for_a_female_subject(self):
        sentence = "I set a place for my wife at the table."
        self.assertEqual(spouse_sentence_flags(sentence, "female"),
                         ["spouse_term_mismatch"])
        self.assertEqual(spouse_sentence_flags(sentence, "male"),
                         [])


class TestCorrectAndCastSentencesPass(unittest.TestCase):
    def assert_clean(self, sentence, gender="male"):
        self.assertEqual(spouse_sentence_flags(sentence, gender),
                         [], sentence)

    def test_kept_hours_page_9_my_wife(self):
        self.assert_clean(
            "Amber Flames is my wife and holds witness to what "
            "I keep.")

    def test_kept_hours_page_17_my_wife(self):
        self.assert_clean(
            "Amber Flames, my wife and practice witness, "
            "photographs unseen moments, adding depth to "
            "written records.")

    def test_kept_hours_page_54_my_wife(self):
        self.assert_clean(
            "Holding my wife asks of the practice the one thing "
            "it does not ask itself: to be interrupted.")

    def test_cast_members_spouse_named(self):
        self.assert_clean(
            "Ruby's husband Onyx kept the bench the way she "
            "kept the table.")

    def test_cast_members_spouse_pronoun(self):
        self.assert_clean(
            "She learned the keeping from her husband's line "
            "as much as from her own.")

    def test_mothers_husband_is_not_the_narrators(self):
        self.assert_clean(
            "My mother's husband was a quiet man who fixed "
            "what the street brought him.")

    def test_no_recorded_gender_screen_inert(self):
        self.assertEqual(
            spouse_sentence_flags("I set a place for my husband "
                                  "at the table.", None), [])
        self.assertEqual(
            spouse_flags("My husband came home late.", None), [])


class TestPageAndAudit(unittest.TestCase):
    def test_page_level_flags(self):
        page = ("The table was set before light. The family "
                "name of my husband's line is Flames. I wrote "
                "the day down.")
        flags = spouse_flags(page, "male")
        self.assertEqual(len(flags), 1)
        self.assertEqual(flags[0]["rules"],
                         ["spouse_term_mismatch"])

    def test_instances_counted_individually(self):
        text = ("My husband's line is Flames, and my husband "
                "kept the bench.")
        self.assertEqual(count_spouse_instances(text, "male"), 2)

    def test_audit_shape(self):
        pages = [
            {"index": 0, "question_id": "q001",
             "text": "My wife is Amber. We keep the day."},
            {"index": 1, "question_id": "q002",
             "text": "The name of my husband's line is "
                     "Flames."},
        ]
        audit = audit_spouse_terms(pages, "male")
        self.assertEqual(audit["instances"], 1)
        self.assertEqual(audit["pages_with_instances"], 1)
        self.assertEqual(audit["wrong_term"], "husband")
        self.assertEqual(audit["per_page"][0]["page_index"], 1)


class TestCalibrationAgainstV060(unittest.TestCase):
    """Calibration on the shipped first edition's saved state:
    the screen must find exactly the defect DEFECTS V2
    measured -- 109 instances on 62 of 100 pages -- and the
    book's three correct "my wife" pages contribute none of
    them."""

    def test_v060_state_calibration(self):
        state_path = (ROOT / "books" / "devotional-first-book"
                      / "state.json")
        if not state_path.exists():
            self.skipTest("v0.6.0 build state not present")
        with open(state_path, encoding="utf-8") as fh:
            state = json.load(fh)
        pages = sorted(state["pages"].values(),
                       key=lambda p: p["index"])
        # The corrected edition regenerates this directory; the
        # calibration applies only while the saved state is the
        # first edition's: complete at 100 pages, with a report
        # that names no spouse gate. A corrected build in
        # progress (fewer pages) or finished (spouse audit in
        # its report) skips.
        report_path = state_path.parent / "report.json"
        with open(report_path, encoding="utf-8") as fh:
            report = json.load(fh)
        if "spouse_audit" in report or len(pages) != 100:
            self.skipTest("state is the corrected edition's, "
                          "not v0.6.0's")
        audit = audit_spouse_terms(pages, "male")
        self.assertEqual(audit["instances"], 109)
        self.assertEqual(audit["pages_with_instances"], 62)


if __name__ == "__main__":
    unittest.main()
