"""Tests for the generation-time subject-gender gate.

The positive controls are the measured instances from the
series record: The Keeping Book page 79 (DEFECTS.md, F4) and
The Day Book pages 100 and 94 (DEFECTS.md, S7). The negative
controls are sentences from The Keeping Book whose female
pronouns and role words attach to the book's female cast; the
gate is a referent screen, not a pronoun ban, and those
sentences must pass untouched.
"""

import unittest

from engine.gendergate import sentence_flags, subject_gender_flags


class TestDefiniteInstancesFlag(unittest.TestCase):
    def test_keeping_book_page_79_two_women(self):
        sentence = ("In my lifetime, it falls to my mother and "
                    "I—two women who have embraced the same task.")
        self.assertIn("group_inclusion", sentence_flags(sentence))

    def test_day_book_page_100_appositive_daughter(self):
        sentence = ("When I, Ruby's son and Onyx's daughter, "
                    "arrived later at the social to see what "
                    "damage my mother had caused, she smiled "
                    "with pride.")
        self.assertIn("self_ascription", sentence_flags(sentence))

    def test_day_book_page_94_herself_appositive(self):
        sentence = ("That night, I sat at my father's bench in "
                    "the front room of our house, a piano teacher "
                    "and church organist herself.")
        self.assertIn("herself_appositive",
                      sentence_flags(sentence))

    def test_predicate_daughter(self):
        sentence = "I am a daughter of the Flames line."
        self.assertIn("self_ascription", sentence_flags(sentence))

    def test_predicate_through_possessive(self):
        sentence = "I am my mother's daughter in this."
        self.assertIn("self_ascription", sentence_flags(sentence))


class TestCastSentencesPass(unittest.TestCase):
    def assert_clean(self, sentence):
        self.assertEqual(sentence_flags(sentence), [], sentence)

    def test_mother_named_with_she(self):
        self.assert_clean(
            "My mother was Ruby Flames, of the Flames lineage—a "
            "family that traced back generations from Mississippi "
            "to Texas before settling in Dallas where she was "
            "born in 1975.")

    def test_wife_amber(self):
        self.assert_clean(
            "My wife, born Amber Verano, arrived as a photographer "
            "hired to photograph a session at the Cold Room and "
            "married me that year.")

    def test_her_son_is_male_and_clean(self):
        self.assert_clean(
            "My childhood rooms were a mix: the shop where my "
            "father let me rewire lamps and guitars by nine, "
            "inspecting and redoing them until they worked "
            "perfectly; and the front room where my mother taught "
            "me on the piano, whether I was her son or not.")

    def test_herself_with_cast_names_present(self):
        self.assert_clean(
            "I see this practiced by Ruby in every detail of her "
            "life: she keeps a daily record of thoughts and "
            "feelings, an act inherited from her mother Jet, who "
            "kept household books herself.")

    def test_generic_women_keepers(self):
        self.assert_clean(
            "In the first generations, women were the keepers of "
            "these records: Jet Flames' household books and piano "
            "lessons in a front room passed down to Ruby's steady "
            "hands on her lesson books.")

    def test_her_daughter_ruby(self):
        self.assert_clean(
            "The tradition lived on through her daughter Ruby, "
            "who wrote down every day with care and precision "
            "like her mother before her—keeping the household's "
            "heat alive even in the coldest weather.")

    def test_taught_by_my_mother(self):
        self.assert_clean(
            "I was taught the record-keeping by my mother, and "
            "I learned the bench from my father.")

    def test_i_am_the_one_who(self):
        # The Keeping Book, page 70: the role word sits twenty
        # words past the predicate and belongs to a list of the
        # narrator's teachers, not to the narrator.
        self.assert_clean(
            "The family's records and heirlooms are in my keeping "
            "now, and I was not chosen so much as fallen to: I am "
            "the one who writes things down, the keeper by habit, "
            "trained by a father with a day book and a mother "
            "with a Bible.")

    def test_plain_male_narration(self):
        self.assert_clean(
            "I learned the bench from my father, and my hands "
            "are steady on the tools he left me.")


class TestScreenOverreachIsPinned(unittest.TestCase):
    """The unresolved_she rule is a screen, not a verdict: it
    flags a first-person sentence whose "she" belongs to a woman
    named only in a neighbouring sentence. The behaviour is
    pinned here so the overreach is a documented property, and
    the post-build S7 audit remains the arbiter."""

    def test_pearl_sentence_trips_only_unresolved_she(self):
        sentence = ("She passed this legacy on to me, as I know "
                    "her through the accounts she meticulously "
                    "entered.")
        self.assertEqual(sentence_flags(sentence),
                         ["unresolved_she"])


class TestPageLevel(unittest.TestCase):
    def test_clean_page(self):
        page = ("My mother was Ruby Flames. She kept the books "
                "with care. I learned the bench from my father.")
        self.assertEqual(subject_gender_flags(page), [])

    def test_page_with_violation(self):
        page = ("The work went on as it always had. In my "
                "lifetime, it falls to my mother and I—two women "
                "who have embraced the same task.")
        flags = subject_gender_flags(page)
        self.assertEqual(len(flags), 1)
        self.assertIn("group_inclusion", flags[0]["rules"])


if __name__ == "__main__":
    unittest.main()
