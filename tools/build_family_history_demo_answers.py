#!/usr/bin/env python3
"""Build the family-history pack's demonstration answers.

The demonstration user of the series is Frozen In Flames, a fictional
persona, and the family-history survey is the one he takes about his
own family. The canonical facts of the character's invented life --
including the family layer: the two lines (the mother's line,
Flames; the father's line, Frozen), their founders, origins,
migrations, matriarchs, and patriarchs, and the family's gem-name
law -- live in demo/frozen-in-flames-character.json, on the canon
the author set on 2026-11-24 (record version 2.0.0), superseding
the values the biography build invented. This script loads that
record and writes his answers to all 100 family-history questions,
with the fact-bearing answers interpolated from the record so the
two cannot drift apart. A consistency check runs before anything
is written: every recorded fact must appear in its designated
answer and begin it, each year fact must be the first year in its
answer, the family doctrine must appear in the record's exact
wording in the answer that plants it, and no token of the
superseded canon (the biography build's Memphis, its invented
names) may appear.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHARACTER_PATH = ROOT / "demo" / "frozen-in-flames-character.json"
OUT_PATH = ROOT / "demo" / "family-history-demo-answers.json"

RECORD = json.loads(CHARACTER_PATH.read_text(encoding="utf-8"))
F = RECORD["facts"]
FF = RECORD["family_facts"]
NAME = F["subject_name"]
MOTHER = F["mother_name"]
FATHER = F["father_name"]
PARTNER = F["partner_name"]
BIRTH_YEAR = F["birth_year"]
BIRTHPLACE = F["birthplace"]
FLAMES_NAME = FF["flames_line_name"]
FROZEN_NAME = FF["frozen_line_name"]
FLAMES_FOUNDER = FF["flames_founding_ancestor"]
FROZEN_FOUNDER = FF["frozen_founding_ancestor"]
FLAMES_MATRIARCH = FF["flames_matriarch"]
FROZEN_MATRIARCH = FF["frozen_matriarch"]
FLAMES_PATRIARCH = FF["flames_patriarch"]
FROZEN_PATRIARCH = FF["frozen_patriarch"]
FLAMES_ORIGIN = FF["flames_origin_place"]
FROZEN_ORIGIN = FF["frozen_origin_place"]
FLAMES_MIGRATION = FF["flames_migration_year"]
FROZEN_MIGRATION = FF["frozen_migration_year"]
DOCTRINE = ("A family keeps what it can fix, and fixes what it "
            "keeps.")

ANSWERS: dict[str, str] = {
    # Chapter 1 -- Two Names
    "q001": (
        f"{FLAMES_NAME}. The family name of my mother's line is "
        "Flames, carried by her people from Mississippi to Texas "
        "and into Dallas, where she was born to it. It is the name "
        "on the family Bible her line keeps, the name her father "
        "worked under and her grandfather was buried under, and "
        "the name she kept when she married -- the joining of our "
        "two families was not going to cost either line its name, "
        "and in the event it cost neither."
    ),
    "q002": (
        f"{FROZEN_NAME}. The family name of my father's line is "
        "Frozen, carried by his people from Pennsylvania to Texas "
        "in the middle of the last century. It is the name on the "
        "day books his line keeps, the name his father made tools "
        "under and his grandfather carried into Dallas in a "
        "toolbox. People hearing the two names together assume "
        "they were invented to fit. They were not. They were "
        "married into fitting, which is a different and longer "
        "process."
    ),
    "q003": (
        f"{NAME}. That is my full name, and it is the two lines "
        "joined in one person: Frozen, my father's family name, "
        "and Flames, my mother's, with 'In' set between them the "
        "way a coupling joins two cars of a train. My parents gave "
        "it to their first child in Dallas in 2000 to declare what "
        "the marriage had made -- not a Flames child or a Frozen "
        "child but the union itself, walking around. In daily life "
        "I am called Frozen. The whole name is for documents, "
        "introductions, and the flyleaf of the family Bible, where "
        "it takes up its full line."
    ),
    "q004": (
        "The family does have a naming tradition, and it is "
        "strict: every child of both lines is given a first name "
        "from the crystals and gems. Ruby, Onyx, Jasper, Garnet, "
        "Jet, Opal, Flint, Pearl, Topaz, Coral, Jade, Zircon, "
        "Slate, Amber -- the roster of this book is the evidence. "
        "The two lines kept the custom independently before they "
        "ever met, which the family counts as proof it was meant. "
        "It is kept by the simplest mechanism: the grandparents "
        "hold the list of what has been used, a name is chosen "
        "before the birth and argued about at the table, and no "
        "child of either line has yet been given a name from "
        "outside the stones. I am the single exception, and the "
        "exception is the point: my name is not a stone but the "
        "two surnames themselves, because I am not one line's "
        "child. I am the joining."
    ),
    "q005": (
        f"{MOTHER}. My mother is Ruby Flames, of the Flames line: "
        "born in Dallas in 1975, the daughter of Slate and Opal "
        "Flames, a piano teacher and church organist who teaches "
        "in the front room of her house and keeps the joined "
        "family's household books in the same careful hand she "
        "uses for music. She is the Flames line in its present "
        "tense: its music, its record-keeping conscience, and its "
        "refusal to sell the piano, which she inherited from her "
        "mother along with the piano itself."
    ),
    "q006": (
        f"{FATHER}. My father is Onyx Frozen, of the Frozen line: "
        "born in Dallas in 1973, the son of Jasper and Coral "
        "Frozen, who runs the small Dallas repair shop his line's "
        "work became -- radios, televisions, guitars, anything "
        "with a circuit and an owner who wants it back. He is the "
        "Frozen line in its present tense: its bench, its day "
        "book, and its standard that a repair is a promise. He "
        "taught me the bench before any studio did."
    ),
    "q007": (
        f"The joined family's doctrine is the Frozen line's "
        f"sentence, brought into the marriage by my father and "
        f"adopted by the whole family: {DOCTRINE} It was my "
        "grandfather Jasper Frozen's saying first, coined at a "
        "toolmaker's bench. His father had lived it without saying "
        "it; his son says it about radios; my mother applies it, "
        "pointedly, to people; and I say it about recording rooms. "
        "The Flames line's own contribution to the joined family's "
        "law is not a sentence but a practice: write it down. "
        "Between the two of them -- keep it, and enter it -- the "
        "joined family has its whole constitution."
    ),
    "q008": (
        "The two lines keep two different archives, and the "
        "difference is the lines in miniature. The Flames line "
        "keeps a Bible: births, marriages, and deaths, entered in "
        "the flyleaf from 1949 forward, because the Flameses hold "
        "that a family is its people. The Frozen line keeps day "
        "books: the work of every day, job by job, entered by "
        "Flint, then Jasper, then my father, because the Frozens "
        "hold that a family is what it does. The joined family's "
        "record is both, and they correct each other constantly: "
        "the Bible knows when Jasper died; the day book knows "
        "what he was working on the week before."
    ),
    "q009": (
        "What the joined family believes about itself, when it "
        "tells the story whole, is that it is the people Dallas "
        "sends for: the Frozens when a machine stops, the "
        "Flameses when a choir needs an organist or a child needs "
        "teaching, and the joined household for the larger "
        "category of things that have broken and should not have "
        "to stay broken. It is a proud belief and the record "
        "supports more of it than modesty would like. Its trap is "
        "the same as its pride: a family that believes it can fix "
        "anything must learn, generation by generation, the short "
        "list of things it cannot, and the learning is never "
        "finished."
    ),
    "q010": (
        "The two lines came from two places that explain them "
        "still. The Flameses came from Holly Springs, Mississippi "
        "-- hill country, furnaces, a town that was shrinking -- "
        "and they remain a line that understands fire: how to keep "
        "it, feed it, and bank it against the night. The Frozens "
        "came from Pittsburgh, Pennsylvania -- steel, cold, "
        "machines the size of houses -- and they remain a line "
        "that understands iron and patience. Fire and iron, music "
        "and machinery: the joined family is what happened when "
        "the two elements were put in one household in Dallas, "
        "and the next two chapters take each line back to its "
        "own beginning."
    ),
    # Chapter 2 -- The Flames Line: Fire and Music
    "q011": (
        f"{FLAMES_FOUNDER}. He is the founding ancestor of the "
        "Flames line in Texas: born in Holly Springs, Mississippi, "
        "in 1920, a keeper of furnaces and boilers, who brought "
        "his wife and small son to Dallas in 1949 and stayed. I "
        "never met him -- he died in 1994, six years before I was "
        "born -- and I know him the way this book knows all its "
        "dead: through the record his wife started the year he "
        "arrived, and the telling that surrounds it."
    ),
    "q012": (
        f"{FLAMES_ORIGIN}, Mississippi. The Flames line came from "
        "Holly Springs, a hill-country town in the north of the "
        "state, where Garnet's people had kept the mill's furnaces "
        "for two generations and where the name is still on a "
        "church roll. It is the line's origin the way Dallas is "
        "its home: the place it came from, not the place it is "
        "from, and the distinction matters to everybody who has "
        "ever had to make it."
    ),
    "q013": (
        f"{FLAMES_MIGRATION}. The Flames family came to Dallas in "
        "1949: Garnet, aged twenty-nine, his wife Jet, and their "
        "son Slate, aged three. The telling says they came down "
        "the river, and the telling is wrong in the way this book "
        "will examine later -- there is no river route from Holly "
        "Springs to Dallas, and a railway timetable in Jet's "
        "papers says otherwise. What is certain is the shape of "
        "the arrival: a furnace man with a trade a growing city "
        "needed, a wife carrying a Bible she meant to start a "
        "record in, and eleven years of Texas growth ahead of "
        "anyone who could keep a boiler alive."
    ),
    "q014": (
        f"{FLAMES_MATRIARCH}, born Jet Callahan in 1923. She is "
        "the Flames family's matriarch by the line's own naming: "
        "Garnet's wife, who came with him from Holly Springs in "
        "1949, kept the household through the lean first Texas "
        "years, and began the family Bible whose flyleaf carries "
        "the line's births, marriages, and deaths in her hand for "
        "fifty-two years. The founder arrived; the matriarch is "
        "why there was a family, and not just a man, to arrive."
    ),
    "q015": (
        "Garnet's trade was fire: he kept furnaces and boilers -- "
        "at the mill in Holly Springs, then at heating plants and "
        "laundries and a hospital in Dallas -- the man sent for "
        "when the fire in a building's basement went wrong or went "
        "out. The family telling gives the name itself to the "
        "trade: the Flameses, it says, were called for the flame "
        "they kept. The record, which begins in 1949, shows the "
        "name already old in Mississippi and offers no opinion. "
        "The family keeps the telling anyway, labelled as telling, "
        "because a name with a story in it is easier to hand to a "
        "child than a name without one."
    ),
    "q016": (
        "The Flames arrival in Dallas was unspectacular, which "
        "the line counts as its good fortune: a rented house near "
        "Garnet's first plant, work within the week on the "
        "strength of a Mississippi foreman's letter, Jet's table "
        "feeding the household and then the neighbours' children "
        "who materialized at its edges. The first Texas winter "
        "tested the furnace man's own furnace, in the telling's "
        "favorite irony, and he fixed it, and the story has been "
        "told at every Flames Christmas since as the line's "
        "founding parable: the keeper's own fire, kept."
    ),
    "q017": (
        "The Flames record was begun in the year of the arrival: "
        "Jet entered the marriage, the journey, and the names of "
        "the dead they had left in Mississippi in the flyleaf of "
        "the Bible she carried from Holly Springs, ruling the "
        "columns herself -- born, married, died -- in a hand like "
        "copperplate. The entries are plain and they are the "
        "reason this line's history can be written at all. Every "
        "keeper since has understood the assignment the same way: "
        "enter what happened, in the year it happened, in a hand "
        "the next keeper can read."
    ),
    "q018": (
        f"{FLAMES_PATRIARCH}. My grandfather Slate Flames -- "
        "Garnet's son, my mother's father -- is the Flames "
        "family's patriarch in Texas: born in Holly Springs in "
        "1946, brought to Dallas at three, and a heating and "
        "refrigeration man all his working life, which is the "
        "founder's fire trade translated into the century of cold "
        "air. He kept his father's standard -- the plant does not "
        "go down on your watch -- and his mother's book, whose "
        "entries pass into his hand in the years after hers gives "
        "out. He died in 2016."
    ),
    "q019": (
        "Music entered the Flames line through Slate's wife, my "
        "grandmother Opal Flames, born Opal Reyes: a piano teacher "
        "and church organist who taught the neighbourhood's "
        "children in her front room for cake, for eggs, for "
        "nothing, and played for services for fifty years. What "
        "she changed about the line was its element: the Flameses "
        "had kept fire for other people; through her they began "
        "keeping music for themselves, and the front room became "
        "the line's second hearth. My mother inherited the piano, "
        "the pupils, and the doctrine that a child is taught by "
        "whoever is nearest and musical."
    ),
    "q020": (
        "The Flames line, by the time my mother was born into it "
        "in 1975, was a Dallas family of the second Texas "
        "generation: Slate's refrigeration work steady, Opal's "
        "front room full of other people's children, the Bible "
        "kept, the Mississippi origin already passing from memory "
        "into telling. Its expectations of a daughter were the "
        "line's own: learn the music, keep the record, marry as "
        "you choose but bring them to the table first. My mother "
        "fulfilled the first two exactly and the third in her own "
        "way -- she brought home a repairman, which the line "
        "agreed was within the spirit of the thing."
    ),
    # Chapter 3 -- The Frozen Line: Iron and Patience
    "q021": (
        f"{FROZEN_FOUNDER}. He is the founding ancestor of the "
        "Frozen line in Texas: born in Pittsburgh, Pennsylvania, "
        "in 1918, a millwright and machinist who came to Dallas "
        "in 1947 after wartime service in the machine shops, with "
        "a wife, a toolbox, and a trade the postwar city was "
        "short of. He died in 1992. Everything the Frozen line is "
        "in Texas descends from that arrival, as everything "
        "Flames in Texas descends from Garnet's, two years later "
        "and from the opposite direction."
    ),
    "q022": (
        f"{FROZEN_ORIGIN}, Pennsylvania. The Frozen line came "
        "from Pittsburgh: steel country, river country, a city of "
        "machines the size of houses, where Flint learned his "
        "trade in shops that ran day and night. The line's origin "
        "explains its temperament the way Holly Springs explains "
        "the Flameses': where the Flames line learned fire, the "
        "Frozen line learned iron -- weight, tolerance, patience, "
        "and the long cold arithmetic of work that cannot be "
        "hurried."
    ),
    "q023": (
        f"{FROZEN_MIGRATION}. The Frozen family came to Dallas in "
        "1947: Flint, aged twenty-nine, discharged from wartime "
        "machine-shop service, and his wife Pearl, whom he had "
        "married in Pittsburgh in 1944. He came ahead of the "
        "household by some weeks, in the winter of 1946, to find "
        "the work and the rooms; the family counts the migration "
        "from 1947, the year the household arrived whole and the "
        "day book's Dallas entries begin. He found both, in a "
        "city building machine shops as fast as it could pour "
        "their floors."
    ),
    "q024": (
        f"{FROZEN_MATRIARCH}, born Pearl Kowalski in 1921. She is "
        "the Frozen family's matriarch: Flint's wife, who kept "
        "the line's papers, its accounts, and its table through "
        "the founding decades, and who instituted the Frozen "
        "custom that no job and no debt goes unentered -- the "
        "day book was Flint's habit, but its completeness was "
        "Pearl's enforcement. She died in 1999, a year before I "
        "was born, and I know her through the accounts she kept, "
        "which are as exact as the Flames Bible and twice as "
        "argumentative in the margins."
    ),
    "q025": (
        "Flint's trade was the millwright's and machinist's: the "
        "keeping of great machines, learned in Pittsburgh's shops "
        "and practiced in Dallas for forty years. What he carried "
        "into Texas that the line still keeps is his toolbox: an "
        "iron-bound chest, carpenter-made, its fitted slots "
        "holding the hand tools of the trade, each bought singly "
        "and initialed. It was his capital and his credentials -- "
        "a man hiring a stranger hires the box as much as the man "
        "-- and it sits in my keeping now, still heavy enough to "
        "make its point."
    ),
    "q026": (
        "The Frozen arrival in Dallas was a workingman's landing "
        "of the classic kind: rooms found through the shop, the "
        "shop found through a foreman who had served with men "
        "Flint had served with, the first Dallas entry in the day "
        "book recording a job, a wage, and a landlord in three "
        "level lines. Pearl arrived in the spring with the "
        "household goods and immediately began the accounts. The "
        "line remembers the arrival without romance, which is its "
        "own kind of romance: nothing was promised, everything "
        "was entered, and the city paid for competence in the "
        "usual coin of more work."
    ),
    "q027": (
        f"{FROZEN_PATRIARCH}. My grandfather Jasper Frozen -- "
        "Flint's son, my father's father -- is the Frozen "
        "family's patriarch: born in Dallas in 1948, a toolmaker "
        "all his working life, and the author of the doctrine "
        "the joined family still quotes: a family keeps what it "
        "can fix, and fixes what it keeps. If Flint founded the "
        "line in Texas, Jasper defined it -- the standard of "
        "work, the keeping of the day book, the refusal to "
        "discard anything that could still be understood. He died "
        "in 2018, when I was eighteen, and he is the grandfather "
        "I knew best."
    ),
    "q028": (
        "The doctrine in Jasper's own era meant something harder "
        "than it means in mine. He formed it in the decades when "
        "Dallas threw away machines, furniture, and whole trades "
        "for want of small repairs, and in his mouth the sentence "
        "-- a family keeps what it can fix, and fixes what it "
        "keeps -- was an accusation aimed at a wasteful age and a "
        "job description for his children: nothing in this house "
        "is disposable while it can still be understood. His wife "
        "Coral's amendment, preserved by the telling alone, was "
        "that people were included in the inventory. The joined "
        "family has been living inside the sentence and the "
        "amendment ever since."
    ),
    "q029": (
        "Jasper and Coral's children were my father Onyx, born in "
        "1973, and my aunt Jade, born in 1976, who took the "
        "line's keeping instinct into nursing and lives in Fort "
        "Worth. Jasper's own sister was Topaz, born in 1951, the "
        "line's great leaver: she went to Chicago in 1969, at "
        "eighteen, married Obsidian Whitfield there, and raised "
        "a son she named Jasper, for her brother, in a city where "
        "the name meant nothing to anyone but us. The line's "
        "hopes divided the way families' hopes do: the son at "
        "home took the bench, the daughter who left kept the "
        "family anyway, at six hundred miles, which is its own "
        "chapter of this book."
    ),
    "q030": (
        "The Frozen line, by the time my father was born into it "
        "in 1973, was a Dallas family of the second Texas "
        "generation: Jasper's toolmaking respected, the day books "
        "filling a shelf, the Pittsburgh origin already a story "
        "the children asked for rather than a place anyone "
        "remembered. Its expectations of a son were the line's "
        "own: learn the bench, keep the book, be the man they "
        "send for. My father fulfilled all three and then did the "
        "one thing the line had not scripted -- he married the "
        "organist, and brought the fire line into the iron line's "
        "house."
    ),
    # Chapter 4 -- The Parents: The Joining
    "q031": (
        "My mother as the carrier of her line is the Flames "
        "inheritance in one person: Opal's ear and front room, "
        "Slate's stubbornness about standards, Jet's instinct "
        "that everything important gets written down. She teaches "
        "piano to half the street's children, plays the organ at "
        "the church where she met my father, and keeps the joined "
        "family's books -- the household accounts in the Frozen "
        "manner and the Bible's new entries in the Flames manner, "
        "both in the same hand. The Flames line in her is not a "
        "memory. It is a going concern."
    ),
    "q032": (
        "My father as the carrier of his line is the Frozen "
        "inheritance likewise: Flint's hands, Jasper's standard, "
        "Pearl's completeness about paperwork. His repair shop is "
        "the line's work in its third Texas form -- his "
        "grandfather kept mills, his father made tools, he makes "
        "dead radios and guitars answer again, and the descent is "
        "not a decline but a translation, each generation's "
        "machines smaller and more numerous. He enters every job "
        "in the day book. He has never once, to my knowledge, "
        "thrown away a machine he had not first understood."
    ),
    "q033": (
        "My parents met over a broken piano pedal, which the "
        "joined family tells the way other families tell a "
        "creation myth. Ruby Flames was playing for a church "
        "social in 1998 when the pedal failed under her foot; the "
        "church called the repairman, and the repairman was Onyx "
        "Frozen. He fixed the pedal, stayed for the singing, and, "
        "by the family's account, was engaged in his mind before "
        "she had played one whole service through without "
        "stopping. The record supports the pedal, the church, and "
        "the year. The rest is telling, and neither line has ever "
        "seen a reason to improve on it."
    ),
    "q034": (
        "My parents married in 1999, in the church where they "
        "met, with Opal Flames at the organ her daughter usually "
        "played and Jasper Frozen standing witness with his hands "
        "washed for once past the wrists. The Bible records it in "
        "Ruby's hand -- she had taken up the keeping of the book "
        "by then -- in one line: the date, the names, the church. "
        "The day book records it in Onyx's, in one line also: the "
        "date, the names, 'no charge'. The two archives agree "
        "about the joining in everything except bookkeeping, "
        "which is to say they agree entirely."
    ),
    "q035": (
        "The two families took the match in their own styles. The "
        "Frozens gained a musician and were quietly aware the "
        "Flameses thought them a little too proud of their day "
        "book; the Flameses gained a repairman and were quietly "
        "aware the Frozens thought them a little too fond of "
        "their Bible's margins. What the households became to "
        "each other was one extended family with two capitals -- "
        "the shop and the front room -- and a standing "
        "arrangement, never written and never broken, that "
        "Christmas alternates and funerals do not."
    ),
    "q036": (
        "My father's work is the repair shop: a small Dallas "
        "storefront with a bench at the back, spools of wire, "
        "guitars waiting in a row, and the day book in which every "
        "job is entered, described, and priced in his hand. The "
        "shop's economy was the joined household's economy for "
        "the years of my childhood -- it paid the mortgage, "
        "bought the piano strings and the school shoes, and in "
        "thin months ran on his reputation, which is a form of "
        "capital no bank has ever seen. A customer of my father's "
        "does not buy a repair. He buys the certainty that the "
        "thing has been understood."
    ),
    "q037": (
        "My mother's work is the front room: piano lessons, the "
        "organ at church, weddings and funerals at a rate the "
        "family considers a ministry and the church considers a "
        "bargain. Her labor made possible what the shop's could "
        "not -- it was steady when repair work was seasonal, it "
        "filled the house with music as a daily condition rather "
        "than an occasion, and it taught every child who crossed "
        "the threshold, including hers, that a household can run "
        "on art practiced as discipline. The joined family's "
        "books, kept in her hand, balance to the penny. So does "
        "her choir."
    ),
    "q038": (
        "The household my parents made was a small Dallas house "
        "within earshot of both capitals: the shop's sounds at one "
        "end of the day, the piano's at the other, my mother's "
        "students through the front door and my father's customers "
        "phoning the back line, and the children raised, in "
        "effect, in the doorway between music made and music "
        "mended. Its rules were the two lines' rules domesticated "
        "together: nothing discarded that could be mended, no "
        "debt that could be avoided, every job and every birth "
        "entered in a book, everybody fed."
    ),
    "q039": (
        "What my parents carried into their household from their "
        "own lines can be itemized like an inventory, and the "
        "family has: from Jasper, the doctrine, the day book "
        "habit, and the standard that a repair is a promise; from "
        "Coral, the amendment that people are in the inventory "
        "too; from Slate, the keeper's rule that the plant does "
        "not go down on your watch; from Opal, the front room and "
        "the lesson that music is a household utility, like "
        "water; from Jet, behind them all, the Bible and its "
        "columns. I grew up inside the sum of those inheritances "
        "and mistook it, for years, for just how houses were."
    ),
    "q040": (
        "The children born to my parents were two: I came first, "
        "in 2000, with the joined name, and my sister Opal in "
        "2003, named for our grandmother Opal Flames, whose piano "
        "she would one day teach on. The naming declared the "
        "joining twice over, in the family's two dialects: the "
        "son carries both surnames, the union itself; the "
        "daughter carries a grandmother, the continuity. Both of "
        "us were entered in the family Bible in our mother's "
        "hand, the new generation arriving, as every generation "
        "of both lines has, already inside the record -- named, "
        "dated, and expected."
    ),
    # Chapter 5 -- My Generation
    "q041": (
        f"{BIRTH_YEAR}. I was born in 2000, the first child of "
        "Ruby Flames and Onyx Frozen, into a joined family one "
        "year old and two lines more than fifty years in Texas. "
        "The family's state that year was settled and narrow: the "
        "shop established, the front room full, my grandfather "
        "Jasper at the head of one table and my grandfather Slate "
        "at the other, both grandmothers living. I was born into "
        "the doctrine's third Texas generation, and the record of "
        "my birth, in my mother's hand in the Bible, gives the "
        "date and the long name and nothing else, as if the rest "
        "were up to me."
    ),
    "q042": (
        f"{BIRTHPLACE}. I was born in Dallas, Texas, in a hospital "
        "across town from the river-flat wards where my father was "
        "born, and brought home to the small house between the "
        "shop and the front room. The place mattered to the two "
        "lines by then in a way it had not in 1947 or 1949: "
        "Dallas was no longer the destination either line had "
        "wagered on. It was the premise both of them stood on, "
        "and I received it as a birthplace, which is a wager's "
        "winnings, spent without ever knowing their price."
    ),
    "q043": (
        "My sister is Opal Flames, born in 2003, named for our "
        "mother's mother, and the joined family's second string "
        "in every sense: she sang -- harmony in our mother's front "
        "room, then on sessions at other people's studios and "
        "mine -- and as a teenager she kept the Cold Room's books "
        "in its first years, in a hand as exact as our mother's. "
        "Her place in the household was always the one who could "
        "say the unsaid thing at the table and then pass the "
        "bread. She teaches piano now, in our mother's front room, "
        "on our grandmother's piano, to the children of her "
        "street -- the Flames line's music in its fourth Texas "
        "generation, arriving right on schedule."
    ),
    "q044": (
        "The branch that left is the Frozen line's Chicago line: "
        "my great-aunt Topaz Frozen, my grandfather Jasper's "
        "sister, who went north in 1969 at eighteen for work and "
        "for the oldest reason -- the life laid out for her in "
        "Dallas was visible to her, and she declined to watch it "
        "arrive. She married Obsidian Whitfield there, worked in "
        "the school system for forty years, and raised Jasper "
        "Whitfield, whose daughter Topaz carries her "
        "great-grandmother's name into a fourth generation. The "
        "Chicago line is the family's one standing branch: rooted "
        "in the same day books, flowering six hundred miles north, "
        "on the telephone at Christmas and in the flesh at "
        "funerals."
    ),
    "q045": (
        "Growing up between two lines meant growing up inside "
        "both lines' work. My childhood rooms were the shop and "
        "the front room: the bench where my father let me rewire "
        "a lamp at nine and restring guitars at eleven, inspected "
        "and redone until they were right; the piano where my "
        "mother taught me in the order she taught everyone, "
        "whether I was her son or not. At one family's table I was "
        "Jasper's grandson, expected to listen before touching; "
        "at the other I was Slate's, expected to have practiced. "
        "I took my toys apart to hear what was inside them, and "
        "both families, instead of scolding me, learned to give "
        "me broken things, which I preferred to new ones."
    ),
    "q046": (
        "What the two lines required of their children in my "
        "generation was plain and total, and remarkably agreed "
        "between them: work, entered honestly; music, practiced "
        "whether or not it was loved; church, because our mother "
        "played the organ and the family sat where it could see "
        "her hands; and the keeping -- of things, of records, of "
        "each other -- absorbed as household physics rather than "
        "taught as a lesson. I cannot remember being told to keep "
        "a thing that could be fixed. I can only remember never "
        "once seeing anyone in either family throw away a thing "
        "that could be."
    ),
    "q047": (
        "The doctrine reached me the way it reaches everyone in "
        "this family: not as a speech but as a sentence overheard "
        "until it became a reflex. My grandfather Jasper said it "
        "at his bench when I was small and he was old -- a family "
        "keeps what it can fix, and fixes what it keeps -- about a "
        "customer's lathe, I think, or a radio. My father said it "
        "about machines; my mother applied it, pointedly, to "
        "people's marriages and children's fevers; my grandmother "
        "Opal, from the other line, said the Flames version of it "
        "at her piano: you do not discard a slow student. What I "
        "understood then was: do not throw away. What I understand "
        "now is harder: some keeping is work, and some is only "
        "fear with good posture, and the sentence does not tell "
        "you which is which."
    ),
    "q048": (
        "The gathering I remember whole is a Christmas in the "
        "middle of my childhood, at my Frozen grandparents' "
        "house: Jasper at the head, Coral moving between kitchen "
        "and table, my father and aunt Jade arguing happily about "
        "a radio, my mother at the piano between courses, Slate "
        "and Opal Flames across the table like a visiting "
        "delegation that had been visiting for a decade, and the "
        "children underfoot in a house that smelled of machine oil "
        "and greens in about equal measure. What was said has "
        "mostly gone. What was unsaid was that this arrangement "
        "of people was temporary, and every adult at the table "
        "knew it, and passed the bread anyway."
    ),
    "q049": (
        "The names repeat across the two lines like verses "
        "answering each other. Topaz Frozen named her Chicago son "
        "Jasper, for her brother, and his daughter is Topaz, for "
        "her. My sister is Opal, for our grandmother. My uncle "
        "Jet Flames is Jet for his grandmother, the matriarch, "
        "and carries her name into the male line without anyone "
        "finding it strange. And I am the two surnames themselves, "
        "the only one of us whose name is a sentence about the "
        "family rather than a stone from its list. The naming law "
        "makes the family's genealogy legible at roll call: you "
        "can hear the generations in the names before you ever "
        "open the books."
    ),
    "q050": (
        "I first understood the joined family was something I "
        "would one day have to carry in 2018, at my grandfather "
        "Jasper's funeral, when the day book changed hands in the "
        "front room afterward -- not ceremonially, just my father "
        "taking it from the shelf because someone had to enter "
        "the death, and entering it in a hand that had aged into "
        "something very like his father's. Nobody said the office "
        "had passed. The book was simply in different hands, and "
        "I understood, standing there at eighteen with a plate in "
        "my hand, that one day both books would be in mine, and "
        "that carrying a family turns out to be mostly a matter "
        "of entering the deaths and the births in a hand the next "
        "keeper can read."
    ),
}

ANSWERS.update({
    # Chapter 6 -- The Family Trades
    "q051": (
        "The Frozen line's founding trade was keeping other "
        "people's machines alive: Flint was a millwright and "
        "machinist, the man a plant sends for when the line shaft "
        "dies, and the trade shaped what that line thought work "
        "was in ways it has never escaped. Work, in the founding "
        "definition, is not making things. It is understanding "
        "things that have stopped, in the presence of the people "
        "who depend on them, and returning them to service. Every "
        "trade the joined family practices descends from that "
        "definition or answers to it."
    ),
    "q052": (
        "Jasper's trade differed from his father's in the way a "
        "son's always does: Flint kept machines running; Jasper "
        "made the tools that the keeping required, one remove "
        "further into precision. What passed between them "
        "unchanged was the standard and the paperwork: measure "
        "twice, enter it in the book, sign nothing you would not "
        "want found. The family's trades have moved one remove "
        "further in every generation since -- from machines, to "
        "tools, to radios, to recordings -- and the thing "
        "transferred intact is never the skill. It is the standard "
        "the skill is held to."
    ),
    "q053": (
        "My father's trade carried the Frozen work forward by "
        "translating it into electronics: where Flint read a dead "
        "machine by ear and Jasper by measurement, Onyx reads a "
        "dead radio by schematic and by ear together, and the "
        "guitars that cross his bench added music to the Frozen "
        "business for the first time. What he added of his own "
        "was a teacher's patience: every kid on the street who "
        "hangs around the bench gets handed the next heavier "
        "thing, as he was, and as I was after him."
    ),
    "q054": (
        "The work that ran down the Flames line was fire first "
        "and music after: Garnet kept boilers and furnaces, the "
        "buildings' hidden fires; Slate translated the same "
        "keeping into heating and refrigeration, the century's "
        "cold machinery; and through Opal the line took up its "
        "second trade, the teaching of music, which her daughter "
        "Ruby carries and her granddaughter Opal now practices. "
        "The family has sometimes spoken as if the Frozen trades "
        "were the work and the Flames music was the atmosphere. "
        "The books refute the household that believes it: my "
        "mother's income was the steadier for thirty years, and "
        "her trade requires the same ear, the same discipline, "
        "and the same refusal to discard a slow student that the "
        "bench requires for a dead radio."
    ),
    "q055": (
        "My own trade is recording: I founded the Cold Room, a "
        "small studio in a converted icehouse in Dallas, in 2022, "
        "and have kept it since, fire and rebuilding included. In "
        "the two lines' work it is a translation, not a break: a "
        "recording session is a machine for keeping performances "
        "that would otherwise stop, and my whole craft is the "
        "family definition with tape in it -- listen first, "
        "understand the thing in front of you, return it to "
        "service, enter it in the log. My great-grandfather kept "
        "plants running so a city could work. I keep a room ready "
        "so a song can stay. Both families recognize the posture "
        "even where they do not know the equipment."
    ),
    "q056": (
        "My sister Opal's work is double, in the family's "
        "pattern: she sings -- harmony in the front room, then on "
        "sessions, a voice engineers ask for by description -- "
        "and she teaches, giving piano lessons in our mother's "
        "front room on our grandmother's piano, for fees her "
        "grandmother would have called cake and eggs in modern "
        "denominations. As a teenager she kept the Cold Room's "
        "books in its first years, and the log habit she "
        "installed outlasted her tenure; the studio's paperwork "
        "still runs on Opal's forms. She is the Flames line's "
        "music and the Frozen line's bookkeeping in one person, "
        "which the family regards as the joining working exactly "
        "as designed."
    ),
    "q057": (
        "What the two lines' trades, taken together, taught the "
        "joined family about work can be stated as the doctrine's "
        "working form: a person should be able to be sent for. Be "
        "the one whose name is spoken when the thing stops -- the "
        "machine, the boiler, the choir, the session, the "
        "household -- and be worthy of the sending: arrive with "
        "your tools, listen before you touch, write down what you "
        "found, charge honestly, and leave the thing better "
        "documented than you found it. It is not a glamorous "
        "ethic and it has never made any of us rich. It has made "
        "four generations of us employable by our neighbours, "
        "which the family counts as the same thing as honorable."
    ),
    "q058": (
        "The tools of the lines' trades that survive are kept in "
        "three places, like a distributed archive: Flint's "
        "toolbox is in my keeping, its fitted slots still holding "
        "most of what he carried into Dallas; my father's "
        "soldering iron and the day books are at his shop and my "
        "studio respectively, the iron still in use, which he "
        "would consider the only fit memorial; and the Flames "
        "piano stands in my mother's front room, played daily, "
        "with my sister teaching on it. Jasper's measuring tools "
        "went to Jasper Whitfield in Chicago, by Jasper's own "
        "direction -- the namesake receiving the namesake's "
        "instruments, which is how this family files its "
        "affections: in objects, addressed."
    ),
    "q059": (
        "The trades the lines lost are the founding ones "
        "themselves: millwrighting, the keeping of great "
        "belt-driven machines, died under the Frozens as the "
        "machines died, and furnace-keeping died under the "
        "Flameses as the boilers were replaced by systems with no "
        "fire in them to keep. What the losing cost was not "
        "income -- each generation found the next remove -- but a "
        "kind of certainty: Flint and Garnet knew exactly what "
        "their work was for, in a way the rest of us, translating "
        "and translating again, have had to reconstruct. The "
        "family keeps the founders' tools partly as evidence that "
        "the certainty existed."
    ),
    "q060": (
        "The joined family's line of work stands now in a "
        "converted icehouse and a front room: the Cold Room, "
        "rebuilt after its fire, where I record other people's "
        "music to the standard my father set for radios; and my "
        "sister's piano lessons, which she gives to the children "
        "of her street in a direct descent from her grandmother "
        "Opal's front room that nobody arranged and everybody "
        "recognizes. The trades will translate again -- they "
        "always have. What I watch for, at my age, is not the "
        "skill. It is whether the standard survives the "
        "translation, and so far, in the evidence available to "
        "me, it does."
    ),
    # Chapter 7 -- Houses, Heirlooms, and Records
    "q061": (
        "The Flames record book is a Bible of the heavy kind, "
        "bound in boards that have been re-backed once, its "
        "flyleaf and margins ruled into columns by Jet Flames in "
        "1949: born, married, died. Her hand fills the first "
        "fifty-two years, small, level, and exact. Slate's hand "
        "follows, heavier; my mother's after his, the copperplate "
        "come back; and mine last, in the margins, where the "
        "newest keeper writes smallest. It contains no commentary "
        "except one footnote, which is mine. It is the Flames "
        "line's constitution in three columns, and everything "
        "else that line tells is case law."
    ),
    "q062": (
        "The Frozen records are day books: a shelf of ruled "
        "ledgers running from Flint's first Dallas job in 1947 to "
        "my father's entries this year, every job entered, "
        "described, and priced, every failure entered with its "
        "cause. Where the Bible knows who the family was, the day "
        "books know what the family did on ten thousand ordinary "
        "days -- which is more, in bulk, and less, in meaning, "
        "and the joined family needs both kinds of knowing. My "
        "own session logs are the day books' fourth generation, "
        "kept on the same rule my great-grandfather kept: a thing "
        "not written down has not been learned, only survived."
    ),
    "q063": (
        "Flint's toolbox survives in my keeping: an iron-bound "
        "chest, carpenter-made, the fitted slots worn bright "
        "where the tools have slid home ten thousand times. Some "
        "tools are his, initialed in a machinist's punch; some are "
        "Jasper's, added when the chest stood at his bench; one "
        "wrench is my father's. It is not a relic in a case. It "
        "is a working object that three generations have reached "
        "into, and its testimony is plain: this family measures "
        "its continuity not in blood, which is common, but in "
        "custody -- in who was trusted to keep the box."
    ),
    "q064": (
        "The object that carries the Flames line's memory is the "
        "piano: bought used into Opal Reyes's household before "
        "she was Opal Flames, played by her through fifty years "
        "of lessons and services, inherited by my mother, and "
        "refused -- this is the operative fact -- to every bill "
        "that ever threatened it. When money was shortest, in my "
        "own thin years, it was my wife Amber who restated the "
        "rule the line has always lived by: some things are not "
        "the accounts' business. The piano stands in my mother's "
        "front room still, and my sister teaches the street's "
        "children on the keys her grandmother wore smooth."
    ),
    "q065": (
        "The two lines' houses make a legible sequence: rented "
        "rooms near the Dallas plants, where both families were "
        "wagers; the small houses Flint and Garnet each bought "
        "out of decades of wages, where they were facts; my "
        "parents' house between the shop and the front room, "
        "where the joining was a business and a household at "
        "once; and my own small house two streets from the "
        "studio, where the family became an archive. Each house "
        "marks its era's economics honestly -- rent, wages, "
        "trade, keeping -- and the family's sentiment attaches "
        "not to any one of them but to the succession: we have "
        "always lived within earshot of our work."
    ),
    "q066": (
        "The joined family's paper memory, beyond the two sets "
        "of books, is letters and photographs: Topaz's letters "
        "from Chicago, kept in a labelled box; my mother's lesson "
        "books and choir lists; Coral's annotated accounts; and, "
        "in the present generation, my wife Amber's prints -- she "
        "has photographed every room this family has worked in, "
        "so the archive now has a visual index made by the woman "
        "who married into it. The keeping of all of it was "
        "women's work in the first generations and is mine now by "
        "default and by training: I was raised by people who "
        "wrote things down, and it never occurred to me that a "
        "family had a choice."
    ),
    "q067": (
        "My own generation's records are the session logs: every "
        "session at the Cold Room entered to the minute -- who "
        "played, what broke, what worked -- in a practice I "
        "learned from my studio master and he, though he never "
        "knew it, from the same doctrine that ran my father's day "
        "book and my great-grandmother's Bible. The two older "
        "archives divide the world between them -- the Bible "
        "keeps the people, the day books keep the work -- and "
        "mine keeps the work only. A future keeper reading the "
        "logs will know what this family did; for who we loved, "
        "they will need the Bible and Amber's prints, and the "
        "three archives correct each other, which is why the "
        "family keeps all three."
    ),
    "q068": (
        "What the family has lost from its archives is specific "
        "and still felt: Flint's wartime shop notebooks, left "
        "with a Pittsburgh landlady in the hurry of 1946 and "
        "never recovered, so the Frozen line's founding skill is "
        "documented only from Dallas; the Flames line's "
        "Mississippi years before 1949, which are telling and not "
        "record, because Jet began the Bible in Texas and entered "
        "the Mississippi dead from memory; and a box of Topaz's "
        "early Chicago letters, water-damaged in a basement in "
        "the eighties. The gaps are entered in the books too, as "
        "gaps: a family that records its losses keeps them from "
        "becoming inventions."
    ),
    "q069": (
        "The record and the telling disagree most famously about "
        "the river. The Flames telling has always said Garnet "
        "and Jet came down the river to Dallas; the geography, "
        "the railway timetables, and one surviving ticket stub in "
        "Jet's papers say they came by rail from Holly Springs, "
        "west and slightly south, no river involved. The family "
        "lives with the difference the way it lives with most of "
        "its inheritances: the record is right about the journey "
        "and the telling is right about the meaning, because "
        "arriving in Texas felt, to a Mississippi furnace man's "
        "family, like a river had delivered them out of a "
        "shrinking town into a growing one. I have entered both "
        "in the Bible, labelled. It is the book's one footnote, "
        "and the footnote is mine."
    ),
    "q070": (
        "The family's records and heirlooms are in my keeping "
        "now, and I was not chosen so much as fallen to: I am the "
        "one who writes things down, the keeper by habit, trained "
        "by a father with a day book and a mother with a Bible. "
        "The custody is understood in the family to be an office, "
        "not a possession -- the books are in my house the way "
        "the toolbox is in my house, in trust for my sister, for "
        "the Chicago young, and for keepers none of us will meet. "
        "Opal holds copies of everything essential. The Chicago "
        "branch holds its own papers. The archive, like the "
        "family, survives by being distributed."
    ),
    # Chapter 8 -- Hard Years and Partings
    "q071": (
        "My grandfather Jasper Frozen died in 2018, at home, "
        "with his tools in reach, as he would have specified. He "
        "was seventy. What stayed in the house afterward was the "
        "day book, open on his bench to a job half-entered, which "
        "my father finished entering because someone in this "
        "family finishes the entry; the customers of three "
        "generations, who came to the funeral in their work "
        "clothes; and his standard, which turned out to be "
        "load-bearing in my own work in ways I had mistaken for "
        "my own ideas. My father entered the death in the day "
        "book, and my mother entered it in the Bible, and the "
        "two entries, read together, are the joined family's "
        "whole method in one sad page."
    ),
    "q072": (
        "My grandfather Slate Flames died in 2016, two years "
        "before Jasper, of the lungs his trade had spent fifty "
        "years testing. He was seventy. What his death closed in "
        "the Flames line was its living memory of Mississippi: he "
        "was the last person alive who had been born in Holly "
        "Springs, a three-year-old immigrant in his own country, "
        "and with him the origin passed entirely from memory into "
        "telling and record. My mother played the organ at his "
        "funeral -- her father's funeral, on her grandmother's "
        "church's organ -- and entered his death in the Bible in "
        "the hand her grandmother taught her mother, who taught "
        "her."
    ),
    "q073": (
        "The founding generations passed in the order the books "
        "show: Flint first, in 1992, entered by Jasper in the day "
        "book with the job he had been working left respectfully "
        "unfinished on the page; Garnet in 1994, entered by Jet "
        "in the Bible in a hand still level at seventy-one; Pearl "
        "in 1999, whose accounts end mid-year in her own hand and "
        "are completed by Coral's, the matriarch's office passing "
        "in the paperwork before anyone said it aloud; and Jet in "
        "2001, the last of the founders, whose death my mother "
        "entered as a girl's hand enters nothing -- carefully, "
        "in the columns Jet herself had ruled. After 2001, no one "
        "living had made either journey, and both lines' pasts "
        "passed entirely into the records' keeping."
    ),
    "q074": (
        "The disaster of my own generation was the fire of 2024: "
        "a fire in the building next to the Cold Room, and then "
        "in mine, which took the studio as first built -- the "
        "room of my young ambition, two years of accumulated "
        "place. The log books were at the house. The standard was "
        "in the man. The joined family answered the way it "
        "answers: my sister did the arithmetic, Amber "
        "photographed the ruin before anyone could sentimentalize "
        "it, Topaz's line sent money from Chicago with a note "
        "that said only 'for the keeping', and I rebuilt the room "
        "over two years, slower and smaller, in the same thick "
        "icehouse walls. Some things understood can be mended. "
        "The fire is the doctrine's hardest exam, and the family "
        "grades it a pass with the cost itemized."
    ),
    "q075": (
        "The family's oldest parting is Topaz's leaving, in 1969, "
        "and it must be weighed in its own era's terms: an "
        "eighteen-year-old daughter of a respectable Dallas "
        "household going north alone was read, then, as a kind "
        "of family failure, and my grandfather Jasper -- who "
        "believed in keeping everything -- had to learn to keep "
        "a sister at six hundred miles, by letter and telephone, "
        "which he did, weekly, for forty-nine years, without ever "
        "once asking her to come home to live. What the leaving "
        "cost both sides was presence. What it bought was the "
        "branch, and the proof that the doctrine travels."
    ),
    "q076": (
        "The family's standing estrangement is Zircon Flames, my "
        "grandfather Slate's younger brother, who quarreled with "
        "the family over Garnet's estate in 1994 -- the house, "
        "the tools, the small money -- and took his line out of "
        "visiting, out of letters, out of the record. What is "
        "honestly known is the quarrel's subject, which was "
        "property, and its year, and nothing reliable about its "
        "merits, because both sides' accounts were kept by "
        "partisans. His descendants are in the Bible as names "
        "without dates after a certain year. The family does not "
        "pretend the column continues. It is the book's one "
        "admitted defeat, and I have left the space for the "
        "entries blank rather than tidy."
    ),
    "q077": (
        "The thinnest years of my own time came in 2020, when I "
        "was twenty and working sessions in other people's rooms "
        "and the rooms, all of them, went quiet at once. What was "
        "short was work, in the specific form of other people's "
        "sessions. What I did was the family's old thing: I "
        "repaired -- radios, guitars, a church organ's blower, "
        "anything with a circuit or a bellows -- out of my "
        "father's shop and then out of a corner of it that became "
        "mine, and the repair money is, in the end, what "
        "capitalized the Cold Room two years later. My father had "
        "done precisely this in his own thin years. I recognized "
        "the maneuver only while I was performing it, which the "
        "family says is how the doctrine prefers to be learned."
    ),
    "q078": (
        "The hard years tested the doctrine at its weakest word, "
        "which is 'can'. A family keeps what it can fix -- but "
        "the fire could not be unburned, the grandfathers could "
        "not be repaired, Zircon's column could not be filled by "
        "wishing, and a doctrine that only works on objects would "
        "have died in those years. What the joined family "
        "learned, and what I now take the sentence to have always "
        "meant, is that keeping is not always restoring: "
        "sometimes it is entering the death in both books, "
        "keeping the piano in the family, keeping the room's "
        "walls and rebuilding inside them. The doctrine bent. It "
        "bent toward custody, away from repair, and it did not "
        "break, and the bending is the development the next "
        "generation will inherit along with the sentence."
    ),
    "q079": (
        "Who held the family in its hard years was, in sequence, "
        "the same office in different hands: Jet at her table in "
        "the Flames founding years; Pearl at her accounts in the "
        "Frozen ones; Coral through the decades of Jasper's "
        "prime, quietly, in the margins of the day books; Opal "
        "Flames through the Flames line's transitions, at the "
        "piano and the table both; and in my generation my mother "
        "and my wife, who between them did the arithmetic and the "
        "photography and the plain refusal to let the thing "
        "scatter. The matriarch's pattern is not a person, the "
        "family has learned. It is a job that descends, in both "
        "lines, to whoever is willing to feed people and write "
        "things down."
    ),
    "q080": (
        "What survived the hard years intact is a short list and "
        "the family recites it like one: the Bible, the day "
        "books, the toolbox, the piano, the doctrine, the two "
        "names. What survived changed is the longer and truer "
        "list: the studio, rebuilt smaller inside its old walls; "
        "the family itself, smaller in Dallas and larger in the "
        "world; the doctrine, bent toward custody; the records, "
        "annotated now with their own gaps. The distinction "
        "matters to us. A family that claims everything survived "
        "intact is lying in a way the records would catch. Ours "
        "survived the way its objects did: kept, mended where "
        "mending was possible, and entered honestly where it was "
        "not."
    ),
    # Chapter 9 -- Reunions and the Living Family
    "q081": (
        f"{PARTNER}, born Amber Verano, a photographer. My wife "
        "came into this family in 2022, hired to photograph a "
        "session at the Cold Room, and married me in 2023, and "
        "thereby did the thing this book has watched three "
        "generations do: she brought another family's whole "
        "inheritance into the house and set about the long work "
        "of joining the archives. Her prints of our rooms hang in "
        "every room I have worked in since. The records enter her "
        "as what she is: not an addition to the family but one of "
        "its two present heads, and the keeper of its visual "
        "memory."
    ),
    "q082": (
        "Amber's family, the Veranos, are people of images and "
        "letters: her father Agate paints signs -- the lettering "
        "on half the storefronts of her childhood street -- and "
        "her mother Beryl taught school and writes, in a "
        "beautiful hand, letters her family keeps the way mine "
        "keeps its books. What her line brought into mine was the "
        "eye: my family documented itself in entries and logs, in "
        "words and numbers, and Amber taught it to document "
        "itself in light. Her family's naming custom is the same "
        "as ours -- the stones -- which her parents and mine "
        "discovered at the first joint Christmas with the "
        "delight of people finding a shared relative. The two "
        "doctrines get along. They are, at bottom, the same "
        "instruction in different media: pay attention, and keep "
        "the evidence."
    ),
    "q083": (
        "The family's next generation, as it stands, is headed in "
        "Dallas by my sister Opal, who teaches the street's "
        "children on the family piano and sings on the city's "
        "sessions, and in Chicago by Topaz Whitfield, Jasper "
        "Whitfield's daughter, who carries her great-grandmother "
        "Topaz's name and is, by the branch's reports, the keeper "
        "of its copy of the record. Beside them stand cousins by "
        "marriage and Jade's children in Fort Worth. There are "
        "fewer of them than there were of us. The family does not "
        "hide this from itself; it is entered, like everything "
        "else, and the entering is plain: the lines continue, "
        "narrower, in good hands."
    ),
    "q084": (
        "The family's reunion, as it happens now, is not an event "
        "so much as a gravity: Christmas at my parents' house or "
        "mine, the Chicago line down by train when it can be "
        "managed, the table extended with the board my father "
        "made for exactly this purpose, and the whole living "
        "family assembled in one room at least once a year to be "
        "counted by eye. The young are fed first, the old are "
        "consulted, the piano gets played whether anyone "
        "schedules it or not, and somebody -- lately it has been "
        "Opal -- reads the year's entries aloud from a copy of "
        "the Bible, births and deaths together, which is the "
        "family's liturgy and takes four minutes."
    ),
    "q085": (
        "The Chicago branch stands with the root today in good "
        "repair, which was not inevitable and is not automatic: "
        "visits in both directions most years, the telephone "
        "habits Jasper established with Topaz continued by their "
        "grandchildren on newer machines, obligations kept -- the "
        "money the branch sent at the fire was answered, in kind "
        "and in silence, when the branch had its own hard year, "
        "and both sides entered the exchange in their books "
        "without ever calling it a debt. Distance, the family has "
        "learned, is a condition, not a verdict. The verdict is "
        "made by the keeping, and the keeping, on present "
        "evidence, is mutual."
    ),
    "q086": (
        "What my generation is teaching the young, deliberately, "
        "is the keeping itself: Opal's students get the scales "
        "before the songs, the way four generations of Flames "
        "children did; the Chicago young have copies of the "
        "record and instruction in its columns; two engineers I "
        "trained at the Cold Room learned the log book as my "
        "master taught it to me, which is the doctrine exported "
        "outside the bloodline, where it seems to grow fine. What "
        "the young refuse to learn is also entered honestly: the "
        "day book's patience; the belief that a thing must be "
        "understood before it is replaced. They will learn those "
        "the way we did, by breaking something they love, or they "
        "will not, and the records will say which."
    ),
    "q087": (
        "The doctrine as the young say it is shorter and has a "
        "laugh in it: keep what you can fix, they say, and know "
        "what you can't. Opal's version, delivered at the table "
        "and now quoted back at me, adds the clause my generation "
        "learned from the fire -- and keep the ashes out of the "
        "book, meaning: enter the loss, don't embalm it. I record "
        "their version without endorsing every word of it, which "
        "is exactly the relation Jasper would have had to mine. "
        "The sentence has survived three generations by being "
        "argued with in every one. A doctrine nobody argues with "
        "is a slogan, and this family has never kept slogans in "
        "the books."
    ),
    "q088": (
        "The family lives now in three places: Dallas, where my "
        "parents, my sister, and I are within a few streets of "
        "the ground both lines chose in the forties; Chicago, "
        "where the branch is rooted as deeply in its city as we "
        "are in ours; and Fort Worth, where my aunt Jade's "
        "household keeps the family's western door. It came to be "
        "spread so by the family's oldest law, which is that it "
        "goes where the work is and stays where the keeping is. "
        "The map of us would fit on the Bible's flyleaf. Some "
        "years I think it should be drawn there."
    ),
    "q089": (
        "What the living family still argues about is the old "
        "subjects in their present forms: whether the Cold Room "
        "should pass one day to my engineers or stay in the "
        "blood, which is the doctrine against the standard, round "
        "forty-one; whether Opal's students should be charged "
        "real money, which is the front room against the rent; "
        "whether the Chicago young are Dallas family or Chicago "
        "family, which is 1969, still warm. The arguments are "
        "entered here without resolution because they are the "
        "family's vital signs. We have never agreed about the "
        "inheritance. We have only ever agreed to keep arguing "
        "inside the house."
    ),
    "q090": (
        "The joined family as it stands now, in one honest "
        "assessment: smaller in number, wider in the world, "
        "poorer in nothing it counts and richer in one thing it "
        "counts above the rest, which is that its records are "
        "complete and its young can read them. It is kept -- that "
        "is the verdict, in the family's own verb. Not preserved, "
        "not embalmed: kept, the way a room is kept ready and a "
        "book is kept current, by work, in the present tense, by "
        "people who expect to hand it on. What we hand on is the "
        "subject of the last chapter, and it is shorter than the "
        "chapters of getting, because keeping turns out to be a "
        "brief art to describe and a long one to practice."
    ),
    # Chapter 10 -- What Was Passed Down
    "q091": (
        "The doctrine, handed on, is this: a family keeps what "
        "it can fix, and fixes what it keeps. At the root it "
        "meant machines -- Flint's plants, Jasper's tools, the "
        "refusal to let a broken thing leave the world while it "
        "could still be understood. In my father's hands it came "
        "to mean work and its record; in my mother's, people, "
        "who are also kept or lost by attention; in mine, rooms "
        "and songs and the ashes clause the fire taught; in the "
        "young's, already, it means knowing the difference. What "
        "it will ask of the next generation is what it has asked "
        "of every one: arrive with your tools, listen before you "
        "touch, write down what you found, and leave the thing "
        "-- the machine, the room, the family -- better "
        "documented than you found it."
    ),
    "q092": (
        "In my own keeping are the Bible, Flint's toolbox, the "
        "day books, and the session logs of my own years -- the "
        "family's written self, in four kinds of record. Already "
        "passed on: the piano's future, designated to Opal while "
        "it still stands in our mother's front room, so the "
        "transfer will be a visit and not a probate; Jasper's "
        "measuring tools, to the Chicago namesake, before me and "
        "not by me; copies of the records, to Opal and to "
        "Chicago, against fire and the other archivist, "
        "forgetfulness. A keeper who holds everything holds it "
        "for one lifetime only. The family's rule, learned from "
        "its losses, is to distribute the keeping while the "
        "keeper can still explain the columns."
    ),
    "q093": (
        "What I have passed down already, beyond objects: the log "
        "book standard, to two young engineers who now teach it "
        "to their own assistants in rooms I have never seen, so "
        "the family's paperwork runs in studios that have never "
        "heard the family names; the bench standard, to every kid "
        "who hung around my father's counter and mine and got "
        "handed the next heavier thing; and to my sister's "
        "students, through her, the front room's doctrine that a "
        "child is taught by whoever is nearest and musical. A "
        "person passes down what they practice in front of "
        "witnesses. The rest is furniture."
    ),
    "q094": (
        "The names carried by the living young are Jasper and "
        "Topaz in Chicago, in their second bearers and doing "
        "well; Opal in Dallas, in hers; Jet, in my uncle, holding "
        "the matriarch's name in the male line; and the two "
        "family names themselves, Frozen and Flames, on both "
        "branches, on a shop door and a studio door, and joined "
        "entire in my own. What I hope the names will do for "
        "their bearers is what names in this family have always "
        "done: give the bearer a standard to argue with. What I "
        "fear is only that a name might be mistaken for the thing "
        "it names -- that a young Frozen or Flames might think "
        "the keeping is in the blood. It is not. It is in the "
        "columns, and the columns are work."
    ),
    "q095": (
        "What the records still get wrong, I correct here while "
        "I can: the Bible gives Zircon's birth in 1950 and his "
        "birth certificate, which Amber found among Jet's "
        "papers, says 1951, and the certificate is right -- Jet "
        "entered her youngest son's year from memory, a year "
        "late, in a hard winter; the Frozen day book's first "
        "Dallas entry is dated 1947 and Flint's discharge papers "
        "show he reached the city in 1946, and both are kept, "
        "labelled, because the family counts its migration from "
        "the household's arrival and the papers count the man; "
        "and the river in the Flames arrival story is a metaphor "
        "the family has agreed to keep, labelled as one, in the "
        "footnote that is mine. Records that cannot be corrected "
        "are monuments. These are books, and books in this family "
        "are kept the way rooms are kept: open, and in use."
    ),
    "q096": (
        "The family's unfinished business is the blank column: "
        "Zircon Flames's descendants, my mother's cousins, whose "
        "entries stop in 1994 where the quarrel stopped them. "
        "Somewhere there are people whose births, marriages, and "
        "deaths belong in the Bible and are not in it, and the "
        "space for them is kept, ruled and empty, against the day "
        "the family is whole or the day a keeper braver than I "
        "goes and asks. Beside it, smaller: the Chicago branch's "
        "own entries, kept in their copy there, not yet merged "
        "into ours; and my own album, the songs I have kept in a "
        "drawer through the studio's whole life, which the "
        "family counts, correctly, as an entry I owe the record "
        "and have not made."
    ),
    "q097": (
        "What this joined family is for, told whole, is keeping: "
        "it came into the world, in our part of it, as two lines "
        "of people who are sent for when a thing stops, and it "
        "has spent three generations in Texas widening the "
        "definition of the thing -- machines, boilers, tools, "
        "radios, choirs, rooms, songs, each other -- without ever "
        "changing the posture. The founding myth said we were the "
        "people the city sent for. The records, told whole, say "
        "something both smaller and larger: we were the people "
        "who wrote it down. Cities forget whom they sent for. "
        "The books remember. That is what the family was doing in "
        "the world, and on the evidence of the columns, it is "
        "still doing it."
    ),
    "q098": (
        "The plain advice the family gives its young, beneath "
        "the doctrine, is working instructions and fits on one "
        "page of the Bible's back flyleaf, where Jet wrote it in "
        "her copperplate: learn a trade that can be sent for; "
        "keep a book and write in it the day things happen; never "
        "sell the piano; feed whoever is at the table; marry, if "
        "you marry, someone who keeps their own records; and when "
        "a thing breaks, understand it before you mourn it or "
        "replace it. Children of these lines have carried that "
        "page into three cities and two centuries. It travels "
        "well because it is short, and it is short because "
        "everything on it has been paid for."
    ),
    "q099": (
        "The next entry I want written in the family's records "
        "is not a birth or a death, though the books will take "
        "those in their turn. It is the entry for the day the "
        "keeping itself changes hands whole -- Bible, day books, "
        "toolbox, logs -- from my keeping to my sister's or to "
        "the Chicago keeper's, in a front room, with the piano "
        "played and the columns explained and the transfer "
        "entered, in the new keeper's hand, as an event of the "
        "family like any other. Keepers in this family have too "
        "often received the office at a funeral. I should like "
        "the books to record one handover that happened at a "
        "table, in daylight, with everybody fed."
    ),
    "q100": (
        "The single fact about this family that should outlast "
        "every story told about it is not either arrival, not the "
        "doctrine, not any name in the columns. It is this: in "
        "seventy-nine years in Texas, through two migrations, a "
        "fire, an estrangement, and the ordinary attrition of "
        "four generations, the books were kept. Every birth and "
        "death that the family could know was entered, in the "
        "year it happened, in a hand the next keeper could read. "
        "Peoples' stories about themselves are weather. A kept "
        "record is climate. If the telling of this family is "
        "forgotten entirely and only the fact survives, let it "
        "be that one: they wrote it down, all of it, and the "
        "writing is how they loved each other across the years "
        "when they could not be in the room."
    ),
})

FACT_ANSWERS = {
    "flames_line_name": ("q001", FLAMES_NAME),
    "frozen_line_name": ("q002", FROZEN_NAME),
    "subject_name": ("q003", NAME),
    "mother_name": ("q005", MOTHER),
    "father_name": ("q006", FATHER),
    "flames_founding_ancestor": ("q011", FLAMES_FOUNDER),
    "flames_origin_place": ("q012", FLAMES_ORIGIN),
    "flames_migration_year": ("q013", str(FLAMES_MIGRATION)),
    "flames_matriarch": ("q014", FLAMES_MATRIARCH),
    "flames_patriarch": ("q018", FLAMES_PATRIARCH),
    "frozen_founding_ancestor": ("q021", FROZEN_FOUNDER),
    "frozen_origin_place": ("q022", FROZEN_ORIGIN),
    "frozen_migration_year": ("q023", str(FROZEN_MIGRATION)),
    "frozen_matriarch": ("q024", FROZEN_MATRIARCH),
    "frozen_patriarch": ("q027", FROZEN_PATRIARCH),
    "birth_year": ("q041", str(BIRTH_YEAR)),
    "birthplace": ("q042", BIRTHPLACE),
    "partner_name": ("q081", PARTNER),
}

YEAR_FACT_ANSWERS = {"flames_migration_year", "frozen_migration_year",
                     "birth_year"}

# Tokens of the superseded canon (the biography build's invented
# Memphis life) that must not appear in these answers.
STALE_TOKENS = ("Memphis", "Evelyn", "Harold", "Alice", "Lydia",
                "Amos", "Emil", "Mabel", "Hart", "Ruth", "Calloway",
                "Brandt", "June", "Walter", "Josef", "Clara", "Anna",
                "Samuel", "Tomas", "Odette")


def main() -> int:
    problems = []
    if len(ANSWERS) != 100:
        problems.append(f"expected 100 answers, have {len(ANSWERS)}")
    for slot, (qid, value) in FACT_ANSWERS.items():
        answer = ANSWERS.get(qid, "")
        if value not in answer:
            problems.append(
                f"character fact {slot}={value!r} missing from {qid}")
        if not answer.startswith(value):
            problems.append(
                f"fact answer {qid} must begin with its value "
                f"{value!r} (the bible extracts the leading value)")
        if slot in YEAR_FACT_ANSWERS:
            first_year = re.search(r"\b(1[0-9]{3}|20[0-9]{2})\b", answer)
            if not first_year or first_year.group(1) != value:
                problems.append(
                    f"year fact {slot}: first year in {qid} is "
                    f"{first_year.group(1) if first_year else None!r}, "
                    f"expected {value!r}")
    if DOCTRINE not in ANSWERS["q007"]:
        problems.append("family doctrine missing from q007")
    if RECORD["family"]["family_saying"].split(".")[0].lower() \
            not in DOCTRINE.lower():
        problems.append("doctrine wording diverges from the record")
    gem_names = set(RECORD["family"]["gem_names"])
    for member in RECORD["family"]["members"]:
        first = member["name"].split()[0]
        if first not in gem_names:
            problems.append(
                f"family member {member['name']!r}: first name "
                f"{first!r} is not a crystal/gem name")
    for stale in STALE_TOKENS:
        for qid, text in ANSWERS.items():
            if stale in text:
                problems.append(f"stale canon token {stale!r} in {qid}")
    if problems:
        print("consistency check FAILED:")
        for p in problems:
            print(" -", p)
        return 1
    doc = {
        "persona": (
            "Frozen In Flames (fictional demonstration persona; the "
            "series' demonstration user)"
        ),
        "provenance": (
            "Fabricated demonstration material. These are the survey "
            "answers of Frozen In Flames, a fictional character, "
            "answering the family-history survey about his own "
            "invented family: two lines, the Flames line of his "
            "mother Ruby Flames and the Frozen line of his father "
            "Onyx Frozen, joined in his parents' marriage and in "
            "his own name. The answers are drawn from the canonical "
            "character record in "
            "demo/frozen-in-flames-character.json (record version "
            "2.0.0, on the canon set by the author on 2026-11-24). "
            "The family described was invented as test data for "
            "the family-history pack and is not the family of any "
            "real person."
        ),
        "answers": ANSWERS,
    }
    OUT_PATH.write_text(json.dumps(doc, indent=1, sort_keys=True),
                        encoding="utf-8")
    print(f"wrote {OUT_PATH}: {len(ANSWERS)} answers, "
          f"consistent with {CHARACTER_PATH.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
