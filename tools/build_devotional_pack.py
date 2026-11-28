#!/usr/bin/env python3
"""Builds packs/devotional.json: the devotional / inspirational
pack (100 questions).

Each question is authored as a tuple:
    (prompt, narrative_job, [device_ids], [bible_keys], fact_or_None)
and expanded here with its chapter and generated position string.

The pack's defining difference from the packs before it is its
unit: not a life (memoir, biography), not a lineage (family
history), not a practice rendered as recipes (cookbook), and not
the single story (short story collection), but the single day
kept -- one reflective entry per answer, keyed to the
respondent's belief and experience, modular as the days are
modular, the whole held together by the keeper and the practice
rather than by plot. The roadmap's feasibility note for this
genre is the design: short reflective entries keyed to answers
about belief and experience; modular pages; voice carries it.

The pack is religion-agnostic in structure, on the same terms
the closing genre (testimony) will use at full length: the
questions ask about the respondent's own practices, sources of
strength, gratitude, hardship, hope, and daily disciplines in
the respondent's own terms. No question presumes a tradition,
names a scripture or a rite, or corrects the respondent's
vocabulary into another tradition's; what the respondent holds
sacred enters the book only in the words the respondent uses
for it, and what happened is kept distinct from what he
understands it to mean.

Clean-proof rule (adopted 2026-11-24): if a fact had to be
obtained by asking the author outside the survey, the survey
failed to ask it, and the question belongs in the pack. The
rule's identity corollary: who the main character is is itself
respondent data, elicited by an explicit identity question
early in the survey (q003, in this genre's form: who is the
main character of this devotional, the keeper whose practice
these entries record), never a fact the build supplies; in the
demonstration answers that question is answered from the
canonical record, and the story bible's subject_name fact
traces to it under the traceability gate.

Pack v1.1.0 (the corrected-edition revision, after the first
book; see DEFECTS.md, V11--V14): three changes, each the
survey-level encoding of an engine-level fix. (1) The identity
question at q003 now also asks whether the keeper is a man or
a woman, and the question declares a second typed fact,
subject_gender, beside subject_name: the first book's largest
defect was a narrator cast as a wife, and the survey had never
asked the subject's gender at all -- the clean-proof rule
applied to the fact the build most needed. The recorded
gender keys the engine's spouse-term screen and is stated in
every page prompt. (2) The return device is renamed in
display ("The kept sentence") and its instruction rewritten,
and the global instructions no longer speak of "the book's
anchor": the first book's prose repeated the machinery's
vocabulary on 68 of 100 pages because the prompts supplied
it, so the pack stops supplying it. (3) Nothing else changes:
the same 100 questions, chapters, and fact spine otherwise.

Refrain default: ON, chosen deliberately -- the opposite call
from the story collection, for the opposite reason. A
devotional is refrain-shaped by genre: the practice is the
same words returned to daily, and the return is the point.
The refrain parameter is recurrence with development, and a
kept practice is exactly that: the anchor sentence meets a
new day and is changed by what the day has done since its
last statement -- the fire, the rebuilding, the griefs, the
gratitudes all re-read it. The anchor mechanism takes the
first page's opening sentences as the theme; this pack's
first chapter fixes the keeper and his two lines as facts,
and the respondent's anchor sentence is planted as answer
content at q010 and returned to across the chapters as
content, so the theme the mechanism carries is the keeping
itself. The development check is run and reported as it
falls: if the recurrences do not develop, that is recorded
as a failed check, not edited away. The verbatim guard
applies in full, as in every pack.
"""

import json
from pathlib import Path

