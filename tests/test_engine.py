"""Engine sequencing tests with a deterministic recording stub model.

The central claim under test: page N is generated conditioned on the
state accumulated from pages before it. A sentinel token is placed in
the first answer (where only the story bible can carry it forward);
the recorded prompt for a later page must contain it, and the
recorded prompt for a page in chapter 2 must contain chapter 1's
rolling synopsis. The empty-answer control verifies that a blank
answer produces no page and is reported, never padded.
"""

import tempfile
import unittest
from pathlib import Path

from engine.generate import BookBuilder
from engine.model import StubModel


def tiny_pack() -> dict:
    return {
        "genre": "memoir",
        "version": "test",
        "framework": {
            "voice": "test voice",
            "pov": "first person",
            "refrain": False,
            "tense": "past",
            "page_target_words": 250,
            "global_instructions": "test instructions",
            "devices": {
                "scene_rendering": {
                    "name": "Scene rendering",
                    "instruction": "render a scene",
                },
            },
        },
        "chapters": [
            {"id": "ch01", "title": "One"},
            {"id": "ch02", "title": "Two"},
        ],
        "questions": [
            {"id": "q001", "chapter": "ch01", "prompt": "p1",
             "narrative_job": "j1", "position": "pos1",
             "devices": ["scene_rendering"],
             "bible_keys": ["people.mother"]},
            {"id": "q002", "chapter": "ch01", "prompt": "p2",
             "narrative_job": "j2", "position": "pos2",
             "devices": ["scene_rendering"],
             "bible_keys": ["places.home"]},
            {"id": "q003", "chapter": "ch02", "prompt": "p3",
             "narrative_job": "j3", "position": "pos3",
             "devices": ["scene_rendering"],
             "bible_keys": ["motifs.thing"]},
        ],
    }


class RecordingStub(StubModel):
    def __init__(self):
        self.prompts: list[str] = []

    def complete(self, prompt: str, max_tokens: int = 512) -> str:
        self.prompts.append(prompt)
        return super().complete(prompt, max_tokens)


class TestSequencing(unittest.TestCase):
    def _build(self, answers):
        model = RecordingStub()
        with tempfile.TemporaryDirectory() as tmp:
            builder = BookBuilder(tiny_pack(), answers, model,
                                  Path(tmp) / "state.json")
            report = builder.build()
            return model, builder, report

    def test_bible_state_conditions_later_pages(self):
        answers = {
            "q001": "My mother kept a SENTINEL_ALPHA in the kitchen.",
            "q002": "The house stood at the end of a dirt road.",
            "q003": "Years later I understood the kitchen differently.",
        }
        model, builder, report = self._build(answers)
        self.assertEqual(report["pages_built"], 3)
        page_prompts = [p for p in model.prompts
                        if "TASK: SUMMARIZE_CHAPTER" not in p]
        # Page 2's prompt must carry page 1's bible entry (the sentinel
        # appears in no other answer and in no framework text).
        self.assertIn("SENTINEL_ALPHA", page_prompts[1])
        # Page 3 (chapter 2) must also carry it, via the bible.
        self.assertIn("SENTINEL_ALPHA", page_prompts[2])

    def test_synopsis_conditions_next_chapter(self):
        answers = {
            "q001": "First answer.",
            "q002": "Second answer.",
            "q003": "Third answer.",
        }
        model, builder, report = self._build(answers)
        page_prompts = [p for p in model.prompts
                        if "TASK: SUMMARIZE_CHAPTER" not in p]
        # Chapter 2's page prompt includes chapter 1's synopsis.
        self.assertIn("Stub synopsis of chapter ch01", page_prompts[2])
        # And chapter 1's pages were written before any synopsis existed.
        self.assertNotIn("Stub synopsis", page_prompts[0])

    def test_recent_page_excerpt_present(self):
        answers = {
            "q001": "First answer.",
            "q002": "Second answer.",
            "q003": "Third answer.",
        }
        model, builder, report = self._build(answers)
        page_prompts = [p for p in model.prompts
                        if "TASK: SUMMARIZE_CHAPTER" not in p]
        # Page 3's prompt carries the closing lines of page 2 as
        # background (the stub page's final sentence), but not page 2
        # in full: its opening sentence must be absent. Feeding whole
        # pages forward is what taught the first book to repeat them.
        self.assertIn("The page for q002 ends here", page_prompts[2])
        self.assertNotIn("This is the stub page for question q002",
                         page_prompts[2])

    def test_resume_repairs_missing_synopsis(self):
        """The interruption defect, as a regression test: a build
        that stops between a chapter's last page save and its
        synopsis write leaves pages without a synopsis, and the
        resumed build used to skip the finished pages and ship the
        gap (memoir chapter 9, biography chapter 7). A resumed
        build must regenerate the missing synopsis from the saved
        pages, without regenerating any page."""
        import json
        answers = {
            "q001": "First answer.",
            "q002": "Second answer.",
            "q003": "Third answer.",
        }
        with tempfile.TemporaryDirectory() as tmp:
            state_path = Path(tmp) / "state.json"
            first = BookBuilder(tiny_pack(), answers, RecordingStub(),
                                state_path)
            report = first.build()
            self.assertEqual(report["pages_built"], 3)
            self.assertIn("ch01", first.state["synopses"])
            page_texts = {qid: p["text"] for qid, p in
                          first.state["pages"].items()}

            # Simulate the interruption: chapter 1's pages survive,
            # its synopsis does not.
            state = json.loads(state_path.read_text(encoding="utf-8"))
            del state["synopses"]["ch01"]
            state_path.write_text(json.dumps(state), encoding="utf-8")

            resumed_model = RecordingStub()
            resumed = BookBuilder(tiny_pack(), answers, resumed_model,
                                  state_path)
            report = resumed.build()
            self.assertEqual(report["pages_built"], 3)
            # The synopsis was regenerated from the saved pages...
            self.assertIn("Stub synopsis of chapter ch01",
                          resumed.state["synopses"]["ch01"])
            # ...and no page was regenerated to do it: the only
            # model call of the resumed build is the synopsis call,
            # and every page text is byte-identical.
            self.assertEqual(len(resumed_model.prompts), 1)
            self.assertIn("TASK: SUMMARIZE_CHAPTER",
                          resumed_model.prompts[0])
            self.assertEqual(
                {qid: p["text"] for qid, p in
                 resumed.state["pages"].items()}, page_texts)

    def test_empty_answer_produces_no_page(self):
        answers = {
            "q001": "First answer.",
            "q002": "   ",
            "q003": "Third answer.",
        }
        model, builder, report = self._build(answers)
        self.assertEqual(report["pages_built"], 2)
        self.assertEqual(report["skipped_empty"], ["q002"])
        self.assertNotIn("q002", builder.state["pages"])


if __name__ == "__main__":
    unittest.main()
