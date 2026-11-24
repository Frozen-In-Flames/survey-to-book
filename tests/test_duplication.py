"""Duplication checker tests, with negative and clean controls.

The failure under test is the one the first shipped book exhibited:
pages repeating earlier pages' sentences verbatim (90 of 100 memoir
pages shared a full sentence with the previous page), because the
generator fed whole pages forward as context. The checker must flag
planted repetition, must pass genuinely distinct pages, and the
generator must treat a duplicating page as failed and regenerate it
a bounded number of times, recording the outcome either way.
"""

import tempfile
import unittest
from pathlib import Path

from engine.duplication import check_duplication, page_overlap, \
    split_sentences
from engine.generate import BookBuilder


def page(index, qid, text):
    return {"index": index, "question_id": qid, "text": text}


PAGE_A = (
    "The harbor bell rang over the water at dawn. Marta counted "
    "the boats as they left the harbor one by one. The ledger lay "
    "open on the table beside her tea. Gulls quarreled above the "
    "ferry landing all morning long. She wrote the date carefully "
    "at the top of the page. The tide was already turning by the "
    "time she finished writing."
)
PAGE_B_DISTINCT = (
    "A storm came in from the gulf after midnight. Rain hammered "
    "the tin roof of the cafe until sunrise. Daniel mended the torn "
    "net by lantern light in the back room. Nobody in the house "
    "slept through the worst of the wind. By morning the road to "
    "the ferry had washed out completely."
)
PAGE_B_REPEATING = (
    "The storm had kept everyone awake since midnight. The ledger "
    "lay open on the table beside her tea. Rain hammered the tin "
    "roof of the cafe until sunrise. Daniel mended the torn net by "
    "lantern light in the back room. By morning the road to the "
    "ferry had washed out completely."
)


class TestDuplicationChecker(unittest.TestCase):
    def test_negative_control_planted_repeat_is_flagged(self):
        pages = [page(0, "q001", PAGE_A), page(1, "q002", PAGE_B_REPEATING)]
        result = check_duplication(pages)
        self.assertEqual(result["pages_sharing_sentence_with_previous"], 1)
        self.assertEqual(result["per_page"][1]["shared_with_previous"], 1)
        repeated = {r["sentence"] for r in result["most_repeated_sentences"]}
        self.assertIn("the ledger lay open on the table beside her tea.",
                      repeated)

    def test_clean_control_distinct_pages_pass(self):
        pages = [page(0, "q001", PAGE_A), page(1, "q002", PAGE_B_DISTINCT)]
        result = check_duplication(pages)
        self.assertEqual(result["pages_sharing_sentence_with_previous"], 0)
        self.assertEqual(result["most_repeated_sentences"], [])

    def test_nonconsecutive_repeat_counted_but_not_headline(self):
        page_c = (
            "Years later the shop stood empty above the harbor. The "
            "ledger lay open on the table beside her tea. A buyer from "
            "the city walked through the rooms at noon. Dust covered "
            "every surface that the family had kept polished."
        )
        pages = [page(0, "q001", PAGE_A),
                 page(1, "q002", PAGE_B_DISTINCT),
                 page(2, "q003", page_c)]
        result = check_duplication(pages)
        # Page 3 repeats page 1, not its predecessor page 2.
        self.assertEqual(result["pages_sharing_sentence_with_previous"], 0)
        self.assertEqual(result["per_page"][2]["shared_with_any_earlier"], 1)

    def test_short_sentences_do_not_count(self):
        a = "He died. The harbor bell rang over the water at dawn today."
        b = "He died. Rain hammered the tin roof of the cafe until sunrise."
        result = check_duplication([page(0, "q001", a), page(1, "q002", b)])
        self.assertEqual(result["pages_sharing_sentence_with_previous"], 0)

    def test_page_overlap_reports_shared_sentences(self):
        overlap = page_overlap(PAGE_B_REPEATING, [PAGE_A], PAGE_A)
        self.assertEqual(overlap["shared_with_previous"], 1)
        self.assertIn("the ledger lay open on the table beside her tea.",
                      overlap["shared_sentences"])

    def test_split_sentences_normalizes(self):
        sents = split_sentences("The Bell  Rang   Twice at Dawn. He died.")
        self.assertEqual(sents, ["the bell rang twice at dawn."])


def tiny_pack() -> dict:
    return {
        "genre": "biography",
        "version": "test",
        "framework": {
            "voice": "test voice",
            "pov": "third person",
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


class FlakyModel:
    """Returns a duplicating page for q002 until the prompt carries
    the retry note, then writes it cleanly."""

    name = "flaky-test-model"

    def complete(self, prompt: str, max_tokens: int = 512) -> str:
        if "TASK: SUMMARIZE_CHAPTER" in prompt:
            return "Synopsis of the chapter."
        if "QUESTION_ID: q001" in prompt:
            return PAGE_A
        if "RETRY" in prompt:
            return PAGE_B_DISTINCT
        return PAGE_B_REPEATING


class StubbornModel:
    """Always returns the duplicating page for q002, retry or not."""

    name = "stubborn-test-model"

    def complete(self, prompt: str, max_tokens: int = 512) -> str:
        if "TASK: SUMMARIZE_CHAPTER" in prompt:
            return "Synopsis of the chapter."
        if "QUESTION_ID: q001" in prompt:
            return PAGE_A
        return PAGE_B_REPEATING


class TestGeneratorDuplicationGuard(unittest.TestCase):
    def _build(self, model):
        with tempfile.TemporaryDirectory() as tmp:
            builder = BookBuilder(tiny_pack(), ANSWERS, model,
                                  Path(tmp) / "state.json")
            report = builder.build()
            return builder, report

    def test_duplicating_page_is_regenerated(self):
        builder, report = self._build(FlakyModel())
        kept = builder.state["pages"]["q002"]
        self.assertEqual(kept["text"], PAGE_B_DISTINCT)
        self.assertEqual(kept["duplication_retries"], 1)
        self.assertEqual(
            report["duplication"]["pages_sharing_sentence_with_previous"],
            0)

    def test_bounded_retries_record_honest_failure(self):
        builder, report = self._build(StubbornModel())
        kept = builder.state["pages"]["q002"]
        self.assertEqual(kept["duplication_retries"], 2)
        self.assertEqual(kept["shared_with_previous"], 1)
        self.assertEqual(
            report["duplication"]["pages_sharing_sentence_with_previous"],
            1)


if __name__ == "__main__":
    unittest.main()
