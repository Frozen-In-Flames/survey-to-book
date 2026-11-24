"""Builds packs/family-history.json: the family-history pack (100 questions).

Each question is authored as a tuple:
    (prompt, narrative_job, [device_ids], [bible_keys], fact_or_None)
and expanded here with its chapter and generated position string.

The pack's defining difference from the memoir and biography packs
is its subject: not one life but a family across generations. For
this series' demonstration character the family has a specific
structure, set by the author: the family name splits into two lines
-- the mother's line, Flames, and the father's line, Frozen -- and
the respondent's own name, Frozen In Flames, is the union of the
two. The pack is built on that spine: the two lines are traced
separately (their own founders, origins, migrations, matriarchs,
patriarchs, trades, and records) and converge in the respondent's
parents and the respondent. Fact slots are kept per line, so each
line's facts are established by that line's own questions.

The respondent answers about his own family, so the framework
writes in the first person, as a member of the family rather than
its biographer; fact triggers are phrased from the respondent ("my
mother", "I was born", "the Flames family came to Dallas in").

Clean-proof rule (adopted 2026-11-24): if a fact had to be obtained
by asking the author outside the survey, the survey failed to ask
it, and the question belongs in the pack. The questions that exist
under this rule are marked in the chapter comments below: the two
line-name questions, the direct mother/father name-and-line
questions, the naming-tradition question (where the family's
gem-name law comes from, in-world), and the per-line founder,
origin, and migration questions that the five-interrogative audit
(who, what, when, where, how) found missing for a two-line family.

Refrain default: ON, chosen deliberately. A family history is
organized by generations, and the genre's characteristic device is
the inherited saying -- the doctrine each generation receives,
restates against its own circumstances, and hands on changed. The
canonical character record carries such a saying (Jasper Frozen's
doctrine: a family keeps what it can fix, and fixes what it
keeps), adopted by the joined family at the joining. Where
biography's single chronological life made recurrence read as
error, recurrence with development is the family history's native
structure: the generations are the return points. The refrain
definition binds as everywhere in this system: the saying returns
developed, never as a verbatim loop, and both quantities are
measured in the build report.
"""

import json
from pathlib import Path

FRAMEWORK = {
    "voice": (
        "First-person family voice: a member of the family telling "
        "its history from inside it, saying 'we' as readily as 'I', "
        "who keeps what the records show distinct from what the "
        "telling hands down and says which is which. Plain, warm, "
        "and exact about names and years; the family is rendered as "
        "people, not as a legend, and its faults are entered in the "
        "same hand as its virtues."
    ),
    "pov": "first person",
    "refrain": True,
    "tense": "past tense for the generations that are gone, present "
             "tense for the living family and what it still keeps",
    "page_target_words": 250,
    "global_instructions": (
        "Transform the respondent's answers about his family into "
        "family-history prose in the first person. The subject of "
        "every page is the family across its generations -- two "
        "lines, Frozen and Flames, traced separately and joined in "
        "the respondent -- not the respondent alone. Never "
        "contradict the story bible or the fixed facts. Do not "
        "invent named people, places, or dates that are not in the "
        "supplied material. Where the material is thin, expand by "
        "rendering its documented implications as scene and "
        "context, not by fabricating events. Keep the written "
        "record and the family telling distinct, and attribute "
        "each to its source. Let the family's doctrine return "
        "where a page calls it back, restated as the generation "
        "on the page has developed it, never copied."
    ),
    "devices": {
        "generation_portrait": {
            "name": "Generation portrait",
            "instruction": "Render one generation's world whole: its "
                           "work, its house, its weather, the public "
                           "events that pressed on it. One page should "
                           "leave one generation standing as a time, "
                           "not just a set of names.",
        },
        "lineage_rendering": {
            "name": "Lineage rendering",
            "instruction": "Trace one thing down the generations -- "
                           "a trait, a trade, a name, an object, a "
                           "wound -- and show it changing hands and "
                           "changing shape at each transfer.",
        },
        "migration_scene": {
            "name": "Migration scene",
            "instruction": "Render a leaving or an arriving as a "
                           "scene in time: what was carried, what was "
                           "left behind, the first sight of the new "
                           "place. Stay inside what the material "
                           "supports.",
        },
        "heirloom_evidence": {
            "name": "Heirloom evidence",
            "instruction": "Let a surviving object or record carry "
                           "the page: a toolbox, a Bible with names "
                           "entered in one hand, a piano, a "
                           "photograph. Describe it exactly and let "
                           "it testify about the people who kept it.",
        },
        "record_and_telling": {
            "name": "Record and telling",
            "instruction": "Set the document beside the family "
                           "story: where the Bible entry, the "
                           "certificate, or the letter agrees with "
                           "what the family tells, say so; where they "
                           "differ, keep both visible, follow the "
                           "record for fact and the telling for "
                           "meaning.",
        },
        "table_scene": {
            "name": "The table scene",
            "instruction": "Gather the family in one place -- a "
                           "kitchen table, a porch, a church supper, "
                           "a reunion -- and let the generations meet "
                           "in dialogue, habit, and appetite. Who sat "
                           "where is evidence.",
        },
        "trade_line": {
            "name": "The trade line",
            "instruction": "Follow the family's work as it passes "
                           "hand to hand: who taught whom, what the "
                           "work demanded in each era, and what it "
                           "made of the people who held it.",
        },
        "branch_and_return": {
            "name": "Branch and return",
            "instruction": "Follow a line that left -- another "
                           "city, another name, another trade -- and "
                           "weigh its distance from the root honestly: "
                           "what was kept, what was lost, what still "
                           "writes home.",
        },
        "namesake_echo": {
            "name": "Namesake echo",
            "instruction": "Where a name repeats across "
                           "generations, render both bearers and let "
                           "the repetition comment: what the name was "
                           "meant to carry, and what each bearer did "
                           "with it.",
        },
        "era_frame": {
            "name": "Era frame",
            "instruction": "Place the family against the era's "
                           "public events for a paragraph at most -- "
                           "depression, war, migration, law -- then "
                           "return to the household; the era explains "
                           "the family, it does not replace it.",
        },
        "the_doctrine": {
            "name": "The doctrine",
            "instruction": "State the family's saying or rule of "
                           "life as the generation on the page "
                           "received it, and test it against that "
                           "generation's circumstances: where it held, "
                           "where it bent, what it cost. The doctrine "
                           "returns changed by each era that speaks "
                           "it; never repeat it as a bare slogan "
                           "without the era inside it.",
        },
        "household_economy": {
            "name": "Household economy",
            "instruction": "Render how the family actually lived "
                           "in the generation on the page: income, "
                           "food, rent, debt, the work of children, "
                           "the economics of keeping a household "
                           "standing.",
        },
        "chapter_turn": {
            "name": "Chapter turn",
            "instruction": "End the page on a turn toward the next "
                           "generation: a birth, a leaving, an "
                           "inheritance changing hands, or a question "
                           "the next chapter's generation must answer.",
        },
    },
}

