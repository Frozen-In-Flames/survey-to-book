"""Builds packs/short-story-collection.json: the short story
collection pack (100 questions).

Each question is authored as a tuple:
    (prompt, narrative_job, [device_ids], [bible_keys], fact_or_None)
and expanded here with its chapter and generated position string.

The pack's defining difference from the packs before it is its
unit: not a life (memoir, biography), not a lineage (family
history), and not a practice (cookbook), but the single story.
Each answer seeds one standalone story, and the collection is
the teller who tells them: for this series' demonstration
character, Frozen In Flames, musician and recording engineer,
whose stories live where his life has lived -- his father's
repair shop, his mother's front room, the recording studio he
founded (the Cold Room), its fire and rebuilding, the road, the
strangers at the counter, and the two family lines' inherited
tales behind all of it. The roadmap's feasibility note for this
genre is the design: each answer seeds a standalone story; no
long-range plot to hold; the bible only tracks the recurring
names the author wants tracked. So the survey's work is twofold:
frame questions fix the teller and his recurring cast as typed
facts, and story questions each elicit one complete story
kernel -- who was there, where, when, what happened, where it
turned, and how it ended -- because a story the answer only
half-tells is a story the model would have to guess the rest
of, and guessing is the one thing this engine is built not to
do.

Clean-proof rule (adopted 2026-11-24): if a fact had to be
obtained by asking the author outside the survey, the survey
failed to ask it, and the question belongs in the pack. The
rule's identity corollary: who the main character is is itself
respondent data, elicited by an explicit identity question
early in the survey (q003, in this genre's form: who is the
main character of this story collection, the storyteller whose
stories these are), never a fact the build supplies; in the
demonstration answers that question is answered from the
canonical record, and the story bible's subject_name fact
traces to it under the traceability gate.

Refrain default: OFF, chosen deliberately. The refrain is
recurrence with development of an anchor theme across pages.
A story collection's native recurrence is not a theme but a
cast, a set of places, and a teller's voice returning story
after story -- which is content, carried by the answers
themselves, not an anchor the prompt restates. The stories
stand alone by design; an imposed anchor would weld them into
a false arc none of them asked for, and it would do so from
the wrong material, since the anchor mechanism takes the
first page's opening sentences -- here a fact-fixing page
naming a family line -- as the book's theme. The family's
doctrine still appears in this book -- as an answer, at q010,
inside stories wherever the respondent's own kernels bring it
back, and restated by the respondent in the final chapter --
but as content, not as a prompt mechanism. The anti-loop
duplication guard applies in full: verbatim sentence overlap
is measured and bounded exactly as in the other packs.
"""

import json
from pathlib import Path

FRAMEWORK = {
    "voice": (
        "First-person storyteller's voice: the respondent telling "
        "stories from his own life and his family's telling, plain "
        "and concrete, led by objects and places, exact about years "
        "and names. A story page must be a story whole: an opening "
        "situation, the incident, the turn, and the ending the "
        "story actually had -- not a summary of one, and not a "
        "scene that stops where the story should start. A frame "
        "page must know the difference between what the teller "
        "witnessed and what the telling hands down, and say which "
        "is which."
    ),
    "pov": "first person",
    "refrain": False,
    "tense": "past tense for the stories themselves, present "
             "tense for the teller's frame -- where he stands "
             "now, telling them",
    "page_target_words": 250,
    "global_instructions": (
        "Transform the respondent's answers into a story "
        "collection in the first person: one story or one frame "
        "page per answer, each standing on its own. The "
        "collection's continuity is its cast and its places -- "
        "the storyteller, his two family lines (the Flames line "
        "of his mother, the Frozen line of his father), the "
        "repair shop, the front room, and the Cold Room studio "
        "-- not a plot carried between stories. Never contradict "
        "the story bible or the fixed facts. Do not invent named "
        "people, places, or dates that are not in the supplied "
        "material. Where an answer gives a story, render it "
        "whole: the opening situation, the incident, the turn, "
        "and the ending it actually had; do not improve the "
        "ending, and do not append a moral the answer does not "
        "state. Where the material is thin, expand by rendering "
        "its documented implications as scene and context, not "
        "by fabricating events."
    ),
    "devices": {
        "story_rendering": {
            "name": "Story rendering",
            "instruction": "Render the answer as a complete "
                           "story: the opening situation, the "
                           "incident that disturbs it, the turn, "
                           "and the ending the story actually "
                           "had, in that order. A reader should "
                           "be able to retell the story from the "
                           "page alone.",
        },
        "scene_opening": {
            "name": "Scene opening",
            "instruction": "Open inside the moment: the place, "
                           "the light, the object in hand, the "
                           "sound in the room -- before any "
                           "explanation of how the teller comes "
                           "to be telling this.",
        },
        "character_sketch": {
            "name": "Character sketch",
            "instruction": "Render one person through gesture, "
                           "habit, and one line of speech: what "
                           "the hands do, what the person always "
                           "says, what they never say.",
        },
        "dialogue_beats": {
            "name": "Dialogue beats",
            "instruction": "Let the story's exchange carry the "
                           "turn: who said what, in order, with "
                           "the silences kept. Speech in this "
                           "book is evidence, not decoration.",
        },
        "object_anchor": {
            "name": "Object anchor",
            "instruction": "Hang the story on its object -- the "
                           "radio, the guitar, the toolbox, the "
                           "tape, the book -- and let the "
                           "object's state be the plot's clock: "
                           "what is broken, carried, fixed, or "
                           "lost, and when that changes.",
        },
        "turning_point": {
            "name": "Turning point",
            "instruction": "Isolate the moment the story "
                           "changes direction and slow down for "
                           "it: the sentence, the sound, the "
                           "arrival, after which the ending "
                           "became the one it had.",
        },
        "ending_line": {
            "name": "Ending line",
            "instruction": "Close on the story's own last fact "
                           "or last line of speech, unadorned. "
                           "No moral appended, no summary after "
                           "the ending.",
        },
        "inherited_tale": {
            "name": "Inherited tale",
            "instruction": "Retell a story the teller did not "
                           "witness: name whose telling it comes "
                           "in, mark where the record ends and "
                           "the telling begins, and keep the "
                           "dead in their own time -- the teller "
                           "was not there, and the page must not "
                           "pretend he was.",
        },
        "frame_voice": {
            "name": "Frame voice",
            "instruction": "Let the teller step forward: why "
                           "this story is told, what telling it "
                           "settles or costs, and what he knows "
                           "about his own telling of it.",
        },
        "sensory_palette": {
            "name": "Sensory palette",
            "instruction": "Render the scene through sound "
                           "first -- this teller is an engineer "
                           "of sound -- then sight, smell, and "
                           "touch: the hum, the static, the "
                           "room's tone before anyone speaks.",
        },
        "place_portrait": {
            "name": "Place portrait",
            "instruction": "Render one place whole: its "
                           "furniture, its light, its working "
                           "sounds, who stands where in it. One "
                           "page should leave one place standing "
                           "as a place.",
        },
        "time_frame": {
            "name": "Time frame",
            "instruction": "Fix the story in its year and "
                           "season plainly, early, and let the "
                           "date do its work without commentary: "
                           "the reader should always know when "
                           "they are.",
        },
        "chapter_turn": {
            "name": "Chapter turn",
            "instruction": "End the page turning toward the "
                           "next subject: a person, a place, or "
                           "an object the coming pages take up.",
        },
    },
}

