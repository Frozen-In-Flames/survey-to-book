"""Tests for the meta-narrative screen (engine/metagate.py).

The positive controls are the leakage phrases measured in The
Kept Hours v0.6.0 (DEFECTS.md, V6): "anchor sentence" on 60
pages, the "carrying the newer facts" formula on 19, prompt
language reproduced on page 9. The negative controls pin the
screen's narrowness: the bare word "anchor" is the
respondent's own word for his family's saying and must pass,
and ordinary talk of entries and pages must pass.
"""

import unittest

from engine.metagate import audit_meta_terms, meta_flags, \
    meta_sentence_phrases


class TestMeasuredLeakageFlags(unittest.TestCase):
    def test_anchor_sentence(self):
        self.assertIn(
            "anchor sentence",
            meta_sentence_phrases(
                "I return to the anchor sentence before the "
                "day begins."))

    def test_carrying_the_newer_facts_formula(self):
        phrases = meta_sentence_phrases(
            "As I write today's entry, carrying the newer "
            "facts of the fire and the rebuilding, I set the "
            "table.")
        self.assertIn("carrying the newer facts", phrases)
        self.assertIn("newer facts", phrases)

    def test_prompt_language_reproduced(self):
        self.assertIn(
            "carry this theme changed",
            meta_sentence_phrases(
                "Carry this theme changed: the keeping is the "
                "day's first work."))

    def test_prompt_section_names(self):
        for phrase, sentence in (
                ("story bible",
                 "The story bible of this house is kept in a "
                 "drawer."),
                ("source answer",
                 "Each source answer becomes an entry here."),
                ("refrain",
                 "The refrain carries through the week whether "
                 "I attend to it or not.")):
            self.assertIn(phrase, meta_sentence_phrases(sentence),
                          sentence)


class TestOrdinaryProsePasses(unittest.TestCase):
    def assert_clean(self, sentence):
        self.assertEqual(meta_sentence_phrases(sentence), [],
                         sentence)

    def test_bare_anchor_is_the_respondents_word(self):
        self.assert_clean(
            "The saying is the anchor of my own keeping, and "
            "I say it standing at the table.")

    def test_entry_talk_without_the_formula(self):
        self.assert_clean(
            "As I write today's entry, the room is cold and "
            "the lamp is lit.")

    def test_plain_devotional_prose(self):
        self.assert_clean(
            "I thanked her for the bread, named the day's "
            "gifts one by one, and closed the book.")

    def test_page_talk_in_a_scene(self):
        self.assert_clean(
            "She turned the page of the day book and wrote "
            "the date in her steady hand.")


class TestPageAndAudit(unittest.TestCase):
    def test_page_level(self):
        page = ("The kettle sang before light. I return to "
                "the anchor sentence and write the day down.")
        flags = meta_flags(page)
        self.assertEqual(len(flags), 1)
        self.assertEqual(flags[0]["phrases"], ["anchor sentence"])

    def test_audit_counts(self):
        pages = [
            {"index": 0, "question_id": "q001",
             "text": "The anchor sentence opens the day. The "
                     "room was cold."},
            {"index": 1, "question_id": "q002",
             "text": "A plain page with nothing of the "
                     "machinery in it."},
        ]
        audit = audit_meta_terms(pages)
        self.assertEqual(audit["pages_with_meta_terms"], 1)
        self.assertEqual(audit["by_phrase"]["anchor sentence"], 1)


class TestRefrainFormulaLeakV17(unittest.TestCase):
    """DEFECTS V17: the refrain block's own instruction formula,
    quoted back as narration in The Kept Hours corrected edition
    (v0.6.1) on pages 50, 53 and 94. The block is reworded; the
    old formula's phrases are screened so an echo costs a retry.
    """

    def test_v061_page_94_sentence_flags(self):
        flags = meta_flags(
            "A sentence runs through this book, first said on "
            "its first page: \"in the front room where the day "
            "begins to unfold.\" If this page comes back to "
            "that sentence, let it arrive changed by the days "
            "since it was first said: what has happened since "
            "must live inside it, in fresh words.")
        self.assertTrue(flags)

    def test_v061_page_50_variant_flags(self):
        flags = meta_flags(
            "The kept sentence runs through this book. If it "
            "comes back to that sentence, let it arrive changed "
            "by the days since it was first said.")
        self.assertTrue(flags)

    def test_developed_return_in_scene_words_is_clean(self):
        self.assertEqual(meta_flags(
            "Sunlight came through the lace curtain again, but "
            "this morning it fell on the letter I had been "
            "afraid to open, and the table held one plate "
            "fewer."), [])

    def test_innocent_runs_through_is_clean(self):
        self.assertEqual(meta_flags(
            "The creek runs through this valley and under the "
            "bridge by the shop."), [])


if __name__ == "__main__":
    unittest.main()
