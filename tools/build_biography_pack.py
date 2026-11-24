"""Builds packs/biography.json: the biography genre pack (100 questions).

Each question is authored as a tuple:
    (prompt, narrative_job, [device_ids], [bible_keys], fact_or_None)
and expanded here with its chapter and generated position string.

The pack's defining difference from the memoir pack is point of view:
the respondent answers about another person, and the framework writes
that life in the third person. Fact triggers are therefore phrased
from the subject ("his mother", "He was born") rather than from a
first-person narrator ("my mother", "I was born"), and both pronoun
sets are declared so the pack serves a subject of any gender.
"""

import json
from pathlib import Path

FRAMEWORK = {
    "voice": (
        "Third-person retrospective: a narrator outside the life, "
        "writing after the fact, who keeps what the record shows "
        "distinct from what witnesses remember. Plain, exact, and warm "
        "without worship; the subject is rendered as a person, not a "
        "monument, and judgment is earned by evidence."
    ),
    "pov": "third person",
    "refrain": False,
    "tense": "past tense for the life, present tense for the record "
             "and the legacy",
    "page_target_words": 250,
    "global_instructions": (
        "Transform the respondent's answers about the subject into "
        "biography prose in the third person. Never contradict the "
        "story bible or the fixed facts. Do not invent named people, "
        "places, or dates that are not in the supplied material. "
        "Where the material is thin, expand by rendering its "
        "documented implications as scene and context, not by "
        "fabricating events. Attribute memory as memory and record "
        "as record."
    ),
    "devices": {
        "scene_reconstruction": {
            "name": "Scene reconstruction",
            "instruction": "Reconstruct a documented moment as a scene "
                           "unfolding in time. Stay inside what the "
                           "material supports: setting, gesture, and "
                           "sequence may be rendered, but no event, "
                           "person, or date may be added that the "
                           "material does not contain.",
        },
        "period_detail": {
            "name": "Period detail",
            "instruction": "Anchor the page in two or three concrete "
                           "period details drawn from the material "
                           "(tools, prices, clothing, sounds, the "
                           "weather of the era).",
        },
        "documentary_anchor": {
            "name": "Documentary anchor",
            "instruction": "Fix the page to a datable record: a year, "
                           "a document, a public event, or an artifact "
                           "named in the material, and let the "
                           "narrative hang from it.",
        },
        "voice_of_record": {
            "name": "Voice of the record",
            "instruction": "Distinguish the record from the memory: "
                           "where the material gives documents, dates, "
                           "or official fact, present them as record; "
                           "where it gives recollection, present it as "
                           "recollection, attributed to who remembers.",
        },
        "subjects_own_words": {
            "name": "The subject's own words",
            "instruction": "Where the material supplies the subject's "
                           "own recorded words (a letter, a saying, a "
                           "written note), bring them onto the page as "
                           "the subject's voice, clearly theirs, not "
                           "the narrator's.",
        },
        "contextual_frame": {
            "name": "Contextual frame",
            "instruction": "Place the life against the era's public "
                           "events for a paragraph at most, then "
                           "return to the person; the era explains the "
                           "life, it does not replace it.",
        },
        "character_portrait": {
            "name": "Character portrait",
            "instruction": "Build the subject through observed habit: "
                           "how the subject worked, spoke, dressed, "
                           "decided. One page should leave one trait "
                           "standing.",
        },
        "testimony_weave": {
            "name": "Testimony weave",
            "instruction": "Bring in what others said about the "
                           "subject (family, colleagues, rivals), "
                           "attributed to them, and let agreement or "
                           "disagreement with the record stand visible.",
        },
        "object_evidence": {
            "name": "Object evidence",
            "instruction": "Let a surviving object carry the page: a "
                           "tool, a photograph, a patent, a house. "
                           "Describe it exactly and let it testify.",
        },
        "turning_point": {
            "name": "Turning point",
            "instruction": "Mark the decision or event the life "
                           "pivots on. Show the state of things before "
                           "it and the first consequence after it.",
        },
        "reputation_vs_record": {
            "name": "Reputation against record",
            "instruction": "Set the legend about the subject beside "
                           "the documented fact and weigh them openly; "
                           "where they differ, say so and follow the "
                           "record.",
        },
        "legacy_lens": {
            "name": "Legacy lens",
            "instruction": "Trace one consequence of the subject's "
                           "life or work forward into the present: what "
                           "still exists, is still used, is still told.",
        },
        "chapter_turn": {
            "name": "Chapter turn",
            "instruction": "End the page on a turn: a question the "
                           "next chapter answers, an image that points "
                           "forward, or a fact that reframes what came "
                           "before.",
        },
    },
}

