"""Devotional pack tests: schema, structure, answer
alignment, record agreement, fact traceability, and the
pack's religion-agnostic design.

These tests prove, before any generation is attempted, that
the devotional pack and its demonstration answers align
exactly: every question has exactly one non-empty answer, no
answer names an unknown question, and the typed facts the
pack declares are the values the bible extracts from those
answers.

The demonstration respondent is the series' demonstration
user, the fictional persona Frozen In Flames, answering the
survey about his own invented keeping: a daily practice kept
at a kitchen table, a repair bench, the recording studio he
founded (the Cold Room), and a night day book, among the two
family lines his name joins. A canonical character record
(demo/frozen-in-flames-character.json, record version 2.0.0)
holds the facts of the character exactly once; the demo
answers were drawn from it, and this suite proves the bible
extracted from the answers agrees with the record.

Canon (2026-11-24): born 2000 in Dallas, Texas; white
American male, red hair, blue eyes; mother Ruby Flames;
father Onyx Frozen; partner Amber Flames. Every family
member's first name is a crystal or gem name, enforced below
against the record's explicit list; the respondent is the
sole exception, his name being the two family surnames
joined.

Two facts sit outside the record's fact fields: studio_year
is the founding year of the character's studio, carried in
the record's defining events (2022, the Cold Room founded in
a converted Dallas icehouse), and subject_gender (added in
pack v1.1.0) is the record's character sex, stated in the
identity answer. The record-agreement test below checks each
against its source.

Religion-agnostic design: the pack's questions ask about
the respondent's practices, strength, gratitude, hardship,
hope, and disciplines in the respondent's own terms. No
question prompt presumes a tradition: the tradition test
below proves no prompt names a religion, a scripture, a
rite, or a name for the divine. What the respondent holds
sacred may enter his answers in his own words; the survey
itself supplies none.

Completeness gate: every fact in the story bible must trace
to a survey answer. The bible carries each fact's source
question id; the traceability test below proves, for every
extracted fact, that the source question exists, declares
that fact's slot, and has a non-empty answer -- measured
coverage is facts traced / total facts, and any untraced
fact fails the suite.
"""

import json
import re
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
    "subject_gender": "male",
    "mother_name": "Ruby Flames",
    "father_name": "Onyx Frozen",
    "birth_year": "2000",
    "birthplace": "Dallas",
    "sister_name": "Opal Flames",
    "partner_name": "Amber Flames",
    "studio_year": "2022",
}

PACK_FACT_SLOTS = set(EXPECTED_FACTS)

# Terms whose presence in a survey question would presume a
# tradition the respondent never declared. The pack must ask
# in the respondent's own terms or in none.
TRADITION_TERMS = (
    "bible", "church", "scripture", "god", "jesus", "christ",
    "mosque", "synagogue", "temple", "quran", "torah",
    "prayer", "sermon", "hymn", "baptism", "communion",
    "christian", "muslim", "jewish", "hindu", "buddhist",
    "catholic", "protestant", "denomination", "clergy",
    "priest", "pastor", "rabbi", "imam",
)