FRAMEWORK = {
    "voice": (
        "First-person devotional voice: the respondent at his "
        "practice, plain and concrete, speaking of belief the "
        "way he speaks of work -- by what the hands do, what "
        "the words are, what the day required. An entry must be "
        "an entry whole: one matter taken up, the practice "
        "brought to bear on it, and the entry's own honest "
        "close -- not a sermon, not a summary, and never a "
        "lesson the answer does not teach. What he holds "
        "sacred is stated only in his own terms, and what "
        "happened is kept distinct from what he understands "
        "it to mean."
    ),
    "pov": "first person",
    "refrain": True,
    "tense": "present tense for the practice itself -- the day "
             "being kept -- past tense for the remembered "
             "events the practice carries",
    "page_target_words": 250,
    "global_instructions": (
        "Transform the respondent's answers into a devotional "
        "book in the first person: one reflective entry per "
        "answer, each standing on its own and each returning, "
        "as the day's practice returns, to the sentence the "
        "practice keeps. "
        "The book's continuity is the keeper and his practice "
        "-- the respondent, his two family lines (the Flames "
        "line of his mother, the Frozen line of his father), "
        "the front room, the repair bench, the Cold Room "
        "studio, and the daily disciplines the answers "
        "describe -- not a plot carried between entries. Never "
        "contradict the story bible or the fixed facts. Do "
        "not invent named people, places, or dates that are "
        "not in the supplied material. The respondent's "
        "belief is rendered only in his own terms: name no "
        "religion, scripture, rite, or name for the divine "
        "that the answers do not themselves use, and never "
        "translate his vocabulary into another tradition's. "
        "Keep what happened distinct from what he understands "
        "it to mean. Where an answer gives an event, render it "
        "whole and in order; where it gives a discipline, "
        "render the discipline as it is actually performed -- "
        "the place, the hour, the words, the hands. Do not "
        "append consolation or a moral the answer does not "
        "state. Where the material is thin, expand by "
        "rendering its documented implications as scene and "
        "reflection, not by fabricating events."
    ),
    "devices": {
        "anchor_return": {
            "name": "The kept sentence",
            "instruction": "Come back to the sentence the "
                           "practice keeps -- the one first "
                           "said at the book's opening -- as "
                           "the days between have changed "
                           "it: let what has happened since "
                           "live inside it, in fresh wording "
                           "that means something the first "
                           "saying could not have meant.",
        },
        "practice_rendering": {
            "name": "Practice rendering",
            "instruction": "Render a discipline as it is "
                           "actually performed, in order: the "
                           "place, the hour, the posture, the "
                           "words said or withheld, what the "
                           "hands do. A practice page should "
                           "let a reader perform the practice "
                           "from the page alone.",
        },
        "moment_opening": {
            "name": "Moment opening",
            "instruction": "Open inside one moment of the "
                           "day: the light, the sound in the "
                           "room, the object in hand -- before "
                           "any reflection on what the moment "
                           "means.",
        },
        "gratitude_naming": {
            "name": "Gratitude naming",
            "instruction": "Name the gifts one by one, "
                           "concretely -- the thing itself, "
                           "not the feeling about it. Thanks in "
                           "this book is counting, not mood.",
        },
        "hardship_witness": {
            "name": "Hardship witness",
            "instruction": "Render a hard season plainly: "
                           "what it cost, what the practice "
                           "did, and what it did not do. No "
                           "easy consolation, no suffering "
                           "redeemed before its time.",
        },
        "intercession": {
            "name": "Intercession",
            "instruction": "Hold another person in the "
                           "practice: who they are, what is "
                           "carried for them and in what "
                           "words, and what the carrying "
                           "changes in the keeper.",
        },
        "silence_rendering": {
            "name": "Silence rendering",
            "instruction": "Render stillness: what is not "
                           "said, how long the quiet lasts, "
                           "what it is for, and what it leaves "
                           "room for. The silence is the event.",
        },
        "listening": {
            "name": "Listening",
            "instruction": "Render attention for guidance in "
                           "the respondent's own terms: what "
                           "was heard or noticed, and what he "
                           "understands it to mean -- the two "
                           "kept distinct on the page.",
        },
        "day_examen": {
            "name": "Day examen",
            "instruction": "Review the day honestly: where "
                           "the practice was kept, where it "
                           "failed, and what is handed over at "
                           "the day's end. Nothing varnished.",
        },
        "kept_object": {
            "name": "Kept object",
            "instruction": "Hang the entry on the practice's "
                           "object -- the book of names, the "
                           "day book, the bench, the cup -- "
                           "and let the object's state be the "
                           "entry's clock: what is opened, "
                           "entered, carried, or closed, and "
                           "when.",
        },
        "place_portrait": {
            "name": "Place portrait",
            "instruction": "Render one place of the practice "
                           "whole: its furniture, its light, "
                           "its working sounds, who stands "
                           "where in it. One page should leave "
                           "one place standing as a place.",
        },
        "sensory_palette": {
            "name": "Sensory palette",
            "instruction": "Render the scene through sound "
                           "first -- this keeper is an "
                           "engineer of sound -- then sight, "
                           "smell, and touch: the room's tone "
                           "before anyone speaks.",
        },
        "sending": {
            "name": "Sending",
            "instruction": "Close the entry by handing its "
                           "matter onward: a word of release, "
                           "resolve, or thanks in the "
                           "respondent's own terms. No sermon "
                           "after the sending.",
        },
    },
}

CHAPTERS = [
    ("ch01", "The Keeper", "Act I: The Practice"),
    ("ch02", "First Light", "Act I: The Practice"),
    ("ch03", "The Kept Table", "Act I: The Practice"),
    ("ch04", "Work as Practice", "Act II: The Day"),
    ("ch05", "The Hard Hours", "Act II: The Day"),
    ("ch06", "Other People", "Act II: The Day"),
    ("ch07", "Gratitude Counted", "Act III: The Turning"),
    ("ch08", "Silence and Listening", "Act III: The Turning"),
    ("ch09", "The Night Watch", "Act III: The Turning"),
    ("ch10", "The Practice Kept", "Act IV: The Return"),
]

Q: dict[str, list] = {}