CHAPTERS = [
    ("ch01", "Two Names", "Act I: The Two Lines"),
    ("ch02", "The Flames Line: Fire and Music", "Act I: The Two Lines"),
    ("ch03", "The Frozen Line: Iron and Patience", "Act I: The Two Lines"),
    ("ch04", "The Parents: The Joining", "Act II: The Joining"),
    ("ch05", "My Generation", "Act II: The Joining"),
    ("ch06", "The Family Trades", "Act III: The Keeping"),
    ("ch07", "Houses, Heirlooms, and Records", "Act III: The Keeping"),
    ("ch08", "Hard Years and Partings", "Act IV: The Inheritance"),
    ("ch09", "Reunions and the Living Family", "Act IV: The Inheritance"),
    ("ch10", "What Was Passed Down", "Act IV: The Inheritance"),
]

FACT_FLAMES_NAME = {"slot": "flames_line_name", "kind": "person_name",
                    "triggers": ["the Flames family name",
                                 "the Flames line's name"]}
FACT_FROZEN_NAME = {"slot": "frozen_line_name", "kind": "person_name",
                    "triggers": ["the Frozen family name",
                                 "the Frozen line's name"]}
FACT_RESPONDENT = {"slot": "subject_name", "kind": "person_name",
                   "triggers": ["the respondent"]}
FACT_MOTHER = {"slot": "mother_name", "kind": "person_name",
               "triggers": ["my mother", "the respondent's mother"]}
FACT_FATHER = {"slot": "father_name", "kind": "person_name",
               "triggers": ["my father", "the respondent's father"]}
FACT_FLAMES_FOUNDER = {
    "slot": "flames_founding_ancestor", "kind": "person_name",
    "triggers": ["the founding ancestor of the Flames line",
                 "the Flames line's founder"]}
FACT_FLAMES_ORIGIN = {
    "slot": "flames_origin_place", "kind": "place_name",
    "triggers": ["the Flames family came from",
                 "the Flames line came from"]}
FACT_FLAMES_MIGRATION = {
    "slot": "flames_migration_year", "kind": "year",
    "triggers": ["the Flames family came to Dallas in",
                 "the Flames line came to Dallas in"]}
FACT_FLAMES_MATRIARCH = {
    "slot": "flames_matriarch", "kind": "person_name",
    "triggers": ["the Flames family's matriarch",
                 "the matriarch of the Flames line"]}
FACT_FLAMES_PATRIARCH = {
    "slot": "flames_patriarch", "kind": "person_name",
    "triggers": ["the Flames family's patriarch",
                 "the patriarch of the Flames line"]}
FACT_FROZEN_FOUNDER = {
    "slot": "frozen_founding_ancestor", "kind": "person_name",
    "triggers": ["the founding ancestor of the Frozen line",
                 "the Frozen line's founder"]}
