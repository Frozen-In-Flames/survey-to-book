"""Duplication checker tests, with negative and clean controls.

The failure under test is the one the first shipped book exhibited:
pages repeating earlier pages' sentences verbatim (90 of 100 memoir
pages shared a full sentence with the previous page), because the
generator fed whole pages forward as context. The checker must flag
planted repetition, must pass genuinely distinct pages, and the
generator must treat a duplicating page as failed and regenerate it
a bounded number of times, recording the outcome either way.
"""

import json
import tempfile
import unittest
from pathlib import Path

from engine.duplication import check_duplication, check_refrain, \
    page_overlap, split_sentences
from engine.generate import BookBuilder

ROOT = Path(__file__).resolve().parent.parent


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


def refrain_pack() -> dict:
    pack = tiny_pack()
    pack["framework"]["refrain"] = True
    # The return is a device like any other: q002's slot assigns
    # it, q001's does not. The builder carries the book's first
    # sentence into a prompt only where the slot assigns the
    # return (the saturation fix: the first devotional attached
    # it to all 100 prompts although 21 slots assigned it).
    pack["framework"]["devices"]["anchor_return"] = {
        "name": "Anchor return",
        "instruction": "return to the book's first sentence, "
                       "changed by what has happened since",
    }
    pack["questions"][1]["devices"] = ["scene_reconstruction",
                                       "anchor_return"]
    return pack


PAGE_B_ANCHOR_COPY = (
    "The harbor bell rang over the water at dawn. Then the "
    "narrative moved on to other matters entirely. Daniel mended "
    "the torn net by lantern light in the back room. By morning "
    "the road to the ferry had washed out completely."
)
PAGE_B_DEVELOPED = (
    "Daniel mended the torn net by lantern light in the back "
    "room. The harbor bell rang over the water at dawn, and "
    "Daniel answered it from the ferry office. By morning the "
    "road to the ferry had washed out completely."
)
PAGE_UNDEVELOPED = (
    "At dawn the bell rang over the harbor water. Then the "
    "narrative moved on to other matters entirely. Daniel mended "
    "the torn net by lantern light in the back room."
)
PAGE_LONG_A = (
    "The harbor bell rang over the water at dawn. Marta counted "
    "the boats as they left the harbor one by one. The ledger lay "
    "open on the table beside her tea. Gulls quarreled above the "
    "ferry landing all morning long. She wrote the date carefully "
    "at the top of the page. The quartermaster hid the silver "
    "compass inside the hollow mast. Nobody on the dock admitted "
    "to knowing anything about the matter at all. The tide was "
    "already turning by the time she finished writing. Boats "
    "knocked gently against the pilings in the brown harbor "
    "water. A boy carried crates of oranges down the length of "
    "the wharf. The ferry captain drank his coffee standing up "
    "and watched the weather. By noon the whole harbor smelled "
    "of tar and salt and oranges."
)


class TestRefrainChecker(unittest.TestCase):
    """The development check: recurrence must return changed."""

    def test_verbatim_anchor_copy_fails(self):
        pages = [page(0, "q001", PAGE_A),
                 page(1, "q002", PAGE_B_DISTINCT),
                 page(2, "q003", PAGE_B_ANCHOR_COPY)]
        result = check_refrain(pages)
        self.assertFalse(result["development_pass"])
        self.assertGreaterEqual(result["verbatim_anchor_copies"], 1)
        self.assertIn(2, result["failing_pages"])

    def test_developed_recurrence_passes(self):
        pages = [page(0, "q001", PAGE_A),
                 page(1, "q002", PAGE_B_DEVELOPED)]
        result = check_refrain(pages)
        self.assertTrue(result["development_pass"])
        self.assertEqual(result["thematic_recurrences"], 1)
        self.assertEqual(result["developed_recurrences"], 1)
        self.assertEqual(result["verbatim_anchor_copies"], 0)

    def test_undeveloped_recurrence_fails(self):
        # Same anchor words reshuffled, nothing new absorbed: a
        # recurrence in wording only, not in meaning.
        pages = [page(0, "q001", PAGE_A),
                 page(1, "q002", PAGE_UNDEVELOPED)]
        result = check_refrain(pages)
        self.assertFalse(result["development_pass"])
        self.assertEqual(result["thematic_recurrences"], 1)
        self.assertEqual(result["developed_recurrences"], 0)
        self.assertIn(1, result["failing_pages"])

    def test_no_recurrence_passes(self):
        pages = [page(0, "q001", PAGE_A),
                 page(1, "q002", PAGE_B_DISTINCT)]
        result = check_refrain(pages)
        self.assertTrue(result["development_pass"])
        self.assertEqual(result["thematic_recurrences"], 0)