# Chapter 1 -- The Keeper. The fact spine of the book: both
# lines' names, the keeper himself, his parents, his birth, his
# sister, his partner, fixed as typed facts before any entry
# leans on them -- and the practice's anchor sentence planted
# as content at q010.
Q["ch01"] = [
    ("What is the family name of your mother's line -- the "
     "line whose keeping you first saw practiced? Begin the "
     "answer with the name.",
     "Open the book by naming the mother's line, the first "
     "school of the keeper's practice, and fix the fact.",
     ["moment_opening", "place_portrait"],
     ["family.flames_name"],
     {"slot": "flames_line_name", "kind": "person_name",
      "triggers": ["the Flames family name",
                   "the Flames line's name"]}),
    ("What is the family name of your father's line -- the "
     "line that taught you a kept thing is a thing entered "
     "honestly in a book? Begin the answer with the name.",
     "Name the father's line, the second school of the "
     "practice, and fix the fact.",
     ["moment_opening", "place_portrait"],
     ["family.frozen_name"],
     {"slot": "frozen_line_name", "kind": "person_name",
      "triggers": ["the Frozen family name",
                   "the Frozen line's name"]}),
    ("Who is the main character of this devotional -- the "
     "keeper whose practice these entries record, who keeps "
     "it and stands inside every entry? Give that keeper's "
     "full name, say whether the keeper is a man or a "
     "woman, and say how the name comes from the two "
     "lines. Begin the answer with the full name.",
     "Establish the book's central identity as respondent "
     "data: the main character is the keeper the respondent "
     "names here, and the name and the recorded gender are "
     "fixed as facts from this answer alone.",
     ["practice_rendering", "anchor_return"],
     ["respondent.identity"],
     {"slot": "subject_name", "kind": "person_name",
      "triggers": ["the respondent"]}),
    ("What is your mother's full name, and what is her place "
     "in your practice -- what did she teach you about how a "
     "day is kept, and what of hers do you still do every "
     "day? Begin the answer with her full name.",
     "Name the first teacher of the practice directly, and "
     "fix the fact.",
     ["intercession", "place_portrait"], ["people.mother"],
     {"slot": "mother_name", "kind": "person_name",
      "triggers": ["my mother", "the respondent's mother"]}),
    ("What is your father's full name, and what is his place "
     "in your practice -- what did the day book and the bench "
     "teach you about what a kept day must contain? Begin "
     "the answer with his full name.",
     "Name the second teacher of the practice directly, and "
     "fix the fact.",
     ["intercession", "kept_object"], ["people.father"],
     {"slot": "father_name", "kind": "person_name",
      "triggers": ["my father", "the respondent's father"]}),
    ("In what year were you born, and what keepings were "
     "already old in the house when you arrived? Begin the "
     "answer with the year.",
     "Fix the keeper's birth year as fact, set inside the "
     "house's stock of practices at his arrival.",
     ["moment_opening", "anchor_return"],
     ["respondent.birth"],
     {"slot": "birth_year", "kind": "year",
      "triggers": ["I was born"]}),
    ("In what place were you born, and what does that place "
     "sound like at the hour you now keep? Begin the answer "
     "with the place.",
     "Fix the keeper's birthplace as fact and as his first "
     "soundscape.",
     ["place_portrait", "sensory_palette"],
     ["places.birthplace"],
     {"slot": "birthplace", "kind": "place_name",
      "triggers": ["I was born in"]}),
    ("What is your sister's full name, and what is her place "
     "in the keeping -- what does she keep that you do not, "
     "and how does her keeping differ from yours? Begin the "
     "answer with her full name.",
     "Name the book's second keeper, and fix the fact.",
     ["intercession", "anchor_return"], ["people.sister"],
     {"slot": "sister_name", "kind": "person_name",
      "triggers": ["my sister", "the respondent's sister"]}),
    ("What is your wife's full name, and what is her place "
     "in the keeping -- she photographs the practice's "
     "rooms: what does her camera keep that your entries "
     "miss? Begin the answer with her full name.",
     "Name the practice's witness, and fix the fact.",
     ["intercession", "kept_object"], ["people.partner"],
     {"slot": "partner_name", "kind": "person_name",
      "triggers": ["my wife", "the respondent's wife"]}),
    ("What sentence does your practice return to -- the "
     "saying your family hands down that you have made the "
     "anchor of your own keeping -- which line brought it, "
     "and how do you actually use it: when is it said, and "
     "what is it for?",
     "Plant the anchor: the family's doctrine stated as "
     "this book's law of keeping, in the respondent's own "
     "words, as content the entries themselves return to.",
     ["anchor_return", "practice_rendering"],
     ["practice.anchor"], None),
]

# Chapter 2 -- First Light. The morning practice rendered
# discipline by discipline, including its failures and its
# inherited forms, ending in the chapter's own statement of
# what the morning is for.
Q["ch02"] = [
    ("Describe the first moment of your kept day: what you "
     "do before your feet touch the floor, the first words "
     "if there are words, and what the moment is for.",
     "Open the practice at its first act, before the day "
     "begins.",
     ["moment_opening", "practice_rendering"],
     ["practice.first_moment"], None),
    ("Describe the table in the dark: the book of your "
     "family's names opened to its first pages, what you "
     "read there and in what order, and what reading names "
     "does that reading a lesson would not.",
     "Render the morning's central act: the names kept by "
     "being read.",
     ["kept_object", "practice_rendering"],
     ["practice.names"], None),
    ("Describe saying the anchor aloud: where you stand, "
     "how it is spoken, what has to be true of the room, "
     "and what the saying does that thinking it would not.",
     "Render the anchor as a performed act, not a thought.",
     ["practice_rendering", "anchor_return"],
     ["practice.anchor_spoken"], None),
    ("Describe the silence before the house wakes: how long "
     "it lasts, what fills it, what you are not allowed to "
     "do inside it, and what it is for.",
     "Render the morning's stillness as a discipline with "
     "rules.",
     ["silence_rendering", "sensory_palette"],
     ["practice.morning_silence"], None),
    ("Describe the coffee and the window: the day's weather "
     "received standing up, what you look for first outside, "
     "and what the looking settles before work.",
     "Render the day's first receiving: weather as given, "
     "not chosen.",
     ["moment_opening", "sensory_palette"],
     ["practice.window"], None),
    ("Describe a morning the practice failed: the "
     "oversleeping or the emergency, what the day did "
     "without its keeping, and what you learned from the "
     "day going unkept.",
     "Render the discipline by its absence: a failure kept "
     "honestly.",
     ["day_examen", "hardship_witness"],
     ["practice.failed_morning"], None),
    ("Describe your mother's morning as you saw it from a "
     "child's doorway: her hour, her sounds, what she did "
     "before the house was fed, and what of it you "
     "understood only later.",
     "Render the inherited morning, witnessed before it "
     "was understood.",
     ["moment_opening", "place_portrait"],
     ["practice.mothers_morning"], None),
    ("Describe your father's morning: the shop opened in "
     "the dark, the bench uncovered, the first entry made "
     "-- what did his keeping look like from outside it?",
     "Render the second inherited morning, at the bench.",
     ["kept_object", "place_portrait"],
     ["practice.fathers_morning"], None),
    ("Describe the practice on the road: a morning kept in "
     "a strange room, without its table or its book -- what "
     "you carried, what you did instead, and what the "
     "makeshift taught you about the furniture.",
     "Render the practice portable: what survives the "
     "loss of its setting.",
     ["practice_rendering", "place_portrait"],
     ["practice.road_morning"], None),
    ("What is the morning for, at the end of this chapter: "
     "state what the first hour of a kept day is meant to "
     "accomplish, and what a day is that begins any other "
     "way.",
     "State the chapter's doctrine in the respondent's "
     "own terms.",
     ["anchor_return", "sending"], ["practice.morning_why"],
     None),
]