FACT_FROZEN_ORIGIN = {
    "slot": "frozen_origin_place", "kind": "place_name",
    "triggers": ["the Frozen family came from",
                 "the Frozen line came from"]}
FACT_FROZEN_MIGRATION = {
    "slot": "frozen_migration_year", "kind": "year",
    "triggers": ["the Frozen family came to Dallas in",
                 "the Frozen line came to Dallas in"]}
FACT_FROZEN_MATRIARCH = {
    "slot": "frozen_matriarch", "kind": "person_name",
    "triggers": ["the Frozen family's matriarch",
                 "the matriarch of the Frozen line"]}
FACT_FROZEN_PATRIARCH = {
    "slot": "frozen_patriarch", "kind": "person_name",
    "triggers": ["the Frozen family's patriarch",
                 "the patriarch of the Frozen line"]}
FACT_BIRTH_YEAR = {"slot": "birth_year", "kind": "year",
                   "triggers": ["I was born"]}
FACT_BIRTHPLACE = {"slot": "birthplace", "kind": "place_name",
                   "triggers": ["I was born in"]}
FACT_PARTNER = {"slot": "partner_name", "kind": "person_name",
                "triggers": ["my wife", "the respondent's wife"]}

Q = {}
# Chapter 1 -- Two Names. The line-name questions, the direct
# mother/father name-and-line questions, and the naming-tradition
# question exist under the clean-proof rule: these facts had to be
# asked outside the survey before the rule put them in it.
Q["ch01"] = [
    ("What is the family name of your mother's line -- the surname "
     "her family carries? Begin the answer with the name.",
     "Open the book by naming the mother's line, and fix the fact.",
     ["generation_portrait", "record_and_telling"],
     ["family.flames_name"], FACT_FLAMES_NAME),
    ("What is the family name of your father's line -- the surname "
     "his family carries? Begin the answer with the name.",
     "Name the father's line, and fix the fact.",
     ["generation_portrait", "record_and_telling"],
     ["family.frozen_name"], FACT_FROZEN_NAME),
    ("What is your full name, and how does it come from the two "
     "lines? Begin the answer with your full name.",
     "Introduce the respondent as the union of the two lines, "
     "and fix the fact.",
     ["generation_portrait", "namesake_echo"],
     ["respondent.identity"], FACT_RESPONDENT),
    ("Does your family have a naming tradition -- a rule or custom "
     "that governs the first names its children are given? What is "
     "it, and how is it kept?",
     "Establish the naming law both lines kept, the custom the "
     "whole book's names obey.",
     ["record_and_telling", "namesake_echo"],
     ["family.naming_tradition"], None),
    ("What is your mother's full name, and which line does she "
     "come from? Begin the answer with her full name.",
     "Name the mother directly, with her line, and fix the fact.",
     ["generation_portrait", "record_and_telling"],
     ["people.mother"], FACT_MOTHER),
    ("What is your father's full name, and which line does he come "
     "from? Begin the answer with his full name.",
     "Name the father directly, with his line, and fix the fact.",
     ["generation_portrait", "record_and_telling"],
     ["people.father"], FACT_FATHER),
    ("What saying, rule, or doctrine does the joined family hand "
     "down -- the sentence its members quote when they explain how "
     "this family lives -- and which line brought it?",
     "Plant the family's doctrine, the refrain this book will "
     "return to as each generation develops it.",
     ["the_doctrine", "record_and_telling"], ["family.doctrine"],
     None),
    ("What records do the two lines keep -- each line's book, "
     "register, or papers -- and how do the two archives differ?",
     "Introduce the two archives the family history will rest on.",
     ["heirloom_evidence", "record_and_telling"],
     ["records.two_archives"], None),
    ("What does the joined family believe about itself: the story "
     "it tells about what the two lines are, together?",
     "State the joined family's myth, the one the book will test.",
     ["generation_portrait", "record_and_telling"], ["family.myth"],
     None),
    ("The two lines came from two different places. What are those "
     "places, in the family's telling, and what does each place "
     "explain about its line?",
     "Close the chapter by pointing at the two origins the next "
     "two chapters will trace.",
     ["generation_portrait", "chapter_turn"], ["family.two_origins"],
     None),
]
# Chapter 2 -- The Flames Line. The founder, origin, and migration
# questions exist per line under the clean-proof rule and the
# five-interrogative audit (who, where, when for each line).
Q["ch02"] = [
    ("Who is the founding ancestor of the Flames line -- the first "
     "of that line to come to Texas? Begin the answer with the "
     "ancestor's full name.",
     "Name the Flames founder the line descends from, and fix "
     "the fact.",
     ["generation_portrait", "heirloom_evidence"],
     ["family.flames_founder"], FACT_FLAMES_FOUNDER),
    ("Where did the Flames line come from before Texas: the town "
     "or country it calls its origin? Begin the answer with the "
     "place.",
     "Fix the Flames origin place as fact and as ground.",
     ["generation_portrait", "era_frame"], ["family.flames_origins"],
     FACT_FLAMES_ORIGIN),
    ("In what year did the Flames family come to Dallas, and who "
     "made the journey? Begin the answer with the year.",
     "Fix the Flames migration year as fact and open the arrival.",
     ["migration_scene", "era_frame"], ["family.flames_migration"],
     FACT_FLAMES_MIGRATION),
    ("Who is the Flames family's matriarch -- the woman the line "
     "itself names as the one who held it together in the founding "
     "generation? Begin the answer with her full name.",
     "Name the Flames matriarch and fix the fact.",
     ["generation_portrait", "heirloom_evidence"],
     ["people.flames_matriarch"], FACT_FLAMES_MATRIARCH),
    ("What was the Flames founder's trade, and what does the family "
     "tell about where the name Flames itself came from?",
     "Ground the line in its founding work and its name's telling.",
     ["trade_line", "record_and_telling"],
     ["family.flames_founder_trade"], None),
    ("Describe the Flames line's arrival in Dallas: the journey, "
     "the first work, the first household.",
     "Render the Flames migration as scene and settlement.",
     ["migration_scene", "household_economy"],
     ["family.flames_arrival"], None),
    ("What record did the Flames matriarch begin on the arrival, "
     "and what were its first entries?",
     "Fix the Flames Bible's beginning as the line's second "
     "founding.",
     ["record_and_telling", "heirloom_evidence"],
     ["records.flames_bible_begun"], None),
    ("Who was the Flames family's patriarch in the next "
     "generation -- the man whose work set the line's standard in "
     "Texas? Begin the answer with his full name.",
     "Name the Flames patriarch and fix the fact.",
     ["generation_portrait", "trade_line"],
     ["people.flames_patriarch"], FACT_FLAMES_PATRIARCH),
    ("How did music enter the Flames line: who brought it, and "
     "what did it change about the line's life?",
     "Trace the line's second inheritance, the one the "
     "respondent's mother descends from.",
     ["trade_line", "generation_portrait"],
     ["family.flames_music"], None),
    ("What was the Flames line, by the time the respondent's "
     "mother was born into it: its standing, its household, its "
     "expectations?",
     "Close the Flames chapter on the line the mother carries "
     "into the joining.",
     ["chapter_turn", "generation_portrait"],
     ["family.flames_at_mother"], None),
]
# Chapter 3 -- The Frozen Line. Per-line founder, origin, and
# migration questions, as in chapter 2, under the same rule.
Q["ch03"] = [
    ("Who is the founding ancestor of the Frozen line -- the first "
     "of that line to come to Texas? Begin the answer with the "
     "ancestor's full name.",
     "Name the Frozen founder the line descends from, and fix "
     "the fact.",
     ["generation_portrait", "heirloom_evidence"],
     ["family.frozen_founder"], FACT_FROZEN_FOUNDER),
    ("Where did the Frozen line come from before Texas: the town "
     "or country it calls its origin? Begin the answer with the "
     "place.",
     "Fix the Frozen origin place as fact and as ground.",
     ["generation_portrait", "era_frame"], ["family.frozen_origins"],
     FACT_FROZEN_ORIGIN),
    ("In what year did the Frozen family come to Dallas, and who "
     "made the journey? Begin the answer with the year.",
     "Fix the Frozen migration year as fact and open the arrival.",
     ["migration_scene", "era_frame"], ["family.frozen_migration"],
     FACT_FROZEN_MIGRATION),
    ("Who is the Frozen family's matriarch -- the woman the line "
     "itself names as the one who held it together in the founding "
     "generation? Begin the answer with her full name.",
     "Name the Frozen matriarch and fix the fact.",
     ["generation_portrait", "heirloom_evidence"],
     ["people.frozen_matriarch"], FACT_FROZEN_MATRIARCH),
    ("What was the Frozen founder's trade, and what did he carry "
     "into Texas that the line still keeps?",
     "Ground the line in its founding work and its surviving "
     "object.",
     ["trade_line", "heirloom_evidence"],
     ["family.frozen_founder_trade"], None),
    ("Describe the Frozen line's arrival in Dallas: the "
     "circumstances, the first work, the first household.",
     "Render the Frozen migration as scene and settlement.",
     ["migration_scene", "household_economy"],
     ["family.frozen_arrival"], None),
    ("Who was the Frozen family's patriarch in the next "
     "generation -- the man whose word and work set the line's "
     "standard? Begin the answer with his full name.",
     "Name the Frozen patriarch and fix the fact.",
     ["generation_portrait", "trade_line"],
     ["people.frozen_patriarch"], FACT_FROZEN_PATRIARCH),
    ("State the family's doctrine as the Frozen patriarch's "
     "generation received and restated it: what did his version "
     "of the saying mean in his circumstances?",
     "Return the refrain, developed by the patriarch's era.",
     ["the_doctrine", "generation_portrait"],
     ["family.doctrine_patriarch"], None),
    ("Who were the Frozen patriarch's children and his sister or "
     "brother, and how did the line divide its hopes among them "
     "-- including any who left Texas?",
     "Populate the line's next generation and seed its branch.",
     ["generation_portrait", "branch_and_return"],
     ["family.frozen_patriarch_children"], None),
    ("What was the Frozen line, by the time the respondent's "
     "father was born into it: its standing, its household, its "
     "expectations?",
     "Close the Frozen chapter on the line the father carries "
     "into the joining.",
     ["chapter_turn", "generation_portrait"],
     ["family.frozen_at_father"], None),
]
Q["ch04"] = [
    ("Describe your mother as the carrier of her line: her work, "
     "her gifts, what the Flames line looks like in her.",
     "Portrait of the mother as one line's living form.",
     ["generation_portrait", "trade_line"], ["people.mother_portrait"],
     None),
    ("Describe your father as the carrier of his line: his work, "
     "his gifts, what the Frozen line looks like in him.",
     "Portrait of the father as the other line's living form.",
     ["generation_portrait", "trade_line"], ["people.father_portrait"],
     None),
    ("How did your parents meet, and what does the family tell "
     "about the meeting?",
     "State the joining's first scene, as record and as telling.",
     ["table_scene", "record_and_telling"],
     ["family.parents_meeting"], None),
    ("When and where did your parents marry, and what did the "
     "wedding look like in the family's telling and its record?",
     "Fix the joining as record and as scene: the when and where "
     "of the two lines becoming one family.",
     ["record_and_telling", "table_scene"], ["family.parents_wedding"],
     None),
    ("What did each of your parents' families think of the match, "
     "and what did the two households become to each other?",
     "Render the alliance of the two lines, with its frictions.",
     ["table_scene", "generation_portrait"],
     ["family.two_households"], None),
    ("Describe your father's work as the joined household's "
     "economy: the shop, the bench, the customers, the standing "
     "it bought.",
     "Define the father's line through its trade, inside the "
     "joining.",
     ["trade_line", "household_economy"], ["people.father_work"],
     None),
    ("Describe your mother's work, in her trade and in the "
     "household, and what it made possible for the joined family.",
     "Define the mother's line through its labor, inside the "
     "joining.",
     ["trade_line", "household_economy"], ["people.mother_work"],
     None),
    ("Describe the household your parents made in Dallas: its "
     "rooms, its economy, its rules, its sounds.",
     "Establish the household the respondent grew up inside.",
     ["generation_portrait", "household_economy"],
     ["places.parents_household"], None),
    ("What did each of your parents carry from their own line -- a "
     "saying, a skill, a record, an object -- into the household "
     "they made?",
     "Trace both inheritances at the moment they come under one "
     "roof.",
     ["lineage_rendering", "heirloom_evidence"],
     ["family.parents_inheritance"], None),
    ("What children were born to your parents, and what names were "
     "they given -- and what did the naming declare about the "
     "joining?",
     "Close the joining on the children, whose names are the "
     "union made literal.",
     ["chapter_turn", "namesake_echo"], ["family.parents_children"],
     None),
]
Q["ch05"] = [
    ("In what year were you born, and what was the joined "
     "family's state in that year? Begin the answer with the year.",
     "Fix the respondent's birth year as fact, set inside the "
     "family's circumstances.",
     ["generation_portrait", "era_frame"], ["respondent.birth"],
     FACT_BIRTH_YEAR),
    ("In what place were you born, and what did that place mean to "
     "the two lines by then? Begin the answer with the place.",
     "Fix the respondent's birthplace as fact and as the lines' "
     "shared ground.",
     ["generation_portrait", "record_and_telling"],
     ["places.birthplace"], FACT_BIRTHPLACE),
    ("Who is your sister, and what is her place in the joined "
     "family -- her name, her gifts, her line of descent from "
     "both sides?",
     "Introduce the respondent's generation in its plurality.",
     ["generation_portrait", "table_scene"], ["people.sister"],
     None),
    ("Tell of the family's branch that left Texas: who went, "
     "where, and what became of their line?",
     "Open the branching line the later chapters will weigh.",
     ["branch_and_return", "generation_portrait"],
     ["family.branch"], None),
    ("Describe growing up between two lines: the rooms, the work "
     "you watched on each side, the place you were given at each "
     "family's table.",
     "Render the respondent's childhood as membership in two "
     "lines at once.",
     ["table_scene", "generation_portrait"],
     ["respondent.childhood"], None),
    ("What did each line require of its children in your "
     "generation: work, faith, music, silence, achievement, care?",
     "State the two households' demands as the generation's "
     "first law.",
     ["record_and_telling", "household_economy"],
     ["family.requirements"], None),
    ("State the family's doctrine as you yourself received it: who "
     "said it to you, in what circumstances, and what you "
     "understood it to mean then?",
     "Return the refrain, developed by the respondent's own "
     "receiving of it.",
     ["the_doctrine", "lineage_rendering"],
     ["family.doctrine_received"], None),
    ("Describe a gathering of the whole joined family from your "
     "childhood: who came from each line, what was eaten, what "
     "was said and unsaid.",
     "Let the two lines meet at one table.",
     ["table_scene", "generation_portrait"],
     ["family.childhood_gathering"], None),
    ("What names repeat across the two lines, and who in your "
     "generation was named for whom?",
     "Render the naming law's echoes in the respondent's own "
     "generation.",
     ["namesake_echo", "record_and_telling"], ["family.names"],
     None),
    ("When did you first understand that the joined family was "
     "something you would one day have to carry, and what showed "
     "you?",
     "Close the generation's chapter on the inheritance becoming "
     "conscious.",
     ["chapter_turn", "lineage_rendering"],
     ["respondent.carrying"], None),
]

