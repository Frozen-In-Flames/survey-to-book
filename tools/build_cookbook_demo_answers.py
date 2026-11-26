#!/usr/bin/env python3
"""Build the cookbook pack's demonstration answers.

The demonstration user of the series is Frozen In Flames, a
fictional persona, and the cookbook survey is the one he takes
about his own cooking: learned in two family lines' kitchens --
the Flames line of his mother Ruby Flames (fire, music, feeding
whoever is at the table) and the Frozen line of his father Onyx
Frozen (iron, patience, accounts, no waste) -- and practiced in
his own household and in the kitchen corner of his recording
studio, the Cold Room. The canonical facts of the character's
invented life live in demo/frozen-in-flames-character.json, on
the canon the author set on 2026-11-24 (record version 2.0.0).
This script loads that record and writes his answers to all 100
cookbook questions, with the fact-bearing answers interpolated
from the record so the two cannot drift apart. A consistency
check runs before anything is written: every recorded fact must
appear in its designated answer and begin it, each year fact
must be the first year in its answer, every year mentioned in
any answer must be a year the record supports, the family
doctrine must appear in the record's exact wording in the
answer that plants it, and no token of the superseded canon
(the biography build's invented Memphis life) may appear.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHARACTER_PATH = ROOT / "demo" / "frozen-in-flames-character.json"
OUT_PATH = ROOT / "demo" / "cookbook-demo-answers.json"

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
FLAMES_MATRIARCH = FF["flames_matriarch"]
FROZEN_MATRIARCH = FF["frozen_matriarch"]
FLAMES_ORIGIN = FF["flames_origin_place"]
FROZEN_ORIGIN = FF["frozen_origin_place"]
STUDIO_YEAR = 2022  # record: founding of the Cold Room
DOCTRINE = ("A family keeps what it can fix, and fixes what it "
            "keeps.")

ANSWERS: dict[str, str] = {
    # Chapter 1 -- The Cook
    "q001": (
        f"{FLAMES_NAME}. The family name of my mother's line is "
        "Flames, and its kitchen is the first one I ever stood "
        "in: a Dallas front room and a stove behind it, where "
        "her mother taught children piano for cake and eggs and "
        "fed everyone who crossed the threshold, and where my "
        "mother teaches and cooks still. The Flames kitchen is "
        "the fire line's: heat kept by hand, music in the next "
        "room, and a table that has never once been set for "
        "exactly the number expected."
    ),
    "q002": (
        f"{FROZEN_NAME}. The family name of my father's line is "
        "Frozen, and its kitchen is the second one I learned in: "
        "a toolmaker's household where the accounts were kept "
        "as exactly as the tools, where nothing edible was "
        "thrown away while it could still be understood, and "
        "where my father still enters every repair in a day "
        "book in the same spirit his grandmother entered every "
        "meal's cost. The Frozen kitchen taught me keeping: of "
        "stock, of records, of standards."
    ),
    "q003": (
        f"{NAME}. That is my full name, and I am the cook this "
        "book comes from: the two lines joined in one person, "
        "Frozen for my father's family and Flames for my "
        "mother's, with 'In' between them the way a coupling "
        "joins two cars of a train. My parents gave the name to "
        "their first child in Dallas in 2000 to declare what "
        "the marriage had made. In daily life I am called "
        "Frozen. I cook in my own household's kitchen and in "
        "the kitchen corner of my recording studio, and "
        "everything in this book is what those rooms, and the "
        "two kitchens behind them, taught me."
    ),
    "q004": (
        f"{MOTHER}. My mother is Ruby Flames, a piano teacher "
        "and church organist in Dallas, and her place in my "
        "cooking is first: she taught me that feeding people "
        "and teaching people are the same act done at different "
        "furniture. From her I have the fried chicken her table "
        "is known by, the lemon chess pie of the church "
        "socials, the rule that a child is taught by whoever "
        "is nearest and musical, and the habit -- hers from her "
        "grandmother -- of writing everything down. What of "
        "hers is still on my stove is the chicken, the pie, "
        "and the standard: everybody fed, and the books kept "
        "in the same hand."
    ),
    "q005": (
        f"{FATHER}. My father is Onyx Frozen, who runs the "
        "small Dallas repair shop his line's work became -- "
        "radios, televisions, guitars -- and his place in my "
        "cooking is the standard underneath it. He taught me "
        "the bench before any kitchen did: listen before you "
        "touch, understand the thing in front of you, enter "
        "the job in the book, charge honestly. What of his is "
        "still on my counter is the day book habit become a "
        "session log and a recipe record, the measuring "
        "instinct, and the rule that a repair -- of a radio, "
        "of a sauce -- is a promise."
    ),
    "q006": (
        f"{BIRTH_YEAR}. I was born in 2000, the first child of "
        "the joining, and the family's table that year was a "
        "young household's: my parents married the year "
        "before, the shop established, the front room full of "
        "other people's children, my grandfather Jasper at "
        "the head of one table and my grandfather Slate at "
        "the other, both grandmothers living and cooking. I "
        "was born into the doctrine's third Texas generation "
        "and fed from both lines' kitchens before I could "
        "stand at either stove."
    ),
    "q007": (
        f"{BIRTHPLACE}. I was born in Dallas, Texas, and "
        "Dallas is my first cuisine: brisket and beans, "
        "cornbread in iron, chess pie at church socials, the "
        "Gulf's food coming up the highways and Louisiana's "
        "coming across them, all of it cooked in a city built "
        "by people who arrived from somewhere else carrying a "
        "taste of home. The two lines' kitchens were "
        "themselves arrivals -- Mississippi fire and "
        "Pennsylvania iron, set down in Dallas two years "
        "apart -- and the city's table is where they learned "
        "to be one family's food."
    ),
    "q008": (
        "The first taste I remember whole is my grandmother "
        "Opal's peach cobbler, eaten warm in her front room "
        "while a pupil's lesson went on at the piano behind "
        "me -- I can still produce it entire: the peaches "
        "soft and amber, the batter crust crisped at the "
        "edges where it met the dish, the juice too hot and "
        "taken anyway. I must have been four. Every cobbler "
        "since, including the one in this book, is measured "
        "against that dish and that room, and the measuring "
        "is not nostalgia. It is calibration. A cook's first "
        "memory is his first standard."
    ),
    "q009": (
        f"The family's doctrine, at the table as at the "
        f"bench, is my grandfather Jasper Frozen's sentence: "
        f"{DOCTRINE} It came from the Frozen line, coined at "
        "a toolmaker's bench, and the Flames line's "
        "contribution to the joined family's law is not a "
        "sentence but a practice: write it down. Between the "
        "two of them -- keep it, and enter it -- this kitchen "
        "has its whole constitution. Coral Frozen's amendment, "
        "preserved by the telling, is that people are included "
        "in the inventory: a family keeps its people first, "
        "and its beans and briskets after."
    ),
    "q010": (
        "This cookbook exists because a family's knowledge "
        "dies the way its cooks do, one unwritten dish at a "
        "time, unless somebody enters it in the book. It is "
        "written for three readers: the young of my own "
        "family, in Dallas and Chicago and Fort Worth, who "
        "will one day stand where I stand; the musicians and "
        "engineers my studio feeds, who keep asking how the "
        "chili is made; and any cook who inherited two "
        "kitchens and has to make them one. At its end a "
        "reader should be able to cook the ten signature "
        "dishes whole, run a pantry on the accounts standard, "
        "keep food against a hard season, and feed a room of "
        "working people at midnight. That is the standard. "
        "The next ninety pages are held to it."
    ),
    # Chapter 2 -- The Flames Kitchen: Fire and Feeding
    "q011": (
        f"{FLAMES_MATRIARCH}, born Jet Callahan in 1923. She "
        "is the Flames family's matriarch by the line's own "
        "naming: the founder Garnet's wife, who came with him "
        "from Holly Springs in 1949, kept the household "
        "through the lean first Texas years, fed the "
        "neighbours' children who materialized at her table's "
        "edges, and began the family Bible whose flyleaf "
        "carries the line's births, marriages, and deaths in "
        "her hand for fifty-two years. Her kitchen was the "
        "line's first Texas institution: a stove, a table, "
        "and the standing rule that whoever was present was "
        "fed. She died in 2001."
    ),
    "q012": (
        f"{FLAMES_ORIGIN}, Mississippi. The Flames line came "
        "from Holly Springs, a hill-country town in the north "
        "of the state, and the cooking it carried to Texas "
        "was Mississippi's: cornbread in iron, greens cooked "
        "in their own liquor, peaches in season, pork in "
        "every form a poor county's ingenuity allows, and "
        "chess pie when there was little else to make a "
        "dessert from. The line's origin explains its "
        "kitchen the way Dallas explains its present: the "
        "place it came from is in every dish, adjusted, never "
        "erased."
    ),
    "q013": (
        "Garnet Flames kept furnaces and boilers for a "
        "living, and his household learned heat from a man "
        "whose trade was fire that must not go out and must "
        "not get loose. What that taught his kitchen was "
        "judgment without instruments: a fire is read by its "
        "color and its sound, a stove's temper is known by "
        "holding a hand where the cookbooks say to hold a "
        "thermometer, and patience with heat is a moral "
        "quality before it is a technical one. My own heat "
        "control, taught in this book's techniques chapter, "
        "is Garnet's trade at three generations' remove: "
        "listen first, then touch."
    ),
    "q014": (
        "Jet's table fed more than the family, and that was "
        "its design. A meal there was built the way she built "
        "everything: a pot large enough for the unexpected, "
        "bread always, one dish that stretched -- beans, "
        "greens, a stew -- and one dish that celebrated, and "
        "the children of the street materializing at the "
        "edges and being seated without ceremony or comment. "
        "Her standard for feeding people was the one my "
        "mother inherited entire: nobody at the table is a "
        "guest, because a guest is fed differently, and "
        "worse, than family. At Jet's table you were family "
        "by the act of sitting down."
    ),
    "q015": (
        "Jet left her recipes the way she left everything: "
        "entered, in a hand like copperplate, on cards kept "
        "with her papers and in the margins of the one "
        "cookbook she owned, which the family still has. Her "
        "way of writing a recipe teaches who she was: "
        "quantities exact where exactness matters, and where "
        "it does not, an instruction instead of a measure -- "
        "'buttermilk until it looks right', with a sentence "
        "saying what right looks like. The cards live now in "
        "my keeping, with the Bible. The cornbread in this "
        "book is hers, from her card, tested against my "
        "mother's memory of her mother's stove."
    ),
    "q016": (
        "The Flames kitchen's second generation ran on cold. "
        "Slate Flames, the founder's son, was a heating and "
        "refrigeration man, and his household was among the "
        "first on its street where cold storage was a "
        "profession rather than a purchase: the icebox "
        "understood, then the refrigerator kept at its exact "
        "temperature and entered in his notes like a plant "
        "he was responsible for. What refrigeration did to "
        "the family's cooking was time: milk that kept, meat "
        "that waited, leftovers that became a second day's "
        "dish instead of a first day's waste. The founder "
        "kept fire; his son kept cold; the joined family's "
        "kitchen runs on both inheritances at once."
    ),
    "q017": (
        "My grandmother Opal's front room was a feeding "
        "place disguised as a music studio. Children came "
        "for piano lessons and were taught, in her phrase, "
        "by whoever was nearest and musical -- and they were "
        "fed, because a hungry child cannot hear a scale. "
        "Payment arrived as cake, as eggs, as nothing, and "
        "the room's economy ran on the principle that "
        "teaching and feeding were one act: the lesson at "
        "the piano, the plate after it. Church people came "
        "through the same room on the same terms. My mother "
        "teaches in that room now, on that piano, and the "
        "plate after the lesson has survived three "
        "generations of pupils."
    ),
    "q018": (
        "Music ran the Flames kitchen's clock. Opal cooked "
        "to the piano the way other cooks cook to a timer: a "
        "dish that takes three songs is a dish whose time is "
        "known by ear, and a pupil's lesson in the front "
        "room was the length of a pot of greens coming right. "
        "What it did to the food was attention. A kitchen "
        "with music in it is a kitchen somebody is listening "
        "to, and a listened-to pot does not boil dry. My "
        "studio runs on the same discovery, made "
        "independently in both rooms: people who are playing "
        "music in the next room eat better, and cook better, "
        "than people who are waiting in silence."
    ),
    "q019": (
        "My mother's kitchen, as I received it, is a small "
        "Dallas room run at a professional standard by a "
        "woman whose other room is a teaching studio: the "
        "stove seasoned by decades of fried chicken, the "
        "piano audible through the wall, her rules written "
        "nowhere and known by everyone -- wash as you go, "
        "salt in layers, the good pan is not lent, everybody "
        "fed. What she kept of her line's kitchen is its "
        "whole constitution: Jet's table, Opal's front room, "
        "the writing down. What she changed is its precision: "
        "my mother measures what her grandmother judged, and "
        "writes the measure beside the judgment, so the "
        "cards in my keeping are in two hands, agreeing."
    ),
    "q020": (
        "The Flames kitchen's rule, if a stranger asked its "
        "cooks for one sentence, is this: feed whoever is at "
        "the table, and write down what you fed them. It sits "
        "beside the family's doctrine the way a hand sits "
        "beside its glove. The doctrine says what the family "
        "keeps; the Flames rule says the first thing kept is "
        "people, and the instrument of keeping is a meal "
        "followed by an entry in a book. Every recipe in the "
        "chapters ahead that descends from this line carries "
        "both marks: it feeds more than were expected, and "
        "it is written down."
    ),
    # Chapter 3 -- The Frozen Kitchen: Iron and Patience
    "q021": (
        f"{FROZEN_MATRIARCH}, born Pearl Kowalski in 1921. "
        "She is the Frozen family's matriarch: the founder "
        "Flint's wife, who kept the line's papers, its "
        "accounts, and its table through the founding "
        "decades, and who instituted the custom that no job "
        "and no debt goes unentered -- the day book was "
        "Flint's habit, but its completeness was Pearl's "
        "enforcement. Her kitchen ran on the same "
        "completeness: what the household ate, and what it "
        "cost, and what was left, entered in her hand. She "
        "died in 1999, a year before I was born, and I know "
        "her through her accounts, which are as exact as the "
        "Flames Bible and twice as argumentative in the "
        "margins."
    ),
    "q022": (
        f"{FROZEN_ORIGIN}, Pennsylvania. The Frozen line "
        "came from Pittsburgh: steel country, river country, "
        "and the cooking it carried to Texas was a mill "
        "town's -- potatoes in every form, cabbage, beans, "
        "soups built to wait for a shift's end, bread baked "
        "to keep. The line's origin explains its kitchen "
        "the way Holly Springs explains the Flameses': "
        "where the Flames line learned fire, the Frozen "
        "line learned patience -- weight, tolerance, and the "
        "long cold arithmetic of food that cannot be "
        "hurried and must not be wasted."
    ),
    "q023": (
        "Flint Frozen cooked the way he machined: plainly, "
        "exactly, and with contempt for waste disguised as "
        "generosity. A millwright's food in Pittsburgh and "
        "in the first Dallas years was food that kept and "
        "traveled: beans, salt pork, potatoes, coffee strong "
        "enough to stand a shift on. What a machinist's "
        "habits did to his kitchen was measurement -- he is "
        "the only founder in this book who weighed his "
        "coffee -- and a fitted place for every tool, the "
        "toolbox principle applied to a stove. His toolbox "
        "is in my keeping. His skillet's fate is not "
        "recorded, which the family counts as the record's "
        "one kitchen failure."
    ),
    "q024": (
        "Pearl's food accounts are a cooking instrument "
        "disguised as bookkeeping. She entered what the "
        "household ate, what it cost, and what remained, "
        "week by week, in the same ledgers' spirit as the "
        "day books; and her standard against waste was not "
        "stinginess but information: a household that knows "
        "what it eats can feed itself on less, and feed "
        "others on the difference. That standard runs my "
        "kitchen still. My pantry chapter is Pearl's method "
        "with a studio attached: the inventory first, the "
        "shopping from the inventory, the meal from the "
        "shopping, and the entry afterward, in a hand the "
        "next keeper can read."
    ),
    "q025": (
        "Jasper Frozen at a stove was his doctrine with an "
        "apron on. The toolmaker's standing dishes were the "
        "patient ones: beans that took the afternoon, a "
        "potato soup of four ingredients made exactly, "
        "stocks that ran overnight because a thing "
        "understood slowly is understood whole. His method "
        "was the bench's: nothing discarded that could be "
        "understood, and a pot of beans could be understood "
        "-- the soak, the simmer, the salt at the end, each "
        "step entered in his mind the way he entered a job. "
        "When the family quotes his sentence about keeping "
        "and fixing, I hear it in his kitchen voice: it was "
        "always partly about dinner."
    ),
    "q026": (
        "Coral Boudreaux came into the Frozen kitchen from "
        "Louisiana people, and she changed what it ate. "
        "Hers is the gumbo in this book: the dark roux, the "
        "trinity, the patience of a different river. Her "
        "amendment to the doctrine -- that people are "
        "included in the inventory -- was, at her table, a "
        "practice before it was a sentence: the pot was "
        "sized for whoever might come, and her count of the "
        "family always ran one or two souls higher than the "
        "census. The Frozen kitchen ate differently because "
        "of her in the plainest sense: it ate Louisiana's "
        "food, cooked by a woman who regarded a too-small "
        "pot as a failure of imagination."
    ),
    "q027": (
        "My father's cooking is a repairman's: competent, "
        "unshowy, and exact about the things that matter. "
        "At the shop there is a hot plate and a kettle, and "
        "his lunches are the bench's -- soup from a jar my "
        "mother sends, sandwiches built like assemblies, "
        "everything in its order. At home he cooks the "
        "Frozen line's plain dishes to the standard he "
        "repairs by: a meal, like a radio, is first "
        "understood, then fixed, then returned to service "
        "better documented than it arrived. He has never "
        "once served a dish he had not first tasted and "
        "adjusted, and he has never thrown away a machine "
        "or a meal he had not understood."
    ),
    "q028": (
        "The Frozen kitchen keeps its tools the way the "
        "line keeps everything: fitted, entered, and in "
        "reach. The knives are carbon steel, sharpened on "
        "the same stone discipline as the bench's edges; "
        "the iron is seasoned and never soaked; the measures "
        "are metal and old. A toolmaker's line believes a "
        "kitchen's equipment is a moral document: a dull "
        "knife is a lie told to the hand, a warped pan a "
        "broken promise to the food. My own tool chapter, "
        "ahead, is this belief written as a shopping list "
        "with standards attached."
    ),
    "q029": (
        "My aunt Jade keeps the Frozen line's other present "
        "kitchen, in Fort Worth: a nurse's household, where "
        "cooking bends around shifts the way my studio's "
        "bends around sessions. What survives of the line's "
        "kitchen in hers is the accounts discipline -- her "
        "freezer is labelled like a ward's stores, dated and "
        "rotated -- and the patient dishes, made on days "
        "off and portioned against the working week. What "
        "changed is the hour: the Frozen line's table used "
        "to gather at a benchman's supper time; Jade's "
        "gathers when the hospital allows, and the food "
        "waits, which is what the line's food was always "
        "built to do."
    ),
    "q030": (
        "Set side by side, the two kitchens disagree about "
        "nearly everything except the thing that matters. "
        "The Flames kitchen believes food is for people: "
        "abundance, the unexpected seated, the dish that "
        "celebrates. The Frozen kitchen believes food is "
        "for keeping: the account, the inventory, the dish "
        "that waits. They agree, without either line quite "
        "knowing it, that a meal is a record -- of who was "
        "there, what the family had, what it did with what "
        "it had. They will argue until the end of the "
        "family about sugar in cornbread, about salt's "
        "timing in beans, about whether a recipe is a law "
        "or a letter from the dead. This book is written "
        "from inside that argument. It is the sound my "
        "whole cooking makes."
    ),
}

ANSWERS.update({
    # Chapter 4 -- The Pantry
    "q031": (
        "My staples shelf holds the foundation in Pearl's "
        "order: stone-ground yellow cornmeal, five pounds, "
        "for the cornbread; all-purpose flour, ten pounds, "
        "for biscuits, pie crusts, and the gumbo's roux; "
        "long-grain rice, ten pounds; dried pinto beans, "
        "five pounds, and black-eyed peas, two; grits, two "
        "pounds, for the mornings after sessions; sugar, "
        "brown and white; baking powder, soda, and salt in "
        "duplicate, because running out of a leavening "
        "mid-recipe is a failure of the accounts, not of "
        "the shopping. Each staple is there because a dish "
        "in this book cannot be made without it, and "
        "nothing is there that no dish uses."
    ),
    "q032": (
        "My heat is kept in three forms: dried chiles -- "
        "ancho for depth, chipotle for smoke, arbol for "
        "plain fire -- black pepper in two grinds, cayenne, "
        "paprika sweet and smoked, and two hot sauces, one "
        "Louisiana and one my sister's choosing. The level "
        "was set by two palates in negotiation: Coral's "
        "Louisiana standard, which holds that heat is a "
        "flavor and not a punishment, and my mother's, "
        "which holds that a dish's heat is decided by who "
        "is eating, and the cook who cannot make the same "
        "dish mild and fierce has only made it once. A "
        "dish's heat in my kitchen is therefore a decision, "
        "entered like any other: for the table that night, "
        "not for the cook's vanity."
    ),
    "q033": (
        "My fats are kept the old way and the new together: "
        "a grease can on the stove's back, bacon drippings "
        "strained through cloth, which Jet would recognize "
        "and approve; butter, salted, in quantity, for the "
        "baking and the finishing; lard rendered for the "
        "pie crusts and the fried chicken's best days; and "
        "peanut oil for the deep frying, because it takes "
        "the heat without arguing. My grandmothers' verdict "
        "on the arrangement is preserved by the telling: "
        "Opal would ask why a kitchen needs four fats, and "
        "Pearl's accounts would answer her, in the margins, "
        "with the cost per dish of each."
    ),
    "q034": (
        "The cold side runs on Pearl's discipline in Slate's "
        "profession. The refrigerator holds the week's plan "
        "in order: milk, eggs, butter, the greens washed "
        "and wrapped, the meats dated in my hand on tape. "
        "The freezer is an archive with an index: stocks in "
        "flat bags, beans portioned, the brisket's remainder "
        "sliced and laid out like files. Nothing enters "
        "either box unlabelled, because an unlabelled "
        "package is a debt the kitchen owes its future self, "
        "and this family's whole religion is that debts of "
        "that kind get entered the day they are incurred."
    ),
    "q035": (
        "My tools are few and kept: a ten-inch chef's knife "
        "and a paring knife, carbon steel, from my father's "
        "bench discipline; two iron skillets, one of them "
        "Jet's by descent through my mother; a Dutch oven "
        "heavy enough to be Flint's kind of object; a "
        "stockpot; wooden spoons worn to their tasks; and "
        "the one utensil I would save from a fire, my "
        "grandmother Opal's slotted spoon, which has lifted "
        "fifty years of other people's dinners. The standard "
        "by which a tool earns its place is my father's: it "
        "must be understood, maintainable, and entered in "
        "the keeper's mind like a job -- a tool I cannot "
        "sharpen, season, or repair does not stay."
    ),
    "q036": (
        "I shop the way Pearl accounted: from the "
        "inventory, never from appetite. The list is made "
        "at the counter from the shelves' actual state, in "
        "the order the market lays its goods out, staples "
        "first and celebration last. I never buy a spice I "
        "cannot name a dish for, and I never run out of "
        "coffee, cornmeal, beans, or eggs -- the four whose "
        "absence closes the kitchen. Fresh things come "
        "from the market twice a week; the rest is the "
        "pantry's business. My father's discipline rides on "
        "the whole method: understand the thing in front of "
        "you -- in this case the shelf -- before you spend "
        "anything on it."
    ),
    "q037": (
        "Dallas seasons are two long arguments -- heat and "
        "the brief cool -- and the cooking follows them. "
        "Summer is peaches, tomatoes that taste of "
        "something, okra, black-eyed peas fresh, and the "
        "kitchen's cold dishes; the brisket moves outside "
        "and the stove rests at noon. The cool months are "
        "the pot's: beans, stocks, gumbo, the long simmers "
        "that warm a house while they feed it. Two dishes "
        "belong to one season only and are not made out of "
        "it, on Jet's rule that a dish out of season is a "
        "letter read aloud in the wrong room: the peach "
        "cobbler, summer's; and the Christmas table's "
        "standing rib of beef, winter's."
    ),
    "q038": (
        "The kitchen's drinks are coffee first, and the "
        "rest in its service. Coffee is kept in quantity "
        "and made strong, in a pot that serves the house "
        "and a second that serves the studio; tea is iced, "
        "sweetened at my mother's measure, for the table; "
        "and there is always water cold and something "
        "lemonade-like in summer for whoever is working. A "
        "pot of coffee in a house that runs a studio is not "
        "a beverage but a signal and a tool: fresh coffee "
        "means the night is still young and the room is "
        "still working, and the last pot of the night is a "
        "decision everybody in the building understands "
        "without a word being said."
    ),
    "q039": (
        "The empty-shelf meal, in my kitchen, is migas "
        "built on Pearl's scraps discipline: the last eggs, "
        "the stale tortillas cut and crisped in the grease "
        "can's leavings, an onion, a tomato going soft, "
        "whatever cheese remains, hot sauce at the table. "
        "The method of making do is the pantry's reasoning "
        "in reverse: start from what must be used, not from "
        "what the dish wants; cook the perishable first; "
        "let eggs, the great forgivers, bind the result; "
        "and serve it as a decision, not an apology. I have "
        "fed a full session on that meal more than once, "
        "and the room has asked for it since by name, which "
        "is how a substitute becomes a signature."
    ),
    "q040": (
        "The pantry's rule is one sentence, and it is "
        "Pearl's accounts crossed with Coral's amendment: "
        "stock for the people you might have to feed, and "
        "know what you have. How much is decided by the "
        "household's real arithmetic -- the family, the "
        "studio's nights, the stranger the doctrine "
        "includes in the inventory -- and of what, by the "
        "dishes this book contains. Against what day is the "
        "whole shelf the answer: against the thin season, "
        "the burned studio, the week the work stops. A "
        "pantry stocked on that rule is not hoarding. It is "
        "the doctrine, shelved."
    ),
    # Chapter 5 -- Techniques
    "q041": (
        "My knife work was taught at a bench before it was "
        "taught at a counter, and it keeps the bench's "
        "order: the grip firm and forward, the guiding hand "
        "curled like a claw, the cut made by the blade's "
        "length and not the arm's force. Sharpening is a "
        "ritual with a standard -- the stone wetted, the "
        "angle held at a machinist's consistency, the edge "
        "tested on paper and then on a tomato's skin, which "
        "lies to no one. A toolmaker's grandson believes a "
        "knife is not a utensil but an instrument, and an "
        "instrument is either in calibration or it is "
        "furniture. The test that the work was done right "
        "is the board's: even pieces, no juice lost to "
        "crushing, and a hand that is not tired at the end."
    ),
    "q042": (
        "Heat control, in the Flames inheritance, is read "
        "and not dialed. A pan is judged by the shimmer of "
        "its oil and the sound a drop of water makes in it; "
        "a fire by its color and its voice; a stove's temper "
        "by holding the hand at the height the old cooks "
        "specified, counting to the number the dish "
        "requires. What a furnace man's line knows about "
        "heat that a dial cannot say is that heat is a "
        "relationship, not a setting: the same burner is "
        "three temperatures across an hour, and the cook's "
        "job is attendance, the way Garnet attended a "
        "boiler -- present, listening, adjusting before the "
        "instrument would have told him to."
    ),
    "q043": (
        "Seasoning is done in layers, and tasted at every "
        "layer: salt the onions as they sweat, the meat "
        "before it meets the pan, the pot at its beginning "
        "and again -- lightly, always lightly -- before it "
        "is served. Acid comes late, heat is decided by the "
        "table, fat is the finish that carries the rest to "
        "the tongue. The hard case is the dish you cannot "
        "taste one more time -- the palate tired, the "
        "fourth hour of a session -- and the method for it "
        "is the record's: season by the measures the cards "
        "give, which were written by palates that were "
        "fresh, and trust the book the way a pilot trusts "
        "instruments in cloud. Jet's margins are my "
        "instrument panel."
    ),
    "q044": (
        "My stocks begin with what the scrap discipline "
        "saved: bones from the week's meats, the ends of "
        "onions, celery gone honest, carrot tops, herb "
        "stems -- never the bitter, never the spoiled, "
        "never anything I would be ashamed to name. The pot "
        "is brought up slowly, skimmed without apology, and "
        "left at the barest simmer for the hours the Frozen "
        "line considers a minimum; a boiled stock is a "
        "cloudy conscience. Gravies are the stock's "
        "children: drippings, flour cooked in them to the "
        "color the dish wants, stock added in patience. A "
        "stock is kept for three uses -- soup, sauce, and "
        "the rice and beans that cook in it and are "
        "transformed -- and a freezer without stock in it "
        "is, in this family's judgment, a house without a "
        "day book."
    ),
    "q045": (
        "Frying is the book's most dangerous technique and "
        "I teach it the way my mother taught me: with "
        "respect stated first. The oil's temperature is "
        "known by the flour's behavior -- a pinch dances "
        "and browns in the count of five -- or by the "
        "thermometer my father's line insists on, the one "
        "modern instrument this kitchen admits without "
        "argument. The coating is seasoned flour, twice "
        "dredged for chicken; the pieces go in away from "
        "the body, in an order, never crowded, because a "
        "crowded pan steams and a steamed crust is a "
        "promise broken. The iron pan's part is its memory: "
        "cast iron holds the heat the food tries to steal, "
        "and returns it, which is the whole doctrine in a "
        "utensil."
    ),
    "q046": (
        "Beans and grains are the slow techniques the two "
        "lines agree on, and their agreement is the "
        "method's proof. The soak is overnight, in cold "
        "water, without apology to the quick-soak heresies; "
        "the simmer is bare, the pot's lid ajar, the salt "
        "at the end -- on which the lines also agree, "
        "whatever else they dispute. Rice is rinsed, "
        "measured by the knuckle as Opal taught, and rested "
        "off the heat a full ten minutes, because rice "
        "finishes in its own steam and a cook who lifts the "
        "lid early is stealing from his own dish. What "
        "patience does that hurry cannot is texture with "
        "integrity: a bean whole and creamy, a grain "
        "distinct and tender. Hurry makes porridge of both, "
        "and calls it dinner."
    ),
    "q047": (
        "Eggs are my examination dish, as they were every "
        "cook's in this book's lineage. The scramble is low "
        "and slow, butter first, the eggs moved with a "
        "spatula in folds and taken off while they still "
        "shine, because they finish on the plate. The fry "
        "is in bacon grease, the white set and laced at the "
        "edges, the yolk warm and running. The boil is "
        "timed from the water's return, seven minutes for "
        "the jammy center the studio asks for. What each "
        "proves about the hand that made it is the whole "
        "craft in miniature: heat judged, timing kept, "
        "seasoning decided, and the humility to serve a "
        "two-ingredient dish exactly right or not at all."
    ),
    "q048": (
        "Baking measures begin with the fat's cut: cold "
        "butter or lard worked into flour with fingertips "
        "or a cutter until the pieces are pea-sized and "
        "uneven, because an even cut makes an even, "
        "forgetable crumb. The liquid -- buttermilk, always "
        "-- is cold and added once, stirred to just "
        "combined; a biscuit dough kneaded is a biscuit "
        "ruined in advance. The oven's readiness is the "
        "hand test at the door and the iron's preheat for "
        "cornbread, which must meet the batter already "
        "smoking faintly with grease. These are techniques "
        "before they are recipes: the next chapter renders "
        "two of them whole, and a reader who has this page "
        "will know why the recipes order what they order."
    ),
    "q049": (
        "The pan sauce is the two-minute technique the "
        "studio nights run on. The meat comes out; the "
        "drippings stay; a shallot or onion goes in for the "
        "minute the pan is hottest; then the deglaze -- "
        "stock, coffee on the nights the pot is what there "
        "is, wine when the session has earned it -- scraped "
        "with the wooden spoon until the pan's whole "
        "history lifts into the liquid. Butter off the "
        "heat, a squeeze of lemon, salt decided last. It "
        "decides whether plain meat becomes a dish because "
        "it is the cook's signature written in the pan's own "
        "ink: everything the meat knew, returned to it as "
        "sauce."
    ),
    "q050": (
        "Repairs, in order. Too salt: dilution is honest -- "
        "more of the dish's body, a potato in a soup to be "
        "lifted out, acid and fat to rebalance what cannot "
        "be removed. Too thin: reduction, patience, or a "
        "roux made separately and married in. Broken -- a "
        "sauce split, a gravy lumped: the blender or the "
        "sieve, and the lesson entered. Scorched at the "
        "edge: decant at once to a clean pot, take only "
        "what never touched the burn, and season up to meet "
        "what was lost. The one failure I do not save is "
        "the dish whose keeping was neglected -- the stock "
        "left warm overnight, the jar whose seal failed. "
        "The doctrine fixes what it can; it does not gamble "
        "with what it cannot understand, and a doubtful "
        "dish is not understood. That one goes out, and the "
        "loss is entered in the book beside the rule that "
        "prevents it."
    ),
    # Chapter 6 -- Signature Dishes
    "q051": (
        "Jet's skillet cornbread. Two cups stone-ground "
        "yellow cornmeal; one teaspoon salt; one teaspoon "
        "baking soda; two eggs; two cups buttermilk; a "
        "quarter cup of bacon drippings, half in the batter "
        "and half in the iron. The skillet goes into a "
        "425-degree oven with its grease until it smokes "
        "faintly; the batter -- mixed once, never beaten -- "
        "goes in with a hiss, and bakes twenty-five minutes "
        "to a crust the color of a good roof. Serve it from "
        "the pan, in wedges, hot. The family's unsettled "
        "argument is sugar: the Flames line says never, that "
        "sugar makes it cake and cake is a different "
        "sacrament; Coral's people allow a spoonful; the "
        "Chicago branch, at six hundred miles, has gone its "
        "own way and is not discussed. My verdict, as the "
        "cook who must serve both lines at one table, is "
        "Jet's: none in the bread. The sweetening is the "
        "eater's business, at the table, with sorghum."
    ),
    "q052": (
        "Pearl's pot beans. One pound of pinto beans, "
        "picked over and soaked overnight in cold water; a "
        "smoked ham hock; one onion, quartered; water to "
        "cover by two inches. The soak water is kept -- "
        "Pearl's accounts counted its flavor as an asset -- "
        "and the pot goes on at a bare simmer for three "
        "hours, the lid ajar, nothing stirred that does not "
        "need it. Salt comes in the last half hour, a "
        "tablespoon of bacon grease at the end, and the "
        "beans are done when five blown on in a spoon are "
        "tender all through and the liquor coats the spoon "
        "like a thin gravy. They are served with the "
        "cornbread of the page before, raw onion, and hot "
        "sauce at the table. Yield: eight bowls, and the "
        "second day's are better, which Pearl entered in "
        "her accounts as a fact of economics."
    ),
    "q053": (
        "Slate's brisket. A whole packer brisket, twelve "
        "pounds; coarse salt and coarse black pepper, "
        "equal by weight, and nothing else -- the "
        "refrigeration man's rub is an argument that the "
        "meat and the fire are the recipe. The fire is oak, "
        "the pit at 250 degrees, the brisket fat-side up, "
        "and the time is twelve hours and the cook's whole "
        "attention: Slate tended a pit the way he tended a "
        "plant, in rounds, with notes. Doneness is known "
        "without a thermometer of the modern kind by the "
        "probe's slide, the bark's set, and the bend of a "
        "slice over the knife -- it should fold, not break. "
        "Rest it an hour, wrapped, in the cooler his trade "
        "kept at temperature. Slice against the grain, "
        "pencil-thick at the flat. Yield: a family, a "
        "session, and a freezer's worth of second days."
    ),
    "q054": (
        "My mother's fried chicken. One chicken, cut in "
        "eight pieces, soaked overnight in buttermilk with "
        "a tablespoon of salt and a teaspoon of cayenne. "
        "The coating is two cups of flour, a tablespoon of "
        "paprika, a teaspoon each of garlic powder and black "
        "pepper, salt to the line's measure; the pieces are "
        "dredged, rested ten minutes so the crust sets its "
        "grip, and dredged again. The fat is lard or peanut "
        "oil, an inch deep in the iron skillet, at 350 "
        "degrees by the thermometer the Frozen line insists "
        "on and her own hand confirms by the flour test. "
        "Dark meat first, then light, never crowded, "
        "twelve to fifteen minutes, turned once. The test "
        "for done is the juice clear and the crust the color "
        "of her front room's piano wood. Drain on a rack, "
        "never paper. Yield: Sunday, and the cold pieces "
        "Monday that the family argues are the true dish."
    ),
    "q055": (
        "Coral's gumbo, as the Frozen kitchen makes it. One "
        "cup of flour and one cup of oil, cooked in the "
        "Dutch oven at a steady stir for forty-five minutes "
        "to the color of an old penny -- the roux is the "
        "recipe, and it cannot be hurried, telephoned "
        "through, or left. Then the trinity: two onions, a "
        "bell pepper, three stalks of celery, diced, into "
        "the roux until soft; garlic; two quarts of stock; "
        "a chicken, cut up and browned; a pound of "
        "andouille; two cups of okra; bay, thyme, cayenne "
        "to Coral's standard. Two hours at the simmer. It "
        "is served over rice, file at the table, never in "
        "the pot. What her people would say about this "
        "Texas version is preserved by the telling: that it "
        "is a good gumbo that has learned brisket smoke the "
        "way a person learns a second language -- fluently, "
        "with an accent, and proud of both."
    ),
    "q056": (
        "My session chili. Three pounds of beef chuck, "
        "ground coarse or cut small; no beans in the pot -- "
        "the beans of page fifty-two are served beside it, "
        "and the argument between the pots is older than "
        "the studio. The chiles are four anchos and two "
        "chipotles, toasted and soaked and ground with "
        "their liquor; an onion; garlic; cumin; a cup of "
        "the studio's coffee, which is the recipe's "
        "signature and its joke -- the pot drinks what the "
        "room drinks. It simmers four hours, built in the "
        "afternoon for a midnight eating, because chili "
        "made for working people must be a dish that waits "
        "without deteriorating and improves by being "
        "reheated at the hour of the break. Salt at the "
        "end, lime and raw onion at the table. Yield: a "
        "session, twice."
    ),
    "q057": (
        "My midnight migas. Six eggs; four stale corn "
        "tortillas, cut in strips and crisped in a "
        "tablespoon of bacon grease; half an onion, diced; "
        "a tomato, or a spoon of salsa when the tomato is "
        "gone; a handful of grated cheese; hot sauce at the "
        "table. The method is five minutes and one pan: "
        "crisp the tortillas, soften the onion among them, "
        "pour in the beaten eggs, fold twice, off the heat "
        "while they shine, cheese over, serve in the pan. "
        "It was invented in 2019, in my unpaid-assistant "
        "months, in another man's studio kitchen at an hour "
        "when the cupboard held exactly its ingredients; it "
        "is the empty-shelf meal of this book's pantry "
        "chapter become a standing dish, and musicians "
        "have asked for it by name on three continents of "
        "telephone calls since."
    ),
    "q058": (
        "Jasper's potato soup. Two pounds of potatoes, "
        "peeled and cut in honest pieces; one onion; water "
        "to cover; a knob of butter; a cup of milk; salt "
        "and black pepper. That is the whole of it, and its "
        "plainness is the declaration: the potatoes simmer "
        "until they slump, half are crushed in the pot "
        "against its side with the spoon's back, the milk "
        "goes in off the boil, and the soup is served in "
        "heavy bowls with nothing on top but pepper. The "
        "toolmaker made it on the nights a job had gone "
        "wrong, as a standard of sufficiency -- a dish that "
        "asks almost nothing and gives back warmth, "
        "substance, and the reminder that a family is not "
        "fed by variety. It is fed by somebody cooking. "
        "Yield: four bowls, and the doctrine's whole first "
        "verse."
    ),
    "q059": (
        "Opal's peach cobbler. Six ripe peaches, sliced, "
        "with three-quarters of a cup of sugar and a "
        "squeeze of lemon, left to make their juice. The "
        "batter is the front room's formula: a cup of "
        "flour, a cup of sugar, a cup of milk, a teaspoon "
        "of baking powder, a pinch of salt, poured over "
        "half a stick of butter melted in the baking dish "
        "-- never stirred -- and the peaches and all their "
        "juice laid over it. It bakes at 350 degrees for "
        "forty-five minutes, the batter rising through the "
        "fruit in the way that still seems like a card "
        "trick. My grandmother Opal made it through fifty "
        "summers of lessons; her namesake, my sister Opal, "
        "carries the recipe now and makes it on the same "
        "piano-side afternoons, which is how this family "
        "files its affections: in dishes, addressed."
    ),
    "q060": (
        "My mother's lemon chess pie. A crust of the "
        "baking chapter's measure, in the pie plate, cold. "
        "The filling: a cup and a half of sugar, a "
        "tablespoon of cornmeal -- the chess pie's "
        "signature pinch -- a tablespoon of flour, the "
        "zest and juice of two lemons, a quarter cup of "
        "milk, four eggs, half a stick of butter melted. "
        "Whisked in that order, poured into the shell, "
        "baked at 350 degrees for forty minutes until the "
        "top is set and freckled gold. It is the "
        "church-social dish of the Flames line, the pie of "
        "the poor pantry that tastes like a rich one, and "
        "it stood on the table at the social in 1998 where "
        "a piano pedal broke and a repairman was called -- "
        "the pie, the family says, witnessed the joining "
        "before the families did, and it has been served at "
        "every joining occasion since, including my own "
        "wedding."
    ),
    # Chapter 7 -- Feeding the Studio
    "q061": (
        f"{STUDIO_YEAR}. I founded the Cold Room in 2022, "
        "in a converted Dallas icehouse, and its first "
        "kitchen corner consisted of the following, entered "
        "like a job: a hot plate, a kettle, an electric "
        "skillet that had been my aunt Jade's, four mugs, "
        "and the studio coffee pot, which was bought before "
        "the second microphone. The icehouse walls that "
        "made the room's sound -- thick, cold-keeping, "
        "built for ice -- made its kitchen too: a room "
        "designed to hold temperature holds a meal's heat "
        "and a cook's temper equally. Everything since -- "
        "the table, the shelf, the second burner -- is an "
        "addition to that first inventory, and the "
        "inventory is kept."
    ),
    "q062": (
        "Feeding a session is a practiced form. The meal "
        "falls at the break the work itself declares -- "
        "when the take is got or the ears are tired, "
        "usually past midnight -- and it must be food that "
        "waits without deteriorating, eats with one hand "
        "and no ceremony, and returns people to work "
        "warmer than it found them. A working musician at "
        "that hour needs substance, salt, and the feeling "
        "of having been considered. What I have learned "
        "never to serve is anything that requires the "
        "room's attention to survive: no dish that must be "
        "eaten in its first five minutes, nothing fried to "
        "order, nothing whose failure would be the night's "
        "story. The chili waits. The migas take five "
        "minutes. The beans were made for exactly this."
    ),
    "q063": (
        "The studio's coffee is a clock the room reads "
        "without looking at one. The pot is a twelve-cup "
        "drip machine of no distinction, the coffee strong "
        "-- a heaped measure per cup of water, Flint's "
        "weighing instinct surviving as a scoop -- and it "
        "is made fresh at the session's start, at the "
        "meal, and once more at the hour the night decides "
        "what it is. A fresh pot signals that the work is "
        "still young; a pot left to cook down signals the "
        "opposite, and engineers begin, unconsciously, to "
        "pack. My wife photographs the room, and her prints "
        "show the pot in the background of a decade's "
        "sessions like a moon in every photograph of a "
        "landscape."
    ),
    "q064": (
        "The studio's table is a door laid across two "
        "filing cabinets, which the room chose in its first "
        "year and has refused to upgrade, on the doctrine's "
        "reasoning: it is understood, it is kept, it works. "
        "People eat in the icehouse's thick-walled cool, "
        "the meal steaming in air that never quite warms, "
        "and the arrangement between kitchen corner and "
        "work is the arrangement of my whole life -- the "
        "food within earshot of the music, the music within "
        "smell of the food. Amber's prints of the room show "
        "the table set with session food and session paper "
        "in about equal measure, which is the truest "
        "portrait of the Cold Room that exists."
    ),
    "q065": (
        "The thin year's cooking was 2020's: the sessions "
        "stopped all at once, and I repaired -- radios, "
        "guitars, a church organ's blower -- out of my "
        "father's shop, and cooked like a man whose pantry "
        "was his bank. What that year's kitchen ran on was "
        "the keeping: beans in rotation, rice, eggs, the "
        "freezer's index worked like a ledger, every scrap "
        "into stock. The cost was entered and the lesson "
        "kept: a cook who can feed people well on almost "
        "nothing owns a skill no season can take, and the "
        "repair money of that year -- saved by a kitchen "
        "that spent almost nothing badly -- is, in the "
        "end, what capitalized the Cold Room two years "
        "later."
    ),
    "q066": (
        "Feeding a room of musicians on a session budget "
        "is Pearl's arithmetic with guitars. The meal for "
        "six is costed before it is cooked: the money goes "
        "first to the protein that waits well -- the chili "
        "meat, the beans' hock -- then to the bread, then "
        "to coffee, which is never economized on, because "
        "coffee is the session's fuel and a cheap pot is a "
        "false economy measured in takes. What I refuse to "
        "economize on is salt, fat, and the cook's "
        "attention, the three that cost least and decide "
        "most. The budget's rule is my grandmother's: a "
        "household that knows what it eats can feed others "
        "on the difference."
    ),
    "q067": (
        "The fire year was 2024: a fire in the building "
        "next to the Cold Room, and then in mine, took the "
        "studio as first built. The log books were at the "
        "house; the kitchen corner was not saved, except "
        "its inventory, which was in the log. I cooked that "
        "year from my own household's kitchen and my "
        "mother's, and the family fed the rebuilding the "
        "way it answers everything: my sister did the "
        "arithmetic, Amber photographed the ruin before "
        "anyone could sentimentalize it, the Chicago line "
        "sent money with a note that said only 'for the "
        "keeping'. The first meal in the rebuilt room was "
        "the session chili, made on a new hot plate in a "
        "room still smelling of its own rebuilding, and it "
        "is entered in the log as the studio's second "
        "founding."
    ),
    "q068": (
        "My sister Opal's part in the studio's feeding "
        "began with its books, which she kept as a teenager "
        "in a hand as exact as our mother's, and grew into "
        "its table. She brings the front room with her: a "
        "session she feeds is a session that eats at a set "
        "hour, together, with the work put down -- her "
        "grandmother's rule that feeding and teaching are "
        "one act, applied to engineers. Her cobbler has "
        "closed more sessions than any dish of mine. What "
        "shows of the front room in how she feeds people is "
        "the assumption underneath it: that the people at "
        "the table are hers to take care of, by the act of "
        "sitting down."
    ),
    "q069": (
        "The studio's standing meal is the session chili, "
        "and its arrival is a certification. It is asked "
        "for, never scheduled; the room asks when the work "
        "has gone well enough that the night deserves "
        "marking, and I have learned to read a session's "
        "health in the hour of the asking -- early is "
        "despair, never is a death, and the right hour, "
        "somewhere past the best take, is the sound of a "
        "room that knows it has done something. It is "
        "served in the studio's mugs, because the bowls "
        "were never replaced after the fire in matched "
        "numbers, and the mugs have become the dish's "
        "proper vessels by the family's oldest mechanism: "
        "use, entered and kept."
    ),
    "q070": (
        "The studio taught my kitchen patience with an "
        "audience: a session is a meal in reverse, people "
        "sustained through a long act of attention toward "
        "a moment that cannot be hurried, and a pot teaches "
        "the same lesson to a cook who will listen. My "
        "kitchen taught the studio the log: every session "
        "entered to the minute, who played, what broke, "
        "what worked -- a day book, learned at my father's "
        "bench and my great-grandmother's flyleaf. The two "
        "rooms are one practice in two materials: keep the "
        "thing, enter the thing, feed the people doing it. "
        "The next chapter takes the practice out of the "
        "studio and sets it at the family's full table."
    ),
})

ANSWERS.update({
    # Chapter 8 -- Occasions
    "q071": (
        f"{PARTNER}, born Amber Verano, a photographer. My "
        "wife came into this family in 2022, hired to "
        "photograph a session at the Cold Room, and married "
        "me in 2023, and what she brought to my table was a "
        "third family's whole inheritance: the Veranos are "
        "people of images and letters, and her cooking "
        "carries her mother's schoolteacher precision and "
        "her father's sign painter's eye -- her plates are "
        "composed the way her prints are, and a table she "
        "has set is recognizable across a room. Her "
        "standards joined the household's without a "
        "contest: she is the reason the studio's meals are "
        "photographed before they are eaten, and the "
        "archive now has a visual index of everything this "
        "book describes."
    ),
    "q072": (
        "Our wedding feast was in 2023, in the church hall "
        "where my parents' joining began, and the cooking "
        "was the families' own: no caterer was considered, "
        "which both lines regarded as a point of doctrine. "
        "My mother made the fried chicken and the lemon "
        "chess pie; the brisket was Slate's recipe in my "
        "father's hands; Amber's mother Beryl made the "
        "rolls she is known by; and the gumbo stood at the "
        "end of the table as the Frozen line's tribute to "
        "its own incoming bride, one generation honoring "
        "the next. What the two -- by then three -- "
        "families made of eating together as one family "
        "was entered in the Bible in my mother's hand, "
        "under the marriage, in one line: fed everybody."
    ),
    "q073": (
        "Christmas at the joined table happens in my "
        "parents' house or mine, the table extended with "
        "the board my father made for exactly this purpose, "
        "the Chicago line down by train when it can be "
        "managed, and the whole living family counted by "
        "eye at least once a year. The dishes without "
        "which it is not Christmas are fixed by a "
        "constitution nobody wrote: the standing rib of "
        "beef that is winter's only dish; my mother's "
        "chicken for the ones who do not eat beef; Pearl's "
        "beans, because they are always made; greens; the "
        "cornbread; and two pies, because one pie at "
        "Christmas is a family that has stopped expecting "
        "anyone. The young are fed first, the old are "
        "consulted, and the piano gets played whether "
        "anyone schedules it or not."
    ),
    "q074": (
        "The church socials belong to the church where my "
        "mother plays the organ and my parents met over "
        "its broken pedal. A congregation's table asks of "
        "its cooks what a family's does not: quantity "
        "without warning, dishes that travel and wait, and "
        "food for people whose troubles you may not know "
        "and must not ask about at the serving table. My "
        "mother's place there is double -- the organ and "
        "the kitchen, the music and the feeding, one "
        "ministry in her accounting -- and the chess pie "
        "of this book is that table's dish. I learned at "
        "those socials the lesson my studio runs on: a "
        "room of people working at something together eats "
        "like a family if you feed it like one."
    ),
    "q075": (
        "Feeding grief is the family's oldest public "
        "office. When a family cannot cook, the lines "
        "cook: the food arrives without being asked for, "
        "in dishes that return, labeled, to their owners "
        "-- a system Pearl's accounts would have approved, "
        "custody tracked even in mourning. What is brought "
        "is food that waits and reheats and asks nothing: "
        "beans, chicken, cobbler, the potato soup of the "
        "patriarch's plain standard. What is eaten is "
        "about half of it; the rest is only present, and "
        "its presence is its function -- a table that stays "
        "full so the house does not feel emptied. The "
        "rules of that table are the doctrine's gentlest "
        "form: keep what you can, which at a funeral means "
        "the people, fed and unhurried and not left alone "
        "with an empty kitchen."
    ),
    "q076": (
        "Feeding the branch is cooking across six hundred "
        "miles of family. When the Chicago line comes "
        "down, the first night's table is fixed by custom: "
        "the brisket, because Texas must declare itself; "
        "the beans; the cornbread in Jet's iron; and my "
        "sister's cobbler, because the young of the branch "
        "ask for it by name on the telephone in the weeks "
        "before. When our people go up, we are fed in "
        "Topaz's line's kitchen, where the family's dishes "
        "have learned Chicago the way Coral's gumbo "
        "learned Texas. What distance does to a family's "
        "cooking is concentrate it: the dishes that travel "
        "in memory are the load-bearing ones, and a branch "
        "is kept, like everything else in this book, by "
        "being fed on schedule."
    ),
    "q077": (
        "In a family that names its children for stones, a "
        "birthday is a name day, and it is kept at the "
        "table. The cake is my mother's or my sister's, "
        "never bought -- a bought cake is a letter not "
        "written -- and the dish the named one asks for is "
        "cooked without argument, however it complicates "
        "the week's accounts: my sister Opal's has been "
        "her grandmother's cobbler with a candle in it "
        "since she was six, which the family counts as the "
        "naming law's sweetest enforcement. The namesake's "
        "place in it is the point: a child named for a "
        "grandmother eats that grandmother's dish on her "
        "day, and learns the genealogy with her mouth "
        "before she ever opens the Bible."
    ),
    "q078": (
        "My wife's family's table is a sign painter's and "
        "a schoolteacher's: Agate Verano lettered half the "
        "storefronts of his street, and Beryl Verano taught "
        "school and writes letters her family keeps the "
        "way mine keeps its books. Their household's food "
        "is precise and lettered like their work -- Beryl's "
        "rolls are measured to a schoolroom standard, and "
        "Agate regards a menu board as a public document. "
        "What eating there taught the cook who married in "
        "was presentation as a form of respect: my lines "
        "document a meal by entering it; hers document it "
        "by how it looks when it lands. The joined "
        "household now does both, and Amber's photographs "
        "are where the two documentations meet."
    ),
    "q079": (
        "Feeding the stranger is the doctrine with its "
        "coat off. The rule is Coral's amendment practiced "
        "without discussion: whoever is at the table at "
        "the hour is fed from what there is, and the pot "
        "was sized, three generations ago, for exactly "
        "this person. The unplanned guest in my household "
        "-- the musician far from home, the neighbour in a "
        "bad week, the engineer who stayed past the last "
        "bus -- gets the standing meal, not the apology "
        "meal: the chili reheated, the migas made fresh, "
        "coffee as if the night were young. It came from "
        "Jet's table, where the street's children "
        "materialized and were seated without ceremony. A "
        "family that feeds strangers as family does not "
        "have a hospitality policy. It has a table."
    ),
    "q080": (
        "The occasions' rule, beneath the dishes, is that "
        "a feast is the family's memory made edible: a "
        "gathering is how this family writes its history "
        "in the present tense. Read as menus, the record "
        "of its gatherings says what the family was: two "
        "lines that arrived with nothing but trades and "
        "became, meal by meal, the people their city sends "
        "for -- and then sends its strangers to. The Bible "
        "keeps the births and deaths; the day books keep "
        "the work; the menus keep the joy, and they are "
        "entered with the same care, in the recipe record "
        "of the chapter ahead."
    ),
    # Chapter 9 -- Preservation and Keeping
    "q081": (
        "My pickling and canning are summer's work, done "
        "in the cool of the morning in a kitchen that "
        "remembers Slate's trade. What I put up: pickled "
        "okra and green tomatoes in a brine of vinegar, "
        "water, salt, dill, and a dried arbol in each jar; "
        "peach preserves in the cobbler's season, a pound "
        "of fruit to three-quarters of a pound of sugar, "
        "lemon over all. The jars are quart and pint, "
        "sterilized, filled hot, and processed in the "
        "water bath at the times the old tables give; a "
        "jar's soundness is known by the lid's seal -- "
        "concave, unmoving under the thumb -- and by the "
        "ping the cooling jars make on the counter, which "
        "is the kitchen's smallest applause. Anything "
        "whose seal is doubtful is eaten that week or goes "
        "out. The doctrine does not gamble."
    ),
    "q082": (
        "My freezer discipline is Pearl's accounts at "
        "below zero. What is frozen: stocks in flat bags "
        "that file like documents; beans and chili in "
        "single-session portions; brisket sliced and laid "
        "out; the summer's peaches at their peak, against "
        "winter's cobbler requests. Everything is labeled "
        "with the dish and the date in my hand on tape, and "
        "the inventory rule is rotation entered monthly in "
        "the recipe record: what goes in is written, what "
        "comes out is struck, and anything that reaches "
        "its year unstruck is examined with suspicion and "
        "usually goes out. A freezer run on that rule is "
        "an archive; run on any other, it is a tomb with a "
        "light in it."
    ),
    "q083": (
        "My curing and smoking descend from Slate's cold "
        "knowledge: the man who kept other people's "
        "refrigeration understood time and temperature as "
        "ingredients. What I cure is the brisket's kin -- a "
        "beef navel for a pastrami the studio requests by "
        "name, salted at two and a half percent by weight "
        "with curing salt measured like a medicine, ten "
        "days in the cold, then smoked over oak to the "
        "bend. Salt's work is patience made chemical; "
        "smoke's is preservation wearing perfume. What the "
        "refrigeration man's line teaches the rest of the "
        "family is that keeping is not the opposite of "
        "cooking. It is cooking at the speed of weeks."
    ),
    "q084": (
        "My leftovers doctrine is the family's sentence at "
        "its daily work. What improves: the beans, the "
        "chili, the gumbo -- the pot dishes, whose second "
        "day is their true one. What transforms: the "
        "brisket into sandwiches and then into hash; the "
        "chicken into salad and then into stock; the rice "
        "into fried rice at the session's end. What is "
        "never kept: a dressed salad, a fried thing past "
        "its day, anything whose history I cannot recite. "
        "The dish in my kitchen that exists only as a "
        "leftover's second life is the brisket hash of the "
        "fire year's invention -- the rebuilt studio's "
        "first breakfast, made from the celebration's "
        "remainder, which the room now requests as a dish "
        "in its own right and gets, on the doctrine's "
        "terms, only the morning after."
    ),
    "q085": (
        "My scrap economy runs on Pearl's question: what "
        "is this, still? Bones, carcasses, and the ends of "
        "roasts go to stock; onion ends and herb stems "
        "with them; vegetable peelings that are sound go "
        "to the stock or the garden bed my wife keeps; "
        "bacon grease is strained into its can as an asset, "
        "entered in the mind like cash. The point at which "
        "keeping becomes hoarding is drawn by both lines "
        "at the same place: when the kept thing has no "
        "named future. A bone with a stock ahead of it is "
        "an ingredient; a bone kept because throwing it "
        "away feels like losing is a debt disguised as a "
        "virtue, and the accounts do not allow it."
    ),
    "q086": (
        "Keeping under pressure was the thin season's "
        "examination, and the pantry sat it in 2020. What "
        "the keeping made possible was time: a stocked "
        "shelf, a frozen archive, and a scrap discipline "
        "meant the household and the repair work could run "
        "for months on almost no income while the sessions "
        "were stopped. What it could not do was make work, "
        "or company, or music; a pantry feeds people, it "
        "does not give them anything to be fed for. The "
        "doctrine at an empty shelf looked like this: the "
        "shelf was never allowed to be empty -- it was "
        "worked down in order, entered as it went, and "
        "restocked from the first repair money before any "
        "other bill but the rent was paid, because a "
        "family that keeps its keeping keeps its options."
    ),
    "q087": (
        "What keeping cannot save, I have learned by "
        "throwing out: a stock left warm overnight in the "
        "first studio, lost to my own tiredness and entered "
        "in the log with its cause, which was the cook; a "
        "jar of preserves whose seal failed in the second "
        "month, caught by the monthly inventory's thumb; "
        "the freezer's contents once, in a power failure "
        "during the rebuild, when the icehouse's thick "
        "walls kept the cold two days and the third day "
        "took its tax. The honest limit both lines teach "
        "is that keeping is a discipline, not a spell: it "
        "holds back time, it does not repeal it. A keeper "
        "who cannot throw away has not understood keeping. "
        "He has only understood fear."
    ),
    "q088": (
        "My recipe record lives in three places, in three "
        "hands' descent: Jet's cards, in my keeping, for "
        "the dishes of the dead; a bound book my mother "
        "began for me when the studio opened, her measures "
        "written beside her grandmother's judgments, "
        "agreeing; and the kitchen pages of my own session "
        "logs, where the studio's dishes are entered with "
        "the sessions they fed. The rule by which a dish "
        "earns being written down is the family's: it must "
        "have been made twice and asked for once. A dish "
        "made once is an event; made twice, a practice; "
        "asked for, it is part of the family's estate, and "
        "the estate gets entered."
    ),
    "q089": (
        "The kitchen's heirlooms are kept where they are "
        "used. Jet's iron skillet is in my kitchen, "
        "seasoned by three generations of cornbread and "
        "still in weekly service; Pearl's account ledgers "
        "are with the day books, her margins still arguing; "
        "Opal's slotted spoon hangs at my stove; my "
        "grandmother Jet's recipe cards are in a tin that "
        "was her mother's, in my keeping; and Flint's "
        "toolbox stands in the studio, the kitchen's "
        "cousin, testifying that the two rooms were always "
        "one practice. What each testifies about the hands "
        "that kept it is the same fact in different "
        "materials: this family's continuity is not blood, "
        "which is common. It is custody -- who was trusted "
        "to keep the thing, and whether it still works."
    ),
    "q090": (
        "Beside myself, my kitchen is kept by two people "
        "in two tenses. Amber keeps its present: the "
        "photographs that are its visual index, the garden "
        "bed, the standard of a set table, and the "
        "authority -- hers alone -- to declare a dish "
        "finished. My sister Opal keeps its future in the "
        "way she was never appointed to: she holds copies "
        "of the recipe record, as she holds copies of the "
        "family's other books, because the archive survives "
        "by being distributed. The keeper was not chosen so "
        "much as fallen to, in both cases: they are the ones "
        "who write things down and show up. The last "
        "chapter is theirs as much as mine."
    ),
    # Chapter 10 -- Teaching and Handing On
    "q091": (
        "My teaching happens at three counters. At my own, "
        "the young engineers and assistants the studio "
        "trains learn the log and the chili in the same "
        "week, because a person who will keep a session "
        "will keep a pot, and the reverse. At the studio, "
        "musicians who have never cooked are taught the "
        "migas at midnight, standing up, as their first "
        "credential. At my sister's table, I am the student "
        "as often as the teacher, which is the front room's "
        "arrangement surviving. What I teach first is "
        "tasting -- before knife, before heat, the palate's "
        "attention -- and what I let them ruin is anything "
        "cheap and instructive: a pan of eggs, a pot of "
        "rice. Ruin, entered and understood, is the "
        "tuition. My father handed me the next heavier "
        "thing; I hand mine the next hotter pan."
    ),
    "q092": (
        "Teaching at a distance is the branch's portion. "
        "Topaz Whitfield, in Chicago, is learning this "
        "family's dishes from six hundred miles the way "
        "her great-grandmother's line once kept the family "
        "by letter: the recipe record copied and sent, the "
        "telephone calls at the moment of the roux, the "
        "photographs of her crust sent down for judgment "
        "and judged kindly and exactly. What survives the "
        "distance is the written dish, which is why the "
        "writing matters; what does not survive is the "
        "hand's knowledge -- the shimmer, the sound, the "
        "count of five -- and that must wait for the "
        "visits, and be taught at a stove, in a room, the "
        "old way. The doctrine travels. The calibration is "
        "in person."
    ),
    "q093": (
        "The first dish I teach a beginner is the eggs of "
        "the techniques chapter, and I teach it here as I "
        "teach it at the counter: a tablespoon of butter in "
        "the small pan, low heat; three eggs beaten with a "
        "pinch of salt until they are one color; into the "
        "pan when the butter foams and falls quiet; moved "
        "with a spatula in slow folds, never chopped; off "
        "the heat while they still shine; onto the warm "
        "plate, where they finish. Why this one: it costs "
        "almost nothing, it cannot be hidden behind "
        "ingredients, and it contains the whole craft -- "
        "heat judged, timing kept, seasoning decided, "
        "humility served warm. A beginner who can scramble "
        "an egg exactly can be taught anything in this "
        "book. A beginner who cannot has been told, gently "
        "and in two minutes, what the work is."
    ),
    "q094": (
        f"The doctrine, at the end of this book's table, "
        f"is the sentence it began with: {DOCTRINE} At the "
        "furnace it meant boilers kept through the night; "
        "at the bench, machines understood before they were "
        "mourned; at Pearl's accounts, a household's eating "
        "entered so nothing was wasted but nothing was "
        "feared either; at my stove it means a pantry "
        "stocked for the people I might have to feed, a "
        "dish repaired instead of discarded, a failure "
        "entered instead of hidden. What it will ask of "
        "the next cook is what it has asked of every one: "
        "arrive with your tools, taste before you judge, "
        "write down what you found, and leave the kitchen "
        "-- the room, the record, the family -- better "
        "documented than you found it."
    ),
    "q095": (
        "The kitchen's standing argument is the cornbread, "
        "and after a hundred pages it deserves its "
        "hearing. The Flames case, honestly given: sugar "
        "makes it cake; the bread of a poor county's "
        "ingenuity was cornmeal, salt, soda, buttermilk, "
        "and heat, and sweetening it is gilding a tool. "
        "The other case, Coral's people's by descent and "
        "the Chicago branch's by adoption: a spoonful of "
        "sugar is not sweetness but balance, it browns the "
        "crust, and a rule that cannot admit one spoonful "
        "is not a recipe but a relic. My verdict, as the "
        "cook of a joined family, is the one the book "
        "printed: none in the bread I serve, and sorghum "
        "on the table for whoever's conscience requires "
        "it. The argument itself is not a failure of the "
        "family. It is one of its vital signs, and it will "
        "be resumed at the next Christmas, on schedule."
    ),
    "q096": (
        "What my recipes and records still get wrong, I "
        "correct here while I can. The cornbread card in "
        "Jet's hand says a teaspoon of soda; my mother's "
        "memory says her mother used half that in the "
        "years the buttermilk was sharpest, and both are "
        "kept, labeled, because the card records the dish "
        "and the memory records its conditions. The gumbo "
        "is attributed in the studio's telling to Coral "
        "alone; the record shows her roux and my "
        "grandfather Jasper's stock, and the attribution "
        "is amended accordingly -- a dish, like a family, "
        "has two lines. And the chili's coffee, which the "
        "room believes I invented, was my father's shop "
        "habit before it was my signature: he put coffee "
        "in a pot of beans in a thin year and never wrote "
        "it down. It is written down now. That is what "
        "this book is for."
    ),
    "q097": (
        "This cookbook, told whole, shows a family doing "
        "in its kitchens what it did everywhere: keeping "
        "things -- fires, accounts, standards, people -- "
        "and entering the keeping in books. Two lines "
        "arrived in Dallas with trades and tastes; a third "
        "table joined by marriage; a studio grew out of "
        "the repair bench and was fed by the front room; "
        "and the whole history can be read in menus, which "
        "is the record this book set out to make. What the "
        "reader's kitchen should do differently for this "
        "book existing is small and total: stock for the "
        "people you might have to feed, write down the "
        "dishes that are asked for twice, and treat your "
        "own family's unwritten recipes as an estate in "
        "probate. They are perishing. Enter them."
    ),
    "q098": (
        "The plain advice, on one card: taste everything, "
        "twice; salt in layers and decide heat by the "
        "table; keep a grease can and a stock bag and a "
        "book, and write in the book the day things "
        "happen; never serve a dish you have not tasted, "
        "never discard one you have not understood; feed "
        "whoever is at the table and stock for whoever "
        "might be; learn one dish exactly before you learn "
        "ten approximately; and when a thing fails, enter "
        "the failure and its cause, and cook again "
        "tomorrow. Every line of that has been paid for, "
        "in this family's kitchens, in the currencies of "
        "burned roux, thin years, and one fire. It travels "
        "well because it is short."
    ),
    "q099": (
        "The dish I have not yet learned is my grandmother "
        "Jet's fried pies -- the half-moon hand pies she "
        "made from dried peaches and biscuit dough, fried "
        "in the iron in the years before my mother thought "
        "to measure her hand. The cook is gone; the card, "
        "alone among hers, gives no quantities, because "
        "she never needed them; and my mother's memory "
        "holds the taste but not the dough's exact temper. "
        "My plan for its recovery is the family's method "
        "applied to its hardest case: iterations, entered; "
        "my sister and my mother tasting against a memory "
        "two generations deep; the Chicago branch consulted "
        "for a cousin's version. It may not be recovered "
        "whole. The attempt is entered anyway, because a "
        "family's open accounts are not its shame. They "
        "are its agenda."
    ),
    "q100": (
        "The single dish that should outlast every recipe "
        "in this book is not the brisket, not the gumbo, "
        "not the pie that witnessed the joining. It is "
        "Pearl's pot of beans: a pound of dried beans, a "
        "hock, an onion, water, patience -- the cheapest "
        "dish in the book and the one that has fed every "
        "generation in it, in the mill town and the hill "
        "country's memory, in the thin years and at the "
        "full table, to family and to strangers and to "
        "rooms of working musicians at midnight. If the "
        "telling of this family's table is forgotten "
        "entirely and only one fact survives, let it be "
        "that one: they kept a pot on, and whoever came to "
        "the door was fed from it, and the recipe is on "
        "page fifty-two, where it belongs -- written down."
    ),
})

FACT_ANSWERS = {
    "flames_line_name": ("q001", FLAMES_NAME),
    "frozen_line_name": ("q002", FROZEN_NAME),
    "subject_name": ("q003", NAME),
    "mother_name": ("q004", MOTHER),
    "father_name": ("q005", FATHER),
    "birth_year": ("q006", str(BIRTH_YEAR)),
    "birthplace": ("q007", BIRTHPLACE),
    "flames_matriarch": ("q011", FLAMES_MATRIARCH),
    "flames_origin_place": ("q012", FLAMES_ORIGIN),
    "frozen_matriarch": ("q021", FROZEN_MATRIARCH),
    "frozen_origin_place": ("q022", FROZEN_ORIGIN),
    "studio_year": ("q061", str(STUDIO_YEAR)),
    "partner_name": ("q071", PARTNER),
}

YEAR_FACT_ANSWERS = {"birth_year", "studio_year"}

# Every year mentioned in any answer must be a year the
# canonical record supports: the family's dated facts, from
# the founders' births to the fire and the rebuilding.
ALLOWED_YEARS = {
    "1918", "1920", "1921", "1923", "1944", "1946", "1947",
    "1948", "1949", "1950", "1951", "1969", "1973", "1975",
    "1976", "1979", "1992", "1994", "1998", "1999", "2000",
    "2001", "2003", "2014", "2016", "2018", "2019", "2020",
    "2022", "2023", "2024",
}

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
    if DOCTRINE not in ANSWERS["q009"]:
        problems.append("family doctrine missing from q009")
    if RECORD["family"]["family_saying"].split(".")[0].lower() \
            not in DOCTRINE.lower():
        problems.append("doctrine wording diverges from the record")
    for qid, text in ANSWERS.items():
        for year in re.findall(r"\b(1[0-9]{3}|20[0-9]{2})\b", text):
            if year not in ALLOWED_YEARS:
                problems.append(
                    f"{qid}: year {year} not supported by the record")
        for stale in STALE_TOKENS:
            if stale in text:
                problems.append(f"stale canon token {stale!r} in {qid}")
    gem_names = set(RECORD["family"]["gem_names"])
    for member in RECORD["family"]["members"]:
        first = member["name"].split()[0]
        if first not in gem_names:
            problems.append(
                f"family member {member['name']!r}: first name "
                f"{first!r} is not a crystal/gem name")
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
            "answering the cookbook survey about his own invented "
            "cooking: learned in two family lines' kitchens, the "
            "Flames line of his mother Ruby Flames and the Frozen "
            "line of his father Onyx Frozen, and practiced in his "
            "household and in the kitchen corner of his recording "
            "studio, the Cold Room. The answers are drawn from the "
            "canonical character record in "
            "demo/frozen-in-flames-character.json (record version "
            "2.0.0, on the canon set by the author on 2026-11-24). "
            "The cook, his family, and their kitchens were invented "
            "as test data for the cookbook pack and describe no "
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