class LongModelRecorder:
    """Records every prompt; page 1 is the long page, every
    later page the distinct one."""

    name = "long-recorder-test-model"

    def __init__(self):
        self.prompts: list[str] = []

    def complete(self, prompt: str, max_tokens: int = 512) -> str:
        self.prompts.append(prompt)
        if "TASK: SUMMARIZE_CHAPTER" in prompt:
            return "Synopsis of the chapter."
        if "QUESTION_ID: q001" in prompt:
            return PAGE_LONG_A
        return PAGE_B_DISTINCT


class AnchorCopyModel:
    """Always returns a page that copies the anchor sentence
    verbatim, retry or not."""

    name = "anchor-copy-test-model"

    def complete(self, prompt: str, max_tokens: int = 512) -> str:
        if "TASK: SUMMARIZE_CHAPTER" in prompt:
            return "Synopsis of the chapter."
        if "QUESTION_ID: q001" in prompt:
            return PAGE_A
        return PAGE_B_ANCHOR_COPY


class FlakyRefrainModel:
    """Copies the anchor until the retry calls for development,
    then restates the theme developed, with newer material."""

    name = "flaky-refrain-test-model"

    def complete(self, prompt: str, max_tokens: int = 512) -> str:
        if "TASK: SUMMARIZE_CHAPTER" in prompt:
            return "Synopsis of the chapter."
        if "QUESTION_ID: q001" in prompt:
            return PAGE_A
        if "RETRY" in prompt:
            return PAGE_B_DEVELOPED
        return PAGE_B_ANCHOR_COPY