Q["ch06"] = [
    ("What was the Frozen line's founding trade, and how did it "
     "shape what that line thought work was?",
     "Open the trades chapter at the Frozen root: work as a "
     "line's first definition of itself.",
     ["trade_line", "generation_portrait"], ["trades.frozen_founding"],
     None),
    ("How did the Frozen patriarch's trade differ from the "
     "founder's, and what passed between them unchanged?",
     "Trace the bench line across its first transfer.",
     ["trade_line", "lineage_rendering"], ["trades.frozen_patriarch"],
     None),
    ("How did your father's trade carry the Frozen line's work "
     "forward, and what did he add of his own?",
     "Trace the bench line into the parents' generation.",
     ["trade_line", "generation_portrait"], ["trades.father"], None),
    ("What work ran down the Flames line -- the founder's fire "
     "work, its Texas form, and the music that entered it?",
     "Give the Flames line's labor its standing beside the bench "
     "trades.",
     ["trade_line", "generation_portrait"], ["trades.flames"],
     None),
    ("What is your own trade, and how does it stand in the two "
     "lines' work -- continuation, translation, or break?",
     "Place the respondent's work inside both lines' economies.",
     ["trade_line", "record_and_telling"], ["trades.respondent"],
     None),
    ("What work has your sister taken up, inside or beside the "
     "family's trades?",
     "Populate the present generation's working world.",
     ["trade_line", "generation_portrait"], ["trades.sister"],
     None),
    ("What did the two lines' trades, taken together, teach the "
     "joined family about how a person should work and what work "
     "is for?",
     "State the work ethic the trades deposited in the family.",
     ["the_doctrine", "trade_line"], ["trades.ethic"], None),
    ("What tools or instruments of the lines' trades survive, and "
     "in whose keeping are they now?",
     "Let the trades' objects testify to the line of hands.",
     ["heirloom_evidence", "trade_line"], ["motifs.trade_tools"],
     None),
    ("What trade, skill, or way of working did either line lose on "
     "the way -- and what did the losing cost?",
     "Account for the lines' chosen and unchosen losses.",
     ["trade_line", "branch_and_return"], ["trades.lost"], None),
    ("Where does the joined family's line of work stand now, in "
     "your hands and the hands coming after you?",
     "Close the trades chapter on the work's present tense.",
     ["chapter_turn", "trade_line"], ["trades.present"], None),
]
Q["ch07"] = [
    ("Describe the Flames line's record book itself: its physical "
     "form, whose hands have written in it, and what it contains.",
     "Open the records chapter on the Flames archive as an object.",
     ["heirloom_evidence", "record_and_telling"],
     ["records.flames_book"], None),
    ("Describe the Frozen line's records -- its day books and "
     "logs: their form, whose hands kept them, and what they "
     "contain that the Bible does not.",
     "Set the second archive beside the first, in its own kind.",
     ["heirloom_evidence", "record_and_telling"],
     ["records.frozen_books"], None),
    ("Describe the Frozen founder's carried object as it survives "
     "now: its condition, its keeping place, what it shows.",
     "Return to the migration's object with the records "
     "chapter's eyes.",
     ["heirloom_evidence", "lineage_rendering"],
     ["motifs.founder_object_now"], None),
    ("What instrument or household object carries the Flames "
     "line's memory, and where is it now?",
     "Choose the object that testifies for the music line.",
     ["heirloom_evidence", "lineage_rendering"],
     ["motifs.flames_object"], None),
    ("What houses have the two lines lived in, in Texas and "
     "before it, and what does each house mark about its era?",
     "Render the family's geography as a succession of roofs.",
     ["generation_portrait", "household_economy"],
     ["places.family_houses"], None),
    ("What photographs, letters, or papers does the joined family "
     "hold, and who has done the work of keeping them?",
     "Account for the family's paper memory and its keepers.",
     ["record_and_telling", "heirloom_evidence"],
     ["records.papers"], None),
    ("What records has your own generation made -- logs, "
     "recordings, photographs -- and how do they continue the two "
     "lines' older keeping?",
     "Bring the record forward into the respondent's own "
     "practice.",
     ["record_and_telling", "lineage_rendering"],
     ["records.own_generation"], None),
    ("What records or objects has the family lost -- to fire, "
     "moving, neglect, or dispute -- and what went with them?",
     "Name the archives' gaps honestly.",
     ["record_and_telling", "heirloom_evidence"],
     ["records.lost"], None),
    ("Where do the written records and the family's telling most "
     "clearly disagree, and how does the family live with the "
     "difference?",
     "Perform the family history's central act of weighing.",
     ["record_and_telling", "the_doctrine"],
     ["records.disagreement"], None),
    ("Who keeps the family's records and heirlooms now, and how "
     "was that keeper chosen or fallen to?",
     "Fix the archives' present custody, and point the chapter "
     "at its purpose.",
     ["heirloom_evidence", "chapter_turn"], ["records.keeper"],
     None),
]
Q["ch08"] = [
    ("Tell of the Frozen patriarch's death: when, how the family "
     "met it, and what of his passed into your hands.",
     "Open the hard years with the patriarch's parting, plainly.",
     ["generation_portrait", "record_and_telling"],
     ["family.patriarch_death"], None),
    ("Tell of the Flames patriarch's death: when, and what it "
     "closed in that line.",
     "Render the other line's patriarch's passing in its own "
     "terms.",
     ["generation_portrait", "record_and_telling"],
     ["family.flames_patriarch_death"], None),
    ("How did the founding generations of both lines pass: who "
     "went first, who last, and what did each death close?",
     "Take roll of the founders' and matriarchs' endings.",
     ["generation_portrait", "record_and_telling"],
     ["family.founders_deaths"], None),
    ("Tell of the disaster that struck your own work -- the fire "
     "or ruin -- and how the joined family answered it.",
     "Place the respondent's generation's catastrophe and its "
     "rebuilding.",
     ["generation_portrait", "the_doctrine"], ["family.disaster"],
     None),
    ("Tell of the family's oldest parting: the one who left Texas "
     "and did not come back to live, and what the leaving cost "
     "both sides at the time.",
     "Weigh the branch's leaving as a parting, in its own era's "
     "terms.",
     ["branch_and_return", "table_scene"], ["family.oldest_parting"],
     None),
    ("What estrangement, silence, or lost touch runs in either "
     "line, and what is honestly known about its cause?",
     "Name the family's unspoken break without inventing its "
     "resolution.",
     ["record_and_telling", "branch_and_return"],
     ["family.estrangement"], None),
    ("Tell of the joined family's thinnest years in your own time: "
     "what was short, and what did the family do about it?",
     "Render the present generation's material hardship.",
     ["household_economy", "era_frame"], ["family.thin_years"],
     None),
    ("State the family's doctrine as the hard years tested it: "
     "where did it hold, where did it bend, and what did keeping "
     "it cost?",
     "Return the refrain under pressure, developed by loss.",
     ["the_doctrine", "generation_portrait"],
     ["family.doctrine_tested"], None),
    ("Who held the family together in its hard years, in each "
     "line and in the joined family -- and how does that holding "
     "repeat the matriarchs' pattern?",
     "Trace the matriarchs' office as it passes to later hands.",
     ["lineage_rendering", "generation_portrait"],
     ["family.holders"], None),
    ("What survived the hard years intact -- and what survived "
     "changed, which is a different thing?",
     "Close the hard years on an honest inventory of survival.",
     ["chapter_turn", "heirloom_evidence"], ["family.survivals"],
     None),
]
Q["ch09"] = [
    ("What is your wife's name, and how did she come into this "
     "family? Begin the answer with her full name.",
     "Bring the partner into the family as a third line's "
     "joining, and fix the fact.",
     ["table_scene", "record_and_telling"], ["people.partner"],
     FACT_PARTNER),
    ("What family did your wife come from, and what did her line "
     "bring into yours -- its work, its ways, its own customs of "
     "naming and keeping?",
     "Give the incoming line its own standing in the history.",
     ["generation_portrait", "branch_and_return"],
     ["family.partner_line"], None),
    ("Who are the family's next generation -- your sister, the "
     "branch's young, the children coming up -- and where do they "
     "stand in the lines?",
     "Populate the generation the book will hand everything to.",
     ["generation_portrait", "table_scene"],
     ["family.next_generation"], None),
    ("Describe a reunion or gathering of the joined family as it "
     "happens now: who comes, from how far, and what the day is "
     "like.",
     "Let the whole living family meet at one table.",
     ["table_scene", "generation_portrait"], ["family.reunion"],
     None),
    ("How does the branch that left stand with the root today: "
     "visits, calls, obligations kept or lapsed?",
     "Weigh the branch's present distance honestly.",
     ["branch_and_return", "record_and_telling"],
     ["family.branch_today"], None),
    ("What are you and your generation teaching the young of the "
     "family, deliberately -- and what are they refusing to "
     "learn?",
     "Render the transfer in progress, with its friction.",
     ["lineage_rendering", "table_scene"], ["family.teaching"],
     None),
    ("State the family's doctrine as the young now say it, or "
     "refuse it: what has their version kept, and what has it "
     "changed?",
     "Return the refrain in the newest mouths, developed or "
     "contested.",
     ["the_doctrine", "namesake_echo"], ["family.doctrine_young"],
     None),
    ("Where does the family live now, house by house and city by "
     "city, and how did it come to be spread so?",
     "Fix the family's present geography.",
     ["generation_portrait", "branch_and_return"],
     ["places.family_now"], None),
    ("What does the living family still argue about -- the old "
     "subjects, in their present forms?",
     "Name the family's continuing fault lines without flinching.",
     ["table_scene", "record_and_telling"], ["family.arguments"],
     None),
    ("What is the joined family, as it stands now, in one honest "
     "assessment: stronger, smaller, scattered, kept?",
     "Close the living-family chapter on a plain verdict.",
     ["chapter_turn", "record_and_telling"], ["family.verdict"],
     None),
]
Q["ch10"] = [
    ("State the family's doctrine one last time, as you would hand "
     "it on: what it meant at the root, what it has come to mean, "
     "and what you believe it will ask of the next generation.",
     "Give the refrain its fullest development, carrying every "
     "era the book has passed through.",
     ["the_doctrine", "lineage_rendering"],
     ["family.doctrine_final"], None),
    ("What of the two lines' heirlooms and records is in your own "
     "keeping, and what have you already passed on, and to whom?",
     "Take the keeper's inventory at the book's end.",
     ["heirloom_evidence", "record_and_telling"],
     ["records.keeping_final"], None),
    ("What have you yourself passed down already -- a skill, a "
     "standard, a saying, a room -- and who carries it now?",
     "Account for the respondent's own act of handing down.",
     ["lineage_rendering", "trade_line"], ["family.passed_on"],
     None),
    ("Which of the family's names are carried by the living young, "
     "in both lines and the branch, and what do you hope or fear "
     "those names will do for them?",
     "Close the naming argument with its future tense.",
     ["namesake_echo", "chapter_turn"], ["family.names_forward"],
     None),
    ("What do the family's records still get wrong, or leave out, "
     "that you want corrected while you can correct it?",
     "Let the respondent amend the archives in his own voice.",
     ["record_and_telling", "heirloom_evidence"],
     ["records.corrections"], None),
    ("What part of the family's story is still unfinished -- the "
     "branch unvisited, the column left blank, the page not yet "
     "written?",
     "Name the history's open account honestly.",
     ["branch_and_return", "chapter_turn"], ["family.unfinished"],
     None),
    ("What is this joined family for: what does its whole history, "
     "told whole, show it was doing in the world?",
     "Test the founding myth against the full record.",
     ["the_doctrine", "record_and_telling"], ["family.purpose"],
     None),
    ("What plain advice does the family give its young, beneath "
     "the doctrine -- the working instructions for a life in these "
     "lines?",
     "Translate the inheritance into instructions a child could "
     "carry.",
     ["the_doctrine", "table_scene"], ["family.advice"], None),
    ("What do you want entered next in the family's records -- the "
     "entry you hope the next keeper writes?",
     "Point the archives at their next page.",
     ["record_and_telling", "chapter_turn"], ["records.next_entry"],
     None),
    ("End the book: what is the single fact about this family that "
     "should outlast every story told about it?",
     "Close on the fact that survives the telling.",
     ["record_and_telling", "chapter_turn"], ["family.final_fact"],
     None),
]


def main() -> None:
    questions = []
    n = 0
    for cid, title, act in CHAPTERS:
        for k, (prompt, job, devices, keys, fact) in enumerate(Q[cid], 1):
            n += 1
            q = {
                "id": f"q{n:03d}",
                "chapter": cid,
                "prompt": prompt,
                "narrative_job": job,
                "position": (f"{act}, Chapter: {title}; page {k} of 10 "
                             f"within the chapter"),
                "devices": devices,
                "bible_keys": keys,
            }
            if fact is not None:
                q["fact"] = fact
            questions.append(q)
    pack = {
        "genre": "family-history",
        "version": "1.0.0",
        "framework": FRAMEWORK,
        "chapters": [
            {"id": cid, "title": title, "act": act}
            for cid, title, act in CHAPTERS
        ],
        "questions": questions,
    }
    out = Path(__file__).resolve().parent.parent / "packs" / "family-history.json"
    out.write_text(json.dumps(pack, indent=1), encoding="utf-8")
    print(f"wrote {out}: {len(questions)} questions, "
          f"{len(CHAPTERS)} chapters")


if __name__ == "__main__":
    main()