# Chapter 3 -- The Kept Table. Gratitude and provision at
# the table the mother's line keeps: the words before eating,
# the rule that everybody is fed, the empty chair, the fast,
# and the table's own doctrine.
Q["ch03"] = [
    ("Describe the words before eating in your house: who "
     "says them, their shape and length, the rule about who "
     "is named, and what happens on the nights nobody wants "
     "to say them.",
     "Render the table's spoken keeping, with its rules.",
     ["practice_rendering", "gratitude_naming"],
     ["table.words"], None),
    ("Describe your mother's rule that everybody is fed: "
     "where it came from in her line, how it runs the "
     "kitchen in practice, and what it has cost and bought "
     "over the years.",
     "Render feeding as the house's first devotion.",
     ["gratitude_naming", "place_portrait"],
     ["table.everybody_fed"], None),
    ("Describe gratitude named at supper: each person at "
     "the table names one thing, in turn -- and the hardest "
     "night you remember for naming one, and what got named "
     "in the end.",
     "Render thanks as a counted discipline at the table.",
     ["gratitude_naming", "moment_opening"],
     ["table.naming"], None),
    ("Describe the empty chair: who is missing from the "
     "table in this season of the family's life, how the "
     "table keeps them anyway, and what is not done about "
     "the chair.",
     "Render absence kept at the table, without remedy.",
     ["kept_object", "hardship_witness"], ["table.chair"],
     None),
    ("Describe feeding a stranger: the pupil, the customer, "
     "or the one who came to the counter hungry -- who was "
     "fed at your table or your mother's, and what the "
     "feeding settled that words had not.",
     "Render the table extended past the family.",
     ["intercession", "place_portrait"],
     ["table.stranger"], None),
    ("Describe the fast you keep: the going-without you "
     "practice on purpose -- what is given up, how often, "
     "and what the hunger is for.",
     "Render the deliberate empty place in the keeping.",
     ["practice_rendering", "silence_rendering"],
     ["table.fast"], None),
    ("Describe the meal where a quarrel ended: who had been "
     "at odds, what was cooked, who sat down first, and "
     "what the eating did that the talking had not managed.",
     "Render reconciliation as a table act.",
     ["moment_opening", "intercession"], ["table.quarrel"],
     None),
    ("Describe cooking as practice: your hands in the "
     "work, what the kitchen's disciplines are, and what "
     "the stove teaches that the bench and the board do "
     "not.",
     "Render the kitchen as a school of the same keeping.",
     ["practice_rendering", "sensory_palette"],
     ["table.cooking"], None),
    ("Describe the table inside the studio: the kitchen "
     "corner, who eats there and when, and what a session "
     "fed is that a session unfed is not.",
     "Render the kept table carried into the workplace.",
     ["place_portrait", "gratitude_naming"],
     ["table.studio"], None),
    ("What is the table for, at the end of this chapter: "
     "state what a kept table accomplishes in a house, and "
     "what a house is whose table is only furniture.",
     "State the chapter's doctrine in the respondent's "
     "own terms.",
     ["anchor_return", "sending"], ["table.why"], None),
]

# Chapter 4 -- Work as Practice. The working day kept: the
# studio's founding fixed as fact at the chapter's head, then
# the disciplines of the bench and the board -- opening,
# pause, honest entries, rest -- and the chapter's doctrine.
Q["ch04"] = [
    ("In what year did you found the Cold Room, and what "
     "keeping did you carry into the room on its first day "
     "-- what was done before any work was done? Begin the "
     "answer with the year.",
     "Fix the studio's founding year as fact, and open "
     "its working keeping with the rite of its first day.",
     ["moment_opening", "place_portrait"],
     ["studio.founding"],
     {"slot": "studio_year", "kind": "year",
      "triggers": ["I founded the Cold Room in",
                   "the Cold Room opened in"]}),
    ("Describe opening the workplace: the first acts of "
     "the working day in the studio and at the bench, in "
     "order, and what makes them a keeping rather than a "
     "routine.",
     "Render the workday's threshold as a practice.",
     ["practice_rendering", "kept_object"],
     ["work.opening"], None),
    ("Describe the midday pause: the radio off, the board "
     "quiet, the length of one song with nothing done in "
     "it -- what the pause is for, and what breaks when it "
     "is skipped.",
     "Render the kept stop inside the working day.",
     ["silence_rendering", "practice_rendering"],
     ["work.pause"], None),
    ("Describe what your hands know: the knowledge in the "
     "bench work and the board work that your words do not "
     "have, and why work you can do with your hands is the "
     "keeping you can perform on the days you cannot "
     "perform any other.",
     "Render work as the practice of last resort, honestly "
     "kept.",
     ["practice_rendering", "hardship_witness"],
     ["work.hands"], None),
    ("Describe the honest entry at work: the day book "
     "habit applied to the studio log -- what gets entered "
     "when a session fails, and why the failure is written "
     "in the same hand as the success.",
     "Render record-keeping as a moral discipline.",
     ["kept_object", "day_examen"], ["work.honest_entry"],
     None),
    ("Describe a repair done as a carrying: a stranger's "
     "radio or guitar fixed in the knowledge of what it "
     "meant to them -- what you knew of their trouble, "
     "what the fixing held, and what you charged.",
     "Render the bench's work as intercession by hand.",
     ["intercession", "kept_object"], ["work.repair_carried"],
     None),
    ("Describe the session held for someone grieving: who "
     "booked it, what was recorded, how the room's keeping "
     "changed for them, and what you did from the board "
     "that was not engineering.",
     "Render the studio as a place where grief books "
     "time, and the keeper as witness.",
     ["intercession", "place_portrait"],
     ["work.grief_session"], None),
    ("Describe money under the practice: how a price is set "
     "honestly, the repair you did not charge for and why, "
     "and what the day book says about both.",
     "Render the shop's economy under the keeping.",
     ["day_examen", "kept_object"], ["work.money"], None),
    ("Describe the kept day away from work: the one day in "
     "seven the bench stays covered and the studio dark -- "
     "what is done instead, what is refused, and what the "
     "refusal protects.",
     "Render rest as a discipline with edges.",
     ["practice_rendering", "silence_rendering"],
     ["work.rest_day"], None),
    ("What is work for, at the end of this chapter: state "
     "what kept work accomplishes that unkept work does "
     "not, and what a trade is that is only a living.",
     "State the chapter's doctrine in the respondent's "
     "own terms.",
     ["anchor_return", "sending"], ["work.why"], None),
]

