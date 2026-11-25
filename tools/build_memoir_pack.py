"""Builds packs/memoir.json: the memoir genre pack.

Each question is authored as a tuple:
    (prompt, narrative_job, [device_ids], [bible_keys], fact_or_None)
and expanded here with its chapter and generated position string.

Pack v1.1.0 adds one question the original survey never asked: who
the main character is. The first survey moved straight to the
narrator's birth year, and the narrator's identity entered the
build only as answer-file metadata -- build data, not respondent
data, the defect class the clean-proof rule exists to close (see
DEFECTS.md, M7). The identity question opens chapter 1 and declares
the subject_name fact. Published question ids are never renumbered
(the E3 lesson), so the added question takes the unused id q000 and
stands first in the question list; the original 100 questions keep
their ids, order, and pairing with the shipped book, which was
generated under pack v1.0.0 and stands as published.
"""

import json
from pathlib import Path

FRAMEWORK = {
    "voice": (
        "First-person retrospective: an older narrator looking back at a "
        "younger self, with warmth and unsparing honesty in equal measure. "
        "Concrete and plain-spoken; lyricism is earned by detail, never "
        "applied as decoration."
    ),
    "pov": "first person",
    "refrain": True,
    "tense": "past tense for scenes, present tense for reflection",
    "page_target_words": 250,
    "global_instructions": (
        "Transform the respondent's answer into memoir prose. Never "
        "contradict the story bible or the fixed facts. Do not invent "
        "named people, places, or dates that are not in the supplied "
        "material. Where the answer is brief, expand by rendering its "
        "implications as scene and detail, not by fabricating events."
    ),
    "devices": {
        "scene_rendering": {
            "name": "Scene rendering",
            "instruction": "Render the material as a lived scene with "
                           "action unfolding in time, not as summary.",
        },
        "sensory_palette": {
            "name": "Sensory palette",
            "instruction": "Anchor the page in two or three concrete "
                           "sensory details drawn from the answer "
                           "(smell, sound, texture, light).",
        },
        "motif_plant": {
            "name": "Motif planting",
            "instruction": "Introduce or repeat a concrete image from "
                           "the material so it can recur later in the "
                           "book with accumulated meaning.",
        },
        "motif_payoff": {
            "name": "Motif payoff",
            "instruction": "Return to an image established earlier in "
                           "the book and let its meaning have changed.",
        },
        "reflection_voice": {
            "name": "Reflection voice",
            "instruction": "Let the older narrator comment on the "
                           "younger self's understanding, briefly and "
                           "without condescension.",
        },
        "show_dont_tell": {
            "name": "Show, don't tell",
            "instruction": "Convert any stated emotion or judgment into "
                           "behavior, gesture, or object detail that "
                           "embodies it.",
        },
        "temporal_anchor": {
            "name": "Temporal anchor",
            "instruction": "Fix the page in time with a specific dated "
                           "or datable detail from the material.",
        },
        "character_voice": {
            "name": "Character voice",
            "instruction": "Give the person a distinctive way of "
                           "speaking or acting that could belong to no "
                           "one else in the book.",
        },
        "contrast_then_now": {
            "name": "Then-and-now contrast",
            "instruction": "Juxtapose what the narrator believed then "
                           "with what the narrator understands now.",
        },
        "object_memory": {
            "name": "Object memory",
            "instruction": "Let a physical object carry the memory; "
                           "describe the object precisely and let it "
                           "hold the feeling.",
        },
        "dialogue_reconstruction": {
            "name": "Dialogue reconstruction",
            "instruction": "Reconstruct a short exchange of dialogue "
                           "faithful to the material, with beats of "
                           "action between lines.",
        },
        "chapter_turn": {
            "name": "Chapter turn",
            "instruction": "End the page on a turn: a realization, a "
                           "question left open, or an image that points "
                           "forward in the arc.",
        },
    },
}

CHAPTERS = [
    ("ch01", "Origins", "Act I: Roots"),
    ("ch02", "The Childhood Home", "Act I: Roots"),
    ("ch03", "The People Who Raised Me", "Act I: Roots"),
    ("ch04", "The Early World", "Act II: Becoming"),
    ("ch05", "First Wounds", "Act II: Becoming"),
    ("ch06", "Becoming", "Act II: Becoming"),
    ("ch07", "Work and Calling", "Act III: The Life Built"),
    ("ch08", "Love and Partnership", "Act III: The Life Built"),
    ("ch09", "Losses and Turning Points", "Act III: The Life Built"),
    ("ch10", "Present Day and Legacy", "Act IV: The View From Here"),
]

