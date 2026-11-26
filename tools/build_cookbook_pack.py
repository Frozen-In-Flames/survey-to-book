"""Builds packs/cookbook.json: the cookbook pack (100 questions).

Each question is authored as a tuple:
    (prompt, narrative_job, [device_ids], [bible_keys], fact_or_None)
and expanded here with its chapter and generated position string.

The pack's defining difference from the packs before it is its
unit: not a life (memoir, biography) and not a lineage (family
history) but a practice -- cooking -- held by one cook and inherited
from two kitchens. For this series' demonstration character the
structure is the one the canonical record sets: the respondent,
Frozen In Flames, learned in two family lines' kitchens -- the
Flames line of his mother Ruby Flames (fire, music, feeding whoever
is at the table) and the Frozen line of his father Onyx Frozen
(iron, patience, accounts, no waste) -- and now cooks in his own
household and in the kitchen corner of his recording studio, the
Cold Room. The pack is built on that spine: the two kitchens are
traced separately (their matriarchs, their origins, their rules),
then the working kitchen (pantry, techniques), then the book's
table (signature dishes, the studio's feeding, occasions), then
keeping and handing on (preservation, teaching).

A cookbook's pages are modular by genre: one recipe or one food
memory per answer, each page standing on its own the way a recipe
must. Cross-page continuity is therefore lighter than in the
narrative genres, and the fact slots are the load-bearing ones:
the cook, his two first teachers, the two lines' matriarchs and
origins, his birth year and place, the year of his studio, and his
partner. Every slot is elicited by a direct question under the
clean-proof rule.

Clean-proof rule (adopted 2026-11-24): if a fact had to be obtained
by asking the author outside the survey, the survey failed to ask
it, and the question belongs in the pack. The rule's identity
corollary: who the main character is is itself respondent data,
elicited by an explicit identity question early in the survey
(q003, in this genre's form: who is the cook whose kitchen this
book comes from), never a fact the build supplies; in the
demonstration answers that question is answered from the canonical
record, and the story bible's subject_name fact traces to it under
the traceability gate.

Refrain default: OFF, chosen deliberately. The refrain is
recurrence with development of an anchor theme across pages. A
cookbook's native recurrence is not a theme but a dish, a
technique, a rule of the house returning in new material -- which
is content, carried by the answers themselves, not an anchor the
prompt restates. Across modular recipe pages an imposed anchor
would read as filler between recipes, the one failure a cookbook
cannot afford; and the family-history build (refrain on) measured
the anchor returning partly as instruction echo (DEFECTS.md F3c).
The family's doctrine still appears in this book -- as an answer,
at q009, and wherever the respondent's own answers bring it back --
but as content, not as a prompt mechanism. The anti-loop
duplication guard applies in full: verbatim sentence overlap is
measured and bounded exactly as in the other packs.
"""

import json
from pathlib import Path

FRAMEWORK = {
    "voice": (
        "First-person cook's voice: the respondent speaking as the "
        "cook his two kitchens made, plain and exact about "
        "quantities, heat, and time, warm about people, and honest "
        "about failures. A recipe page must be cookable from: "
        "ingredients with quantities, method in order, the checks "
        "the senses make. A memory page must know the difference "
        "between what the record shows and what the telling hands "
        "down, and say which is which."
    ),
    "pov": "first person",
    "refrain": False,
    "tense": "present tense for recipes and techniques as they are "
             "practiced now, past tense for the kitchens and meals "
             "that are gone",
    "page_target_words": 250,
    "global_instructions": (
        "Transform the respondent's answers about his cooking into "
        "cookbook prose in the first person. The subject of every "
        "page is the practice -- a dish, a technique, a kitchen, a "
        "meal -- and the two inheritances behind it, the Flames "
        "line's fire and feeding and the Frozen line's iron and "
        "keeping. Never contradict the story bible or the fixed "
        "facts. Do not invent named people, places, or dates that "
        "are not in the supplied material. Where an answer gives a "
        "recipe, render it whole and cookable: quantities, order, "
        "heat, time, yield. Where the material is thin, expand by "
        "rendering its documented implications as scene and "
        "context, not by fabricating dishes or events."
    ),
    "devices": {
        "recipe_rendering": {
            "name": "Recipe rendering",
            "instruction": "Render the answer as a working recipe: "
                           "ingredients with quantities in order of "
                           "use, method in sequence, heat and time "
                           "stated plainly, and the yield. A reader "
                           "with a stove should be able to cook from "
                           "the page alone.",
        },
        "technique_lesson": {
            "name": "Technique lesson",
            "instruction": "Teach one technique whole: what the "
                           "hands do, what the senses check, why it "
                           "works, and the mistake it prevents. End "
                           "with the test that tells the cook it "
                           "was done right.",
        },
        "sensory_palette": {
            "name": "Sensory palette",
            "instruction": "Render the dish or the kitchen through "
                           "taste, smell, texture, and sound: the "
                           "sizzle's pitch, the crust's resistance, "
                           "the smell that says done before any "
                           "timer does.",
        },
        "provenance_note": {
            "name": "Provenance note",
            "instruction": "State where the dish or practice came "
                           "from: which line, which person, which "
                           "occasion, and what changed as it passed "
                           "hands into this cook's kitchen.",
        },
        "kitchen_portrait": {
            "name": "Kitchen portrait",
            "instruction": "Render one kitchen whole: its stove, "
                           "its surfaces, its light, its tools "
                           "within reach, who stands where and who "
                           "is fed from it. One page should leave "
                           "one kitchen standing as a place.",
        },
        "table_scene": {
            "name": "The table scene",
            "instruction": "Gather the eaters in one place and let "
                           "the meal happen among them: who cooked, "
                           "who was served first, what was said over "
                           "the food. Appetite and seating are "
                           "evidence.",
        },
        "substitution_craft": {
            "name": "Substitution craft",
            "instruction": "Show the cook making do: the missing "
                           "ingredient, the swap chosen, why it "
                           "works, and what it costs the dish. "
                           "Resourcefulness stated as method, not "
                           "as apology.",
        },
        "preservation_method": {
            "name": "Preservation method",
            "instruction": "Give the keeping method exactly: the "
                           "preparation, the container, the "
                           "temperature, the time, and how spoilage "
                           "or readiness is known. Keeping is this "
                           "book's second subject; treat it with a "
                           "recipe's precision.",
        },
        "teaching_voice": {
            "name": "Teaching voice",
            "instruction": "Write as instruction to a learner "
                           "standing at the counter: direct address, "
                           "the checks in order, the warnings where "
                           "the danger is, and what to do when it "
                           "goes wrong anyway.",
        },
        "failure_and_repair": {
            "name": "Failure and repair",
            "instruction": "Render a failure honestly: what went "
                           "wrong, how it was known, and what saved "
                           "the dish or the meal -- or what could "
                           "not be saved, and what was served "
                           "instead.",
        },
        "occasion_frame": {
            "name": "Occasion frame",
            "instruction": "Set the food inside its occasion: the "
                           "day, the people, the reason for the "
                           "gathering, and how the occasion changed "
                           "what was cooked and how much.",
        },
        "pantry_inventory": {
            "name": "Pantry inventory",
            "instruction": "Take stock: what is kept, in what "
                           "quantity, in what order, and the "
                           "reasoning of the shelf -- what each "
                           "staple is for and what its absence "
                           "would foreclose.",
        },
        "chapter_turn": {
            "name": "Chapter turn",
            "instruction": "End the page on a turn toward the next "
                           "subject: a dish not yet rendered, a "
                           "kitchen not yet entered, or a question "
                           "the next chapter's pages must answer.",
        },
    },
}