CHAPTERS = [
    ("ch01", "The Storyteller", "Act I: The Teller"),
    ("ch02", "The Repair Shop", "Act I: The Teller"),
    ("ch03", "The Front Room", "Act I: The Teller"),
    ("ch04", "First Work", "Act II: The Work"),
    ("ch05", "The Cold Room", "Act II: The Work"),
    ("ch06", "The Fire and the Rebuilding", "Act II: The Work"),
    ("ch07", "The Road", "Act III: The World"),
    ("ch08", "Strangers at the Counter", "Act III: The World"),
    ("ch09", "The Family Telling", "Act III: The World"),
    ("ch10", "Last Stories", "Act IV: The Telling"),
]

FACT_FLAMES_NAME = {"slot": "flames_line_name", "kind": "person_name",
                    "triggers": ["the Flames family name",
                                 "the Flames line's name"]}
FACT_FROZEN_NAME = {"slot": "frozen_line_name", "kind": "person_name",
                    "triggers": ["the Frozen family name",
                                 "the Frozen line's name"]}
FACT_STORYTELLER = {"slot": "subject_name", "kind": "person_name",
                    "triggers": ["the respondent"]}
FACT_MOTHER = {"slot": "mother_name", "kind": "person_name",
               "triggers": ["my mother", "the respondent's mother"]}
FACT_FATHER = {"slot": "father_name", "kind": "person_name",
               "triggers": ["my father", "the respondent's father"]}
FACT_BIRTH_YEAR = {"slot": "birth_year", "kind": "year",
                   "triggers": ["I was born"]}
FACT_BIRTHPLACE = {"slot": "birthplace", "kind": "place_name",
                   "triggers": ["I was born in"]}
FACT_SISTER = {"slot": "sister_name", "kind": "person_name",
               "triggers": ["my sister", "the respondent's sister"]}
FACT_PARTNER = {"slot": "partner_name", "kind": "person_name",
                "triggers": ["my wife", "the respondent's wife"]}
FACT_STUDIO_YEAR = {"slot": "studio_year", "kind": "year",
                    "triggers": ["I founded the Cold Room in",
                                 "the Cold Room opened in"]}