FACT_MOTHER = {"slot": "mother_name", "kind": "person_name",
               "triggers": ["my mother", "Mother"]}
FACT_FATHER = {"slot": "father_name", "kind": "person_name",
               "triggers": ["my father", "Father"]}
FACT_HOMETOWN = {"slot": "hometown", "kind": "place_name",
                 "triggers": ["hometown", "the town I grew up in"]}
FACT_BIRTH_YEAR = {"slot": "birth_year", "kind": "year",
                   "triggers": ["I was born"]}
FACT_PARTNER = {"slot": "partner_name", "kind": "person_name",
                "triggers": ["my husband", "my wife", "my partner"]}
FACT_SUBJECT = {"slot": "subject_name", "kind": "person_name",
                "triggers": ["my name is", "My name is"]}

# The identity question added in pack v1.1.0 (see the module
# docstring). It is a literal question dict, prepended in main(),
# because the tuple expansion assigns ids sequentially and the
# published ids must not move.
IDENTITY_QUESTION = {
    "id": "q000",
    "chapter": "ch01",
    "prompt": ("Who is the main character of this memoir -- whose "
               "life is this book? Give your full name, and say how "
               "you came by it. Begin the answer with your full "
               "name."),
    "narrative_job": ("Establish the book's central identity as "
                      "respondent data: the main character is "
                      "whoever the respondent names here -- in a "
                      "memoir the narrator and the subject are the "
                      "same person -- and the fact is fixed from "
                      "this answer alone."),
    "position": ("Act I: Roots, Chapter: Origins; the survey's "
                 "opening question, before page 1 of 10 within the "
                 "chapter (added in pack v1.1.0)"),
    "devices": ["character_voice", "reflection_voice"],
    "bible_keys": ["narrator.identity"],
    "fact": FACT_SUBJECT,
}