# Chapter 5 -- The Hard Hours. The practice under load: the
# fire and the rebuilding, doubt, the dead of both lines,
# the unhealed quarrel, the body's limits -- and the
# chapter's honest statement of what hardship is and is
# not for.
Q["ch05"] = [
    ("Describe the night of the fire as a keeping: where "
     "you stood when it was over, what words were said or "
     "could not be said, and what the practice did in the "
     "first hour of the ruin.",
     "Open the hard hours at the ruin itself, whole and "
     "in order.",
     ["hardship_witness", "moment_opening"],
     ["hardship.fire_night"], None),
    ("Describe the morning after the fire: the first "
     "person who came, what was done before anything was "
     "said, and the first kept act of the rebuilding "
     "whether you knew it then or not.",
     "Render help and keeping arriving in their true "
     "order: hands before words.",
     ["hardship_witness", "intercession"],
     ["hardship.morning_after"], None),
    ("Describe the practice thinned: across the two years "
     "of rebuilding, what the keeping shrank to on the "
     "worst days -- the one sentence, the one act -- and "
     "what it means that it shrank instead of stopping.",
     "Render the discipline at its minimum viable form.",
     ["hardship_witness", "anchor_return"],
     ["hardship.thinned"], None),
    ("Describe the season of doubt: when the words felt "
     "empty and the practice felt like nothing -- how long "
     "it lasted, what you did inside it, and what you do "
     "not claim about how it ended.",
     "Render doubt without varnish and without a tidy "
     "exit.",
     ["hardship_witness", "silence_rendering"],
     ["hardship.doubt"], None),
    ("Describe keeping the dead of your father's line: "
     "your grandfather Jasper, who made the family's "
     "sentence -- how he is held in the practice now, what "
     "is asked for the dead, and what is simply remembered.",
     "Render grief for the doctrine's author, in the "
     "practice he authored.",
     ["intercession", "kept_object"], ["hardship.jasper"],
     None),
    ("Describe keeping the dead of your mother's line: "
     "your grandmother Jet, who began the book of names "
     "the year you were not yet born to read -- how a "
     "keeper holds someone he knows only through her own "
     "keeping.",
     "Render grief at one remove: the matriarch known "
     "through her record.",
     ["intercession", "kept_object"], ["hardship.jet"],
     None),
    ("Describe holding the one who will not come back: "
     "your great-uncle Zircon, estranged from the family "
     "since before you were born -- what the practice "
     "requires toward a man who refuses the table, and "
     "what it does not require.",
     "Render the keeping extended to the refuser, with "
     "its limits stated.",
     ["intercession", "hardship_witness"],
     ["hardship.zircon"], None),
    ("Describe the body's limit: the season your hands "
     "and your strength gave out under the rebuilding -- "
     "what the practice does when the keeper himself is "
     "the broken thing, and who kept it for you then.",
     "Render the keeper as the kept, in the body's worst "
     "season.",
     ["hardship_witness", "intercession"],
     ["hardship.body"], None),
    ("Describe sitting up with the sick: a night you kept "
     "watch beside someone ill in your family -- the room, "
     "the hours, what was said at the worst of it, and "
     "what the watching was for.",
     "Render the night watch in its original form: beside "
     "a bed, not a book.",
     ["moment_opening", "silence_rendering"],
     ["hardship.sick_watch"], None),
    ("What is hardship for, at the end of this chapter -- "
     "and what is it not for: state honestly what the hard "
     "hours are claimed to do in a kept life, and the "
     "claim you refuse to make for them.",
     "State the chapter's doctrine, including its "
     "refusal, in the respondent's own terms.",
     ["anchor_return", "sending"], ["hardship.why"], None),
]

