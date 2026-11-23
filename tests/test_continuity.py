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


if __name__ == "__main__":
    unittest.main()