Q = {}
Q["ch01"] = [
    ("In what year were you born, and what was happening in the world "
     "that year?",
     "Open the book by fixing the narrator in historical time.",
     ["temporal_anchor", "reflection_voice"], ["narrator.birth"],
     FACT_BIRTH_YEAR),
    ("What do you know about where your family came from before you "
     "were born?",
     "Establish the ancestral ground the life grows from.",
     ["temporal_anchor", "scene_rendering"], ["family.origins"], None),
    ("Who is the oldest relative you have a clear story about, and what "
     "is that story?",
     "Introduce the family's founding figure.",
     ["character_voice", "scene_rendering"], ["people.elder_relative"],
     None),
    ("What did your family believe about itself, the story it told "
     "about who you were?",
     "State the family myth the rest of the book will test.",
     ["motif_plant", "reflection_voice"], ["family.myth"], None),
    ("What was the economic reality your family lived in when you "
     "arrived?",
     "Ground the book in material circumstance.",
     ["sensory_palette", "show_dont_tell"], ["family.circumstances"],
     None),
    ("Were there family secrets or silences you only understood later?",
     "Plant a mystery thread that later chapters can pay off.",
     ["motif_plant", "contrast_then_now"], ["family.secret"], None),
    ("What object, photograph, or place holds your family's past most "
     "strongly?",
     "Choose the book's first object-memory anchor.",
     ["object_memory", "sensory_palette"], ["motifs.heirloom_object"],
     None),
    ("What language, faith, or custom did your family carry that set "
     "it apart from the neighbors?",
     "Establish the cultural ground of the household.",
     ["sensory_palette", "character_voice"], ["family.customs"], None),
    ("If your family had a motto, spoken or unspoken, what was it?",
     "Name the thesis the life will spend the book arguing with.",
     ["motif_plant", "reflection_voice"], ["motifs.family_motto"], None),
    ("What do you know now about your family's beginnings that you "
     "wish you had known as a child?",
     "Close the chapter on the gap between then and now.",
     ["contrast_then_now", "chapter_turn"], ["family.retrospect"], None),
]
Q["ch02"] = [
    ("Describe the first home you remember. What did it look like from "
     "outside?",
     "Establish the book's central place.",
     ["scene_rendering", "sensory_palette"], ["places.childhood_home"],
     None),
    ("Walk through the front door of that home. What did it smell and "
     "sound like?",
     "Move the reader inside the central place.",
     ["sensory_palette", "scene_rendering"],
     ["places.childhood_home_interior"], None),
    ("What town was that home in, and what was the town known for?",
     "Fix the home in its wider geography.",
     ["temporal_anchor", "sensory_palette"], ["places.hometown"],
     FACT_HOMETOWN),
    ("Which room was the heart of the house, and what happened there?",
     "Locate the household's center of gravity.",
     ["scene_rendering", "object_memory"], ["places.heart_room"], None),
    ("What was just outside your door: street, yard, water, fields?",
     "Define the boundary between home and world.",
     ["sensory_palette", "scene_rendering"], ["places.outside_the_door"],
     None),
    ("Who else lived under that roof, and who visited so often they "
     "nearly did?",
     "Populate the household beyond the immediate family.",
     ["character_voice", "scene_rendering"], ["people.household"], None),
    ("What sound from that house can you still hear exactly?",
     "Plant the household's signature sound as a motif.",
     ["motif_plant", "sensory_palette"], ["motifs.household_sound"],
     None),
    ("What was broken, patched, or made do with in that home?",
     "Show the family's circumstances through its repairs.",
     ["show_dont_tell", "object_memory"], ["places.home_repairs"], None),
    ("Describe one ordinary evening in that house, in order.",
     "Establish the baseline rhythm later chapters will break.",
     ["scene_rendering", "temporal_anchor"], ["family.ordinary_evening"],
     None),
    ("When did you last see that home, and what had changed?",
     "Close the chapter by measuring the place against time.",
     ["contrast_then_now", "chapter_turn"],
     ["places.childhood_home_last_seen"], None),
]
Q["ch03"] = [
    ("What was your mother's name, and what did people call her?",
     "Name the book's first central figure and fix the fact.",
     ["character_voice", "temporal_anchor"], ["people.mother"],
     FACT_MOTHER),
    ("Describe your mother at work, paid or unpaid. What did her hands "
     "do all day?",
     "Define the mother through her labor.",
     ["show_dont_tell", "sensory_palette"], ["people.mother_work"], None),
    ("Tell one scene that shows your mother exactly as she was.",
     "Prove the portrait with a single scene.",
     ["scene_rendering", "dialogue_reconstruction"],
     ["people.mother_scene"], None),
    ("What was your father's name, and what did people call him?",
     "Name the book's second central figure and fix the fact.",
     ["character_voice", "temporal_anchor"], ["people.father"],
     FACT_FATHER),
    ("Describe your father at work. What did the work do to him?",
     "Define the father through his labor and its cost.",
     ["show_dont_tell", "sensory_palette"], ["people.father_work"], None),
    ("Tell one scene that shows your father exactly as he was.",
     "Prove the portrait with a single scene.",
     ["scene_rendering", "dialogue_reconstruction"],
     ["people.father_scene"], None),
    ("What did your parents give each other, and what did they "
     "withhold?",
     "State the marriage's economy, which the child absorbed.",
     ["reflection_voice", "show_dont_tell"], ["family.parents_marriage"],
     None),
    ("Describe your siblings, or what it meant to have none.",
     "Complete the household's cast.",
     ["character_voice", "scene_rendering"], ["people.siblings"], None),
    ("Who in the family were you closest to, and what passed between "
     "you that words did not cover?",
     "Identify the narrator's first deep attachment.",
     ["object_memory", "reflection_voice"], ["people.closest_relative"],
     None),
    ("What did your family never say out loud?",
     "Name the household's governing silence.",
     ["motif_plant", "chapter_turn"], ["family.unsaid"], None),
]
Q["ch04"] = [
    ("Describe your first school and your first day there.",
     "Open the world beyond the household.",
     ["scene_rendering", "temporal_anchor"], ["places.first_school"],
     None),
    ("Who was your first close friend, and how did you find each other?",
     "Introduce the first chosen attachment.",
     ["character_voice", "scene_rendering"], ["people.first_friend"],
     None),
    ("What did the walk or ride to school look like?",
     "Map the daily route between home and world.",
     ["sensory_palette", "scene_rendering"], ["places.school_route"],
     None),
    ("Which teacher saw something in you, and what did they do about "
     "it?",
     "Introduce the first adult outside the family who mattered.",
     ["dialogue_reconstruction", "character_voice"], ["people.teacher"],
     None),
    ("What game, place, or ritual organized your childhood friendships?",
     "Establish the social world of the child.",
     ["scene_rendering", "motif_plant"], ["motifs.childhood_game"], None),
    ("What were you known for among the other kids?",
     "State the child's public identity.",
     ["reflection_voice", "show_dont_tell"],
     ["identity.childhood_reputation"], None),
    ("Describe a meal outside your home that you still remember.",
     "Widen the sensory world beyond the family table.",
     ["sensory_palette", "object_memory"], ["places.remembered_meal"],
     None),
    ("What scared you in that wider world, and how did you manage it?",
     "Introduce fear and the child's first strategies against it.",
     ["show_dont_tell", "scene_rendering"], ["wounds.early_fear"], None),
    ("What did you collect, build, or practice until it was yours?",
     "Plant the first sign of the adult's craft.",
     ["motif_plant", "object_memory"], ["identity.first_craft"], None),
    ("Tell about a day in that early world that still feels perfect.",
     "Set the high-water mark the losses will be measured against.",
     ["scene_rendering", "chapter_turn"], ["memories.perfect_day"], None),
]
Q["ch05"] = [
    ("What is your earliest memory of being hurt, frightened, or "
     "ashamed?",
     "Open the wounds movement with the first injury.",
     ["scene_rendering", "sensory_palette"], ["wounds.earliest"], None),
    ("Who comforted you then, or who failed to?",
     "Assign the comfort, or its absence, that shaped trust.",
     ["character_voice", "reflection_voice"], ["wounds.comfort"], None),
    ("What loss reached you first: a person, a pet, a place, a "
     "certainty?",
     "Introduce loss as a force in the book.",
     ["object_memory", "scene_rendering"], ["wounds.first_loss"], None),
    ("Describe a punishment or discipline that stayed with you.",
     "Show how authority was taught to the child.",
     ["dialogue_reconstruction", "show_dont_tell"],
     ["wounds.discipline"], None),
    ("When did you first understand that adults could be wrong or "
     "unjust?",
     "Mark the fall of adult authority.",
     ["contrast_then_now", "scene_rendering"],
     ["wounds.adult_fallibility"], None),
    ("What did you do with anger or grief as a child, having no words "
     "for it?",
     "Establish the child's coping mechanism as a pattern.",
     ["show_dont_tell", "motif_plant"], ["wounds.childhood_coping"],
     None),
    ("Was there an illness, accident, or danger that divided life into "
     "before and after?",
     "Place the first great dividing line.",
     ["temporal_anchor", "scene_rendering"], ["wounds.accident"], None),
    ("What did you blame yourself for that was not yours to carry?",
     "Name the misplaced guilt the adult must set down.",
     ["reflection_voice", "contrast_then_now"], ["wounds.self_blame"],
     None),
    ("Is there a hurt you have never fully told anyone? Tell as much of "
     "it as belongs in this book.",
     "Acknowledge the book's deepest withheld material.",
     ["reflection_voice", "show_dont_tell"], ["wounds.untold"], None),
    ("What did those early hurts teach you to do automatically, even "
     "now?",
     "Convert the wounds into the pattern the final act must answer.",
     ["motif_payoff", "chapter_turn"], ["wounds.pattern"], None),
]
Q["ch06"] = [
    ("When did you first feel your childhood ending? What happened?",
     "Close childhood with a single felt moment.",
     ["scene_rendering", "temporal_anchor"], ["identity.childhood_end"],
     None),
    ("Describe yourself at fifteen: clothes, music, room, ambitions.",
     "Fix the adolescent self in concrete detail.",
     ["sensory_palette", "show_dont_tell"], ["identity.fifteen"], None),
    ("What did you rebel against, and how did the rebellion actually "
     "look?",
     "Show the break with the household's rules.",
     ["dialogue_reconstruction", "scene_rendering"],
     ["identity.rebellion"], None),
    ("Who did you want to become, and where did that picture come from?",
     "State the adolescent ambition the adult life will judge.",
     ["reflection_voice", "motif_plant"], ["identity.aspiration"], None),
    ("Tell about your first experience of desire or first love, as much "
     "of it as belongs in the book.",
     "Introduce desire as a force.",
     ["scene_rendering", "sensory_palette"], ["love.first"], None),
    ("What did you hide from your family during those years?",
     "Establish the secret self of adolescence.",
     ["show_dont_tell", "reflection_voice"], ["identity.hidden"], None),
    ("Describe the friend or group that formed you most in adolescence.",
     "Identify the peer world that competed with the family.",
     ["character_voice", "scene_rendering"],
     ["people.adolescent_circle"], None),
    ("What risk did you take that could have gone badly, and what "
     "happened?",
     "Test the young self against real danger.",
     ["scene_rendering", "chapter_turn"], ["turning_points.first_risk"],
     None),
    ("When did you first earn, make, or build something entirely your "
     "own?",
     "Bridge adolescence to the working life.",
     ["object_memory", "show_dont_tell"], ["identity.first_making"],
     None),
    ("What did you believe at eighteen that you were certain would "
     "never change?",
     "Plant the conviction the final chapter will revisit.",
     ["contrast_then_now", "motif_plant"], ["beliefs.at_eighteen"], None),
]
Q["ch07"] = [
    ("What was your first paid work, and what did the first money feel "
     "like?",
     "Open the working life with its first transaction.",
     ["scene_rendering", "object_memory"], ["work.first_job"], None),
    ("Who taught you how to work: a boss, a parent, a failure?",
     "Identify the source of the narrator's work ethic.",
     ["character_voice", "reflection_voice"], ["people.work_mentor"],
     None),
    ("Describe the work your hands know best. Walk through it slowly.",
     "Render mastery as physical knowledge.",
     ["sensory_palette", "show_dont_tell"], ["work.craft"], None),
    ("What job or season of work nearly broke you, and how?",
     "State the working life's lowest point.",
     ["scene_rendering", "show_dont_tell"], ["work.hardest"], None),
    ("Tell about a failure at work that rearranged your life.",
     "Place the career's central turning point.",
     ["temporal_anchor", "contrast_then_now"],
     ["turning_points.work_failure"], None),
    ("When did you know what your calling was, or that you would have "
     "to invent it?",
     "State the vocation the rest of the book measures.",
     ["reflection_voice", "chapter_turn"], ["work.calling"], None),
    ("What did you make, build, or start that carries your name or your "
     "mark?",
     "Identify the signature work.",
     ["object_memory", "scene_rendering"], ["work.signature_work"], None),
    ("Who opposed your ambitions, and what did you do with that "
     "opposition?",
     "Give ambition its antagonist.",
     ["dialogue_reconstruction", "character_voice"],
     ["work.opposition"], None),
    ("What did success cost you that you did not expect to pay?",
     "Complicate the success the book has been building toward.",
     ["reflection_voice", "contrast_then_now"],
     ["work.cost_of_success"], None),
    ("If your working life had a single recurring scene, what is it?",
     "Distill the career into its emblematic image.",
     ["motif_plant", "scene_rendering"], ["motifs.work_scene"], None),
]
Q["ch08"] = [
    ("How did you meet the person who mattered most to you "
     "romantically? Begin your answer with their name, and tell the "
     "scene.",
     "Open the love movement with the meeting scene and fix the fact.",
     ["scene_rendering", "temporal_anchor"], ["people.partner"],
     FACT_PARTNER),
    ("How did you know this was different from what came before?",
     "State what distinguished the central love.",
     ["reflection_voice", "contrast_then_now"], ["love.recognition"],
     None),
    ("Describe an ordinary day with them at the relationship's best.",
     "Establish the relationship's baseline happiness.",
     ["scene_rendering", "sensory_palette"], ["love.ordinary_day"], None),
    ("What did you argue about, really, underneath the stated reasons?",
     "Name the relationship's true fault line.",
     ["dialogue_reconstruction", "show_dont_tell"], ["love.conflict"],
     None),
    ("What did love ask you to give up, and did you give it?",
     "State love's price and whether it was paid.",
     ["reflection_voice", "object_memory"], ["love.sacrifice"], None),
    ("Tell about a separation, betrayal, or breaking point, yours or "
     "theirs.",
     "Place the love story's crisis.",
     ["scene_rendering", "temporal_anchor"], ["love.breaking_point"],
     None),
    ("What object, song, or place belongs to that love now?",
     "Choose the love's enduring emblem.",
     ["object_memory", "motif_plant"], ["motifs.love_object"], None),
    ("What did that relationship teach you about your own patterns?",
     "Convert the love story into self-knowledge.",
     ["contrast_then_now", "reflection_voice"], ["love.pattern_lesson"],
     None),
    ("Describe the children, if there are any, or the life that filled "
     "that space.",
     "Account for what the partnership produced or chose.",
     ["character_voice", "scene_rendering"], ["family.children"], None),
    ("What remains unresolved in love, even now?",
     "Leave the love movement honestly unfinished.",
     ["reflection_voice", "chapter_turn"], ["love.unresolved"], None),
]
Q["ch09"] = [
    ("Tell about the death that changed you most. Who were they, and "
     "how did you learn of it?",
     "Open the losses movement with the central death.",
     ["scene_rendering", "temporal_anchor"], ["losses.central_death"],
     None),
    ("What did grief actually look like in your daily life afterward?",
     "Render grief as routine, not event.",
     ["show_dont_tell", "sensory_palette"], ["losses.grief_daily"], None),
    ("Describe a place you lost: a home, a town, a country, a "
     "workplace.",
     "Extend loss from people to places.",
     ["sensory_palette", "contrast_then_now"], ["losses.lost_place"],
     None),
    ("Tell about the day everything changed direction, for better or "
     "worse.",
     "Place the book's hinge day.",
     ["temporal_anchor", "scene_rendering"],
     ["turning_points.the_day"], None),
    ("What did you walk away from, and what did walking away cost?",
     "Account for the chosen loss.",
     ["reflection_voice", "show_dont_tell"],
     ["turning_points.walked_away"], None),
    ("Was there a disaster, a storm, fire, illness, or collapse, that "
     "rearranged your world?",
     "Give the book its external catastrophe, if it has one.",
     ["scene_rendering", "sensory_palette"], ["losses.disaster"], None),
    ("Who did you fail, and what do you carry from it?",
     "Balance the book's grievances with the narrator's own debt.",
     ["reflection_voice", "contrast_then_now"],
     ["losses.failure_toward_other"], None),
    ("What did you survive that you once thought you could not?",
     "State the proven limit of the narrator's endurance.",
     ["scene_rendering", "chapter_turn"], ["turning_points.survival"],
     None),
    ("Tell about a goodbye you did not know was final.",
     "Close the movement on unrecognized finality.",
     ["motif_payoff", "scene_rendering"], ["losses.last_goodbye"], None),
    ("What did loss leave in your hands that you still use?",
     "Convert loss into inheritance.",
     ["object_memory", "motif_payoff"], ["losses.inheritance"], None),
]
Q["ch10"] = [
    ("Describe where you live now, through the same senses you used "
     "for the first home.",
     "Mirror the childhood home chapter to measure the life.",
     ["sensory_palette", "motif_payoff"], ["places.home_now"], None),
    ("Walk through your ordinary day now. What fills it?",
     "Establish the present-day baseline.",
     ["scene_rendering", "show_dont_tell"], ["present.ordinary_day"],
     None),
    ("Which people from this book are still in your life, and which are "
     "gone?",
     "Take roll of the cast at the end.",
     ["reflection_voice", "character_voice"], ["present.who_remains"],
     None),
    ("What do you believe now that your eighteen-year-old self would "
     "argue with?",
     "Pay off the conviction planted in the becoming chapter.",
     ["contrast_then_now", "motif_payoff"], ["beliefs.now"], None),
    ("What pattern from your earliest hurts have you finally "
     "interrupted, or not?",
     "Answer the wounds chapter's pattern question.",
     ["contrast_then_now", "reflection_voice"], ["present.pattern_now"],
     None),
    ("What work of your hands are you proudest of, and where is it now?",
     "Close the work movement with its verdict.",
     ["object_memory", "reflection_voice"], ["present.proudest_work"],
     None),
    ("What do you still want, plainly stated?",
     "Keep the ending open toward desire, not summary.",
     ["reflection_voice", "show_dont_tell"], ["present.want"], None),
    ("What would you tell the child in the first chapters, if you could "
     "stand in that doorway?",
     "Address the younger self directly across the whole book.",
     ["reflection_voice", "motif_payoff"],
     ["legacy.letter_to_child_self"], None),
    ("What should be done with your things, your stories, and your name "
     "when you are gone?",
     "State the narrator's instructions to the future.",
     ["object_memory", "temporal_anchor"], ["legacy.instructions"],
     None),
    ("End the book: what is the single image you want to leave the "
     "reader holding?",
     "Close on the final image, gathering the book's motifs.",
     ["motif_payoff", "chapter_turn"], ["motifs.final_image"], None),
]


def main() -> None:
    questions = []
    chapter_meta = {cid: (title, act) for cid, title, act in CHAPTERS}
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
    questions.insert(0, IDENTITY_QUESTION)
    pack = {
        "genre": "memoir",
        "version": "1.1.0",
        "framework": FRAMEWORK,
        "chapters": [
            {"id": cid, "title": title, "act": act}
            for cid, title, act in CHAPTERS
        ],
        "questions": questions,
    }
    out = Path(__file__).resolve().parent.parent / "packs" / "memoir.json"
    out.write_text(json.dumps(pack, indent=1), encoding="utf-8")
    print(f"wrote {out}: {len(questions)} questions, "
          f"{len(CHAPTERS)} chapters")


if __name__ == "__main__":
    main()