# Chapter 6 -- Other People. The practice turned outward:
# each of the keeper's people held in turn, the stranger,
# the wrongdoer, the hardest case, being held oneself, the
# gathered hour -- and the chapter's doctrine.
Q["ch06"] = [
    ("Describe holding your mother in the practice: what "
     "you carry for her in this season of her life, in "
     "what words, and what the carrying asks of you that "
     "being her son does not already ask.",
     "Render intercession for the first teacher.",
     ["intercession", "gratitude_naming"],
     ["people.held_mother"], None),
    ("Describe holding your father: what the bench's "
     "keeper needs carried that he would never enter in "
     "his own book, and how you carry a man whose keeping "
     "is silence about himself.",
     "Render intercession for the second teacher, in his "
     "own idiom.",
     ["intercession", "silence_rendering"],
     ["people.held_father"], None),
    ("Describe holding your sister: what you hope for her "
     "keeping and her life that you cannot do for her, "
     "and what it is to carry someone whose keeping "
     "differs from your own.",
     "Render intercession across two kinds of keeping.",
     ["intercession", "anchor_return"],
     ["people.held_sister"], None),
    ("Describe holding your wife: what marriage asks of "
     "the practice that the practice does not ask of "
     "itself, and what you carry for the woman who "
     "photographs your rooms.",
     "Render intercession inside the marriage.",
     ["intercession", "kept_object"], ["people.held_wife"],
     None),
    ("Describe holding a stranger: the one who came to the "
     "studio or the shop with a grief or a need and left "
     "as a name in your keeping -- who they were, what you "
     "carried, and for how long.",
     "Render intercession past the family's edge.",
     ["intercession", "moment_opening"],
     ["people.held_stranger"], None),
    ("Describe forgiving the one who wronged the shop: "
     "the dispute at the counter, your side's fault "
     "included -- what forgiveness required in practice, "
     "what it cost, and what it did not restore.",
     "Render forgiveness as an act with a price, honestly "
     "kept.",
     ["intercession", "day_examen"], ["people.forgiven"],
     None),
    ("Describe the hardest person to hold: someone you "
     "will not name, whose name the practice requires you "
     "to carry anyway -- what the requirement is, what "
     "you actually do, and where you fail at it.",
     "Render intercession at its point of failure, "
     "unnamed and honest.",
     ["intercession", "hardship_witness"],
     ["people.held_hardest"], None),
    ("Describe being held: a morning or a season when "
     "someone else's keeping carried you -- who it was, "
     "what they did, and what receiving it taught you "
     "that carrying never had.",
     "Render the keeper as the carried: intercession "
     "received.",
     ["gratitude_naming", "intercession"],
     ["people.being_held"], None),
    ("Describe the gathered hour: the practice done with "
     "others, in the room where your mother plays -- what "
     "the singing and the company do that the table and "
     "the bench cannot, and what they cannot do either.",
     "Render the practice in company, with its powers "
     "and limits.",
     ["place_portrait", "sensory_palette"],
     ["people.gathered"], None),
    ("What are other people for, at the end of this "
     "chapter: state what the keeping owes those outside "
     "the keeper, and what a practice is that keeps only "
     "itself.",
     "State the chapter's doctrine in the respondent's "
     "own terms.",
     ["anchor_return", "sending"], ["people.why"], None),
]

# Chapter 7 -- Gratitude Counted. Thanks as a discipline of
# naming: the counting itself, the unglamorous gifts, the
# fire year's honest thanks, gratitude withheld, gratitude
# paid aloud -- and the chapter's doctrine.
Q["ch07"] = [
    ("Describe the counting itself: the discipline of "
     "naming gifts one by one -- where you learned it, "
     "where it is done, and why a counted thanks differs "
     "from a felt one.",
     "Render gratitude as a practice with a method, not "
     "a mood.",
     ["gratitude_naming", "practice_rendering"],
     ["gratitude.counting"], None),
    ("Describe gratitude for the unglamorous: the boiler, "
     "the roof, the truck that starts -- the gifts nobody "
     "sings about, named one by one, and what naming them "
     "does to a keeper.",
     "Render thanks at the level of infrastructure.",
     ["gratitude_naming", "kept_object"],
     ["gratitude.unglamorous"], None),
    ("Describe gratitude in the fire's year: what could "
     "honestly be thanked for in the year of the ruin -- "
     "the list as it actually stood then, not as it reads "
     "now.",
     "Render thanks inside the worst year, without "
     "revision.",
     ["gratitude_naming", "hardship_witness"],
     ["gratitude.fire_year"], None),
    ("Describe gratitude for the hard gift: the failure "
     "or the loss that taught what success had not -- the "
     "instrument that could not be fixed, or its like -- "
     "and how thanks is said for a thing you would never "
     "choose again.",
     "Render thanks for the unwished-for teacher.",
     ["gratitude_naming", "hardship_witness"],
     ["gratitude.hard_gift"], None),
    ("Describe gratitude for your mother's hands: the "
     "music and the feeding as one gift, named in its "
     "parts -- the lessons, the organ, the table -- and "
     "what of it is in your own hands now.",
     "Render thanks for the first teacher's gift, in "
     "detail.",
     ["gratitude_naming", "sensory_palette"],
     ["gratitude.mother"], None),
    ("Describe gratitude for your father's plainness: the "
     "day book, the honest price, the unsaid things -- "
     "what his way of keeping gave you that a warmer way "
     "would not have.",
     "Render thanks for the second teacher's gift, in "
     "his idiom.",
     ["gratitude_naming", "kept_object"],
     ["gratitude.father"], None),
    ("Describe gratitude for your wife's seeing: what her "
     "photographs keep that your entries and your ears "
     "miss, and what being seen accurately by another "
     "person does to a keeper.",
     "Render thanks for the witness's gift.",
     ["gratitude_naming", "kept_object"],
     ["gratitude.wife"], None),
    ("Describe gratitude withheld: the thing you cannot "
     "yet thank for -- what it is, why the thanks will "
     "not come, and what the practice does with an "
     "unnamable gift in the meantime.",
     "Render the counting's honest gap: a thanks that "
     "fails, kept as a failure.",
     ["hardship_witness", "day_examen"],
     ["gratitude.withheld"], None),
    ("Describe gratitude paid aloud: a thanks owed to a "
     "person, spoken to their face -- who it was, what "
     "was owed, what saying it cost, and what it repaired "
     "that silence had left broken.",
     "Render thanks as a debt entered and paid, in "
     "person.",
     ["gratitude_naming", "intercession"],
     ["gratitude.paid_aloud"], None),
    ("What is gratitude for, at the end of this chapter: "
     "state what counted thanks accomplishes in a kept "
     "life, and what a keeper is who only receives.",
     "State the chapter's doctrine in the respondent's "
     "own terms.",
     ["anchor_return", "sending"], ["gratitude.why"],
     None),
]