class TestDevotionalPack(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack = load_pack(ROOT / "packs" / "devotional.json")
        with open(ROOT / "demo" / "devotional-demo-answers.json",
                  encoding="utf-8") as fh:
            cls.demo = json.load(fh)
        cls.answers = cls.demo["answers"]
        with open(ROOT / "demo" / "frozen-in-flames-character.json",
                  encoding="utf-8") as fh:
            cls.character = json.load(fh)

    def test_pack_is_valid(self):
        self.assertEqual(validate_pack(self.pack), [])

    def test_genre_and_version(self):
        self.assertEqual(self.pack["genre"], "devotional")
        # v1.1.0 is the corrected-edition revision: the
        # identity question elicits the subject's recorded
        # gender as an eleventh typed fact, and the return
        # device's wording no longer supplies the machinery's
        # vocabulary (see DEFECTS.md, V11--V12).
        self.assertEqual(self.pack["version"], "1.1.0")

    def test_first_person_framework(self):
        # A devotional is the keeper's own voice: first
        # person, like memoir, family history, the cookbook,
        # and the story collection.
        self.assertEqual(self.pack["framework"]["pov"],
                         "first person")

    def test_refrain_default_on(self):
        # Deliberate, and the opposite call from the story
        # collection: a devotional is refrain-shaped by
        # genre. The practice is the same words returned to
        # daily, and the refrain parameter is recurrence
        # with development -- the anchor sentence meets a
        # new day and is changed by what the day has done
        # since its last statement. The anchor sentence is
        # planted as answer content at q010 and returned to
        # across the chapters as content, so the theme the
        # mechanism carries is the keeping itself. The pack
        # default is refrain on; the anti-loop duplication
        # guard still applies, and the development check is
        # reported as it falls.
        self.assertIs(self.pack["framework"]["refrain"], True)

    def test_prompts_presume_no_tradition(self):
        # The pack is religion-agnostic in structure: no
        # question names a religion, a scripture, a rite,
        # or a name for the divine, and none corrects the
        # respondent's vocabulary into a tradition's.
        for q in self.pack["questions"]:
            prompt = q["prompt"].lower()
            for term in TRADITION_TERMS:
                self.assertIsNone(
                    re.search(rf"\b{term}\b", prompt),
                    f"{q['id']}: prompt presumes a tradition "
                    f"({term!r})")

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
            for field in ("id", "chapter", "prompt",
                          "narrative_job", "position", "devices",
                          "bible_keys"):
                self.assertIn(field, q, f"{q.get('id')} missing {field}")
                self.assertTrue(q[field], f"{q['id']} empty {field}")

    def _declared_slots(self, question):
        slots = set()
        if "fact" in question:
            slots.add(question["fact"]["slot"])
        for fact in question.get("facts", []):
            slots.add(fact["slot"])
        return slots

    def test_fact_slots_present(self):
        slots = set()
        for q in self.pack["questions"]:
            slots |= self._declared_slots(q)
        self.assertEqual(slots, PACK_FACT_SLOTS)

    def test_keeper_fixed_in_opening_chapter(self):
        """The pack's structural spine: the whole cast of the
        keeping -- both lines' names, the keeper, his
        parents, his birth, his sister, his partner -- is
        elicited by the first chapter, because every later
        entry stands on those names; the studio's founding
        year opens the work chapter, where the kept work
        begins."""
        first_chapter = self.pack["questions"][0]["chapter"]
        opening_slots = set()
        for q in self.pack["questions"]:
            if q["chapter"] == first_chapter:
                opening_slots |= self._declared_slots(q)
        self.assertEqual(opening_slots,
                         PACK_FACT_SLOTS - {"studio_year"})
        studio = [q for q in self.pack["questions"]
                  if q.get("fact", {}).get("slot") == "studio_year"]
        self.assertEqual(len(studio), 1)
        self.assertEqual(studio[0]["id"], "q031")

    def test_identity_question_asks_for_main_character(self):
        """Clean-proof corollary: who the main character is
        is respondent data, elicited by an explicit identity
        question early in the survey -- never a fact the
        build supplies. The question declaring the
        subject_name fact must sit in the first chapter and
        must ask, in terms, who the book's main character
        is; its demo answer names the series' demonstration
        user, from the canonical record."""
        identity = [q for q in self.pack["questions"]
                    if q.get("fact", {}).get("slot")
                    == "subject_name"]
        self.assertEqual(len(identity), 1)
        question = identity[0]
        self.assertEqual(question["chapter"],
                         self.pack["questions"][0]["chapter"])
        self.assertIn("main character",
                      question["prompt"].lower())
        self.assertTrue(
            self.answers[question["id"]].startswith(
                "Frozen In Flames"))
        # Pack v1.1.0: the same question elicits the subject's
        # recorded gender as a typed fact -- the first book's
        # narrator was cast as a wife, and the survey had
        # never asked the subject's gender at all (the
        # clean-proof rule applied to the missing fact). The
        # gender keys the engine's spouse-term screen.
        self.assertIn("man or a woman",
                      question["prompt"].lower())
        gender_facts = [f for f in question.get("facts", [])
                        if f["slot"] == "subject_gender"]
        self.assertEqual(len(gender_facts), 1)
        self.assertEqual(gender_facts[0]["kind"], "gender")
        self.assertIn("I am a man",
                      self.answers[question["id"]])

    def test_demo_answers_labeled_fabricated(self):
        self.assertIn("Frozen In Flames", self.demo["persona"])
        self.assertIn("fictional", self.demo["persona"].lower())
        self.assertIn("fabricated",
                      self.demo["provenance"].lower())

    def test_answers_align_with_questions(self):
        """The memoir defect, as a test: ids must intersect
        fully."""
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
        """The bible extracted from the answers must agree
        with the canonical record: every devotional fact
        that the record carries as a fact or family fact
        must equal it, and studio_year must equal the year
        of the record's Cold Room founding event."""
        record_facts = {k: str(v)
                        for k, v in self.character["facts"].items()}
        record_facts.update(
            {k: str(v)
             for k, v in self.character["family_facts"].items()})
        extracted = self._extracted_facts()
        for slot, value in extracted.items():
            if slot in record_facts:
                self.assertEqual(value, record_facts[slot], slot)
        studio_events = [e for e in
                         self.character["defining_events"]
                         if "Cold Room" in e["event"]
                         and "Founded" in e["event"]]
        self.assertEqual(len(studio_events), 1)
        self.assertEqual(extracted["studio_year"],
                         str(studio_events[0]["year"]))
        self.assertEqual(self.character["character"]["name"],
                         "Frozen In Flames")
        # The eleventh fact is not one of the record's fact
        # fields; it is the record's character sex, stated in
        # the identity answer under the v1.1.0 survey.
        self.assertEqual(extracted["subject_gender"],
                         self.character["character"]["sex"])

    def test_corrected_canon_values(self):
        """The author's canon (2026-11-24), asserted so the
        biography build's invented values cannot regress
        into the record: born 2000 in Dallas; mother Ruby
        Flames; father Onyx Frozen; partner Amber Flames;
        white American male, red hair, blue eyes."""
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
        """Every family member's first name is a crystal or
        gem name, checked against the record's explicit
        list. The respondent is the sole exception: his
        name is the two family surnames joined."""
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
        """Completeness gate: every bible fact traces to a
        survey answer. Coverage is measured as facts traced
        / total facts; an untraced fact fails the suite."""
        bible = self._bible()
        questions = {q["id"]: q for q in self.pack["questions"]}
        traced = 0
        for slot, fact in bible.facts.items():
            qid = fact["source_question"]
            self.assertIn(qid, questions,
                          f"{slot}: source question {qid} not "
                          "in pack")
            question = questions[qid]
            declared = set()
            if "fact" in question:
                declared.add(question["fact"]["slot"])
            for extra in question.get("facts", []):
                declared.add(extra["slot"])
            self.assertIn(slot, declared,
                          f"{slot}: {qid} declares {declared}, "
                          f"not this slot")
            self.assertTrue(self.answers[qid].strip(),
                            f"{slot}: {qid} has an empty answer")
            traced += 1
        total = len(bible.facts)
        self.assertEqual(total, len(PACK_FACT_SLOTS))
        self.assertEqual(traced / total, 1.0)

    def test_stub_build_produces_full_book(self):
        """End-to-end plumbing: 100 answers in, 100 pages
        out."""
        with tempfile.TemporaryDirectory() as tmp:
            builder = BookBuilder(self.pack, self.answers,
                                  StubModel(),
                                  Path(tmp) / "state.json")
            report = builder.build()
        self.assertEqual(report["pages_built"], 100)
        self.assertEqual(report["skipped_empty"], [])
        self.assertEqual(report["continuity_issues"], [])
        self.assertIs(report["refrain"], True)
        self.assertEqual(
            report["duplication"]
            ["pages_sharing_sentence_with_previous"], 0)


if __name__ == "__main__":
    unittest.main()
