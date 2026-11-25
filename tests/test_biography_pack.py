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

The demonstration subject is the series' demonstration user, the
fictional persona Frozen In Flames. A canonical character record
(demo/frozen-in-flames-character.json) holds the invented facts of
the character's life exactly once; the demo answers are drawn from
it, and this suite proves the bible extracted from the answers
equals the record. The character is living, so the pack's
death_year slot is declared but deliberately unestablished by the
demo answers.

Canon history: the biography build (v0.2.0) invented the
character's core facts because the survey never asked the author.
The author set the canon himself on 2026-11-24 (born 2000 in
Dallas; mother Ruby Flames; father Onyx Frozen; partner Amber
Flames), and the corrected edition (v0.2.1) regenerated the demo
answers from the corrected record. This suite now pins agreement:
the bible extracted from the answers must equal the record's facts
exactly, with no divergent fields. The v0.2.0 book and its answers
stand in git history at that tag.
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
    "subject_name": "Frozen In Flames",
    "birth_year": "2000",
    "birthplace": "Dallas",
    "mother_name": "Ruby Flames",
    "father_name": "Onyx Frozen",
    "partner_name": "Amber Flames",
}

PACK_FACT_SLOTS = set(EXPECTED_FACTS) | {"death_year"}


class TestBiographyPack(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack = load_pack(ROOT / "packs" / "biography.json")
        with open(ROOT / "demo" / "biography-demo-answers.json",
                  encoding="utf-8") as fh:
            cls.demo = json.load(fh)
        cls.answers = cls.demo["answers"]
        with open(ROOT / "demo" / "frozen-in-flames-character.json",
                  encoding="utf-8") as fh:
            cls.character = json.load(fh)

    def test_pack_is_valid(self):
        self.assertEqual(validate_pack(self.pack), [])

    def test_genre_and_version(self):
        self.assertEqual(self.pack["genre"], "biography")
        self.assertEqual(self.pack["version"], "1.0.0")

    def test_third_person_framework(self):
        # The pack's defining difference from memoir is point of view.
        self.assertEqual(self.pack["framework"]["pov"], "third person")

    def test_refrain_default_off(self):
        # Biography is third-person and chronological; recurrence
        # reads as error rather than voice, so the pack's refrain
        # default is off. The author's call (2026-11-24) keeps it
        # off for the corrected edition as well.
        self.assertIs(self.pack["framework"]["refrain"], False)

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
        self.assertEqual(slots, PACK_FACT_SLOTS)

    def test_identity_question_asks_for_subject(self):
        """Clean-proof corollary: who the book's subject is is
        respondent data, elicited by an explicit identity question
        early in the survey -- never a fact the build supplies.
        The question declaring the subject_name fact must sit in
        the first chapter and must ask, in terms, who the
        biography's subject is; its demo answer names the series'
        demonstration user, from the canonical record."""
        identity = [q for q in self.pack["questions"]
                    if q.get("fact", {}).get("slot") == "subject_name"]
        self.assertEqual(len(identity), 1)
        question = identity[0]
        self.assertEqual(question["chapter"],
                         self.pack["questions"][0]["chapter"])
        self.assertIn("subject of this biography",
                      question["prompt"].lower())
        self.assertTrue(
            self.answers[question["id"]].startswith("Frozen In Flames"))

    def test_demo_answers_labeled_fabricated(self):
        self.assertIn("Frozen In Flames", self.demo["persona"])
        self.assertIn("fictional", self.demo["persona"].lower())
        self.assertIn("fabricated", self.demo["provenance"].lower())

    def test_answers_align_with_questions(self):
        """The memoir defect, as a test: ids must intersect fully."""
        qids = [q["id"] for q in self.pack["questions"]]
        self.assertEqual(sorted(self.answers), sorted(qids))
        for qid in qids:
            self.assertTrue(self.answers[qid].strip(),
                            f"{qid} has an empty answer")

    def _bible(self):
        bible = Bible()
        for q in self.pack["questions"]:
            bible.update_from_answer(q, self.answers[q["id"]])
        return bible

    def _extracted_facts(self):
        return {slot: fact["value"]
                for slot, fact in self._bible().facts.items()}

    def test_facts_extract_expected_values(self):
        extracted = self._extracted_facts()
        self.assertEqual(extracted, EXPECTED_FACTS)
        # The character is living: no death fact may be established.
        self.assertNotIn("death_year", extracted)

    def test_character_record_agrees_with_answers(self):
        """Corrected edition: the bible extracted from the demo
        answers and the canonical character record must agree
        exactly -- the supersession the v0.2.0 answers carried is
        resolved, and any future divergence between the record and
        the answers fails here."""
        record_facts = {k: str(v)
                        for k, v in self.character["facts"].items()}
        extracted = self._extracted_facts()
        self.assertEqual(extracted, record_facts)
        self.assertEqual(self.character["character"]["name"],
                         "Frozen In Flames")
        self.assertEqual(record_facts["birth_year"], "2000")
        self.assertEqual(record_facts["birthplace"], "Dallas")

    def test_fact_traceability_coverage(self):
        """Completeness gate: every bible fact traces to a survey
        answer. Coverage is measured as facts traced / total
        facts; an untraced fact fails the suite. The pack declares
        one further slot, death_year, which the living subject's
        answers deliberately leave unestablished."""
        bible = self._bible()
        questions = {q["id"]: q for q in self.pack["questions"]}
        traced = 0
        for slot, fact in bible.facts.items():
            qid = fact["source_question"]
            self.assertIn(qid, questions,
                          f"{slot}: source question {qid} not in pack")
            question = questions[qid]
            self.assertIn("fact", question,
                          f"{slot}: {qid} declares no fact")
            self.assertEqual(question["fact"]["slot"], slot,
                             f"{slot}: {qid} declares "
                             f"{question['fact']['slot']}")
            self.assertTrue(self.answers[qid].strip(),
                            f"{slot}: {qid} has an empty answer")
            traced += 1
        total = len(bible.facts)
        self.assertEqual(total, len(EXPECTED_FACTS))
        self.assertEqual(traced / total, 1.0)

    def test_stub_build_produces_full_book(self):
        """End-to-end plumbing: 100 answers in, 100 pages out."""
        with tempfile.TemporaryDirectory() as tmp:
            builder = BookBuilder(self.pack, self.answers, StubModel(),
                                  Path(tmp) / "state.json")
            report = builder.build()
        self.assertEqual(report["pages_built"], 100)
        self.assertEqual(report["skipped_empty"], [])
        self.assertEqual(report["continuity_issues"], [])
        self.assertIs(report["refrain"], False)
        self.assertEqual(
            report["duplication"]["pages_sharing_sentence_with_previous"],
            0)


if __name__ == "__main__":
    unittest.main()
