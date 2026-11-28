"""Tests for sentence completion (the truncation mitigation).

The 480-token page budget is the standing cause of the series'
truncation defect: a page whose budget runs out mid-sentence.
The builder's repair continues the page from its own last
token, once, with a bounded budget, and keeps only the words
that finish the final sentence. These tests pin the three
outcomes: a truncated page is completed and the repair is
recorded; a continuation that never reaches a sentence end
leaves the page standing (and measured as truncated); and a
model that cannot continue text (the stub) leaves pages
exactly as generated.
"""

import tempfile
import unittest
from pathlib import Path

from engine.generate import BookBuilder

PAGE_WHOLE = (
    "Marta kept the harbor book on the table by the window. "
    "She wrote the date at the top of the page each morning. "
    "The boats left one by one into the gray water. Gulls "
    "quarreled above the ferry landing all morning long. She "
    "counted the crates as the boy carried them down the wharf. "
    "By noon the whole harbor smelled of tar and salt."
)
PAGE_CUT = (
    "Daniel mended the torn net by lantern light in the back "
    "room behind the ferry office. The harbor bell rang over "
    "the water at dawn and again at dusk each day. He worked "
    "with his father's tools laid out in their old order on "
    "the bench. The road to the ferry had washed out in the "
    "night, and by morning the water was still"
)


def tiny_pack() -> dict:
    return {
        "genre": "biography",
        "version": "test",
        "framework": {
            "voice": "test voice",
            "pov": "third person",
            "refrain": False,
            "tense": "past",
            "page_target_words": 250,
            "global_instructions": "test instructions",
            "devices": {
                "scene_reconstruction": {
                    "name": "Scene reconstruction",
                    "instruction": "reconstruct a scene",
                },
            },
        },
        "chapters": [{"id": "ch01", "title": "One"}],
        "questions": [
            {"id": "q001", "chapter": "ch01", "prompt": "p1",
             "narrative_job": "j1", "position": "pos1",
             "devices": ["scene_reconstruction"],
             "bible_keys": ["subject.name"]},
            {"id": "q002", "chapter": "ch01", "prompt": "p2",
             "narrative_job": "j2", "position": "pos2",
             "devices": ["scene_reconstruction"],
             "bible_keys": ["subject.work"]},
        ],
    }


ANSWERS = {"q001": "Answer one.", "q002": "Answer two."}


class CutModel:
    """q001 is whole; q002 is cut mid-sentence, and its
    continuation finishes the sentence and then rambles -- the
    builder must keep only the finishing words."""

    name = "cut-test-model"

    def complete(self, prompt: str, max_tokens: int = 512) -> str:
        if "TASK: SUMMARIZE_CHAPTER" in prompt:
            return "Synopsis of the chapter."
        if "QUESTION_ID: q001" in prompt:
            return PAGE_WHOLE
        return PAGE_CUT

    def continue_text(self, text: str, max_tokens: int = 64) -> str:
        return " rising over the roadbed. And then it kept " \
               "rising for the rest of the page and beyond."


class HopelessCutModel(CutModel):
    """The continuation never reaches a sentence end."""

    name = "hopeless-cut-test-model"

    def continue_text(self, text: str, max_tokens: int = 64) -> str:
        return " rising and rising and rising without any end"


class TestSentenceCompletion(unittest.TestCase):
    def test_truncated_page_completed_and_recorded(self):
        with tempfile.TemporaryDirectory() as tmp:
            builder = BookBuilder(tiny_pack(), ANSWERS, CutModel(),
                                  Path(tmp) / "state.json")
            report = builder.build()
        page = builder.state["pages"]["q002"]
        self.assertTrue(page["text"].endswith(
            "the water was still rising over the roadbed."))
        self.assertNotIn("kept rising", page["text"])
        self.assertTrue(page["truncation_repaired"])
        self.assertFalse(
            builder.state["pages"]["q001"]["truncation_repaired"])
        self.assertEqual(report["truncation"]["pages_repaired"], 1)
        self.assertEqual(
            report["truncation"]["pages_ending_mid_sentence"], 0)

    def test_unfinishable_page_stands_and_is_measured(self):
        with tempfile.TemporaryDirectory() as tmp:
            builder = BookBuilder(tiny_pack(), ANSWERS,
                                  HopelessCutModel(),
                                  Path(tmp) / "state.json")
            report = builder.build()
        page = builder.state["pages"]["q002"]
        self.assertEqual(page["text"], PAGE_CUT)
        self.assertFalse(page["truncation_repaired"])
        self.assertEqual(report["truncation"]["pages_repaired"], 0)
        self.assertEqual(
            report["truncation"]["pages_ending_mid_sentence"], 1)


if __name__ == "__main__":
    unittest.main()