CHAPTERS = [
    ("ch01", "Before the Beginning", "Act I: The Ground"),
    ("ch02", "Birth and First Years", "Act I: The Ground"),
    ("ch03", "The Making of the Child", "Act I: The Ground"),
    ("ch04", "Apprenticeship", "Act II: The Trade"),
    ("ch05", "The Young Adult", "Act II: The Trade"),
    ("ch06", "The Work", "Act III: The Achievement"),
    ("ch07", "Love and Household", "Act III: The Achievement"),
    ("ch08", "Standing and Struggle", "Act III: The Achievement"),
    ("ch09", "Late Years and Death", "Act IV: The Reckoning"),
    ("ch10", "Legacy", "Act IV: The Reckoning"),
]

FACT_SUBJECT = {"slot": "subject_name", "kind": "person_name",
                "triggers": ["the subject"]}
FACT_BIRTH_YEAR = {"slot": "birth_year", "kind": "year",
                   "triggers": ["He was born", "She was born",
                                "the subject was born"]}
FACT_BIRTHPLACE = {"slot": "birthplace", "kind": "place_name",
                   "triggers": ["He was born in", "She was born in",
                                "the subject was born in"]}
FACT_MOTHER = {"slot": "mother_name", "kind": "person_name",
               "triggers": ["his mother", "her mother",
                            "the subject's mother"]}
FACT_FATHER = {"slot": "father_name", "kind": "person_name",
               "triggers": ["his father", "her father",
                            "the subject's father"]}
FACT_PARTNER = {"slot": "partner_name", "kind": "person_name",
                "triggers": ["his wife", "her husband", "his husband",
                             "her wife", "his partner", "her partner",
                             "the subject's wife",
                             "the subject's husband"]}
FACT_DEATH_YEAR = {"slot": "death_year", "kind": "year",
                   "triggers": ["He died", "She died",
                                "the subject died"]}