Q = {}
# Chapter 1 -- The Storyteller. The identity question (q003),
# the direct mother/father/sister/partner questions, and the
# two line-name questions exist under the clean-proof rule and
# its identity corollary: the cast this collection's stories
# keep returning to is elicited here, in terms, before any
# story is asked for.
Q["ch01"] = [
    ("What is the family name of your mother's line -- the line "
     "whose telling you first heard stories in? Begin the "
     "answer with the name.",
     "Open the collection by naming the mother's line, the "
     "first of the teller's two inheritances, and fix the fact.",
     ["frame_voice", "place_portrait"],
     ["family.flames_name"], FACT_FLAMES_NAME),
    ("What is the family name of your father's line -- the line "
     "that taught you a story is a thing kept and entered? Begin "
     "the answer with the name.",
     "Name the father's line, the second inheritance, and fix "
     "the fact.",
     ["frame_voice", "place_portrait"],
     ["family.frozen_name"], FACT_FROZEN_NAME),
    ("Who is the main character of this story collection -- the "
     "storyteller whose stories these are, who tells them and "
     "stands inside most of them? Give that storyteller's full "
     "name, and say how the name comes from the two lines. Begin "
     "the answer with the full name.",
     "Establish the book's central identity as respondent data: "
     "the main character is the storyteller the respondent "
     "names here, and the fact is fixed from this answer alone.",
     ["frame_voice", "character_sketch"],
     ["respondent.identity"], FACT_STORYTELLER),
    ("What is your mother's full name, and what is her place in "
     "your storytelling -- what did she teach you about how a "
     "story is told, and which of her stories is still told in "
     "your house? Begin the answer with her full name.",
     "Name the first teller directly, with her front room, and "
     "fix the fact.",
     ["character_sketch", "frame_voice"],
     ["people.mother"], FACT_MOTHER),
    ("What is your father's full name, and what is his place in "
     "your storytelling -- what did the repair bench and the day "
     "book teach you about what a story must contain? Begin the "
     "answer with his full name.",
     "Name the second teller directly, with his bench, and fix "
     "the fact.",
     ["character_sketch", "frame_voice"],
     ["people.father"], FACT_FATHER),
    ("In what year were you born, and what stories were already "
     "old in the family when you arrived? Begin the answer with "
     "the year.",
     "Fix the teller's birth year as fact, set inside the "
     "family's stock of stories at his arrival.",
     ["time_frame", "frame_voice"], ["respondent.birth"],
     FACT_BIRTH_YEAR),
    ("In what place were you born, and what does that place "
     "sound like in your earliest memory of it? Begin the "
     "answer with the place.",
     "Fix the teller's birthplace as fact and as his first "
     "soundscape.",
     ["place_portrait", "sensory_palette"],
     ["places.birthplace"], FACT_BIRTHPLACE),
    ("What is your sister's full name, and what is her place in "
     "the telling -- what stories does she keep that you do "
     "not, and how does her version differ from yours? Begin "
     "the answer with her full name.",
     "Name the collection's second keeper of the family "
     "stories, and fix the fact.",
     ["character_sketch", "frame_voice"],
     ["people.sister"], FACT_SISTER),
    ("What is your wife's full name, and what is her place in "
     "the telling -- she photographs the sessions your stories "
     "come from: what does her camera keep that your telling "
     "misses? Begin the answer with her full name.",
     "Name the collection's witness, and fix the fact.",
     ["character_sketch", "frame_voice"],
     ["people.partner"], FACT_PARTNER),
    ("What saying, rule, or doctrine does your family hand "
     "down -- the sentence quoted when a thing is broken, kept, "
     "or told -- which line brought it, and how does it govern "
     "the way a story gets told in your house?",
     "State the family's doctrine as this collection's law of "
     "telling, planted as content the stories themselves may "
     "draw on.",
     ["frame_voice", "inherited_tale"], ["telling.doctrine"],
     None),
]
# Chapter 2 -- The Repair Shop. Ten stories of the father's
# shop: each question elicits one complete kernel -- who
# brought the thing, what was wrong, where it turned, how it
# ended.
Q["ch02"] = [
    ("Tell the story of the first radio you ever fixed alone in "
     "your father's shop: whose radio it was, what was wrong "
     "with it, what you did at the bench, and how the story "
     "ended when its owner came back for it.",
     "Open the shop's stories with the teller's first solo "
     "repair, the bench's rite of passage.",
     ["story_rendering", "object_anchor"],
     ["stories.first_radio"], None),
    ("Tell the story of the guitar with the broken neck: who "
     "brought it in, how the break happened, what your father "
     "said a neck repair could and could not promise, and what "
     "the guitar's owner decided.",
     "Render a repair whose honest verdict mattered more than "
     "the work.",
     ["story_rendering", "dialogue_beats"],
     ["stories.broken_neck"], None),
    ("Tell the story of the customer who paid for a repair in "
     "something other than money: what they brought, what they "
     "offered, what your father entered in the day book, and "
     "what became of the payment.",
     "Render the shop's economy at its most human: barter, "
     "entered and honored.",
     ["story_rendering", "character_sketch"],
     ["stories.barter"], None),
    ("Tell the story of the repair your father refused to "
     "charge for: what the thing was, whose it was, why the "
     "bench would not take money for it, and what the customer "
     "did with that refusal.",
     "Render the shop's standard as an act, not a slogan.",
     ["story_rendering", "frame_voice"], ["stories.free_repair"],
     None),
    ("Tell the story of the day book entry your father still "
     "reads aloud: what repair it records, what the entry says "
     "and leaves out, and why that page of the book is the one "
     "that gets retold.",
     "Render the shop's written record as a story about "
     "storytelling itself.",
     ["object_anchor", "frame_voice"], ["stories.day_book_entry"],
     None),
    ("Tell the story of the radio that came back three times: "
     "what the fault was, why it hid through two repairs, what "
     "finally exposed it, and what your father wrote in the day "
     "book the third time.",
     "Render a fault that taught the bench its patience.",
     ["story_rendering", "turning_point"],
     ["stories.third_return"], None),
    ("Tell the story of your first paid repair, the year you "
     "began working after school: what the job was, what you "
     "were paid, what your father checked before he let it "
     "leave the shop, and what you did with the money.",
     "Render the teller's entry into the trade, wages and all.",
     ["story_rendering", "time_frame"], ["stories.first_wage"],
     None),
    ("Tell the story of the instrument you could not fix: what "
     "it was, what you tried, the moment you knew, and what "
     "your father said when you carried it to him.",
     "Render an honest failure at the bench, and what the "
     "bench does with failure.",
     ["story_rendering", "ending_line"], ["stories.unfixable"],
     None),
    ("Tell the story your father tells only after hours, when "
     "the shop is shut and the bench is clear: what it is "
     "about, why it is not a daytime story, and what part of "
     "it you are still not sure you believe.",
     "Render the bench's private canon, told in its own "
     "conditions.",
     ["inherited_tale", "scene_opening"],
     ["stories.after_hours"], None),
    ("Tell the story of your grandfather Flint's toolbox in the "
     "shop: how it came to be there, what is in it, the day it "
     "was opened in your hearing, and what your father said the "
     "tools were for now.",
     "Close the chapter on the inherited object that joins "
     "the shop to the line behind it.",
     ["object_anchor", "chapter_turn"], ["stories.toolbox"], None),
]
# Chapter 3 -- The Front Room. Ten stories of the mother's
# room: piano pupils, church people, and the room where music
# and feeding were one practice.
Q["ch03"] = [
    ("Describe your mother's front room as a place stories "
     "happen: the piano, the pupils, what was served to "
     "children who came for lessons, and the room's rule about "
     "who was fed.",
     "Open the front room's stories by standing the room "
     "itself up as a place.",
     ["place_portrait", "sensory_palette"],
     ["places.front_room"], None),
    ("Tell the story of the pupil who could not pay: who the "
     "child was, what your mother charged her instead of "
     "money, and where that arrangement ended years later.",
     "Render the front room's economy: teaching and feeding "
     "as one act.",
     ["story_rendering", "character_sketch"],
     ["stories.unpaid_pupil"], None),
    ("Tell the story of the church social your mother's playing "
     "held together: the occasion, what went wrong with the "
     "program or the food, what she played, and how the "
     "evening ended.",
     "Render the mother's musicianship as the room's load-"
     "bearing wall.",
     ["story_rendering", "sensory_palette"],
     ["stories.church_social"], None),
    ("Tell the story of the broken piano pedal: the church "
     "social where your mother was playing, the repairman the "
     "church called, what passed between them over the "
     "instrument, and how that evening is told in your family "
     "now.",
     "Render the parents' meeting as the front room's "
     "founding story.",
     ["story_rendering", "inherited_tale"],
     ["stories.pedal"], None),
    ("Tell the story of the pupil who went on: the child from "
     "the front room who became a working musician -- what "
     "your mother heard in them first, and the day their road "
     "and the room's road parted.",
     "Render the room's success story, and its limit.",
     ["story_rendering", "ending_line"],
     ["stories.pupil_who_went_on"], None),
    ("Tell the story of the recital where something went wrong: "
     "the hall, the child, the failure in the middle of the "
     "program, and what your mother did from the piano bench "
     "while it happened.",
     "Render the teacher's craft under public failure.",
     ["story_rendering", "turning_point"],
     ["stories.recital"], None),
    ("Tell the story of the song your mother plays when the "
     "house is empty: what the song is, when you first "
     "understood it was not for an audience, and what she said "
     "the one time you asked about it.",
     "Render the room's quietest story: music with no one to "
     "feed.",
     ["scene_opening", "sensory_palette"], ["stories.empty_house"],
     None),
    ("Tell the story of your grandmother Jet's family Bible: "
     "when she began it, what she entered in its flyleaf and "
     "for how long, and the entry -- a birth, a marriage, a "
     "death -- whose writing you can still see in her hand.",
     "Render the written record of the mother's line as an "
     "object with a story.",
     ["object_anchor", "inherited_tale"], ["stories.bible"],
     None),
    ("Tell the story of your sister at the piano: her lessons "
     "in the front room, what kind of pupil she was beside "
     "you, and the piece or the day that settled what music "
     "would be for each of you.",
     "Render the siblings' division of the inheritance at the "
     "keyboard.",
     ["story_rendering", "character_sketch"],
     ["stories.sister_piano"], None),
    ("Tell the story of the front room now: what the room is "
     "for in the present day, who still comes to it, and the "
     "most recent evening that proved the room had not "
     "changed its mind about feeding people.",
     "Close the chapter in the present tense of the telling, "
     "on the room's continuity.",
     ["place_portrait", "chapter_turn"], ["places.front_room_now"],
     None),
]
# Chapter 4 -- First Work. The teller becomes a worker: the
# after-school years at the bench, then the door into recording
# -- the first sessions, the tape he was paid in, the decision
# to found a studio of his own.
Q["ch04"] = [
    ("Tell the story of your first wages: the after-school work "
     "in your father's shop, the first pay you were handed as a "
     "worker rather than a son, and what you bought with it.",
     "Open the work act with the teller's first standing as a "
     "paid hand.",
     ["story_rendering", "time_frame"], ["stories.first_wages"],
     None),
    ("Tell the story of the first guitar you restrung for a "
     "stranger: whose it was, what state it arrived in, what "
     "the owner said while you worked, and what they played "
     "before they left the shop.",
     "Render a small job whole, the kind the trade is built "
     "from.",
     ["story_rendering", "object_anchor"],
     ["stories.first_restring"], None),
    ("Tell the story of the mistake at the bench that cost "
     "money: what you broke or misjudged, what it cost and who "
     "paid, and what your father entered in the day book about "
     "it.",
     "Render the price of learning, honestly kept.",
     ["story_rendering", "ending_line"],
     ["stories.costly_mistake"], None),
    ("Tell the story of the working musician who taught you "
     "something at the counter: who they were, what they "
     "brought in, the thing they said or showed you that you "
     "still use, and when you last saw them.",
     "Render the counter as a school with one unforgettable "
     "teacher.",
     ["character_sketch", "dialogue_beats"],
     ["stories.counter_teacher"], None),
    ("Tell the story of your first recording session: the year, "
     "the studio in Dallas, who ran the session, what an unpaid "
     "assistant was given to do, and the moment you understood "
     "what the work was.",
     "Render the record's hinge: the teller's first sight of "
     "his trade.",
     ["story_rendering", "time_frame"], ["stories.first_session"],
     None),
    ("Tell the story of the tape you were paid in: what was on "
     "it, why the studio paid in tape and lessons instead of "
     "money, what you did with that tape, and where it is now.",
     "Render the session years' currency, and what it bought.",
     ["object_anchor", "frame_voice"], ["stories.tape_payment"],
     None),
    ("Tell the story of the session that went wrong in your "
     "assistant years: what failed, whose fault the room "
     "decided it was, and the lesson that session left in your "
     "hands for good.",
     "Render a failure in the learning years, with its "
     "tuition.",
     ["story_rendering", "turning_point"],
     ["stories.session_gone_wrong"], None),
    ("Tell the story of the first night you were left alone "
     "with the board: who trusted you with it, what the session "
     "was, what you did when something in the room surprised "
     "you, and how the night ended.",
     "Render trust arriving, and being met.",
     ["scene_opening", "story_rendering"],
     ["stories.alone_at_board"], None),
    ("Tell the story of the recording you studied until it "
     "taught you your trade: what it is, where you heard it "
     "first, what you took apart in it, and what of it is in "
     "your own work now.",
     "Render an education by ear, one record deep.",
     ["frame_voice", "sensory_palette"],
     ["stories.studied_record"], None),
    ("Tell the story of the decision to found your own studio: "
     "the day or the session that settled it, who you told "
     "first, what they said, and what you understood the "
     "decision would cost.",
     "Close the chapter on the decision the next act builds "
     "on.",
     ["story_rendering", "chapter_turn"], ["stories.decision"],
     None),
]
# Chapter 5 -- The Cold Room. The studio's stories. Its first
# question carries the studio_year fact under the clean-proof
# rule: the founding year is elicited in terms, in the chapter
# the fact governs.
Q["ch05"] = [
    ("In what year did you found the Cold Room, and what was "
     "the building before it was a studio? Begin the answer "
     "with the year.",
     "Fix the studio's founding year as fact, and open its "
     "stories with the icehouse it was made from.",
     ["time_frame", "place_portrait"], ["studio.founding"],
     FACT_STUDIO_YEAR),
    ("Tell the story of the first session in the Cold Room: who "
     "recorded first, what they brought, what the unfinished "
     "room did to the sound, and how the session ended.",
     "Render the studio's first day of work, in its raw "
     "state.",
     ["story_rendering", "scene_opening"],
     ["stories.first_cold_room_session"], None),
    ("Tell the story of the session the kitchen corner saved: "
     "the hour, the hunger, what got cooked between takes, and "
     "what the food did to the rest of the session.",
     "Render the studio's second inheritance: a session is "
     "fed like a table.",
     ["story_rendering", "sensory_palette"],
     ["stories.kitchen_corner"], None),
    ("Tell the story of the singer who could not find the note: "
     "the song, the note, what the room tried, and how the take "
     "that finally stood was got.",
     "Render the engineer's patience as a plot.",
     ["story_rendering", "turning_point"],
     ["stories.missing_note"], None),
    ("Tell the story of the band that fought in the studio: "
     "what the fight was about, where in the session it broke, "
     "what you did from the board, and what the band left with.",
     "Render conflict inside the room's small weather.",
     ["story_rendering", "dialogue_beats"], ["stories.band_fight"],
     None),
    ("Tell the story of the first time your wife came to the "
     "Cold Room: she was hired to photograph a session -- what "
     "she shot, what she said about the room, and what passed "
     "between you that the session's music covered.",
     "Render the meeting the record dates to a working day, "
     "as the studio remembers it.",
     ["story_rendering", "character_sketch"],
     ["stories.photographer"], None),
    ("Tell the story of the session log entry that became the "
     "studio's legend: what the entry records, how it is "
     "retold to new assistants, and what the retelling has "
     "added that the entry does not say.",
     "Render the studio's written record growing its myth, "
     "honestly marked.",
     ["object_anchor", "frame_voice"], ["stories.log_legend"],
     None),
    ("Tell the story of the machine that failed in the middle "
     "of a take: what failed, what the take was, what the room "
     "did in the next sixty seconds, and whether the take "
     "survived.",
     "Render the repairman's inheritance arriving inside the "
     "engineer's emergency.",
     ["story_rendering", "turning_point"],
     ["stories.machine_failure"], None),
    ("Tell the story of the recording nobody was supposed to "
     "hear about: who asked for the secrecy, what was recorded, "
     "how the secret was kept, and whether it is still kept.",
     "Render the studio's discretion as a kept promise.",
     ["story_rendering", "ending_line"], ["stories.secret_session"],
     None),
    ("Tell the story of how the Cold Room got its standing "
     "rule: the session that forced it, the rule's exact words, "
     "and the first time you had to enforce it.",
     "Close the chapter on the room's law, earned the way "
     "laws are.",
     ["story_rendering", "chapter_turn"], ["stories.studio_rule"],
     None),
]
# Chapter 6 -- The Fire and the Rebuilding. One event and its
# two years: the fire that destroyed the first Cold Room, told
# in ten stories from the night itself to the first session in
# the rebuilt room.
Q["ch06"] = [
    ("Tell the story of the night of the fire: how the word "
     "reached you, what you saw when you arrived, what the "
     "fire did and did not take, and where you stood when it "
     "was over.",
     "Open the fire's stories at the night itself, whole and "
     "in order.",
     ["story_rendering", "scene_opening"], ["stories.fire_night"],
     None),
    ("Tell the story of what was lost and what was saved: the "
     "inventory you made afterward, the one object pulled out "
     "that you still have, and the one loss you still name "
     "first.",
     "Render the arithmetic of ruin, object by object.",
     ["object_anchor", "frame_voice"], ["stories.inventory"],
     None),
    ("Tell the story of the morning after: the first person "
     "who showed up at the ruin, what they brought, what they "
     "did before they said anything, and what was said.",
     "Render help arriving in its true order: hands before "
     "words.",
     ["story_rendering", "character_sketch"],
     ["stories.morning_after"], None),
    ("Tell the story of the ledger of the loss: how the day "
     "book habit met the ruin -- what you entered, what the "
     "insurance and the accounts required, and the entry that "
     "was hardest to write.",
     "Render the Frozen line's bookkeeping applied to "
     "disaster.",
     ["object_anchor", "frame_voice"], ["stories.loss_ledger"],
     None),
    ("Tell the story of the decision to rebuild rather than "
     "close: who argued for closing, what the argument was, "
     "the moment the decision settled, and what you said when "
     "it did.",
     "Render the collection's hinge decision in the open.",
     ["story_rendering", "dialogue_beats"],
     ["stories.rebuild_decision"], None),
    ("Tell the story of your father's part in the rebuilding: "
     "the first repair he made at the site, what he brought "
     "from the shop, and what passed between you over that "
     "work.",
     "Render the bench's doctrine at the ruin: what can be "
     "fixed, fixed.",
     ["story_rendering", "character_sketch"],
     ["stories.fathers_repair"], None),
    ("Tell the story of your mother's part in the rebuilding: "
     "how the front room extended itself to a worksite, who "
     "got fed and when, and the meal that marked the "
     "rebuilding's hardest week.",
     "Render the fire line's answer to ruin: everybody fed.",
     ["story_rendering", "sensory_palette"],
     ["stories.mothers_feeding"], None),
    ("Tell the story of the borrowed room: where you recorded "
     "while the Cold Room was rebuilt, whose space it was, "
     "what working in another's room taught you, and the "
     "session there you would not trade.",
     "Render the exile's studio, and its gifts.",
     ["place_portrait", "story_rendering"],
     ["stories.borrowed_room"], None),
    ("Tell the story of your wife's photographs of the ruin "
     "and the rebuilding: what she shot and when, the "
     "photograph you cannot look at and the one you keep, and "
     "what her record shows that yours does not.",
     "Render the witness's archive beside the teller's.",
     ["frame_voice", "object_anchor"],
     ["stories.wifes_photographs"], None),
    ("Tell the story of the first session in the rebuilt room: "
     "how long the rebuilding took, who recorded, what the new "
     "room sounded like on its first night, and what you "
     "entered in the log.",
     "Close the fire's arc on the room working again, two "
     "years on.",
     ["story_rendering", "chapter_turn"],
     ["stories.first_session_rebuilt"], None),
]
# Chapter 7 -- The Road. Stories away from Dallas: the record
# leaves the geography of the session years deliberately
# loose, and the survey spends that looseness on the road.
Q["ch07"] = [
    ("Tell the story of your first session away from home: "
     "where you were sent, who sent you, what the strange room "
     "asked of you, and what you brought back besides the work.",
     "Open the road's stories with the first leaving.",
     ["story_rendering", "place_portrait"],
     ["stories.first_road_session"], None),
    ("Tell the story of the Chicago branch: the visit to your "
     "great-aunt Topaz's household, who was at her table, what "
     "the Dallas line and the Chicago line made of each other, "
     "and the story exchanged that night that you still carry.",
     "Render the family's spread geography at one table.",
     ["story_rendering", "inherited_tale"], ["stories.chicago"],
     None),
    ("Tell the story of the Fort Worth kitchen: a meal or a "
     "repair at your aunt Jade's household, the nursing "
     "schedule the house runs on, and what of the Frozen "
     "line's kitchen survives inside it.",
     "Render the second line's present geography, one county "
     "over.",
     ["place_portrait", "story_rendering"], ["stories.fort_worth"],
     None),
    ("Tell the story of the church far from home: the service "
     "or session you played or recorded in a strange church, "
     "what its room did to the music, and the person there who "
     "treated you as kin before they knew your name.",
     "Render the road's hospitality, in the mother's line's "
     "own territory.",
     ["story_rendering", "sensory_palette"],
     ["stories.strange_church"], None),
    ("Tell the story of the breakdown on the road: what failed "
     "-- vehicle, instrument, or machine -- where you were, "
     "what the fix required, and whose hands besides yours "
     "were in it.",
     "Render the doctrine tested far from the bench.",
     ["story_rendering", "turning_point"], ["stories.breakdown"],
     None),
    ("Tell the story of working in another engineer's room: "
     "their rules against yours, the moment the two methods "
     "met, and the practice of theirs you brought home.",
     "Render craft compared at close quarters.",
     ["story_rendering", "frame_voice"],
     ["stories.other_engineer"], None),
    ("Tell the story of the song recorded in one night in a "
     "borrowed room: whose song, why one night was all there "
     "was, how the take was got, and where that recording "
     "lives now.",
     "Render the road's best argument: limits as an "
     "instrument.",
     ["story_rendering", "ending_line"], ["stories.one_night_song"],
     None),
    ("Tell the story of coming home: the return to Dallas after "
     "the longest of the road years' absences, what the city "
     "sounded like from the car or the door, and who was awake "
     "when you got in.",
     "Render homecoming by ear, the teller's first sense.",
     ["scene_opening", "sensory_palette"], ["stories.homecoming"],
     None),
    ("Tell the story of the detail in your best road story "
     "that is not strictly true: what the detail is, why the "
     "story grew it, and why you have let it stand every time "
     "you have told it since.",
     "Render the teller's honesty about his own telling, in "
     "the open.",
     ["frame_voice", "inherited_tale"], ["stories.untrue_detail"],
     None),
    ("Tell the story of the practice the road gave the studio: "
     "the habit, rule, or piece of kit the Cold Room runs on "
     "now because a strange room taught it, and the session "
     "where it first proved itself at home.",
     "Close the road's chapter by bringing its wages home.",
     ["frame_voice", "chapter_turn"], ["stories.road_practice"],
     None),
]
# Chapter 8 -- Strangers at the Counter. Ten one-off people:
# the shop's and the studio's walk-ins, each a complete story
# with the teller's world as its frame.
Q["ch08"] = [
    ("Tell the story of the man with the radio older than the "
     "shop: what he carried in, what the radio had survived, "
     "what he asked the bench to promise, and how he left.",
     "Open the strangers' stories with the oldest object and "
     "its keeper.",
     ["story_rendering", "object_anchor"], ["stories.old_radio"],
     None),
    ("Tell the story of the woman who wanted a song recorded "
     "for someone gone: whose song, who it was for, how the "
     "session was run, and what she did when she heard it "
     "back.",
     "Render the studio as a place where grief books time.",
     ["story_rendering", "ending_line"],
     ["stories.memorial_song"], None),
    ("Tell the story of the kid with the broken first guitar: "
     "how old, what the break was, what your father charged "
     "and what you added to the job, and what the kid played "
     "on the way out.",
     "Render the teller meeting his own beginning across the "
     "counter.",
     ["story_rendering", "character_sketch"],
     ["stories.kids_guitar"], None),
    ("Tell the story of the preacher at the counter: what his "
     "church needed repaired or recorded, the bargain he "
     "proposed, and how the bench and the pulpit settled it.",
     "Render two kinds of keeping meeting over a price.",
     ["story_rendering", "dialogue_beats"], ["stories.preacher"],
     None),
    ("Tell the story of the musician who paid with a story: "
     "what work they needed, the story they traded, whether "
     "the bench judged it fair payment, and whether you have "
     "retold it since.",
     "Render the counter's oldest currency, exchanged in the "
     "open.",
     ["story_rendering", "frame_voice"], ["stories.paid_in_story"],
     None),
    ("Tell the story of the argument at the counter: what the "
     "dispute was -- a price, a verdict, a promise -- how it "
     "ran, and how it ended, honestly, including the part that "
     "was your side's fault.",
     "Render a conflict without varnish, the teller's side "
     "included.",
     ["story_rendering", "dialogue_beats"], ["stories.argument"],
     None),
    ("Tell the story of the regular who stopped coming: who "
     "they were at the counter, the last ordinary visit, how "
     "you learned where they had gone, and what their absence "
     "changed in the shop's week.",
     "Render an absence as a story with an ordinary door.",
     ["story_rendering", "ending_line"], ["stories.regular_gone"],
     None),
    ("Tell the story of the session booked under a false name: "
     "what name was given, what was recorded, when you "
     "understood the reason, and what the log says about that "
     "day.",
     "Render discretion tested, and kept.",
     ["story_rendering", "object_anchor"], ["stories.false_name"],
     None),
    ("Tell the story of the child who watched through the "
     "studio door: who they belonged to, what they saw, the "
     "question they asked, and what you let them do before "
     "they were called away.",
     "Render the next generation arriving the way this one "
     "did: by watching.",
     ["scene_opening", "story_rendering"],
     ["stories.child_at_door"], None),
    ("Tell the story of the stranger who became a friend of "
     "the house: the first visit, the turn by which a customer "
     "became kin, and where they sit now when they come.",
     "Close the strangers' chapter on the counter's best "
     "outcome.",
     ["story_rendering", "chapter_turn"],
     ["stories.stranger_to_kin"], None),
]
# Chapter 9 -- The Family Telling. The inherited tales: the
# two lines' founding stories, retold by a teller who was not
# there, each question marking whose telling it comes in.
Q["ch09"] = [
    ("Tell the story of Garnet Flames's coming to Dallas: the "
     "year, what he carried from Holly Springs, the furnaces "
     "and boilers that were his trade, and how the Flames line "
     "tells its founder's arrival now.",
     "Open the inherited tales with the fire line's founder, "
     "in his line's own telling.",
     ["inherited_tale", "time_frame"], ["stories.garnet_arrival"],
     None),
    ("Tell the story of Jet Flames and the family Bible: the "
     "year she began it, what she entered first, how the book "
     "was kept through the line's changes, and whose hand "
     "keeps it now.",
     "Render the matriarch's record as the line's first "
     "story about itself.",
     ["inherited_tale", "object_anchor"], ["stories.jet_bible"],
     None),
    ("Tell the story of Flint Frozen's coming to Dallas: the "
     "year, the wartime service behind him, the toolbox he "
     "carried from Pittsburgh, and how the Frozen line tells "
     "its founder's arrival now.",
     "Set the iron line's founder beside the fire line's, in "
     "his line's own telling.",
     ["inherited_tale", "time_frame"], ["stories.flint_arrival"],
     None),
    ("Tell the story of Pearl Frozen's accounts: what she "
     "entered, what her standard against waste cost and saved, "
     "the occasion the family still cites when her name is "
     "used as an argument, and whose telling you have it in.",
     "Render the second matriarch's economics as the story "
     "the line argues with.",
     ["inherited_tale", "character_sketch"],
     ["stories.pearl_accounts"], None),
    ("Tell the story of the doctrine's first saying: the "
     "occasion on which your grandfather Jasper Frozen first "
     "said the family's sentence, what had broken, who heard "
     "it, and how the sentence traveled from that day to your "
     "own mouth.",
     "Render the book's law at its moment of origin.",
     ["inherited_tale", "turning_point"],
     ["stories.doctrine_origin"], None),
    ("Tell the story of Slate Flames and Opal Reyes: how the "
     "heating-and-refrigeration man met the piano teacher, "
     "what each line made of the match, and the wedding as the "
     "Flames line tells it.",
     "Render the music's entry into the fire line, as a "
     "courtship.",
     ["inherited_tale", "character_sketch"],
     ["stories.slate_and_opal"], None),
    ("Tell the story of the quarrel that estranged your "
     "great-uncle Zircon: the year, what Garnet's estate had "
     "to do with it, what each side said, and what it means "
     "that your telling has only one side's version.",
     "Render the family's open account, honestly one-sided.",
     ["inherited_tale", "frame_voice"], ["stories.zircon_quarrel"],
     None),
    ("Tell the story of your parents' joining as the family "
     "tells it now: the meeting, the courtship, the wedding "
     "year, and the places where the official telling and the "
     "facts as you know them have quietly parted company.",
     "Render the set piece of the joined family, with its "
     "seams showing.",
     ["inherited_tale", "frame_voice"], ["stories.joining_told"],
     None),
    ("Tell the story of Topaz Frozen's leaving: the year she "
     "left Dallas for Chicago, what she left and what she "
     "refused to leave, and how the Frozen line's telling of "
     "her going has changed across the years.",
     "Render the line's departure story, and its revisions.",
     ["inherited_tale", "time_frame"], ["stories.topaz_leaving"],
     None),
    ("Tell the story both lines tell differently: one event "
     "the Flames line and the Frozen line each claim as proof "
     "of their own way -- each version given fairly, and where "
     "you, the child of the joining, have come to stand "
     "between them.",
     "Close the inherited tales on the teller's double "
     "inheritance of the past.",
     ["inherited_tale", "chapter_turn"], ["stories.two_versions"],
     None),
]
# Chapter 10 -- Last Stories. The closing frame: the kept
# story, the other keepers' versions, the doctrine restated by
# the respondent as a story of his own, the collection's
# purpose tested against its whole, and the last story.
Q["ch10"] = [
    ("Tell the story you have never told in the studio: what "
     "it is, why it has been kept out of the room's telling, "
     "and what has changed that lets it be told here, at the "
     "end of the book.",
     "Open the closing chapter with the kept story, admitted "
     "at last.",
     ["frame_voice", "story_rendering"], ["stories.kept_story"],
     None),
    ("Tell a story your sister tells better than you do: the "
     "story itself as she tells it, where her version beats "
     "yours, and what her keeping of it says about the two of "
     "you.",
     "Render the second keeper's title to the family's past.",
     ["inherited_tale", "character_sketch"],
     ["stories.sisters_version"], None),
    ("Tell the story of your wife's photograph: the picture "
     "that tells a story your words have never managed -- what "
     "it shows, when she took it, and what it knows about its "
     "subject that the telling keeps missing.",
     "Render the witness's medium beside the teller's, and "
     "its victory.",
     ["object_anchor", "frame_voice"],
     ["stories.wifes_photograph_story"], None),
    ("Tell the story of the doctrine tested in your own adult "
     "life: the occasion when the family's sentence was quoted "
     "at you or by you over something broken of your own, what "
     "it required, and what it cost to keep it.",
     "Give the doctrine its fullest statement in this book, "
     "as the respondent's own story rather than a frame.",
     ["story_rendering", "frame_voice"],
     ["telling.doctrine_tested"], None),
    ("Tell the story of the first Cold Room's last session: "
     "the session that ran in the room before the fire, who "
     "was in it, what was recorded, and what became of that "
     "recording.",
     "Render the lost room's last working night, in "
     "hindsight's light.",
     ["story_rendering", "scene_opening"],
     ["stories.last_session_before_fire"], None),
    ("Tell the story of a story you let go: one you used to "
     "tell and have stopped telling -- what it was, why it no "
     "longer earns its place, and what its retirement taught "
     "you about the ones you keep.",
     "Render the teller's standard by its negative: a story "
     "dismissed.",
     ["frame_voice", "ending_line"], ["telling.let_go"], None),
    ("Tell the story you tell a beginner: the first story you "
     "give a new assistant in the studio, what it is meant to "
     "teach before any technique, and the last time you told "
     "it.",
     "Render the collection's teaching instrument, in use.",
     ["frame_voice", "story_rendering"],
     ["telling.beginners_story"], None),
    ("Tell the story of the stories that are not yours to "
     "tell: the kind you have heard in the shop and the studio "
     "that you keep untold, the rule you keep about them, and "
     "the one that presses hardest against the rule.",
     "Render the teller's ethics as a kept boundary.",
     ["frame_voice", "ending_line"], ["telling.not_his"], None),
    ("What is this collection for, at the end: what does its "
     "whole telling, told whole, show your family and your "
     "trade were doing with their stories -- and what should "
     "a reader's own telling do differently for this book "
     "existing?",
     "Test the book's declared purpose against its full "
     "record.",
     ["frame_voice", "chapter_turn"], ["book.purpose_final"],
     None),
    ("End the book: what is the single story -- of the shop, "
     "the room, the road, or the lines -- that should outlast "
     "every other story in this collection, and tell it here "
     "as the last one?",
     "Close on the story that survives the telling.",
     ["story_rendering", "ending_line"], ["book.final_story"],
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
        "genre": "short-story-collection",
        "version": "1.0.0",
        "framework": FRAMEWORK,
        "chapters": [
            {"id": cid, "title": title, "act": act}
            for cid, title, act in CHAPTERS
        ],
        "questions": questions,
    }
    out = Path(__file__).resolve().parent.parent / "packs" / \
        "short-story-collection.json"
    out.write_text(json.dumps(pack, indent=1), encoding="utf-8")
    print(f"wrote {out}: {len(questions)} questions, "
          f"{len(CHAPTERS)} chapters")


if __name__ == "__main__":
    main()
