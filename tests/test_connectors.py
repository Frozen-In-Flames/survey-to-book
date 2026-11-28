"""Tests for the beat-connection measurement
(engine/connectors.py) and for the craft standard's presence
in every generation prompt.

The standard (the author, 2026-11-27): beats connect by
causation and contrast -- therefore, but, yet, however, so --
never flat "and then" chains. The metric counts chain markers
against causal/contrast connectors; "so" counts only in its
causal use, not as an intensifier.
"""

import tempfile
import unittest
from pathlib import Path

from engine.connectors import check_connectors, count_connectors
from engine.generate import BookBuilder
from engine.model import StubModel


class TestCounts(unittest.TestCase):
    def test_chain_markers(self):
        counts = count_connectors(
            "He opened the door and then he left, and then the "
            "room was empty.")
        self.assertEqual(counts["chain_markers"], 2)

    def test_causal_and_contrast(self):
        counts = count_connectors(
            "The road had washed out; therefore the ferry did "
            "not run. Marta waited, but the bell did not ring. "
            "It rained, so she wrote the date twice. Yet she "
            "stayed. However, the tide turned because the wind "
            "had dropped.")
        self.assertEqual(counts["causal_contrast"], 6)
        self.assertEqual(counts["chain_markers"], 0)

    def test_sentence_initial_so_is_causal(self):
        counts = count_connectors(
            "The bench was his father's. So he kept it oiled.")
        self.assertEqual(counts["causal_contrast"], 1)

    def test_intensifier_so_is_not_a_connector(self):
        counts = count_connectors(
            "She was so tired that the room swam before her.")
        self.assertEqual(counts["causal_contrast"], 0)

    def test_book_level_shape(self):
        pages = [
            {"index": 0, "question_id": "q001",
             "text": "He came home and then he ate."},
            {"index": 1, "question_id": "q002",
             "text": "The shop was dark; therefore he lit the "
                     "lamp."},
        ]
        result = check_connectors(pages)
        self.assertEqual(result["chain_markers"], 1)
        self.assertEqual(result["causal_contrast_connectors"], 1)
        self.assertEqual(result["pages_with_chain_markers"], 1)
        self.assertAlmostEqual(result["chain_per_connector"], 1.0)


class TestPromptCarriesTheStandard(unittest.TestCase):
    def test_page_prompt_states_the_rule(self):
        pack = {
            "genre": "memoir", "version": "test",
            "framework": {
                "voice": "v", "pov": "first person",
                "refrain": False, "tense": "past",
                "page_target_words": 250,
                "global_instructions": "g",
                "devices": {"d": {"name": "D",
                                  "instruction": "do it"}},
            },
            "chapters": [{"id": "ch01", "title": "One"}],
            "questions": [{
                "id": "q001", "chapter": "ch01", "prompt": "p",
                "narrative_job": "j", "position": "pos",
                "devices": ["d"], "bible_keys": ["k"]}],
        }
        with tempfile.TemporaryDirectory() as tmp:
            builder = BookBuilder(pack, {"q001": "An answer."},
                                  StubModel(),
                                  Path(tmp) / "state.json")
            from engine.bible import Bible
            prompt = builder.page_prompt(pack["questions"][0], 0,
                                         Bible())
        self.assertIn("causation and contrast", prompt)
        self.assertIn('"and then"', prompt)


if __name__ == "__main__":
    unittest.main()