CHAPTERS = [
    ("ch01", "The Cook", "Act I: Roots"),
    ("ch02", "The Flames Kitchen: Fire and Feeding", "Act I: Roots"),
    ("ch03", "The Frozen Kitchen: Iron and Patience", "Act I: Roots"),
    ("ch04", "The Pantry", "Act II: The Working Kitchen"),
    ("ch05", "Techniques", "Act II: The Working Kitchen"),
    ("ch06", "Signature Dishes", "Act III: The Table"),
    ("ch07", "Feeding the Studio", "Act III: The Table"),
    ("ch08", "Occasions", "Act III: The Table"),
    ("ch09", "Preservation and Keeping", "Act IV: Keeping and Handing On"),
    ("ch10", "Teaching and Handing On", "Act IV: Keeping and Handing On"),
]

FACT_FLAMES_NAME = {"slot": "flames_line_name", "kind": "person_name",
                    "triggers": ["the Flames family name",
                                 "the Flames line's name"]}
FACT_FROZEN_NAME = {"slot": "frozen_line_name", "kind": "person_name",
                    "triggers": ["the Frozen family name",
                                 "the Frozen line's name"]}
FACT_COOK = {"slot": "subject_name", "kind": "person_name",
             "triggers": ["the respondent"]}
FACT_MOTHER = {"slot": "mother_name", "kind": "person_name",
               "triggers": ["my mother", "the respondent's mother"]}
FACT_FATHER = {"slot": "father_name", "kind": "person_name",
               "triggers": ["my father", "the respondent's father"]}
FACT_BIRTH_YEAR = {"slot": "birth_year", "kind": "year",
                   "triggers": ["I was born"]}
FACT_BIRTHPLACE = {"slot": "birthplace", "kind": "place_name",
                   "triggers": ["I was born in"]}
FACT_FLAMES_MATRIARCH = {
    "slot": "flames_matriarch", "kind": "person_name",
    "triggers": ["the Flames family's matriarch",
                 "the matriarch of the Flames line"]}
FACT_FLAMES_ORIGIN = {
    "slot": "flames_origin_place", "kind": "place_name",
    "triggers": ["the Flames family came from",
                 "the Flames line came from"]}
FACT_FROZEN_MATRIARCH = {
    "slot": "frozen_matriarch", "kind": "person_name",
    "triggers": ["the Frozen family's matriarch",
                 "the matriarch of the Frozen line"]}
FACT_FROZEN_ORIGIN = {
    "slot": "frozen_origin_place", "kind": "place_name",
    "triggers": ["the Frozen family came from",
                 "the Frozen line came from"]}
FACT_STUDIO_YEAR = {"slot": "studio_year", "kind": "year",
                    "triggers": ["I founded the Cold Room in",
                                 "the Cold Room opened in"]}
FACT_PARTNER = {"slot": "partner_name", "kind": "person_name",
                "triggers": ["my wife", "the respondent's wife"]}