# Chapter 8 -- Silence and Listening. The practice's
# receptive half: the kept silence, guidance in the
# respondent's own terms, the returning sentence, a dream
# with fact and meaning kept distinct, the refused hope,
# noise, listening to people -- and the chapter's doctrine.
Q["ch08"] = [
    ("Describe the silence you keep on purpose: when it "
     "falls, where, how long it lasts, what is set aside "
     "to make it, and what it is for.",
     "Render chosen silence as a discipline with edges.",
     ["silence_rendering", "practice_rendering"],
     ["silence.kept"], None),
    ("Describe listening for guidance in your own terms: "
     "how direction comes to a keeper like you -- what "
     "you attend to, what you discount, and how a heard "
     "thing is tested before it is obeyed.",
     "Render discernment as a method, in the "
     "respondent's own vocabulary.",
     ["listening", "practice_rendering"],
     ["silence.guidance"], None),
    ("Describe the sentence that would not leave: a line "
     "-- your mother's, the doctrine's, a stranger's -- "
     "that followed you through a season, where it met "
     "you, and what it was doing there.",
     "Render a carried sentence as a season's companion.",
     ["listening", "kept_object"], ["silence.sentence"],
     None),
    ("Describe a dream you still keep: the night your "
     "grandfather's shop, or its like, came to you in "
     "sleep -- what happened in it, exactly, and "
     "separately what you understand it to mean.",
     "Render a dream with the event and the meaning kept "
     "distinct on the page.",
     ["listening", "moment_opening"], ["silence.dream"],
     None),
    ("Describe discernment tested: the decision to "
     "rebuild rather than close, weighed in the practice "
     "-- what spoke for closing, what spoke for "
     "rebuilding, and how the weighing actually settled.",
     "Render the book's hinge decision as an act of "
     "listening.",
     ["listening", "hardship_witness"],
     ["silence.rebuild_decision"], None),
    ("Describe the answer that was no: a hope the practice "
     "carried that was refused -- what was hoped, how the "
     "refusal became clear, and how a keeper keeps a no.",
     "Render refusal received and kept, without "
     "varnish.",
     ["listening", "hardship_witness"], ["silence.no"],
     None),
    ("Describe the noise: a sound man's temptation to fill "
     "every silence with the radio, the board, the room's "
     "tone -- what the noise protects you from, and what "
     "it costs.",
     "Render the keeper's native resistance to his own "
     "discipline.",
     ["silence_rendering", "sensory_palette"],
     ["silence.noise"], None),
    ("Describe listening to people: the counter and the "
     "studio door as places where you are told things -- "
     "what being listened to does for the teller, and "
     "what the listening requires of the keeper.",
     "Render attention to people as a practice beside "
     "attention to guidance.",
     ["listening", "place_portrait"], ["silence.people"],
     None),
    ("Describe your mother's music as listening: the song "
     "she plays when the house is empty -- what it is, "
     "what playing with no audience is an act of, and "
     "what you learned about attention from overhearing "
     "it.",
     "Render the inherited form of listening: music as "
     "attention with no one to feed.",
     ["listening", "sensory_palette"],
     ["silence.mothers_music"], None),
    ("What is listening for, at the end of this chapter: "
     "state what attention accomplishes in a kept life "
     "that effort cannot, and what a keeper is who only "
     "speaks.",
     "State the chapter's doctrine in the respondent's "
     "own terms.",
     ["anchor_return", "sending"], ["silence.why"], None),
]

# Chapter 9 -- The Night Watch. The day closed: the examen
# at the day book, the kept and the lost named, the day
# handed over, the house's rounds, night fears, rest
# received -- and the chapter's doctrine.
Q["ch09"] = [
    ("Describe the day entered: the closing of the day "
     "book at night -- what gets written, in what order, "
     "in whose hand's tradition, and what the writing "
     "finishes that the day left open.",
     "Render the examen as a written act, inherited from "
     "the bench.",
     ["kept_object", "day_examen"], ["night.entry"], None),
    ("Describe where the day was kept: in tonight's "
     "review, or in the review as you usually make it -- "
     "the one kept thing you name first, and what naming "
     "it does to the rest of the account.",
     "Render the examen's credit side, concretely.",
     ["day_examen", "gratitude_naming"], ["night.kept"],
     None),
    ("Describe where the day was lost: the failure you "
     "enter without varnish -- the kind that recurs, what "
     "it cost, and what an entered failure is for that a "
     "hidden one is not.",
     "Render the examen's debit side, unvarnished.",
     ["day_examen", "hardship_witness"], ["night.lost"],
     None),
    ("Describe handing the day over: the last words of "
     "the night, said where and how, and what is given up "
     "in them that the day book's closing does not give "
     "up.",
     "Render surrender in the respondent's own terms, as "
     "an act with an address.",
     ["sending", "silence_rendering"], ["night.handing"],
     None),
    ("Describe the house at night: the rounds -- doors, "
     "stove, the sleeping rooms, the studio dark -- what "
     "is checked and in what order, and what the rounds "
     "say that no words are needed for.",
     "Render the keeper's patrol as a wordless entry.",
     ["place_portrait", "practice_rendering"],
     ["night.rounds"], None),
    ("Describe the three o'clock waking: what wakes you "
     "in the deep night in this season of your life, what "
     "you do in the hour that follows, and what the "
     "practice has made of that hour that fear had made "
     "before.",
     "Render the night watch at its hardest hour.",
     ["moment_opening", "hardship_witness"],
     ["night.waking"], None),
    ("Describe the fire's anniversary kept at night: how "
     "the ruin's date is marked after dark -- what is "
     "done, what is read or said, and who is there.",
     "Render the year's darkest date as a kept night.",
     ["kept_object", "hardship_witness"],
     ["night.anniversary"], None),
    ("Describe rest received: sleep taken as a gift "
     "rather than a collapse -- what has to be finished "
     "before it comes, what unfinished thing most often "
     "delays it, and what a keeper dreams of being "
     "forgiven for at the door of sleep.",
     "Render rest as the practice's last daily act.",
     ["silence_rendering", "day_examen"], ["night.rest"],
     None),
    ("Describe your father's night: the day book closed, "
     "the shop dark, the bench covered -- the keeping's "
     "old form at the day's end, as you saw it growing up.",
     "Render the inherited night, the examen's source.",
     ["kept_object", "place_portrait"],
     ["night.fathers"], None),
    ("What is the night for, at the end of this chapter: "
     "state what the dark half of a kept day accomplishes, "
     "and what a keeper is who keeps only the daylight.",
     "State the chapter's doctrine in the respondent's "
     "own terms.",
     ["anchor_return", "sending"], ["night.why"], None),
]

