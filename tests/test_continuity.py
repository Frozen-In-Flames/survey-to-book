"""Continuity checker tests, including the planted-contradiction
negative control: a page that renames the narrator's mother against
the bible's fixed fact MUST be flagged, and a consistent set of pages
must produce no fact-contradiction flags.
"""

import unittest

from engine.continuity import check_continuity

FACTS = {
    "mother_name": {
        "slot": "mother_name", "kind": "person_name",
        "value": "Elena Vasquez",
        "triggers": ["my mother", "Mother"],
        "source_question": "q001",
    },
    "birth_year": {
        "slot": "birth_year", "kind": "year", "value": "1962",
        "triggers": ["born in", "I was born"],
        "source_question": "q002",
    },
}


def page(index, qid, text):
    return {"index": index, "question_id": qid, "text": text}


class TestContinuity(unittest.TestCase):
    def test_consistent_pages_pass(self):
        pages = [
            page(0, "q001", "Elena Vasquez ran the cafe on Harbor Street."),
            page(1, "q002", "I was born in 1962, in the spring."),
            page(2, "q003",
                 "My mother Elena Vasquez kept the ledger by hand, and "
                 "my mother, Elena, sang while she worked."),
        ]
        issues = check_continuity(pages, FACTS)
        contradictions = [i for i in issues
                          if i["type"] == "fact_contradiction"]
        self.assertEqual(contradictions, [])

    def test_planted_contradiction_is_flagged(self):
        pages = [
            page(0, "q001", "Elena Vasquez ran the cafe on Harbor Street."),
            page(1, "q002", "I was born in 1962, in the spring."),
            page(2, "q003",
                 "Years later I thought about my mother, Rosa Delgado, "
                 "and the house she kept."),
        ]
        issues = check_continuity(pages, FACTS)
        contradictions = [i for i in issues
                          if i["type"] == "fact_contradiction"
                          and i["fact_slot"] == "mother_name"]
        self.assertEqual(len(contradictions), 1)
        self.assertEqual(contradictions[0]["found"], "Rosa Delgado")
        self.assertEqual(contradictions[0]["page_index"], 2)

    def test_planted_year_contradiction_is_flagged(self):
        pages = [
            page(0, "q001", "Elena Vasquez ran the cafe."),
            page(1, "q002", "I was born in 1962, in the spring."),
            page(2, "q003", "She liked to say I was born in 1958, "
                            "though the certificate disagreed."),
        ]
        issues = check_continuity(pages, FACTS)
        contradictions = [i for i in issues
                          if i["type"] == "fact_contradiction"
                          and i["fact_slot"] == "birth_year"]
        self.assertEqual(len(contradictions), 1)

    def test_nickname_is_not_a_contradiction(self):
        pages = [
            page(0, "q001", "Elena Vasquez ran the cafe."),
            page(1, "q002", "I was born in 1962."),
            page(2, "q003", "My mother, Lena, laughed at the story."),
        ]
        issues = check_continuity(pages, FACTS)
        contradictions = [i for i in issues
                          if i["type"] == "fact_contradiction"]
        self.assertEqual(contradictions, [])

    def test_grandfather_name_is_not_a_father_contradiction(self):
        # Regression: the bare trigger "Father" used to match inside
        # "grandfather", flagging a correctly named grandfather as a
        # contradiction of the father's name.
        facts = {
            "father_name": {
                "slot": "father_name", "kind": "person_name",
                "value": "Henry Calloway",
                "triggers": ["my father", "Father"],
                "source_question": "q001",
            },
        }
        pages = [
            page(0, "q001", "Henry Calloway repaired engines."),
            page(1, "q002",
                 "My grandfather Tomas Delgado rowed out in the storm "
                 "and refused all thanks."),
            page(2, "q003",
                 "We had inherited the boat from my grandfather "
                 "Tomas Delgado."),
        ]
        issues = check_continuity(pages, facts)
        contradictions = [i for i in issues
                          if i["type"] == "fact_contradiction"]
        self.assertEqual(contradictions, [])

    def test_grandmother_name_is_not_a_mother_contradiction(self):
        # Regression: the bare trigger "Mother" used to match inside
        # "grandmother", flagging a correctly named grandmother as a
        # contradiction of the mother's name.
        pages = [
            page(0, "q001", "Elena Vasquez ran the cafe."),
            page(1, "q002", "I was born in 1962."),
            page(2, "q003",
                 "Sunday dinner at my grandmother Odette's, where the "
                 "gumbo took two days."),
        ]
        issues = check_continuity(pages, FACTS)
        contradictions = [i for i in issues
                          if i["type"] == "fact_contradiction"]
        self.assertEqual(contradictions, [])

    def test_name_in_list_after_grandmother_is_not_flagged(self):
        # Regression: "my grandmother, Eli" used to flag Eli as the
        # mother's name, because the trigger matched inside
        # "grandmother" and the next capitalized name was taken as
        # the value.
        pages = [
            page(0, "q001", "Elena Vasquez ran the cafe."),
            page(1, "q002", "I was born in 1962."),
            page(2, "q003",
                 "Gone: my parents, my grandmother, Eli, and the "
                 "versions of my brother and myself."),
        ]
        issues = check_continuity(pages, FACTS)
        contradictions = [i for i in issues
                          if i["type"] == "fact_contradiction"]
        self.assertEqual(contradictions, [])

    def test_plural_family_name_is_not_name_drift(self):
        # Regression: "Calloways" was flagged as a one-letter drift
        # of the established name "Calloway"; a plural is the same
        # name, not a misspelling.
        facts = {
            "mother_name": {
                "slot": "mother_name", "kind": "person_name",
                "value": "Rosa Calloway",
                "triggers": ["my mother", "Mother"],
                "source_question": "q001",
            },
        }
        pages = [
            page(0, "q001", "Rosa Calloway ran the cafe."),
            page(1, "q002", "The Calloways gathered at the harbor."),
        ]
        issues = check_continuity(pages, facts)
        drift = [i for i in issues if i["type"] == "name_drift"]
        self.assertEqual(drift, [])

    def test_singular_family_name_is_not_name_drift(self):
        # Regression: the family-history book's page 15, "This is
        # the Flame family line", was flagged as a one-letter drift
        # of the established name "Flames". The singular of a plural
        # established name, used as an attributive noun, is the same
        # name, not a misspelling.
        facts = {
            "flames_line_name": {
                "slot": "flames_line_name", "kind": "person_name",
                "value": "Flames",
                "triggers": ["family name"],
                "source_question": "q001",
            },
        }
        pages = [
            page(0, "q001", "The family name of my mother's line "
                            "is Flames."),
            page(1, "q002", "This is the Flame family line, their "
                            "legacy handed down by their work."),
        ]
        issues = check_continuity(pages, facts)
        drift = [i for i in issues if i["type"] == "name_drift"]
        self.assertEqual(drift, [])

    def test_sentence_initial_common_word_is_not_name_drift(self):
        # Regression: the family-history book flagged "Yet" as a
        # one-letter drift of the established name "Jet" on seven
        # pages. "Yet" is an ordinary English word, capitalized
        # only because it opens a sentence; it shares neither the
        # name's first letter nor any mid-sentence capitalized
        # occurrence.
        facts = {
            "flames_matriarch": {
                "slot": "flames_matriarch", "kind": "person_name",
                "value": "Jet Flames",
                "triggers": ["my grandmother"],
                "source_question": "q001",
            },
        }
        pages = [
            page(0, "q001", "Jet Flames began the family Bible."),
            page(1, "q002", "Yet when we meet, people often assume "
                            "our names were simply invented."),
            page(2, "q003", "The names are stones. Yet we are not "
                            "just names; we are families who work."),
        ]
        issues = check_continuity(pages, facts)
        drift = [i for i in issues if i["type"] == "name_drift"]
        self.assertEqual(drift, [])

    def test_genuine_name_drift_is_still_flagged(self):
        # The repair above must not blind the checker: a genuine
        # near-miss spelling of an established name, sharing its
        # first letter, is still flagged.
        facts = {
            "mother_name": {
                "slot": "mother_name", "kind": "person_name",
                "value": "Elena Vasquez",
                "triggers": ["my mother", "Mother"],
                "source_question": "q001",
            },
        }
        pages = [
            page(0, "q001", "Elena Vasquez ran the cafe."),
            page(1, "q002", "At the table, Elenna kept the ledger "
                            "by hand."),
        ]
        issues = check_continuity(pages, facts)
        drift = [i for i in issues if i["type"] == "name_drift"]
        self.assertEqual(len(drift), 1)
        self.assertEqual(drift[0]["found"], "Elenna")
        self.assertEqual(drift[0]["expected"], "Elena")

    def test_mid_sentence_drift_with_different_first_letter_flagged(self):
        # A near-miss that differs in its first letter is still a
        # candidate when it appears capitalized mid-sentence, where
        # position cannot explain the capital.
        facts = {
            "mother_name": {
                "slot": "mother_name", "kind": "person_name",
                "value": "Catherine Hale",
                "triggers": ["my mother", "Mother"],
                "source_question": "q001",
            },
        }
        pages = [
            page(0, "q001", "Catherine Hale ran the cafe."),
            page(1, "q002", "At the table, Katherine kept the "
                            "ledger by hand."),
        ]
        issues = check_continuity(pages, facts)
        drift = [i for i in issues if i["type"] == "name_drift"]
        self.assertEqual(len(drift), 1)
        self.assertEqual(drift[0]["found"], "Katherine")


if __name__ == "__main__":
    unittest.main()