class TestRefrainOn(unittest.TestCase):
    """Refrain on: the anchor theme is carried as a theme and must
    return developed. Verbatim copying is regenerated against in
    this setting too, and the report names the development verdict."""

    def test_anchor_copy_regenerated_and_named_on_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            builder = BookBuilder(refrain_pack(), ANSWERS,
                                  AnchorCopyModel(),
                                  Path(tmp) / "state.json")
            report = builder.build()
        kept = builder.state["pages"]["q002"]
        self.assertEqual(kept["duplication_retries"], 2)
        analysis = report["refrain_analysis"]
        self.assertFalse(analysis["development_pass"])
        self.assertEqual(analysis["verbatim_anchor_copies"], 1)
        self.assertEqual(analysis["failing_pages"], [1])

    def test_developed_retry_is_kept_and_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            builder = BookBuilder(refrain_pack(), ANSWERS,
                                  FlakyRefrainModel(),
                                  Path(tmp) / "state.json")
            report = builder.build()
        kept = builder.state["pages"]["q002"]
        self.assertEqual(kept["text"], PAGE_B_DEVELOPED)
        self.assertEqual(kept["duplication_retries"], 1)
        analysis = report["refrain_analysis"]
        self.assertTrue(analysis["development_pass"])
        self.assertEqual(analysis["developed_recurrences"], 1)

    def test_anchor_theme_carried_not_full_pages(self):
        class LongModel:
            name = "long-test-model"

            def __init__(self):
                self.prompts: list[str] = []

            def complete(self, prompt: str,
                         max_tokens: int = 512) -> str:
                self.prompts.append(prompt)
                if "TASK: SUMMARIZE_CHAPTER" in prompt:
                    return "Synopsis of the chapter."
                if "QUESTION_ID: q001" in prompt:
                    return PAGE_LONG_A
                return PAGE_B_DISTINCT

        model = LongModel()
        with tempfile.TemporaryDirectory() as tmp:
            builder = BookBuilder(refrain_pack(), ANSWERS, model,
                                  Path(tmp) / "state.json")
            builder.build()
        page_prompts = [p for p in model.prompts
                        if "TASK: SUMMARIZE_CHAPTER" not in p]
        prompt2 = page_prompts[1]
        # The book's first sentence is carried into the prompt of
        # the slot that assigns the return, with the development
        # directive -- phrased without the apparatus vocabulary
        # ("anchor", "theme", "refrain") that the first
        # devotional's prose then repeated back (the meta fix).
        self.assertIn("the harbor bell rang over the water at dawn",
                      prompt2)
        # The development directive, in the plain wording the
        # V17 rewording settled on: the earlier formula ("let
        # it arrive changed by the days since...") was quoted
        # back as narration by the corrected devotional and is
        # now on the meta screen instead (tests/test_metagate).
        self.assertIn("write it as today has remade it",
                      prompt2)
        self.assertNotIn("let it arrive changed", prompt2)
        self.assertNotIn("anchor theme", prompt2)
        self.assertNotIn("REFRAIN", prompt2)
        # But the first page is not fed forward in full: a middle
        # sentence of page 1, outside the closing excerpt, is absent.
        self.assertNotIn("quartermaster hid the silver compass",
                         prompt2)

    def test_return_carried_only_where_the_slot_assigns_it(self):
        """The saturation fix: with refrain on, a page whose slot
        does not assign the return device receives no return
        block at all -- in the first devotional the block rode
        on all 100 prompts while 21 slots assigned the device,
        and the book filled with near-verbatim returns."""
        pack = refrain_pack()
        pack["questions"].append({
            "id": "q003", "chapter": "ch01", "prompt": "p3",
            "narrative_job": "j3", "position": "pos3",
            "devices": ["scene_reconstruction"],
            "bible_keys": ["subject.later"]})
        answers = dict(ANSWERS)
        answers["q003"] = "Answer three."
        model = LongModelRecorder()
        with tempfile.TemporaryDirectory() as tmp:
            builder = BookBuilder(pack, answers, model,
                                  Path(tmp) / "state.json")
            builder.build()
        page_prompts = [p for p in model.prompts
                        if "TASK: SUMMARIZE_CHAPTER" not in p]
        # q002 assigns the return; q003 does not.
        self.assertIn("The first page said:",
                      page_prompts[1])
        self.assertNotIn("The first page said:",
                         page_prompts[2])

    def test_undeveloped_recurrence_regenerated_at_generation(self):
        """The generation-time development screen: a thematic
        recurrence carrying nothing new fails alongside verbatim
        duplication, and a developed retry replaces it."""
        class UndevelopedThenDeveloped:
            name = "undeveloped-then-developed"

            def complete(self, prompt: str,
                         max_tokens: int = 512) -> str:
                if "TASK: SUMMARIZE_CHAPTER" in prompt:
                    return "Synopsis of the chapter."
                if "QUESTION_ID: q001" in prompt:
                    return PAGE_A
                if "RETRY" in prompt:
                    return PAGE_B_DEVELOPED
                return PAGE_UNDEVELOPED

        with tempfile.TemporaryDirectory() as tmp:
            builder = BookBuilder(refrain_pack(), ANSWERS,
                                  UndevelopedThenDeveloped(),
                                  Path(tmp) / "state.json")
            report = builder.build()
        kept = builder.state["pages"]["q002"]
        self.assertEqual(kept["text"], PAGE_B_DEVELOPED)
        self.assertEqual(kept["duplication_retries"], 1)
        self.assertEqual(kept["refrain_undeveloped"], 0)
        self.assertTrue(
            report["refrain_analysis"]["development_pass"])


class TestRefrainCliOverride(unittest.TestCase):
    """The build-time CLI flag overrides the pack default, and the
    report records the effective setting."""

    def _run_cli(self, tmp: str, *extra: str) -> dict:
        from engine.cli import main as cli_main
        out = Path(tmp) / "book"
        rc = cli_main([
            "build",
            "--pack", str(ROOT / "packs" / "biography.json"),
            "--answers",
            str(ROOT / "demo" / "biography-demo-answers.json"),
            "--model", "stub",
            "--out", str(out),
            "--title", "T", "--persona-note", "P", "--colophon", "C",
            *extra,
        ])
        self.assertEqual(rc, 0)
        with open(out / "report.json", encoding="utf-8") as fh:
            return json.load(fh)

    def test_pack_default_applies_without_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = self._run_cli(tmp)
        self.assertIs(report["refrain"], False)

    def test_refrain_flag_overrides_pack_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = self._run_cli(tmp, "--refrain")
        self.assertIs(report["refrain"], True)

    def test_no_refrain_flag_keeps_off(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = self._run_cli(tmp, "--no-refrain")
        self.assertIs(report["refrain"], False)


if __name__ == "__main__":
    unittest.main()