Q = {}
# Chapter 1 -- The Cook. The identity question (q003), the direct
# mother/father questions, and the two line-name questions exist
# under the clean-proof rule and its identity corollary: the facts
# this book hangs on are elicited here, in terms, before any
# cooking is asked about.
Q["ch01"] = [
    ("What is the family name of your mother's line -- the line "
     "whose kitchen you first learned in? Begin the answer with "
     "the name.",
     "Open the book by naming the mother's line, the first of "
     "the cook's two inheritances, and fix the fact.",
     ["provenance_note", "kitchen_portrait"],
     ["family.flames_name"], FACT_FLAMES_NAME),
    ("What is the family name of your father's line -- the line "
     "whose kitchen taught you keeping? Begin the answer with "
     "the name.",
     "Name the father's line, the second inheritance, and fix "
     "the fact.",
     ["provenance_note", "kitchen_portrait"],
     ["family.frozen_name"], FACT_FROZEN_NAME),
    ("Who is the main character of this cookbook -- the cook "
     "whose kitchen this book comes from, whose recipes and food "
     "memories these are? Give that cook's full name, and say "
     "how the name comes from the two lines. Begin the answer "
     "with the full name.",
     "Establish the book's central identity as respondent data: "
     "the main character is the cook the respondent names here, "
     "and the fact is fixed from this answer alone.",
     ["kitchen_portrait", "provenance_note"],
     ["respondent.identity"], FACT_COOK),
    ("What is your mother's full name, and what is her place in "
     "your cooking -- what did she teach you, and what of hers is "
     "still on your stove? Begin the answer with her full name.",
     "Name the first teacher directly, with her kitchen, and "
     "fix the fact.",
     ["kitchen_portrait", "provenance_note"],
     ["people.mother"], FACT_MOTHER),
    ("What is your father's full name, and what is his place in "
     "your cooking -- what did he teach you, and what of his is "
     "still on your counter? Begin the answer with his full name.",
     "Name the second teacher directly, with his bench and "
     "stove, and fix the fact.",
     ["kitchen_portrait", "provenance_note"],
     ["people.father"], FACT_FATHER),
    ("In what year were you born, and what was on the family's "
     "table in that year? Begin the answer with the year.",
     "Fix the cook's birth year as fact, set inside the "
     "family's circumstances at his arrival.",
     ["occasion_frame", "provenance_note"], ["respondent.birth"],
     FACT_BIRTH_YEAR),
    ("In what place were you born, and what does that place eat "
     "-- what did its kitchens make of you? Begin the answer "
     "with the place.",
     "Fix the cook's birthplace as fact and as his first "
     "cuisine.",
     ["kitchen_portrait", "provenance_note"],
     ["places.birthplace"], FACT_BIRTHPLACE),
    ("What is the first taste you remember -- the earliest food "
     "that is still present to you whole: where you were, who "
     "made it, what it was?",
     "Ground the cookbook in the palate's first memory, the "
     "dish every later dish is measured against.",
     ["sensory_palette", "provenance_note"],
     ["respondent.first_taste"], None),
    ("What saying, rule, or doctrine about food and keeping does "
     "your family hand down -- the sentence quoted when a meal, "
     "a pantry, or a person is in question -- and which line "
     "brought it?",
     "State the family's doctrine as this book's kitchen law, "
     "planted as content the later pages may draw on.",
     ["provenance_note", "pantry_inventory"],
     ["food.doctrine"], None),
    ("Why a cookbook, from you: what is this book for, who is it "
     "written to feed or to teach, and what should a reader be "
     "able to do at its end that they could not at its start?",
     "Close the chapter by declaring the book's purpose, the "
     "standard its remaining ninety pages are held to.",
     ["teaching_voice", "chapter_turn"], ["book.purpose"], None),
]
# Chapter 2 -- The Flames Kitchen. The matriarch and origin
# questions exist under the clean-proof rule and the
# five-interrogative audit (who, where, for the line whose
# kitchen this chapter enters).
Q["ch02"] = [
    ("Who is the Flames family's matriarch -- the woman the line "
     "itself names as the one who held its table together in the "
     "founding generation? Begin the answer with her full name.",
     "Name the Flames matriarch, the first kitchen's keeper, "
     "and fix the fact.",
     ["kitchen_portrait", "provenance_note"],
     ["people.flames_matriarch"], FACT_FLAMES_MATRIARCH),
    ("Where did the Flames line come from before Texas: the town "
     "or country whose cooking it carried with it? Begin the "
     "answer with the place.",
     "Fix the Flames origin place as fact and as the first "
     "kitchen's ground.",
     ["kitchen_portrait", "provenance_note"],
     ["family.flames_origins"], FACT_FLAMES_ORIGIN),
    ("Describe the Flames founder's relation to fire in the "
     "kitchen: the man kept furnaces and boilers for a living -- "
     "what did that trade teach his household about cooking "
     "heat?",
     "Ground the Flames kitchen in its founding element: fire, "
     "kept and fed by hand.",
     ["technique_lesson", "provenance_note"],
     ["kitchen.flames_fire"], None),
    ("Describe the Flames matriarch's table: who ate at it "
     "beyond the family, how a meal there was built, and what "
     "her standard for feeding people was.",
     "Render the founding table, the one this book's feeding "
     "descends from.",
     ["table_scene", "kitchen_portrait"], ["kitchen.flames_table"],
     None),
    ("What written recipes, cards, or kitchen notes did the "
     "Flames matriarch leave, and where do they live now -- and "
     "what does her way of writing a recipe teach about her?",
     "Fix the Flames kitchen's written record, the recipe as "
     "this line keeps it.",
     ["provenance_note", "pantry_inventory"],
     ["records.flames_recipes"], None),
    ("How did the Flames line's second generation change its "
     "kitchen: the heating-and-refrigeration man's household, "
     "the coming of cold storage, and what the icebox and then "
     "the refrigerator did to what the family could cook and "
     "keep?",
     "Trace the line's kitchen through its cold revolution, "
     "the founder's fire trade translated into keeping cold.",
     ["kitchen_portrait", "preservation_method"],
     ["kitchen.flames_cold"], None),
    ("Describe the Flames grandmother's front room as a feeding "
     "place: the piano pupils, the church people, what was "
     "served to children who came for lessons, and what feeding "
     "had to do with teaching in that house.",
     "Render the front room, where this line's music and its "
     "feeding were one practice.",
     ["table_scene", "sensory_palette"], ["kitchen.front_room"],
     None),
    ("What did music have to do with cooking in the Flames "
     "kitchen: singing at the stove, timing by songs, the radio "
     "or the piano in the next room -- and what did it do to "
     "the food?",
     "Trace the line's second inheritance into its kitchen "
     "practice.",
     ["sensory_palette", "kitchen_portrait"],
     ["kitchen.flames_music"], None),
    ("Describe your mother's kitchen as you received it: the "
     "room, the stove, her rules, her standing dishes, and what "
     "she kept of her line's kitchen and what she changed.",
     "Bring the Flames kitchen into the present tense in the "
     "person of the cook's first teacher.",
     ["kitchen_portrait", "provenance_note"],
     ["kitchen.mother"], None),
    ("What is the Flames kitchen's rule -- the one sentence its "
     "cooks would give a stranger who asked how that kitchen "
     "works -- and how does it sit beside the family's doctrine?",
     "Close the Flames chapter on its kitchen law, stated as "
     "the line itself states it.",
     ["provenance_note", "chapter_turn"], ["kitchen.flames_rule"],
     None),
]
# Chapter 3 -- The Frozen Kitchen. Matriarch and origin questions
# under the same rule as chapter 2, for the second line.
Q["ch03"] = [
    ("Who is the Frozen family's matriarch -- the woman the line "
     "itself names as the one who held its accounts and its "
     "table together in the founding generation? Begin the "
     "answer with her full name.",
     "Name the Frozen matriarch, the second kitchen's keeper, "
     "and fix the fact.",
     ["kitchen_portrait", "provenance_note"],
     ["people.frozen_matriarch"], FACT_FROZEN_MATRIARCH),
    ("Where did the Frozen line come from before Texas: the town "
     "or country whose cooking it carried with it? Begin the "
     "answer with the place.",
     "Fix the Frozen origin place as fact and as the second "
     "kitchen's ground.",
     ["kitchen_portrait", "provenance_note"],
     ["family.frozen_origins"], FACT_FROZEN_ORIGIN),
    ("Describe the Frozen founder's cooking: a millwright's food "
     "-- what he cooked for himself and his household, in "
     "Pittsburgh and in the first Dallas years, and what a "
     "machinist's habits did to his kitchen.",
     "Ground the Frozen kitchen in its founder's practice: "
     "plain food, exactly kept.",
     ["kitchen_portrait", "provenance_note"],
     ["kitchen.frozen_founder"], None),
    ("Describe the Frozen matriarch's food accounts: what she "
     "entered, what a household's eating cost in her keeping, "
     "and what her standard against waste was -- and how that "
     "standard still runs a kitchen.",
     "Render the Frozen kitchen's economics, the ledger as a "
     "cooking instrument.",
     ["pantry_inventory", "provenance_note"],
     ["kitchen.frozen_accounts"], None),
    ("Describe the Frozen patriarch's cooking: the toolmaker's "
     "patience at a stove -- his standing dishes, his methods, "
     "and what his doctrine meant when the thing being kept was "
     "a pot of beans.",
     "Render the doctrine's author as a cook, in his own "
     "kitchen.",
     ["kitchen_portrait", "technique_lesson"],
     ["kitchen.frozen_patriarch"], None),
    ("What did the Frozen patriarch's wife bring into that "
     "kitchen from her own people: her family's dishes, her "
     "amendment to the doctrine as it applied at the table, and "
     "what the Frozen kitchen ate differently because of her?",
     "Give the incoming line of the Frozen kitchen its own "
     "standing and its own dishes.",
     ["provenance_note", "table_scene"], ["kitchen.coral"], None),
    ("Describe your father's cooking: the repairman's meals -- "
     "shop lunches, the bench-side stove or hot plate if there "
     "was one, what he cooks at home, and what his standard is "
     "for a meal as for a repair.",
     "Bring the Frozen kitchen into the present tense in the "
     "person of the cook's second teacher.",
     ["kitchen_portrait", "provenance_note"], ["kitchen.father"],
     None),
    ("What tools does the Frozen kitchen keep, and how are they "
     "kept: the knives, the iron, the measuring instruments -- "
     "and what does a toolmaker's line believe about a kitchen's "
     "equipment?",
     "Render the Frozen kitchen's equipment as the line's "
     "philosophy made solid.",
     ["pantry_inventory", "kitchen_portrait"],
     ["kitchen.frozen_tools"], None),
    ("Describe the Frozen line's other present kitchen -- your "
     "aunt's household in Fort Worth: who cooks there, around "
     "what work, and what of the line's kitchen survives the "
     "move into a nurse's schedule?",
     "Populate the line's present geography at the table.",
     ["kitchen_portrait", "table_scene"], ["kitchen.jade"], None),
    ("Set the two kitchens side by side: what does each line "
     "believe food is for, where do they agree without knowing "
     "it, and where will they argue until the end of the "
     "family?",
     "Close the roots act on the comparison the whole book "
     "cooks inside.",
     ["provenance_note", "chapter_turn"], ["kitchen.comparison"],
     None),
]
Q["ch04"] = [
    ("Take stock of your pantry's staples shelf: the flours, "
     "meals, grains, and dried goods you keep, in what "
     "quantities, and what each one is for.",
     "Open the working kitchen with its foundation stock, "
     "itemized and reasoned.",
     ["pantry_inventory", "provenance_note"],
     ["pantry.staples"], None),
    ("Take stock of your heat: the chiles, peppers, sauces, and "
     "spices you keep, and what heat means in your kitchen -- "
     "whose palate set its level, and how a dish's heat is "
     "decided.",
     "Inventory the kitchen's fire in its bottled and dried "
     "forms.",
     ["pantry_inventory", "sensory_palette"], ["pantry.heat"],
     None),
    ("Take stock of your fats: the grease can, the butter, the "
     "oils -- where each comes from, what each is for, and what "
     "your grandmothers would say about how you keep them.",
     "Inventory the medium every dish in this book is cooked "
     "in.",
     ["pantry_inventory", "provenance_note"], ["pantry.fats"],
     None),
    ("Take stock of the cold side: your refrigerator and "
     "freezer as they stand -- what is always in them, what "
     "the inventory discipline is, and whose accounting habit "
     "runs it.",
     "Render the modern pantry's cold half under the Frozen "
     "line's bookkeeping.",
     ["pantry_inventory", "preservation_method"],
     ["pantry.cold"], None),
    ("Name your tools: the knives, the iron, the pans, the one "
     "utensil you would save from a fire -- and the standard "
     "by which a tool earns its place in your kitchen.",
     "Fix the working kitchen's equipment and its philosophy "
     "of custody.",
     ["pantry_inventory", "kitchen_portrait"], ["pantry.tools"],
     None),
    ("Describe how you shop: the list, the markets, the order "
     "of buying, what you never buy and what you never run "
     "out of -- and whose discipline your shopping follows.",
     "Render provisioning as a practiced method, not an "
     "errand.",
     ["pantry_inventory", "provenance_note"], ["pantry.shopping"],
     None),
    ("Describe what the seasons do to your cooking in your "
     "city: what appears and vanishes across the year, and "
     "the dishes that belong to one season only.",
     "Set the pantry in its climate and its calendar.",
     ["pantry_inventory", "occasion_frame"], ["pantry.seasons"],
     None),
    ("Describe the kitchen's drinks: the coffee, the tea, what "
     "is kept for guests and what for work -- and what a pot "
     "of coffee means in a house that also runs a studio.",
     "Inventory the liquid pantry and its social uses.",
     ["pantry_inventory", "sensory_palette"], ["pantry.drinks"],
     None),
    ("Describe the empty-shelf meal: the cupboard is nearly "
     "bare, people are coming or already here -- what do you "
     "make, from what, and what is the method of making do?",
     "State the substitution craft at its most exposed: the "
     "meal that proves the pantry's reasoning.",
     ["substitution_craft", "recipe_rendering"],
     ["pantry.empty_shelf"], None),
    ("What is the pantry's rule -- the stocking principle that "
     "decides everything on these shelves: how much, of what, "
     "for whom, against what day?",
     "Close the pantry chapter on its governing principle, "
     "stated as the cook states it.",
     ["pantry_inventory", "chapter_turn"], ["pantry.rule"], None),
]
Q["ch05"] = [
    ("Teach your knife work: the grip, the sharpening, the "
     "order of cutting, and what a toolmaker's grandson "
     "believes a knife is.",
     "Open the techniques chapter at the hand's first skill.",
     ["technique_lesson", "teaching_voice"],
     ["techniques.knife"], None),
    ("Teach your heat control: reading a pan, judging a fire "
     "or a burner by eye and ear, and what a furnace man's "
     "line knows about heat that a dial cannot say.",
     "Teach the Flames inheritance as method.",
     ["technique_lesson", "sensory_palette"],
     ["techniques.heat"], None),
    ("Teach your seasoning: salt in layers, tasting as you go, "
     "the order of acid and heat and fat -- and how you know "
     "a dish is seasoned when you cannot taste it one more "
     "time.",
     "Teach the palate's discipline as method.",
     ["technique_lesson", "sensory_palette"],
     ["techniques.seasoning"], None),
    ("Teach your stocks and gravies: what goes into the pot, "
     "what never does, the skimming and the patience, and the "
     "uses a stock is kept for.",
     "Teach the kitchen's liquid foundation, the Frozen "
     "patience in a pot.",
     ["technique_lesson", "preservation_method"],
     ["techniques.stocks"], None),
    ("Teach your frying: the oil's temperature and how you "
     "know it, the coating, the draining, and the iron pan's "
     "part in it.",
     "Teach the book's most dangerous technique whole.",
     ["technique_lesson", "teaching_voice"],
     ["techniques.frying"], None),
    ("Teach your beans and grains: the soak, the simmer, the "
     "rice's rest, and what patience does to each that hurry "
     "cannot.",
     "Teach the slow techniques the two lines agree on.",
     ["technique_lesson", "sensory_palette"],
     ["techniques.beans_grains"], None),
    ("Teach your eggs: the forms you hold as a cook's test -- "
     "the scramble, the fry, the boil -- and what each one "
     "proves about the hand that made it.",
     "Teach the examination dish of every kitchen in this "
     "book's lineage.",
     ["technique_lesson", "teaching_voice"], ["techniques.eggs"],
     None),
    ("Teach your baking measures: the biscuit and cornbread "
     "method at the level of technique -- the fat's cut, the "
     "liquid's temperature, the oven's readiness -- before "
     "the recipes render them whole in the next chapter.",
     "Teach the oven's discipline as transferable method.",
     ["technique_lesson", "teaching_voice"],
     ["techniques.baking"], None),
    ("Teach your pan sauces: the drippings, the deglaze, the "
     "finish -- the two-minute technique that decides whether "
     "a plain meat becomes a dish.",
     "Teach the finishing technique the studio nights run on.",
     ["technique_lesson", "sensory_palette"],
     ["techniques.pan_sauces"], None),
    ("Teach your repairs: a dish is failing at the stove -- "
     "too salt, too thin, broken, scorched at the edge. Take "
     "the failures in order and give the save for each, and "
     "the one failure you do not save and why.",
     "Close the techniques chapter with the family's doctrine "
     "as kitchen method: what can be fixed, fixed; and the "
     "honest limit named.",
     ["failure_and_repair", "chapter_turn"],
     ["techniques.repairs"], None),
]
Q["ch06"] = [
    ("Give the recipe whole: the Flames matriarch's skillet "
     "cornbread, as your line makes it -- ingredients, "
     "quantities, method, and the argument about it that your "
     "family has never settled.",
     "Open the signature dishes with the founding bread of "
     "the fire line.",
     ["recipe_rendering", "provenance_note"],
     ["recipes.cornbread"], None),
    ("Give the recipe whole: the Frozen matriarch's pot beans, "
     "as your line makes them -- the soak, the seasoning, the "
     "simmer's length, and what they are served with.",
     "Render the patience line's founding dish at full "
     "precision.",
     ["recipe_rendering", "provenance_note"], ["recipes.beans"],
     None),
    ("Give the recipe whole: the Flames patriarch's brisket, "
     "the refrigeration man's cut -- the rub, the fire, the "
     "hours, and how doneness is known without a thermometer "
     "of the modern kind.",
     "Render the Texas dish of the line's second generation.",
     ["recipe_rendering", "technique_lesson"],
     ["recipes.brisket"], None),
    ("Give the recipe whole: your mother's fried chicken -- "
     "the brine or the soak, the coating, the fat, the order "
     "of the pieces, and the test for done.",
     "Render the first teacher's standing dish, the one her "
     "table is known by.",
     ["recipe_rendering", "provenance_note"],
     ["recipes.fried_chicken"], None),
    ("Give the recipe whole: the gumbo that came into the "
     "Frozen kitchen with the patriarch's wife -- the roux's "
     "color and its time, the order of building, and what her "
     "people would say about this Texas version.",
     "Render the incoming line's great dish, the Frozen "
     "kitchen's adopted glory.",
     ["recipe_rendering", "provenance_note"], ["recipes.gumbo"],
     None),
    ("Give the recipe whole: your own session chili, the dish "
     "your studio runs on -- its meat, its heat, its hours, "
     "and why it is built to be eaten at midnight by people "
     "who are working.",
     "Render the cook's own signature, the dish the third "
     "place he feeds knows him by.",
     ["recipe_rendering", "sensory_palette"],
     ["recipes.session_chili"], None),
    ("Give the recipe whole: your midnight migas, or the egg "
     "dish of the studio's small hours -- its ingredients, its "
     "five-minute method, and the circumstances it was "
     "invented under.",
     "Render the cook's improvised signature, the "
     "empty-shelf craft become a standing dish.",
     ["recipe_rendering", "substitution_craft"],
     ["recipes.migas"], None),
    ("Give the recipe whole: the Frozen patriarch's potato "
     "soup, the toolmaker's plain dish -- its few ingredients, "
     "its exact method, and what its plainness declares.",
     "Render the doctrine's author at his plainest: the soup "
     "as a standard of sufficiency.",
     ["recipe_rendering", "provenance_note"],
     ["recipes.potato_soup"], None),
    ("Give the recipe whole: the peach cobbler of the Flames "
     "grandmother -- the fruit, the crust or batter, the "
     "sugar's measure, and the namesake who carries the "
     "recipe now.",
     "Render the front room's sweet dish and its line of "
     "custody.",
     ["recipe_rendering", "provenance_note"],
     ["recipes.cobbler"], None),
    ("Give the recipe whole: your mother's lemon chess pie, "
     "the church-social dish -- its filling, its crust, its "
     "occasion, and what that pie has witnessed in your "
     "family's history.",
     "Close the signature dishes on the pie that stood on "
     "the table where the two lines joined.",
     ["recipe_rendering", "occasion_frame"], ["recipes.chess_pie"],
     None),
]
# Chapter 7 -- Feeding the Studio. The studio-year question
# (q061) exists under the clean-proof rule: the Cold Room's
# founding year is a fact this book's middle chapters rely on,
# and no earlier pack's survey elicits it.
Q["ch07"] = [
    ("In what year did you found the Cold Room, your recording "
     "studio, and what did its first kitchen corner consist "
     "of? Begin the answer with the year.",
     "Fix the studio's founding year as fact, and open the "
     "studio's feeding with its first equipment.",
     ["kitchen_portrait", "provenance_note"],
     ["studio.founding"], FACT_STUDIO_YEAR),
    ("Describe feeding a session: who eats, when in the "
     "session's arc the meal falls, what a working musician "
     "needs from food at that hour, and what you have learned "
     "never to serve.",
     "Render the studio meal as a practiced form with its "
     "own rules.",
     ["table_scene", "occasion_frame"], ["studio.session_meals"],
     None),
    ("Describe the studio's coffee: the pot, the strength, the "
     "hours it covers, and what a fresh pot signals in a "
     "room of people deciding whether the night is over.",
     "Render the session's liquid clock.",
     ["sensory_palette", "kitchen_portrait"], ["studio.coffee"],
     None),
    ("Describe the studio's table itself: where people eat in "
     "a converted icehouse, what the room does to a meal, and "
     "the standing arrangement between the kitchen corner and "
     "the work.",
     "Portrait the third kitchen this book keeps: the "
     "icehouse's.",
     ["kitchen_portrait", "table_scene"], ["studio.table"], None),
    ("Describe the thin year's cooking: the season the "
     "sessions stopped and the repair work paid -- what you "
     "cooked then, at what cost, and what that year's kitchen "
     "taught the ones after it.",
     "Place the cook's own hard season inside his kitchen's "
     "history, plainly costed.",
     ["substitution_craft", "pantry_inventory"],
     ["studio.thin_year"], None),
    ("Describe feeding people on a session budget: the "
     "arithmetic of a meal for a room of musicians, where the "
     "money goes first, and what you refuse to economize on.",
     "Render the studio kitchen's economy under the Frozen "
     "accounts discipline.",
     ["pantry_inventory", "table_scene"], ["studio.budget"],
     None),
    ("Describe the fire year's cooking: the studio burned and "
     "was rebuilt over two years -- where did you cook in "
     "that time, what did the family feed the rebuilding, and "
     "what was the first meal in the rebuilt room?",
     "Render the catastrophe and the table's answer to it, "
     "in the doctrine's hardest exam.",
     ["occasion_frame", "failure_and_repair"], ["studio.fire"],
     None),
    ("Describe your sister's part in the studio's feeding: "
     "she kept its books as a teenager -- what else did she "
     "bring to its table, and what of the front room's "
     "teaching shows in how she feeds people?",
     "Give the next generation's keeper her place in the "
     "studio kitchen.",
     ["table_scene", "provenance_note"], ["studio.sister"], None),
    ("Name the studio's standing meal: the dish whose arrival "
     "means a session is going well -- who asks for it, how "
     "it is known the night has earned it, and what it has "
     "come to certify.",
     "Fix the studio's ceremonial dish and its meaning in "
     "the room.",
     ["occasion_frame", "sensory_palette"],
     ["studio.standing_meal"], None),
    ("What has the studio taught your kitchen, and your "
     "kitchen the studio: the transfers of discipline between "
     "the room that keeps performances and the room that "
     "keeps people fed?",
     "Close the studio chapter on the two practices' "
     "exchange, the book's hinge.",
     ["provenance_note", "chapter_turn"], ["studio.exchange"],
     None),
]
# Chapter 8 -- Occasions. The partner question (q071) exists
# under the clean-proof rule: the cook's wife and her table are
# facts the occasions chapters rely on, elicited here in terms.
Q["ch08"] = [
    ("What is your wife's full name, and what did she bring "
     "to your table -- her people's cooking, her own dishes, "
     "her standards? Begin the answer with her full name.",
     "Bring the partner into the cookbook as a third table's "
     "joining, and fix the fact.",
     ["table_scene", "provenance_note"], ["people.partner"],
     FACT_PARTNER),
    ("Describe your wedding feast: the year, the place, who "
     "cooked, what was served, and what the two families made "
     "of eating together as one family for the first time.",
     "Render the joining's meal as the book's central "
     "occasion.",
     ["occasion_frame", "table_scene"], ["occasions.wedding"],
     None),
    ("Describe Christmas at the joined table: the room, the "
     "board the table is extended with, who comes from how "
     "far, and the dishes without which it is not Christmas "
     "in your family.",
     "Render the year's great gathering at full table.",
     ["occasion_frame", "table_scene"], ["occasions.christmas"],
     None),
    ("Describe the church socials: the church where your "
     "parents met, your mother's place at its organ and its "
     "kitchen, and what a congregation's table asks of its "
     "cooks that a family's does not.",
     "Render the public table where the joining began.",
     ["occasion_frame", "table_scene"], ["occasions.church"],
     None),
    ("Describe feeding grief: your family's funeral food -- "
     "who cooks when a family cannot, what is brought, what "
     "is eaten and what is only present, and the rules of "
     "that table.",
     "Render the hardest occasion's customs plainly.",
     ["occasion_frame", "table_scene"], ["occasions.funerals"],
     None),
    ("Describe feeding the branch: when the Chicago line "
     "comes down, or your people go up -- the traveler's "
     "meal, the first night's table, and what distance does "
     "to a family's cooking for its own.",
     "Render the reunion table across the family's spread.",
     ["occasion_frame", "table_scene"], ["occasions.branch"],
     None),
    ("Describe the name-day and birthday table: in a family "
     "that names its children for stones, how is a birthday "
     "kept -- the cake, the dish the named one asks for, the "
     "namesake's place in it?",
     "Render the naming law's sweet expression at the table.",
     ["occasion_frame", "sensory_palette"],
     ["occasions.birthdays"], None),
    ("Describe your wife's family's table: her father's and "
     "mother's household, its work and its dishes, and what "
     "eating there taught the cook who married in.",
     "Give the incoming line's table its own standing, as "
     "the earlier chapters gave the two lines'.",
     ["kitchen_portrait", "provenance_note"],
     ["occasions.verano_table"], None),
    ("Describe feeding the stranger: the unplanned guest, "
     "the musician far from home, the neighbour in a bad "
     "week -- your household's rule for the person who was "
     "not expected, and where the rule came from.",
     "State the table's open door as doctrine and practice.",
     ["table_scene", "provenance_note"], ["occasions.strangers"],
     None),
    ("What is the occasions' rule: what does your family "
     "believe a feast is for, beneath the dishes -- and what "
     "does the record of its gatherings, read as menus, say "
     "the family was?",
     "Close the occasions chapter on the feast's meaning, "
     "tested against the family's own archive.",
     ["occasion_frame", "chapter_turn"], ["occasions.rule"],
     None),
]
Q["ch09"] = [
    ("Give your pickling and canning whole: what you put up, "
     "the jars, the brine or syrup, the processing, and how "
     "a jar's soundness is known.",
     "Open the keeping chapter with the shelf's oldest "
     "method, at recipe precision.",
     ["preservation_method", "recipe_rendering"],
     ["keeping.pickling"], None),
    ("Describe your freezer discipline: what is frozen, in "
     "what portions, labelled how, and the inventory rule "
     "that keeps a freezer from becoming an archive of the "
     "forgotten.",
     "Render the cold archive under the accounts standard.",
     ["preservation_method", "pantry_inventory"],
     ["keeping.freezer"], None),
    ("Describe your curing and smoking: the brisket's kin -- "
     "what you cure, the salt's work, the smoke's, and what "
     "the refrigeration man's line knows about cold and time "
     "that it teaches the rest of the family.",
     "Render the Flames patriarch's trade as a keeping "
     "method.",
     ["preservation_method", "technique_lesson"],
     ["keeping.curing"], None),
    ("Describe your leftovers doctrine: the second day's "
     "rules -- what improves, what transforms, what is never "
     "kept -- and the dish in your kitchen that exists only "
     "as a leftover's second life.",
     "State the keeping of the cooked as the doctrine's "
     "daily form.",
     ["preservation_method", "substitution_craft"],
     ["keeping.leftovers"], None),
    ("Describe your scrap economy: the bones, the ends, the "
     "peelings -- what is saved for stock, what for the "
     "animals or the garden, and the point at which keeping "
     "becomes hoarding, as your lines draw it.",
     "Render the waste line honestly: where keeping stops.",
     ["preservation_method", "pantry_inventory"],
     ["keeping.scraps"], None),
    ("Describe keeping under pressure: the thinnest season's "
     "pantry, when the sessions stopped -- what the keeping "
     "made possible, what it could not do, and what the "
     "family's doctrine looked like at an empty shelf.",
     "Return the keeping to its hardest test, in the cook's "
     "own years.",
     ["preservation_method", "substitution_craft"],
     ["keeping.pressure"], None),
    ("Describe what keeping cannot save: the spoilage you "
     "have thrown out and what it taught, the jar that "
     "failed, and the honest limits your lines teach about "
     "holding on.",
     "Name the keeping's limit as plainly as its methods.",
     ["failure_and_repair", "preservation_method"],
     ["keeping.limits"], None),
    ("Describe your recipe record: where your recipes live "
     "now -- the cards, the book, the session logs' kitchen "
     "pages -- whose handwriting surrounds yours, and the "
     "rule by which a dish earns being written down.",
     "Bring the two lines' archives into the kitchen's own "
     "record.",
     ["provenance_note", "pantry_inventory"],
     ["records.recipe_record"], None),
    ("Name the kitchen's heirlooms: the skillet, the ledger, "
     "the tools and vessels that carry the lines' memory -- "
     "where each is now, and what each testifies about the "
     "hands that kept it.",
     "Let the keeping chapter's objects testify.",
     ["provenance_note", "kitchen_portrait"],
     ["motifs.kitchen_heirlooms"], None),
    ("Who keeps your kitchen now -- its stock, its record, "
     "its standards -- beside yourself, and how was that "
     "keeper chosen or fallen to?",
     "Fix the kitchen's present custody and point the book "
     "at its final chapter.",
     ["kitchen_portrait", "chapter_turn"], ["keeping.keeper"],
     None),
]
Q["ch10"] = [
    ("Describe your teaching: the young cooks you have "
     "taught -- at your counter, at the studio, at your "
     "sister's table -- what you teach first, and what you "
     "let them ruin.",
     "Open the final chapter with the hand-on of the craft.",
     ["teaching_voice", "table_scene"], ["teaching.young"],
     None),
    ("Describe teaching at a distance: the branch's young in "
     "Chicago learning this family's dishes from another "
     "city -- the calls, the written recipes, what survives "
     "the distance and what does not.",
     "Render the handing-on across the family's spread.",
     ["teaching_voice", "provenance_note"],
     ["teaching.distance"], None),
    ("Name the first dish you teach a beginner, and teach it "
     "here: why this one, what it proves, and the order of "
     "its lessons.",
     "Give the book's entry point for the cook it hopes to "
     "make.",
     ["teaching_voice", "recipe_rendering"],
     ["teaching.first_dish"], None),
    ("State the family's doctrine one last time, as the "
     "table has taught it to you: what it meant at the "
     "furnace and the bench, what it means at your stove, "
     "and what you believe it will ask of the next cook.",
     "Give the doctrine its fullest statement, carrying "
     "every kitchen the book has passed through, as the "
     "respondent's own answer.",
     ["provenance_note", "teaching_voice"],
     ["food.doctrine_final"], None),
    ("Describe the kitchen's standing argument: the method "
     "or dish your two lines will never agree on -- each "
     "side's case, honestly given, and your own verdict, if "
     "you dare one.",
     "Name the family's continuing fault line at the stove, "
     "without flinching.",
     ["table_scene", "provenance_note"], ["teaching.argument"],
     None),
    ("What do your recipes and records still get wrong, or "
     "leave out, that you want corrected while you can "
     "correct it -- the measure misremembered, the dish "
     "attributed to the wrong grandmother?",
     "Let the cook amend his archive in his own voice.",
     ["provenance_note", "failure_and_repair"],
     ["records.corrections"], None),
    ("What is this cookbook for, at the end: what does its "
     "whole table, told whole, show your family was doing "
     "in its kitchens -- and what should the reader's "
     "kitchen do differently for this book existing?",
     "Test the book's declared purpose against its full "
     "record.",
     ["provenance_note", "teaching_voice"], ["book.purpose_final"],
     None),
    ("What plain advice do you give a young cook, beneath "
     "the doctrine -- the working instructions that fit on "
     "one card, every line of it paid for?",
     "Translate the inheritance into instructions a "
     "beginner could carry.",
     ["teaching_voice", "pantry_inventory"], ["teaching.advice"],
     None),
    ("What dish have you not yet learned -- the one still "
     "ahead of you, whose cook is gone or distant -- and "
     "what is your plan, if any, for its recovery?",
     "Name the kitchen's open account honestly.",
     ["provenance_note", "chapter_turn"], ["teaching.unlearned"],
     None),
    ("End the book: what is the single dish, or the single "
     "fact about your family's table, that should outlast "
     "every recipe in it?",
     "Close on the dish that survives the telling.",
     ["provenance_note", "chapter_turn"], ["book.final_dish"],
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
        "genre": "cookbook",
        "version": "1.0.0",
        "framework": FRAMEWORK,
        "chapters": [
            {"id": cid, "title": title, "act": act}
            for cid, title, act in CHAPTERS
        ],
        "questions": questions,
    }
    out = Path(__file__).resolve().parent.parent / "packs" / "cookbook.json"
    out.write_text(json.dumps(pack, indent=1), encoding="utf-8")
    print(f"wrote {out}: {len(questions)} questions, "
          f"{len(CHAPTERS)} chapters")


if __name__ == "__main__":
    main()