# Chapter 10 -- The Practice Kept. The return: a year of
# mornings audited, the practice in the rebuilt room, the
# practice taught, the doctrine tested in the keeper's own
# adult life, the practice's honest limits, the book's
# purpose tested against its whole -- and the anchor
# restated as it now stands, closing the book.
Q["ch10"] = [
    ("Describe a year of mornings audited: what a year of "
     "the kept practice actually changed in you and your "
     "house -- and what it did not change, entered as "
     "plainly.",
     "Open the closing chapter with the practice's own "
     "account of itself, credits and debits together.",
     ["day_examen", "anchor_return"], ["book.year"],
     None),
    ("Describe the practice in the rebuilt room: the first "
     "session back after the rebuilding -- what keeping "
     "was done before the work, and how the anchor sounded "
     "in the new room.",
     "Render the practice restored to its workplace, two "
     "years on from the ruin.",
     ["anchor_return", "place_portrait"],
     ["book.rebuilt_room"], None),
    ("Describe teaching the practice: the first discipline "
     "you give a beginner in the studio or at the bench -- "
     "what it is, why it comes first, and the last time "
     "you watched someone take it up.",
     "Render the keeping handed on, as a taught act.",
     ["practice_rendering", "intercession"],
     ["book.teaching"], None),
    ("Describe two keepers in one family: your sister's "
     "keeping and yours, set side by side at the end of "
     "the book -- where they agree, where they will never "
     "agree, and what the house gains by having both.",
     "Render the family's two keepings in their final "
     "relation.",
     ["anchor_return", "intercession"],
     ["book.two_keepers"], None),
    ("Describe the doctrine tested in your own adult life: "
     "the occasion when the family's sentence was quoted "
     "at you or by you over something broken of your own "
     "-- what it required, and what it cost to keep it.",
     "Give the anchor its fullest test in the keeper's "
     "own story.",
     ["anchor_return", "hardship_witness"],
     ["book.doctrine_tested"], None),
    ("Describe what you would tell your younger self at "
     "the first bench: the boy rewiring radios after "
     "school -- what the keeping will ask of him, in "
     "order, and the one thing you would not warn him "
     "about.",
     "Render the book's counsel backward, to its own "
     "beginning.",
     ["sending", "moment_opening"], ["book.younger_self"],
     None),
    ("Describe the practice imagined at seventy: the old "
     "keeper you hope to be -- where he sits, what his "
     "hands can no longer do, what the keeping becomes "
     "when the work is taken away.",
     "Render the practice's far end, as hope rather than "
     "fact.",
     ["place_portrait", "silence_rendering"],
     ["book.at_seventy"], None),
    ("Describe what the practice cannot do: its honest "
     "limits -- the grief it does not shorten, the answer "
     "it does not give, the day it does not save -- and "
     "why a keeper keeps it anyway.",
     "Render the keeping's limits as plainly as its "
     "powers were rendered.",
     ["hardship_witness", "day_examen"],
     ["book.limits"], None),
    ("What is this devotional for, at the end: what does "
     "its whole keeping, kept whole, show a practice is "
     "and does -- and what should a reader's own keeping "
     "do differently for this book existing?",
     "Test the book's declared purpose against its full "
     "record.",
     ["anchor_return", "sending"], ["book.purpose_final"],
     None),
    ("End the book: state the anchor one last time, as it "
     "now stands after a hundred entries -- the family's "
     "sentence as the fire, the rebuilding, the griefs, "
     "and the gratitudes have rewritten it in you -- and "
     "say what keeping it will ask of you next.",
     "Close on the anchor developed: the refrain's final "
     "return, carrying the whole book in it.",
     ["anchor_return", "sending"], ["book.final_anchor"],
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
    # Pack v1.1.0: the identity question (q003) declares a
    # second typed fact beside subject_name -- the subject's
    # recorded gender, elicited by the same answer. It keys
    # the engine's spouse-term screen and the subject line
    # every page prompt carries (see DEFECTS.md, V11).
    for q in questions:
        if q["id"] == "q003":
            q["facts"] = [{
                "slot": "subject_gender", "kind": "gender",
                "triggers": ["the respondent is a", "I am a"],
            }]
    pack = {
        "genre": "devotional",
        "version": "1.1.0",
        "framework": FRAMEWORK,
        "chapters": [
            {"id": cid, "title": title, "act": act}
            for cid, title, act in CHAPTERS
        ],
        "questions": questions,
    }
    out = Path(__file__).resolve().parent.parent / "packs" / \
        "devotional.json"
    out.write_text(json.dumps(pack, indent=1), encoding="utf-8")
    print(f"wrote {out}: {len(questions)} questions, "
          f"{len(CHAPTERS)} chapters")


if __name__ == "__main__":
    main()
