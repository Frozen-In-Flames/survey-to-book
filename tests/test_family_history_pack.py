"""Family-history pack tests: schema, structure, answer alignment,
record agreement, and fact traceability.

The memoir pack's first commit shipped with a defect this suite
exists to prevent from recurring: the pack's question ids and the
demo answers' ids did not intersect, so the pairing of pack and
answers was never actually exercised. These tests therefore prove,
before any generation is attempted, that the family-history pack
and its demonstration answers align exactly: every question has
exactly one non-empty answer, no answer names an unknown question,
and the typed facts the pack declares are the values the bible
extracts from those answers.

The demonstration respondent is the series' demonstration user,
the fictional persona Frozen In Flames, answering the survey about
his own invented family: two lines -- the Flames line of his
mother Ruby Flames and the Frozen line of his father Onyx Frozen --
traced separately and converging in his parents' marriage and in
his own name. A canonical character record
(demo/frozen-in-flames-character.json, record version 2.0.0) holds
the facts of the character and his family exactly once; the demo
answers were drawn from it, and this suite proves the bible
extracted from the answers equals the record's facts.

Canon (2026-11-24): the character's core facts were set by the
author himself and supersede the values the biography build
invented (born 1960 in Memphis; mother Evelyn Flames; father
Harold Flames; partner Alice Flames): born 2000 in Dallas, Texas;
white American male, red hair, blue eyes; mother Ruby Flames;
father Onyx Frozen; partner Amber Flames. Every family member's
first name is a crystal or gem name, enforced below against the
record's explicit list; the respondent is the sole exception, his
name being the two family surnames joined.

Completeness gate: every fact in the story bible must trace to a
survey answer. The bible carries each fact's source question id;
the traceability test below proves, for every extracted fact, that
the source question exists, declares that fact's slot, and has a
non-empty answer -- measured coverage is facts traced / total
facts, and any untraced fact fails the suite.
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
    "flames_line_name": "Flames",
    "frozen_line_name": "Frozen",
    "subject_name": "Frozen In Flames",
    "mother_name": "Ruby Flames",
    "father_name": "Onyx Frozen",
    "flames_founding_ancestor": "Garnet Flames",
    "flames_origin_place": "Holly Springs",
    "flames_migration_year": "1949",
    "flames_matriarch": "Jet Flames",
    "flames_patriarch": "Slate Flames",
    "frozen_founding_ancestor": "Flint Frozen",
    "frozen_origin_place": "Pittsburgh",
    "frozen_migration_year": "1947",
    "frozen_matriarch": "Pearl Frozen",
    "frozen_patriarch": "Jasper Frozen",
    "birth_year": "2000",
    "birthplace": "Dallas",
    "partner_name": "Amber Flames",
}

PACK_FACT_SLOTS = set(EXPECTED_FACTS)


class TestFamilyHistoryPack(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack = load_pack(ROOT / "packs" / "family-history.json")
        with open(ROOT / "demo" / "family-history-demo-answers.json",
                  encoding="utf-8") as fh:
            cls.demo = json.load(fh)
        cls.answers = cls.demo["answers"]
        with open(ROOT / "demo" / "frozen-in-flames-character.json",
                  encoding="utf-8") as fh:
            cls.character = json.load(fh)

    def test_pack_is_valid(self):
        self.assertEqual(validate_pack(self.pack), [])

    def test_genre_and_version(self):
        self.assertEqual(self.pack["genre"], "family-history")
        self.assertEqual(self.pack["version"], "1.0.0")

    def test_first_person_framework(self):
        # Family history is the respondent narrating their own
        # family's record: first person, like memoir.
        self.assertEqual(self.pack["framework"]["pov"], "first person")

    def test_refrain_default_on(self):
        # A family saying returning across generations, developed
        # in each era, is this genre's native structure; the pack
        # default is refrain on, bounded by the verbatim guard and
        # the development check.
        self.assertIs(self.pack["framework"]["refrain"], True)

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

    def test_two_lines_modelled_separately(self):
        """The pack's structural spine: each line has its own
        founding ancestor, origin place, migration year, matriarch,
        and patriarch fact slots."""
        for line in ("flames", "frozen"):
            for kind in ("line_name", "founding_ancestor",
                         "origin_place", "migration_year", "matriarch",
                         "patriarch"):
                self.assertIn(f"{line}_{kind}", PACK_FACT_SLOTS)

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
        self.assertEqual(self._extracted_facts(), EXPECTED_FACTS)

    def test_character_record_agrees_with_answers(self):
        """Unlike the biography, whose shipped answers predate the
        canon correction, the family-history answers were generated
        from the corrected record: the extracted bible must equal
        the record's facts and family facts exactly, as strings."""
        record_facts = {k: str(v)
                        for k, v in self.character["facts"].items()}
        record_facts.update(
            {k: str(v)
             for k, v in self.character["family_facts"].items()})
        self.assertEqual(self._extracted_facts(), record_facts)
        self.assertEqual(self.character["character"]["name"],
                         "Frozen In Flames")

    def test_corrected_canon_values(self):
        """The author's canon (2026-11-24), asserted so the
        biography build's invented values cannot regress into the
        record: born 2000 in Dallas; mother Ruby Flames; father
        Onyx Frozen; partner Amber Flames; white American male,
        red hair, blue eyes."""
        facts = self.character["facts"]
        self.assertEqual(facts["birth_year"], 2000)
        self.assertEqual(facts["birthplace"], "Dallas")
        self.assertEqual(facts["mother_name"], "Ruby Flames")
        self.assertEqual(facts["father_name"], "Onyx Frozen")
        self.assertEqual(facts["partner_name"], "Amber Flames")
        character = self.character["character"]
        self.assertEqual(character["sex"], "male")
        self.assertEqual(character["nationality"], "American")
        appearance = character["appearance"]
        self.assertEqual(appearance["race"], "white")
        self.assertEqual(appearance["hair"], "red")
        self.assertEqual(appearance["eyes"], "blue")

    def test_gem_name_law(self):
        """Every family member's first name is a crystal or gem
        name, checked against the record's explicit list. The
        respondent is the sole exception: his name is the two
        family surnames joined."""
        gem_names = set(self.character["family"]["gem_names"])
        self.assertTrue(gem_names)
        members = self.character["family"]["members"]
        self.assertTrue(members)
        for member in members:
            first = member["name"].split()[0]
            self.assertIn(first, gem_names,
                          f"{member['name']}: {first!r} is not a "
                          "crystal/gem name")
        self.assertNotIn("Frozen", gem_names)
        self.assertEqual(self.character["facts"]["subject_name"],
                         "Frozen In Flames")

    def test_fact_traceability_coverage(self):
        """Completeness gate: every bible fact traces to a survey
        answer. Coverage is measured as facts traced / total
        facts; an untraced fact fails the suite."""
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
        self.assertEqual(total, len(PACK_FACT_SLOTS))
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
        self.assertIs(report["refrain"], True)
        self.assertEqual(
            report["duplication"]["pages_sharing_sentence_with_previous"],
            0)


if __name__ == "__main__":
    unittest.main()