Q = {}
Q["ch01"] = [
    ("What is the subject's full name, and by what name was the "
     "subject known in daily life?",
     "Open the book by naming the subject and fixing the fact.",
     ["documentary_anchor", "character_portrait"], ["subject.name"],
     FACT_SUBJECT),
    ("Where did the subject's family come from, and how did they "
     "arrive in the place where the subject's life begins?",
     "Establish the ancestral ground the life grows from.",
     ["contextual_frame", "documentary_anchor"], ["family.origins"],
     None),
    ("What was the subject's mother's name, and what was she called?",
     "Name the first of the two people who made the subject, and fix "
     "the fact.",
     ["character_portrait", "documentary_anchor"], ["people.mother"],
     FACT_MOTHER),
    ("What did the subject's mother do, in work and in the household, "
     "and what was she known for?",
     "Define the mother through her labor and her reputation.",
     ["character_portrait", "period_detail"], ["people.mother_work"],
     None),
    ("What was the subject's father's name, and what was he called?",
     "Name the second maker of the subject, and fix the fact.",
     ["character_portrait", "documentary_anchor"], ["people.father"],
     FACT_FATHER),
    ("What did the subject's father do for a living, and what did the "
     "work make of him?",
     "Define the father through his trade and its effects.",
     ["character_portrait", "period_detail"], ["people.father_work"],
     None),
    ("How did the subject's parents meet, and what did each bring to "
     "the marriage?",
     "State the founding union of the subject's world.",
     ["scene_reconstruction", "testimony_weave"],
     ["family.parents_meeting"], None),
    ("What did the family believe about itself: the story it told "
     "about who they were?",
     "State the family myth the subject's life will test.",
     ["voice_of_record", "reputation_vs_record"], ["family.myth"],
     None),
    ("What were the family's material circumstances in the generation "
     "before the subject: property, debts, standing?",
     "Ground the book in the family's material reality.",
     ["documentary_anchor", "period_detail"],
     ["family.circumstances"], None),
    ("What object, document, or place survives from the family's "
     "earlier generation, and what does it show?",
     "Choose the book's first piece of physical evidence.",
     ["object_evidence", "chapter_turn"], ["motifs.heirloom_object"],
     None),
]
Q["ch02"] = [
    ("In what year was the subject born, and what was happening in "
     "the world that year?",
     "Fix the subject in historical time, and fix the fact.",
     ["documentary_anchor", "contextual_frame"], ["subject.birth"],
     FACT_BIRTH_YEAR),
    ("In what place was the subject born: the town or city, and the "
     "specific setting, a house, a hospital, a farm?",
     "Fix the birthplace as fact and as scene.",
     ["scene_reconstruction", "period_detail"],
     ["places.birthplace"], FACT_BIRTHPLACE),
    ("What is recorded or remembered about the day of the birth "
     "itself?",
     "Render the first day from record and memory, keeping the two "
     "distinct.",
     ["voice_of_record", "scene_reconstruction"], ["subject.birth_day"],
     None),
    ("Who was present in the household at the subject's birth: "
     "siblings, grandparents, others under the roof?",
     "Populate the world the subject entered.",
     ["character_portrait", "period_detail"],
     ["people.household_at_birth"], None),
    ("What was the subject named for, and who chose the name?",
     "Explain the name as the family's first statement about the "
     "child.",
     ["subjects_own_words", "voice_of_record"], ["subject.name_origin"],
     None),
    ("What did the home the subject was born into look, sound, and "
     "smell like?",
     "Establish the first place through the senses.",
     ["period_detail", "scene_reconstruction"], ["places.first_home"],
     None),
    ("What hardship or good fortune marked the family's circumstances "
     "in the subject's first years?",
     "Set the material weather of the early chapters.",
     ["contextual_frame", "documentary_anchor"],
     ["family.early_circumstances"], None),
    ("What is the earliest surviving record of the subject: a "
     "photograph, a registry entry, an object?",
     "Introduce the archive the biography will draw on.",
     ["object_evidence", "voice_of_record"],
     ["record.earliest_artifact"], None),
    ("What did the people around the subject expect the child to "
     "become?",
     "State the first prediction the life will answer.",
     ["testimony_weave", "chapter_turn"], ["subject.expectations"],
     None),
    ("What story about the subject's infancy did the family retell "
     "most often, and what does it claim about the child?",
     "Close the chapter on the family's first legend of the subject.",
     ["testimony_weave", "reputation_vs_record"],
     ["subject.infancy_story"], None),
]
Q["ch03"] = [
    ("Describe the home the subject grew up in, room by room if the "
     "record allows.",
     "Establish the central place of the childhood.",
     ["scene_reconstruction", "period_detail"],
     ["places.childhood_home"], None),
    ("What work did the child see done every day, and by whom?",
     "Show the child the world's labor at close range.",
     ["character_portrait", "period_detail"], ["childhood.work_seen"],
     None),
    ("What was the subject's schooling: where, how far, and with what "
     "distinction or difficulty?",
     "Fix the formal education as record.",
     ["documentary_anchor", "voice_of_record"], ["subject.schooling"],
     None),
    ("Which teacher, elder, or neighbor first treated the subject as "
     "capable, and what happened?",
     "Introduce the first adult outside the family who mattered.",
     ["scene_reconstruction", "testimony_weave"],
     ["people.first_recognizer"], None),
    ("What did the child make, collect, take apart, or practice until "
     "it was a known trait?",
     "Plant the first sign of the adult's craft.",
     ["character_portrait", "object_evidence"],
     ["identity.first_craft"], None),
    ("Who was the subject's closest childhood friend, and what did "
     "the two do together?",
     "Introduce the first chosen attachment.",
     ["scene_reconstruction", "character_portrait"],
     ["people.childhood_friend"], None),
    ("What illness, accident, loss, or fright marked the childhood?",
     "Place the childhood's dividing event.",
     ["scene_reconstruction", "documentary_anchor"],
     ["childhood.marking_event"], None),
    ("What did the family require of the child: chores, faith, "
     "silence, achievement?",
     "State the household's demands as the child's first law.",
     ["voice_of_record", "period_detail"], ["family.requirements"],
     None),
    ("What trait did adults remark on in the child, in praise or in "
     "complaint?",
     "State the child's public identity as others recorded it.",
     ["testimony_weave", "reputation_vs_record"],
     ["identity.remarked_trait"], None),
    ("When did the child first show the direction of the adult life, "
     "and who noticed?",
     "Close the childhood on its first visible turning.",
     ["turning_point", "chapter_turn"], ["identity.first_direction"],
     None),
]
Q["ch04"] = [
    ("What was the subject's first paid or formal work, and how was "
     "it obtained?",
     "Open the working life with its first transaction.",
     ["documentary_anchor", "scene_reconstruction"],
     ["work.first_job"], None),
    ("Who taught the subject the trade or discipline, and what was "
     "the teacher's method?",
     "Identify the master the apprenticeship answers to.",
     ["character_portrait", "testimony_weave"], ["people.mentor"],
     None),
    ("Describe one working day of the apprenticeship in sequence, "
     "from start to finish.",
     "Establish the baseline rhythm of the learning years.",
     ["scene_reconstruction", "period_detail"],
     ["work.apprentice_day"], None),
    ("What did the subject's hands, or mind, learn in those years "
     "that never left?",
     "Render mastery as physical knowledge acquired early.",
     ["character_portrait", "object_evidence"],
     ["work.early_mastery"], None),
    ("What mistake, failure, or humiliation of the apprenticeship is "
     "still part of the record?",
     "Give the learning years their documented wound.",
     ["voice_of_record", "turning_point"], ["work.early_failure"],
     None),
    ("What did the subject earn, and what did the first earnings buy "
     "or make possible?",
     "Convert wages into the first independence.",
     ["documentary_anchor", "period_detail"], ["work.first_earnings"],
     None),
    ("Who were the subject's rivals or companions in learning the "
     "trade, and where did they end?",
     "Populate the trade's world and measure the subject against it.",
     ["testimony_weave", "character_portrait"],
     ["people.trade_companions"], None),
    ("What tool, instrument, or book of the apprenticeship did the "
     "subject keep for life?",
     "Choose the object that carries the trade's meaning.",
     ["object_evidence", "legacy_lens"], ["motifs.kept_tool"], None),
    ("What did the subject decide, during the apprenticeship, never "
     "to do or never to become?",
     "State the refusal the mature work will honor.",
     ["turning_point", "voice_of_record"], ["identity.refusal"], None),
    ("When did the apprenticeship end, and what marked the subject "
     "as ready?",
     "Close the learning years on the sign of readiness.",
     ["turning_point", "chapter_turn"], ["work.apprenticeship_end"],
     None),
]
Q["ch05"] = [
    ("What did the subject look like, dress like, and sound like on "
     "entering adult life?",
     "Fix the young adult in concrete detail.",
     ["character_portrait", "period_detail"], ["identity.young_adult"],
     None),
    ("What was the first independent decision the subject made that "
     "the family opposed or doubted?",
     "Show the break toward self-direction.",
     ["turning_point", "scene_reconstruction"],
     ["turning_points.first_independence"], None),
    ("What public events of the era (war, depression, migration, "
     "law) pressed on the subject's choices in these years?",
     "Give the young life its historical weather.",
     ["contextual_frame", "documentary_anchor"], ["era.pressures"],
     None),
    ("Where did the subject live as a young adult, and what did the "
     "place demand and allow?",
     "Define the first self-chosen ground.",
     ["scene_reconstruction", "period_detail"],
     ["places.young_adult_home"], None),
    ("What risk did the subject take in these years that could have "
     "ended the story early?",
     "Test the young adult against real danger.",
     ["scene_reconstruction", "turning_point"],
     ["turning_points.early_risk"], None),
    ("Who believed in the subject before there was evidence, and what "
     "did that belief cost them?",
     "Identify the early believer and the price of believing.",
     ["testimony_weave", "character_portrait"],
     ["people.early_believer"], None),
    ("What did the subject want, stated as plainly as the record "
     "allows?",
     "State the ambition the achievement chapters will judge.",
     ["voice_of_record", "subjects_own_words"], ["identity.ambition"],
     None),
    ("What early work of the subject survives, and what does it show "
     "about the mature manner?",
     "Read the mature style in its first surviving evidence.",
     ["object_evidence", "legacy_lens"], ["work.early_surviving"],
     None),
    ("What did the subject give up, or refuse, in these years, and "
     "was it ever recovered?",
     "Account for the young life's chosen loss.",
     ["turning_point", "voice_of_record"], ["turning_points.given_up"],
     None),
    ("What question was the subject's life asking, by the end of the "
     "young adult years?",
     "Close the act on the question the work must answer.",
     ["chapter_turn", "reputation_vs_record"], ["identity.open_question"],
     None),
]
Q["ch06"] = [
    ("What is the work the subject is known for, stated in one plain "
     "sentence?",
     "State the achievement the book exists to examine.",
     ["documentary_anchor", "reputation_vs_record"], ["work.known_for"],
     None),
    ("How did that work begin: the occasion, the problem, the first "
     "attempt?",
     "Place the achievement's origin scene.",
     ["scene_reconstruction", "turning_point"], ["work.beginning"],
     None),
    ("Describe the subject's mature working method: where, when, "
     "with what tools or habits?",
     "Render mastery as routine, not inspiration.",
     ["character_portrait", "period_detail"], ["work.method"], None),
    ("What did the subject make, build, found, or publish that "
     "carries the name into the present?",
     "Identify the signature work and its survival.",
     ["object_evidence", "legacy_lens"], ["work.signature"], None),
    ("Who worked with the subject at the height of the powers, and "
     "what did they say about it?",
     "Let the collaborators testify to the prime.",
     ["testimony_weave", "character_portrait"],
     ["people.collaborators"], None),
    ("What did the work cost: money, health, years, other people's "
     "claims?",
     "State the achievement's price without flinching.",
     ["voice_of_record", "contextual_frame"], ["work.cost"], None),
    ("What was the subject's relation to money and ownership in the "
     "work: wages, patents, shares, credit?",
     "Fix the economics of the achievement as record.",
     ["documentary_anchor", "voice_of_record"], ["work.money"], None),
    ("What is the best-documented single day or episode of the mature "
     "work?",
     "Prove the portrait of the prime with one documented episode.",
     ["scene_reconstruction", "documentary_anchor"],
     ["work.best_documented_episode"], None),
    ("What did the subject refuse to make, do, or sign, even at a "
     "price?",
     "Give the achievement its ethical boundary.",
     ["subjects_own_words", "turning_point"], ["work.refusal"], None),
    ("What did the subject understand about the work that "
     "contemporaries did not?",
     "Close the achievement on the subject's singular insight.",
     ["reputation_vs_record", "chapter_turn"], ["work.understanding"],
     None),
]
Q["ch07"] = [
    ("What was the partner's name, and how did the subject and the "
     "partner meet? Begin the answer with the partner's full name.",
     "Introduce the partner, fix the fact, and render the meeting "
     "from the record.",
     ["scene_reconstruction", "documentary_anchor"], ["people.partner"],
     FACT_PARTNER),
    ("What did the partner bring to the life that the subject could "
     "not supply alone?",
     "State the partnership's division of gifts.",
     ["character_portrait", "testimony_weave"],
     ["people.partner_contribution"], None),
    ("Describe the household the two made: its rooms, routines, and "
     "economy.",
     "Establish the domestic world of the prime years.",
     ["scene_reconstruction", "period_detail"], ["places.household"],
     None),
    ("What children were there, or what filled that place in the "
     "life, and how did the subject meet it?",
     "Account for what the partnership produced or chose.",
     ["character_portrait", "voice_of_record"], ["family.children"],
     None),
    ("What was the subject like in private, according to those who "
     "lived with the subject?",
     "Correct the public portrait with the household's testimony.",
     ["testimony_weave", "reputation_vs_record"],
     ["identity.private_self"], None),
    ("What strain did the work place on the household, and how was "
     "it answered?",
     "Name the domestic price of the achievement.",
     ["scene_reconstruction", "voice_of_record"], ["family.strain"],
     None),
    ("What did the partner and the subject argue about, underneath "
     "the stated reasons?",
     "Name the partnership's true fault line.",
     ["subjects_own_words", "testimony_weave"], ["family.conflict"],
     None),
    ("What object, place, or ritual belonged to the partnership "
     "itself?",
     "Choose the partnership's enduring emblem.",
     ["object_evidence", "period_detail"],
     ["motifs.partnership_object"], None),
    ("What did the partner's own work or life amount to, apart from "
     "the subject?",
     "Restore the partner as a person, not an appendage.",
     ["character_portrait", "documentary_anchor"],
     ["people.partner_life"], None),
    ("What remained unresolved in the household when the prime years "
     "closed?",
     "Leave the household honestly unfinished.",
     ["chapter_turn", "voice_of_record"], ["family.unresolved"], None),
]
Q["ch08"] = [
    ("What was the subject's public standing at its height, and who "
     "conferred it?",
     "Fix the reputation's peak as record.",
     ["documentary_anchor", "reputation_vs_record"], ["standing.height"],
     None),
    ("Who opposed the subject, and on what grounds, stated fairly?",
     "Give the opposition its honest hearing.",
     ["testimony_weave", "voice_of_record"], ["standing.opposition"],
     None),
    ("What was the subject's greatest public failure or reversal, "
     "and how was it recorded at the time?",
     "Place the standing's central wound, as the record kept it.",
     ["documentary_anchor", "scene_reconstruction"],
     ["standing.failure"], None),
    ("What did the subject do in the year after that failure?",
     "Show the character of the recovery, or its absence.",
     ["turning_point", "character_portrait"],
     ["standing.after_failure"], None),
    ("What controversy, dispute, or lawsuit attaches to the name, "
     "and what does the record show?",
     "Examine the name's contested ground on the evidence.",
     ["voice_of_record", "documentary_anchor"],
     ["standing.controversy"], None),
    ("What did the newspapers, journals, or official records of the "
     "day say about the subject?",
     "Let the period's record speak in its own voice.",
     ["voice_of_record", "testimony_weave"], ["record.press"], None),
    ("What did the subject say, in public or in writing, that is "
     "still quoted?",
     "Select the words the present still uses.",
     ["subjects_own_words", "legacy_lens"], ["record.quoted_words"],
     None),
    ("Where does the legend about the subject most clearly part from "
     "the documented record?",
     "Perform the biography's central act of correction.",
     ["reputation_vs_record", "voice_of_record"],
     ["standing.legend_vs_record"], None),
    ("What did standing cost the subject's private life or health?",
     "Carry the reputation's price back into the household.",
     ["character_portrait", "contextual_frame"], ["standing.cost"],
     None),
    ("What did the subject do with honors, money, or fame once they "
     "arrived?",
     "Close the standing on the use made of it.",
     ["scene_reconstruction", "chapter_turn"], ["standing.use_of_fame"],
     None),
]
Q["ch09"] = [
    ("When did the subject's powers begin to change, and how did the "
     "subject meet the change?",
     "Open the final movement on the first diminishment.",
     ["character_portrait", "voice_of_record"], ["late_years.change"],
     None),
    ("What was the subject's last work, and how does it stand against "
     "the prime work?",
     "Judge the last work beside the best.",
     ["object_evidence", "reputation_vs_record"], ["work.last"], None),
    ("Who gathered around the subject in the late years, and who was "
     "absent?",
     "Take roll of the final circle.",
     ["testimony_weave", "character_portrait"], ["late_years.circle"],
     None),
    ("What did the subject settle, forgive, or leave deliberately "
     "unsettled?",
     "Account for the final reckonings.",
     ["subjects_own_words", "turning_point"],
     ["late_years.settlements"], None),
    ("Describe the place of the late years, through the senses, as "
     "the childhood home was described.",
     "Mirror the childhood home chapter to measure the life.",
     ["scene_reconstruction", "period_detail"], ["places.late_home"],
     None),
    ("What illness, decline, or accident framed the final period?",
     "State the body's final terms as record.",
     ["documentary_anchor", "voice_of_record"], ["late_years.decline"],
     None),
    ("In what year did the subject die, and what were the "
     "circumstances, as recorded? Begin the answer with the year.",
     "Record the death as fact, with its circumstances, plainly.",
     ["documentary_anchor", "voice_of_record"], ["subject.death"],
     FACT_DEATH_YEAR),
    ("Who was present at the end, or who received the news, and how?",
     "Render the death's witnesses from the record.",
     ["scene_reconstruction", "testimony_weave"],
     ["subject.death_witnesses"], None),
    ("What were the subject's last recorded words or acts, and how "
     "reliable is the record of them?",
     "Weigh the final testimony as evidence.",
     ["subjects_own_words", "voice_of_record"], ["record.last_words"],
     None),
    ("How was the death marked: funeral, obituary, memorial, "
     "silence?",
     "Close the life on its public marking.",
     ["documentary_anchor", "chapter_turn"], ["subject.funeral"], None),
]
Q["ch10"] = [
    ("What of the subject's work is still in use, standing, or read "
     "today?",
     "Open the legacy on survival, not sentiment.",
     ["legacy_lens", "object_evidence"], ["legacy.work_surviving"],
     None),
    ("What happened to the subject's house, tools, papers, and "
     "effects after the death?",
     "Account for the material remains.",
     ["object_evidence", "documentary_anchor"], ["legacy.effects"],
     None),
    ("How did the partner's and the children's lives run after the "
     "subject's death?",
     "Follow the household past the life's end.",
     ["character_portrait", "voice_of_record"], ["legacy.family_after"],
     None),
    ("What did the obituaries and first assessments get right, and "
     "what did they miss?",
     "Audit the first draft of the reputation.",
     ["reputation_vs_record", "voice_of_record"],
     ["legacy.first_assessments"], None),
    ("Which later figure, firm, or school took up the subject's work, "
     "and what did they change?",
     "Trace the work's descent into other hands.",
     ["legacy_lens", "testimony_weave"], ["legacy.successors"], None),
    ("What is the strongest claim made for the subject's importance, "
     "and does the record support it?",
     "Test the largest claim against the evidence.",
     ["reputation_vs_record", "documentary_anchor"],
     ["legacy.importance_claim"], None),
    ("What is the strongest criticism of the subject, and does the "
     "record support it?",
     "Test the hardest criticism against the evidence.",
     ["reputation_vs_record", "testimony_weave"], ["legacy.criticism"],
     None),
    ("What single object should a stranger hold to understand the "
     "subject, and why?",
     "Choose the legacy's one piece of evidence.",
     ["object_evidence", "legacy_lens"], ["motifs.legacy_object"],
     None),
    ("What would the subject make of the present standing of the "
     "work, judging by the recorded words?",
     "Let the subject's own words judge the legacy.",
     ["subjects_own_words", "legacy_lens"], ["legacy.subjects_view"],
     None),
    ("End the book: what is the single documented fact about the "
     "subject that should outlast every legend?",
     "Close on the fact that survives the legend.",
     ["documentary_anchor", "chapter_turn"], ["legacy.final_fact"],
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
        "genre": "biography",
        "version": "1.0.0",
        "framework": FRAMEWORK,
        "chapters": [
            {"id": cid, "title": title, "act": act}
            for cid, title, act in CHAPTERS
        ],
        "questions": questions,
    }
    out = Path(__file__).resolve().parent.parent / "packs" / "biography.json"
    out.write_text(json.dumps(pack, indent=1), encoding="utf-8")
    print(f"wrote {out}: {len(questions)} questions, "
          f"{len(CHAPTERS)} chapters")


if __name__ == "__main__":
    main()
