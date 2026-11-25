#!/usr/bin/env python3
"""Build the biography pack's demonstration answers.

The demonstration user of the series is Frozen In Flames, a fictional
persona. The canonical facts of the character's invented life live in
demo/frozen-in-flames-character.json; this script loads that record
and writes the character's answers to all 100 biography questions,
with the fact-bearing answers interpolated from the record so the
two cannot drift apart. A consistency check runs before anything is
written: every recorded fact must appear in its designated answer,
the birth-year answer's first year must be the record's year, every
year mentioned anywhere in the answers must be a year the record
supports, the death-year question must contain no year (the
character is living; no death fact is established), and no token of
the superseded canon (the biography build's invented values: born
1960 in Memphis; mother Evelyn; father Harold; partner Alice) may
appear.

Corrected edition (2026-11-25): the answers originally shipped with
release v0.2.0 were written against values the biography build
invented because the survey never asked the author (see DEFECTS.md,
B4). The author has since set the canon (record version 2.0.0):
born 2000 in Dallas, Texas; mother Ruby Flames; father Onyx Frozen;
partner Amber Flames. These answers are drawn from that record, and
they generate the corrected edition of "The Cold Room" (v0.2.1).
The v0.2.0 book and its answers stand in git history at that tag.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHARACTER_PATH = ROOT / "demo" / "frozen-in-flames-character.json"
OUT_PATH = ROOT / "demo" / "biography-demo-answers.json"

RECORD = json.loads(CHARACTER_PATH.read_text(encoding="utf-8"))
F = RECORD["facts"]
NAME = F["subject_name"]
MOTHER = F["mother_name"]
FATHER = F["father_name"]
PARTNER = F["partner_name"]
BIRTH_YEAR = F["birth_year"]
BIRTHPLACE = F["birthplace"]

# Every year the canonical record supports: line founders' births,
# deaths, and migrations; the parents' births, meeting, and
# marriage; the subject's birth and the record's defining events;
# the present year of the record's frame. An answer that reaches
# for any other year is reaching outside the record.
ALLOWED_YEARS = {
    1918, 1920, 1921, 1923, 1946, 1947, 1948, 1949, 1950, 1951,
    1969, 1973, 1975, 1976, 1979, 1992, 1994, 1998, 1999, 2000,
    2001, 2003, 2014, 2016, 2018, 2019, 2022, 2023, 2024, 2026,
}

ANSWERS: dict[str, str] = {
    # Chapter 1 -- Before the Beginning
    "q001": (
        f"{NAME}. The name is given in full because it is the name "
        "the whole record uses: the subject of this biography, a "
        "musician and recording engineer of Dallas, Texas, known in "
        "daily life, and in every studio he has worked in, simply "
        "as Frozen. The name itself is the first fact of the life: "
        "it is the union of his family's two lines, his father's "
        "name and his mother's, joined in the first child of their "
        "marriage. He is a white American, red-haired and "
        "blue-eyed, and the witnesses describe a man who listens "
        "the way other men look: completely, and before anything "
        "else."
    ),
    "q002": (
        "The subject's family came from two places and arrived in "
        "Dallas by two roads a generation apart. His mother's line, "
        "the Flames line, came from Holly Springs, Mississippi: "
        "Garnet Flames, a keeper of furnaces and boilers, brought "
        "his family to Dallas in 1949. His father's line, the "
        "Frozen line, came from Pittsburgh, Pennsylvania: Flint "
        "Frozen, a millwright and machinist, carried his toolbox "
        "into Dallas in 1947 after wartime service and stayed. The "
        "record keeps both arrivals plainly, with no earlier "
        "ancestry claimed than the papers and the family Bibles "
        "can show."
    ),
    "q003": (
        f"{MOTHER}, born in 1975, a piano teacher and church "
        "organist. She is documented in the record first as a "
        "working musician: she teaches lessons in the front room "
        "of her house, plays for services and weddings, and keeps "
        "the joined family's household books in the same careful "
        "hand she uses for music. She is the daughter of Slate and "
        "Opal Flames, and the music of the Flames line descends "
        "through her mother to her, and through her to the subject."
    ),
    "q004": (
        "The subject's mother came from the Flames line of Dallas. "
        "Her father, Slate Flames, worked in heating and "
        "refrigeration; her mother, Opal Flames, born Opal Reyes, "
        "was a piano teacher and church organist before her, and "
        "the piano the subject's mother teaches on is the one she "
        "inherited from her. The subject's ear, by all family "
        "testimony, came down this side: two generations of women "
        "at the same instrument, and the household's books kept in "
        "a musician's careful hand."
    ),
    "q005": (
        f"{FATHER}. He is documented in the record as a repairman: "
        "for most of his working life he has run a small Dallas "
        "shop that repairs radios and guitars, and he is known on "
        "his street as a man who can make a dead machine answer "
        "again. He is the son of Jasper and Coral Frozen. He "
        "taught his son the bench trade before any studio did, and "
        "the shop, its day books, and its standards are the "
        "subject's first documented workplace."
    ),
    "q006": (
        "The subject's father came from the Frozen line, the "
        "Pittsburgh people who became Dallas people. His father, "
        "Jasper Frozen, was a toolmaker and the line's patriarch, "
        "and the doctrine the joined family still lives by is his "
        "sentence: a family keeps what it can fix, and fixes what "
        "it keeps. His grandfather, Flint Frozen, was the "
        "millwright who carried the line to Texas. The repair shop "
        "the subject grew up around is that doctrine with a cash "
        "register."
    ),
    "q007": (
        "His parents met in 1998 over a broken piano pedal. Ruby "
        "Flames was playing for a church social when the pedal "
        "failed; Onyx Frozen was the repairman the church called. "
        "He fixed the pedal and stayed for the singing. They "
        "married in 1999. What each brought to the marriage the "
        "record shows plainly: she brought the music and the "
        "household's books; he brought the bench, the tools, and "
        "his father's doctrine; and each brought a family name "
        "neither was willing to surrender, which is why their "
        "first child's name is both."
    ),
    "q008": (
        "What the family believes about itself is stated in its "
        "doctrine, the sentence of Jasper Frozen's that both lines "
        "now quote: a family keeps what it can fix, and fixes what "
        "it keeps. Around that sentence the joined family keeps a "
        "second custom, older in each line separately: every child "
        "is given a first name from the crystals and gems, Ruby, "
        "Onyx, Jasper, Garnet, Jet, Opal, Flint, Pearl, Coral, "
        "Jade. The subject is the custom's single exception, and "
        "the exception is the family's story about itself in one "
        "name: he is not one line's child but the joining."
    ),
    "q009": (
        "The family's standing in the generation before the subject "
        "was that of respected working people on both sides. The "
        "Frozen repair trade and the Flames music teaching were "
        "known on their streets; neither line was rich and neither "
        "was hungry, and their credit, in the old sense of the "
        "word, was excellent: what the family said it would do, it "
        "did. The property the record shows is modest and entirely "
        "instrumental: a shop, a piano, two sets of tools, and two "
        "archives of paper."
    ),
    "q010": (
        "The object that survives from the earlier generation, and "
        "that the biographer would put first, is the Flames "
        "family's Bible, begun by Jet Flames in 1949, its flyleaf "
        "carrying the line's births, marriages, and deaths in her "
        "hand for fifty-two years and in later hands since. Beside "
        "it stands Flint Frozen's toolbox, the one he carried into "
        "Dallas in 1947. Between the Bible and the toolbox, the "
        "record and the trade, the whole of the subject's "
        "inheritance is already present before he is born."
    ),
    # Chapter 2 -- Birth and First Years
    "q011": (
        f"He was born in {BIRTH_YEAR}, in Dallas, the first child "
        "of Ruby and Onyx, and the first child of the joining of "
        "the two lines. The year matters to the shape of the life: "
        "he was born into a trade already changing under his "
        "father's hands, tape giving way to machines his father's "
        "generation argued about, and he would learn the old "
        "machines and the new ones together, refusing, from the "
        "start, to treat the argument as a religion."
    ),
    "q012": (
        f"{BIRTHPLACE}, Texas, in a city hospital, and he was "
        "brought home to the house where his mother's piano stood "
        "in the front room and his father's bench stood in the "
        "back. The record keeps him in that city, with travels, "
        "for the whole of the life that follows: the shop, the "
        "studio, the fire, and the rebuilding are all Dallas, and "
        "the biography's geography is the geography of one city's "
        "working streets."
    ),
    "q013": (
        "The documented circumstances are plain. The birth was "
        "registered with the city within the week, the certificate "
        "names both parents and both family lines in the child's "
        "own name, and the church where his mother played welcomed "
        "him by that name in its bulletin. No family legend "
        "attaches to the day itself, which the subject, later, "
        "said was the right size of welcome for a person whose "
        "whole distinction was to be a joining."
    ),
    "q014": (
        "The household he entered was a working house: his "
        "mother's students came and went through the front room, "
        "his father's customers through the shop, and the child "
        "was raised, in effect, in the doorway between music made "
        "and music mended. In 2003 a sister arrived, Opal Flames, "
        "named for their grandmother, and the household became the "
        "four-person form the rest of the record knows: two "
        "trades, two children, one doctrine."
    ),
    "q015": (
        "His earliest surroundings, as the record reconstructs "
        "them, were the shop counter with its spools of wire, the "
        "guitars waiting in a row for repair, his mother's piano, "
        "his grandmother Opal's piano before that, and, across the "
        "city he would cross daily as he grew, the old icehouse, a "
        "thick-walled building he passed as a boy without knowing "
        "it was waiting for him. The record preserves the order of "
        "these surroundings because the life keeps returning to "
        "them in it."
    ),
    "q016": (
        "His mother cared for him in the main, between students. "
        "When both parents were working, his grandmother Opal "
        "Flames kept him, at her house or at theirs, and his aunt "
        "Jade Frozen, a nurse in Fort Worth, took him on her days "
        "in the city. The record shows no institution and no "
        "hardship in the arrangement; it shows a family that "
        "regarded the child as partly its collective work, in the "
        "same spirit as everything else it kept."
    ),
    "q017": (
        "His early temperament, by the testimony of everyone who "
        "was asked, was quiet and listening. He talked late and "
        "listened early. He took his toys apart not to break them "
        "but, his mother insisted, to hear what was inside them; "
        "the family learned to give him broken things, which he "
        "preferred to new ones. The witnesses note the red hair "
        "and the stillness together: a child easy to find in a "
        "room, because he was the one facing the sound."
    ),
    "q018": (
        "The family story told about the child, the one his mother "
        "repeated all her life, is that before he could talk in "
        "sentences he would hum back the notes she played, exactly, "
        "from the next room. It cannot be verified and the "
        "biographer does not ask the reader to believe it. It is "
        "recorded because the family believed it, and organized "
        "his childhood around it, the way the Frozen side organized "
        "his other childhood around a bench."
    ),
    "q019": (
        "His own words enter the record early. At about seven, "
        "handed a radio his father had pronounced dead, he is "
        "reported to have said: it is not dead, it is just not "
        "answering yet. The sentence survives because his father "
        "wrote it in the shop's day book, under the date, without "
        "comment, in the same hand that entered the day's repairs "
        "and receipts. The biographer notes it as the first "
        "documented instance of the subject's whole method."
    ),
    "q020": (
        "The chapter turns on a child formed by two rooms: the "
        "front room where music was taught and the back room where "
        "machines were mended. Nothing in the record yet shows the "
        "two becoming one life. Everything in the record after "
        "this chapter is that becoming, and the name he carries, "
        "the joining of the two lines, turns out to have been a "
        "description of the work as well as of the birth."
    ),
    # Chapter 3 -- The Making of the Child
    "q021": (
        "His schooling was the neighbourhood school, and the "
        "record of it is unremarkable except in one subject. His "
        "grades were ordinary; his music teacher let him stay "
        "after school to play the school piano, and wrote on one "
        "report that the boy heard accurately and worked willingly, "
        "which the family kept as the truest sentence any school "
        "produced about him. The rest of his real education, the "
        "record shows, was already scheduled elsewhere: at a bench, "
        "after school, in his father's shop."
    ),
    "q022": (
        "The earliest work of his hands the record can fix is "
        "bench work: rewiring a lamp at nine, restringing guitars "
        "in his father's shop by eleven, unpaid and supervised. "
        "His father inspected every job and made him redo the "
        "careless ones, which the subject later described as the "
        "whole of his real education. The day books of those years "
        "enter the boy's work in the same columns as the men's, "
        "with the amounts blank where the other amounts stand."
    ),
    "q023": (
        "His closest childhood friendship was with his cousin "
        "Jasper Whitfield, his aunt Topaz's son, who came down "
        "from Chicago in the summers and had ambitions neither of "
        "them could yet name. The friendship is documented in the "
        "ordinary way, in photographs and in the cousin's later "
        "testimony: the two of them, a garage, a borrowed drum "
        "kit, and noise the street tolerated longer than it should "
        "have. The record keeps it because it is the first "
        "collaboration: the subject, from the beginning, made "
        "music with whoever the family brought him."
    ),
    "q024": (
        "The hardship of the childhood came the winter a landlord "
        "raised the shop's rent and work fell off together. His "
        "mother took extra students; his father took in sewing "
        "machines and anything else with a motor; nobody in the "
        "family called it hardship at the time. The subject "
        "learned from it the household's answer to worry, which "
        "was work, in both hands, and the doctrine's practical "
        "meaning: the family kept what it could fix that winter "
        "by fixing everything anyone brought it."
    ),
    "q025": (
        "The household's practice was church on Sundays, because "
        "his mother played the organ and the family sat where it "
        "could see her hands. The subject's own later account is "
        "that the music stayed with him longer than the sermons "
        "did, and that he considered this his mother's doing "
        "rather than his failing. The record adds what the "
        "witnesses add: the church was also the family's first "
        "studio, the room where the child learned what a room does "
        "to sound."
    ),
    "q026": (
        "His first instrument was his mother's piano, learned at "
        "her side in the front room, on the instrument she had "
        "inherited from her own mother. His second was a guitar "
        "his father repaired and gave him, an instrument a "
        "customer had brought in broken and never returned for. "
        "The record preserves the order because he insisted on it: "
        "the piano first, because she was first, and because both "
        "instruments came to him the family's way, kept and fixed "
        "rather than bought."
    ),
    "q027": (
        "The books and images that formed him were not, in the "
        "main, books. They were the radio catalogues and repair "
        "manuals of his father's trade, whose circuit diagrams he "
        "studied the way other children studied picture books, and "
        "the record sleeves in the shop's small front rack, which "
        "he handled like documents, because to him they were. His "
        "grandmother Jet's family Bible formed him too, in a "
        "different way: it taught him that a family's facts are "
        "written down, by hand, by someone who intends them to "
        "last."
    ),
    "q028": (
        "The wider world reached him through the radios his family "
        "repaired for other people and tested at the bench. By "
        "night he could catch far stations fading in and out, and "
        "he kept a list, in a school notebook, of the stations he "
        "had caught and the weather when he caught them: his first "
        "log book, though nobody called it that. The biographer "
        "notes the continuity the record insists on: the session "
        "logs of the later studio are this notebook, grown up."
    ),
    "q029": (
        "His character in the record shows early in a small, "
        "documented act. At twelve he found a wallet with money "
        "in it on the street and returned it to its owner the same "
        "day, and was annoyed at being praised for it afterwards. "
        "It was not mine, he said. The biographer notes the story "
        "because it is the first instance of the exactness about "
        "other people's property that the whole later record "
        "shows, in other people's reels, tapes, and songs."
    ),
    "q030": (
        "The chapter turns at fourteen, in 2014, when the unpaid "
        "help in his father's shop became paid work after school: "
        "rewiring radios and restringing guitars, at a small man's "
        "wage for a boy's hours, entered in the day book like any "
        "other job. The boy who listened like it was a job was, in "
        "the plainest sense, employed. The making of the child was "
        "finished. The making of the tradesman began."
    ),
    # Chapter 4 -- Apprenticeship
    "q031": (
        "His first paid work, in 2014, was after-school bench work "
        "in his father's repair shop: radios and guitars, paid at "
        "a small man's wage for a boy's hours. The record is "
        "precise about it because his father was: the day book "
        "shows the first wage entered like any other job, with the "
        "work described and the amount paid. Five years later the "
        "same hand that signed those entries would be keeping a "
        "studio's session log on the same principles."
    ),
    "q032": (
        "His first master was his father, at the bench. His second "
        "was the owner of a Dallas recording studio who knew the "
        "family through the shop, and who took the young man on in "
        "2019 as an unpaid assistant. The master let him watch "
        "sessions from the corner, on the stated condition that he "
        "watch in silence and coil the cables afterwards better "
        "than he found them. The record does not name him here; "
        "the subject's own log books do, and the biography follows "
        "the survey in keeping the emphasis on the terms."
    ),
    "q033": (
        "The terms of the studio apprenticeship, from 2019, were "
        "that there were no wages. He was paid, in the studio's "
        "phrase, in tape and lessons: he swept, he coiled cable, "
        "he kept the session log, and in exchange he was taught "
        "the machines and allowed to stay for the music. The "
        "record shows he never missed a session he was permitted "
        "to attend. It was the family's doctrine in a new trade: "
        "the way in is to keep what the room gives you."
    ),
    "q034": (
        "The standard the apprenticeship taught was absolute: a "
        "cable coiled wrong is a session ruined later; a log kept "
        "loosely is a record lost. Every session was written down "
        "to the minute, who played, what broke, what worked. The "
        "subject kept that standard, and that log book, for the "
        "rest of his working life. The biographer notes that the "
        "standard has two sources the record keeps distinct: the "
        "studio taught it about sessions; his father's bench had "
        "already taught it about everything else."
    ),
    "q035": (
        "The tools of the apprenticeship were his father's "
        "soldering iron at the bench and, at the studio, the tape "
        "machine he was taught to align, patiently, by ear and by "
        "measurement together. The iron survives; it is in the "
        "record because the subject kept it all his life, and used "
        "it, and would not lend it. It had come to him the way "
        "everything in this life arrives: through his father's "
        "hands, worn, working, and exact."
    ),
    "q036": (
        "The failure of the apprenticeship, the one the record "
        "does not soften, is that he once mislabelled a reel and a "
        "singer's best take was erased. He was made to tell the "
        "singer himself, in the room, before anyone else spoke. "
        "He did it, and he never mislabelled anything again; the "
        "log book's care dates, by his own account, from that "
        "afternoon. The biographer records the episode because the "
        "subject does: in this record, the failures are entered "
        "with their causes, like the repairs."
    ),
    "q037": (
        "The discipline of the training was writing. Everything "
        "was entered: the session, the settings, the repairs, the "
        "failures with their causes. The doctrine, which became "
        "the subject's, was that a thing not written down has not "
        "been learned, only survived. The record shows the habit "
        "predates the studio: the Frozen line's day books, the "
        "Flames line's Bible, the boy's notebook of radio stations. "
        "The log books of the apprenticeship years survive and are "
        "the spine of this biography's middle chapters."
    ),
    "q038": (
        "What he read, he read the way his father read: manuals. "
        "Studio manuals now, machine by machine, until he could "
        "align, bias, and repair the room he was learning to run. "
        "The record shows no other curriculum and the subject "
        "claimed no other; his education was a bench, a studio, "
        "and a shelf of other men's instructions, mastered. His "
        "mother's shelf stood behind it: the scores and the church "
        "music, learned earlier, at the piano, by ear and by hand."
    ),
    "q039": (
        "The apprenticeship ended the morning he was left to run a "
        "session alone: a gospel group, a Sunday, a small budget "
        "and no rescue available. The recording came out clean. "
        "The entry in the log that day, in the master's hand, is "
        "four words long, and the biographer will not improve on "
        "them: he is ready now. The subject was nineteen, and the "
        "record's two apprenticeships, the bench and the studio, "
        "stood complete behind him."
    ),
    "q040": (
        "The chapter turns on a completed tradesman. He had a "
        "trade, a standard, and a log book, and he had learned the "
        "thing his whole later life assumes: that music, which "
        "feels like weather, is made in rooms, by work, and can be "
        "kept. The young adult who follows was already formed; "
        "only his circumstances were about to change, and the room "
        "he had been describing since boyhood was still ahead of "
        "him, waiting in thick walls across the city."
    ),
    # Chapter 5 -- The Young Adult
    "q041": (
        "He left home at nineteen, not in anger and not far in "
        "spirit: a rented room near the studio where he assisted, "
        "a mattress, a hot plate, and his mother's piano still the "
        "place he went on Sundays. The record shows a leaving of "
        "the ordinary kind, a household becoming two households "
        "that shared a table every week, and a young man whose "
        "independence was measured in walking distance."
    ),
    "q042": (
        "His first independent work was engineering sessions for "
        "local singers, hired by word of mouth out of the studio "
        "where he had assisted. The first full album the record "
        "credits to him is by a Dallas band whose singer had heard "
        "what he did with a demo and asked for him by name. It is "
        "a modest credit. It is also the first time the name "
        "Frozen appears in print as the man behind the glass, and "
        "the record keeps the clipping the way his family keeps "
        "everything: flat, dated, and unexaggerated."
    ),
    "q043": (
        "The money of those years was by the session, and "
        "sometimes in trade, and he logged it like sessions: rent "
        "first, tape second, food third, which was his own joke "
        "about the order and also, the record suggests, roughly "
        "the truth. He was never, in these years, ahead. He was "
        "also never, the log shows, behind on the rent. The "
        "household book of his childhood had become a tradesman's "
        "ledger without changing its rules."
    ),
    "q044": (
        "The times he came of age in were changing under the "
        "trade: tape giving way, by then rapidly, to newer "
        "machines, and studios arguing about it like a religion. "
        "The record shows him learning both and refusing the "
        "argument. A tool is a tool, he said; the log is the log. "
        "It was his father's doctrine applied to a quarrel his "
        "father's generation had started and his own would finish "
        "by simply outworking it."
    ),
    "q045": (
        "His ambition in those years was stated plainly and often, "
        "to anyone who asked and some who did not: he wanted a "
        "room of his own where the work was done right. I want a "
        "room where it is done right. The sentence is recorded by "
        "three separate witnesses, which in this biography counts "
        "as a document. The biographer notes the ambition's "
        "modesty and its totality: not fame, not fortune, a room, "
        "and the standard kept inside it."
    ),
    "q046": (
        "The setback of the young adult years was a studio closure: "
        "a room he depended on shut its doors with two weeks of "
        "his pay inside it. He worked a winter repairing "
        "televisions to stay even, his father's trade as the net "
        "under his own, and the record notes it without drama "
        "because he noted it without drama: one line in the log, "
        "and the winter's repairs itemized. The doctrine held in "
        "its practical form: what he could fix kept him."
    ),
    "q047": (
        "Session work took him travelling, to other cities' rooms, "
        "for days and once for most of a season. The record is "
        "deliberately loose about the geography; what it keeps is "
        "the notebooks. He came home from every trip with a "
        "notebook full of other rooms' habits, what they did "
        "better, what they did worse, and what he meant to steal. "
        "The biography follows the record in this looseness: the "
        "life's map is one city, and the travels are entries in "
        "its education, not chapters of it."
    ),
    "q048": (
        "His reputation formed in the way reputations in a trade "
        "actually form: singers asked for him by name. Get Frozen, "
        "the record shows them saying, because he listened before "
        "he touched a dial, and because a session with him ended "
        "with everything labelled. It was not fame. It was better "
        "than fame, in his own later judgment: it was repeat work, "
        "the trade's vote, cast in bookings."
    ),
    "q049": (
        "What the record leaves out of these years is his own "
        "music. He was engineering other people's records by day "
        "and writing his own songs at night, and the songs went "
        "into a drawer, unrecorded, while the drawer filled. The "
        "biographer flags the omission because the subject flagged "
        "it himself, later, as the central evasion of his young "
        "life: the keeper of everyone else's work, keeping his own "
        "unfinished."
    ),
    "q050": (
        "The chapter turns in 2022, when the old icehouse he had "
        "passed as a boy, a thick-walled building built for cold, "
        "came up for lease. He took it. The young adult had found "
        "the room he had been describing for a decade, and it had "
        "been waiting, in the city he started in, at the end of "
        "the geography he already knew. The record treats what "
        "follows as the life's hinge, and so does he."
    ),
}

ANSWERS.update({
    # Chapter 6 -- The Work
    "q051": (
        "His principal work, from 2022, was the Cold Room: the "
        "small recording studio he founded in the converted "
        "icehouse in Dallas. The work was recording other people's "
        "music, done to his standard, and slowly, in the hours the "
        "studio was dark, his own. The name he gave the room is "
        "the record's plainest poetry: an icehouse is a building "
        "for keeping things cold and therefore kept, and the "
        "studio was founded, like everything in this life, to keep."
    ),
    "q052": (
        "His method at the height of the work was his father's "
        "saying made into a studio rule: tape does not care what "
        "you meant. Listen first. Set the room before the artist "
        "arrives. Keep the log open on the desk. He held that a "
        "session is decided before the first note, in the "
        "preparation nobody applauds, and the record of the "
        "sessions supports him. The method's other half was the "
        "doctrine's: a family keeps what it can fix, applied to "
        "takes, machines, and musicians alike."
    ),
    "q053": (
        "The work he is best known for is the album the trade "
        "calls the icehouse record: the full-length record, made "
        "in the Cold Room's second year for a Dallas band at its "
        "peak, that most people name when his name comes up. The "
        "documentary record supports the association and "
        "complicates it: the log shows a band at its best and an "
        "engineer who mostly stayed out of the way. He deflects "
        "the credit to the band to this day, and the deflection is "
        "also documented, in the same hand, in the same log."
    ),
    "q054": (
        "A representative day at the height of it: up before the "
        "session, the machine aligned, coffee, the log open. The "
        "artists arrived to a room already listening. The day "
        "ended when the room was reset for tomorrow, the reels "
        "labelled, the failures written down with their causes. "
        "Witnesses describe the routine as unvarying, and the "
        "unvarying as the point: the room's standard was a thing "
        "that happened every day or it did not happen at all."
    ),
    "q055": (
        "The object that best evidences the work is a ribbon "
        "microphone he rebuilt in his father's shop from a dead "
        "unit and spare parts, and used ever after on quiet songs. "
        "It sits on a shelf in the Cold Room still, with its log "
        "entry beside it: what was wrong, what he did, what it has "
        "recorded since. The biographer knows no cleaner summary "
        "of the man, or of the doctrine working: a dead thing, "
        "kept, fixed, and put back into service for other people's "
        "best days."
    ),
    "q056": (
        "His collaborators, as the record documents them, were "
        "his father at the bench at the back of the building, a "
        "circle of Dallas players who came and went through the "
        "Cold Room's door, and, on early sessions, his younger "
        "sister Opal, who sang harmony and kept the books for the "
        "studio's first two years before her own life took her "
        "elsewhere in the city. The work was solitary in method "
        "and crowded in fact, and the record keeps both truths "
        "without reconciling them."
    ),
    "q057": (
        "The recognition the record documents is modest and "
        "mostly in print small enough to miss: album credits, a "
        "newspaper profile that got his age wrong and his work "
        "right, and the trade's own currency, which is the repeat "
        "call. He kept the profile in the log book, the error "
        "uncorrected, as a reminder of what print is worth. The "
        "biographer notes that the witnesses, describing him for "
        "the profile, reached for the same details the family "
        "gives: the red hair, the listening, the labelled reels."
    ),
    "q058": (
        "The money the work made was enough, most years, and the "
        "record is honest about the mechanism: the studio paid its "
        "way, and in the thin years the repair bench at the back "
        "of the building, his father's trade carried on, covered "
        "what the sessions did not. He never separated the two "
        "trades in the accounts, because he never separated them "
        "in himself. The accounts, like the logs, are complete, "
        "and the biographer has relied on their completeness."
    ),
    "q059": (
        "The work he left unfinished is his own album: the songs "
        "from the drawer of his young years, begun as reels in the "
        "studio's dark hours, set aside for other people's records "
        "again and again. The record does not excuse it. It notes "
        "that he finished other people's work first, every time, "
        "and that he knew the cost while he paid it. The drawer, "
        "in the rebuilt room, is the biography's standing open "
        "question, and the legacy chapter will return to it."
    ),
    "q060": (
        "The chapter turns on a work with a place and a name: the "
        "Cold Room, its log books filling, its standard known. And "
        "in the studio's first year the work gained a witness, "
        "when the photographer hired to shoot a session stayed to "
        "argue about the light, and the household chapter of the "
        "life began. The record dates the turn precisely because "
        "she does: her prints of his rooms begin that year, and "
        "they have not stopped."
    ),
    # Chapter 7 -- Love and Household
    "q061": (
        f"{PARTNER}, born Amber Verano, a photographer. She "
        "enters the documented record as a working artist in her "
        "own right: hired in the Cold Room's first year to "
        "photograph a session, married to the subject in 2023, "
        "and thereafter the person whose prints of his rooms hang "
        "in every room he has worked in since. She is the "
        "daughter of Agate Verano, a sign painter, and Beryl "
        "Verano, a schoolteacher, and she took the name Flames at "
        "the marriage the way the family takes all its names: "
        "deliberately, and for good."
    ),
    "q062": (
        "They met at work, when Amber Verano was hired to "
        "photograph a session at the Cold Room and told the "
        "engineer, within the hour, that his studio had the best "
        "light of any room that was not supposed to have any. The "
        "session log for that day survives. Her name is in it, in "
        "his handwriting, spelled right the first time, which "
        "witnesses treat as evidence. The record adds hers: she "
        "came back the next week to shoot the room empty, because, "
        "she said, it photographed like a person."
    ),
    "q063": (
        "The courtship survives in the record as letters, hers "
        "kept in a labelled box in the studio, written from the "
        "road when her work travelled, and in his log books, where "
        "her sessions and visits are entered with the same care as "
        "the music. They married in 2023. The biographer notes "
        "that this is the best-documented chapter of the life, and "
        "that the documentation is mostly hers: the sound is his "
        "archive, and the light is hers."
    ),
    "q064": (
        "The household they made was a small house near the "
        "studio: her darkroom in the back room, his bench in the "
        "shed, and a piano in the front room, bought secondhand "
        "and repaired by him, because a house of his mother's "
        "family does not stand without one. It was a working "
        "house. Both of them said so, as praise. The record shows "
        "the household's shape plainly: two trades, two archives, "
        "one table."
    ),
    "q065": (
        "The household held no children of their own in the years "
        "the record covers; its wider family was near and "
        "constant: his sister Opal, in and out with the ease of "
        "the house's second keeper; her parents, the Veranos, at "
        "the table on Sundays; his parents two streets of the same "
        "city away. The record mentions it plainly because the "
        "witnesses do: the house was full, on the days it was "
        "full, and quiet in a way both of them defended on the "
        "others."
    ),
    "q066": (
        "His partner's work, as the record documents it, was "
        "photography: portraits, rooms, working people at their "
        "benches and instruments. The Cold Room's walls are her "
        "prints. Between them, the witnesses say, the two of them "
        "documented the same world twice, once in sound and once "
        "in light, and the archive of each is the other's index. "
        "Her father's trade stands behind hers in the record: a "
        "sign painter's daughter, exact about what a surface says."
    ),
    "q067": (
        "The household's economy was two irregular incomes and one "
        "regular habit: the log. They kept a household book with "
        "the same rules as the session logs, everything entered, "
        "nothing rounded in their own favour. It is an unromantic "
        "document and the biographer recommends it as the truest "
        "portrait of the marriage that survives: two people who "
        "kept the books of a life the way his family had kept them "
        "for three generations, in ink, in order, without flattery."
    ),
    "q068": (
        "The strain the record shows in the household came with "
        "money, in the thin years, and took the form of his "
        "silences, which she named in a letter the record keeps: "
        "he went quiet the way a room goes quiet, all at once and "
        "on purpose. What held them, by both accounts, was her "
        "refusal to let him sell the rebuilt microphone, ever, for "
        "any bill. Some things were not the accounts' business. "
        "The biographer notes that the microphone still stands on "
        "its shelf, and that she put it there."
    ),
    "q069": (
        "What the witnesses say of the household is consistent to "
        "the point of suspicion, until the biographer notes the "
        "source: most of them ate there. Friends describe a house "
        "where work and supper were the same conversation, where a "
        "session's failure and a soup's failure got the same "
        "post-mortem, and where both were usually fixed by morning. "
        "Her prints on the walls, his logs on the desk: the "
        "witnesses agree the house itself was the couple's joint "
        "work, and their best one."
    ),
    "q070": (
        "The chapter turns with the household proven: two trades, "
        "one house, a book kept honestly. What it had been built "
        "to hold against arrived soon enough, when the standing he "
        "had earned met the years that tested it, and then, in a "
        "single night, the fire. The record's next chapter is the "
        "testing; the one after is the night itself and what the "
        "doctrine is worth when the thing kept is a room full of "
        "other people's music."
    ),
    # Chapter 8 -- Standing and Struggle
    "q071": (
        "His standing at its height, within a few years of the "
        "Cold Room's founding, was that of a fixture: the man "
        "singers asked for, the room other engineers visited to "
        "see how it was done. The record shows it was built the "
        "slow way, on log books and clean sessions and reels "
        "labelled right, and that he trusted it exactly as far as "
        "it was built and no further. A young man's standing, in a "
        "young room: the record is careful to keep both facts in "
        "view."
    ),
    "q072": (
        "The institutional record of the standing is boring, which "
        "is its distinction: the studio's licences in order, its "
        "taxes paid, one bank loan taken for the roof and retired "
        "early. The biographer lists these because the subject "
        "listed them, among his achievements, without irony. "
        "Keeping the paperwork was keeping the room, and the room, "
        "in the doctrine he inherited, was kept the way the family "
        "keeps everything: in writing, in order, in full."
    ),
    "q073": (
        "The opposition the record documents came as an offer: a "
        "larger studio concern proposed to buy the Cold Room, its "
        "name and its book of work, and close it, the building "
        "being worth more to them dark than lit. He refused, in "
        "writing, in one sentence, which the record keeps and the "
        "legacy chapter will return to. The biographer notes the "
        "offer's timing: it came when the room was young enough to "
        "sell and he was young enough to start over, which is what "
        "made the refusal a fact about the man and not the market."
    ),
    "q074": (
        "The money trouble of the standing years came when "
        "recording budgets shrank and sessions thinned across the "
        "whole trade. The record shows the answer was the old one: "
        "the repair bench at the back of the building carried the "
        "studio through, radios and televisions paying for tape. "
        "He entered those years in the log without self-pity, "
        "itemized. His father's trade under his own, as it had "
        "been in the winter of the closed studio, as it had been "
        "in the winter of his childhood: the net held because it "
        "was kept."
    ),
    "q075": (
        "The failure of his own the record keeps in this chapter "
        "is the album: his own record, shelved twice in these "
        "years, once for money and once, by his own entry in the "
        "log, for fear of finishing it. He called it the record of "
        "his cowardice and his standards in equal measure, and the "
        "biographer has found no witness who disagreed with either "
        "half. The drawer's songs grew older in a young man's "
        "drawer, which the record presents as the stranger fact."
    ),
    "q076": (
        "The public criticism the record preserves is a review "
        "that called his production old-fashioned, a generation "
        "behind the fashion. He kept the clipping, pinned inside "
        "the front cover of the current log book, where he would "
        "see it daily. Evidence, not injury, he said, when asked. "
        "It is still there in the record, and so, the biographer "
        "notes, is he: the fashion moved twice more in the years "
        "after, and the room's method did not move at all."
    ),
    "q077": (
        "The private cost the record shows is his hearing: the "
        "left ear is not what it was, after years of loud rooms, "
        "and he mixes accordingly and says so to clients in "
        "advance, in writing. The biographer records it as he "
        "recorded it himself: a tradesman's wear, entered in the "
        "log like a machine's, with the adjustment noted beside "
        "it. In a record this young, the entry stands out: the "
        "first cost the work has charged the worker, paid in the "
        "faculty the work most uses."
    ),
    "q078": (
        "What he refused, in these years, besides the buyout, was "
        "work he thought dishonest: most clearly, a session meant "
        "to copy another singer's record note for note and pass "
        "as an original. He declined it and sent the client, "
        "politely and in writing, to the very concern that had "
        "tried to buy him. The letter survives. It is courteous. "
        "It is final. The record keeps it beside the refusal of "
        "the buyout, where the subject evidently believes it "
        "belongs: the two refusals are one fact."
    ),
    "q079": (
        "The support the record documents around him in the "
        "struggle years was the household first, Amber and the "
        "house near the studio; his sister Opal, who had kept the "
        "studio's books and now kept its spirits; his parents, "
        "whose shop and piano stood behind every thin month; and "
        "the players, who began bringing him their own students to "
        "teach, which he counted, correctly, as the trade's vote. "
        "The record's picture is of a man held up by the exact "
        "structure his name describes: two lines, joined, load-"
        "bearing."
    ),
    "q080": (
        "The chapter turns in 2024, in one night: a fire in the "
        "building next door, and then in his. The Cold Room as "
        "first built, the room of his young ambition, burned. What "
        "the fire could not take is the subject of the rest of "
        "this biography: the log books were at the house, and the "
        "standard was in the man. The record dates the loss "
        "plainly and moves, as he did, to the rebuilding."
    ),
    # Chapter 9 -- Late Years and Death
    "q081": (
        "His later circumstances begin with the rebuilding: two "
        "years after the fire of 2024 in which the Cold Room rose "
        "again in the same thick walls, slower, smaller, and "
        "entirely his. The present years of the record are the "
        "rebuilt room and a calendar he finally chose himself: "
        "fewer sessions, each one wanted. The biographer notes "
        "the chapter's oddity honestly: this is a young man's late "
        "chapter, written at twenty-six, and its lateness is the "
        "fire's doing. The fire made an ending in the middle of "
        "the life, and the life has had to be conducted, since, "
        "in the past tense of its first form."
    ),
    "q082": (
        "His routine in the present years is documented by "
        "everyone who visited: mornings at the repair bench, "
        "afternoons in the studio, evenings at the piano in the "
        "front room of the house. He kept the log. He answered "
        "letters from young engineers in full. Witnesses describe "
        "a man whose days had become, in his twenties, the shape "
        "his young self had asked for, and who found the shape "
        "stranger than the asking: the room ready, the standard "
        "kept, and the drawer still not empty."
    ),
    "q083": (
        "The present work the record shows is twofold: finishing, "
        "at last and in pieces, his own album, the drawer's songs "
        "becoming reels; and teaching, two young engineers taken "
        "on the old terms, no wages at first, paid in tape and "
        "lessons, who learned the log book habit at his bench the "
        "way he had learned it at his father's and at the studio "
        "where he assisted. The record closes the circle without "
        "comment: the terms he was hired on are the terms he "
        "hires on."
    ),
    "q084": (
        "His health in the record is entered as he entered "
        "everything: the left ear, as documented; otherwise sound, "
        "as a man of twenty-six with a tradesman's habits might "
        "expect to be. He was impatient with sympathy and with "
        "questions about retirement, a word he treated as a rumour "
        "about other people. The biographer records the entry for "
        "completeness, in the record's own manner: the machine "
        "inspected, the wear noted, the machine in service."
    ),
    "q085": (
        "The deaths in his immediate family came in their order, "
        "and the record states the order's mercy plainly: they are "
        "his grandparents' generation, not his parents'. Flint "
        "Frozen died in 1992 and Garnet Flames in 1994, before the "
        "subject was born; Pearl Frozen in 1999; Jet Flames, who "
        "began the family Bible, in 2001; Slate Flames in 2016; "
        "and Jasper Frozen, the doctrine's author, in 2018. His "
        "parents are living, and the record keeps them so: his "
        "mother at her piano, his father at his bench, both "
        "entered in the present tense, where the subject insists "
        "they belong."
    ),
    "q086": (
        "Among contemporaries, the death the record weighs most "
        "is Jasper Frozen's, in 2018: his grandfather, the Frozen "
        "line's patriarch, the toolmaker whose sentence the joined "
        "family lives by. The subject, eighteen, spoke at the "
        "service about a family keeping what it can fix, and was "
        "given his grandfather's day books afterward, which he "
        "keeps still, shelved with his own session logs. The "
        "apprenticeship's archive is complete, in one room, in his "
        "keeping: the doctrine's author, entered now in the books "
        "he taught the family to keep."
    ),
    "q087": (
        f"{NAME} has not died. The survey reaches him alive, in "
        "his middle twenties, working in the room he rebuilt, and "
        "the pages that in another life would record an ending "
        "record instead what he has arranged: the log books to "
        "the studio's keeping, the rebuilt microphone to stay on "
        "its shelf, the family Bible to remain in his mother's "
        "keeping and then in his sister's. He is, by every account "
        "including his own, not finished, and the record, "
        "following him, declines to finish him."
    ),
    "q088": (
        "What he has said about his own end is said the way he "
        "says everything, in advance and in writing: he is to lie "
        "in the Dallas ground where both lines now rest, beside "
        "the grandparents of both names, with no stone larger "
        "than theirs. The record notes the instruction exists, in "
        "the front of the current log book, where the right person "
        "will find it. The biographer notes the instruction's "
        "fitness: a man named for a joining asks, at the end, to "
        "be filed with both families, under both names' ground."
    ),
    "q089": (
        "The instructions he has left are kept with the log books "
        "and are practical: the studio to be offered first to the "
        "engineers he taught, at the value of its work and not its "
        "walls; the tapes catalogued and kept; his own album, "
        "finished or not, to be labelled honestly either way. It "
        "is less a will than a session log for an event he will "
        "not engineer. His parents hold copies. His wife holds "
        "the original, in the labelled box, with her letters."
    ),
    "q090": (
        "His most recent recorded words, given to a young engineer "
        "who asked him what all the work had been for, are these: "
        "so the room would be ready for whoever comes next. The "
        "biographer offers them without improvement, as the "
        "subject's own summary of the present years, and notes "
        "that the room, on the day the words were recorded, was "
        "ready, and that the man who said them was twenty-six and "
        "had already rebuilt it once."
    ),
    # Chapter 10 -- Legacy
    "q091": (
        "His reputation today, as the record documents it, lives "
        "in the trade's mouth: among the singers and engineers of "
        "his city he is a standard of comparison, and a session "
        "done the way Frozen does it is a phrase with a meaning "
        "everyone in that world can unpack. It is a local "
        "reputation, and a young one. The record shows he never "
        "wanted a larger kind, and got the kind he wanted, and "
        "that the getting took one founding, one fire, and one "
        "rebuilding."
    ),
    "q092": (
        "The record against the reputation is incomplete, and the "
        "biographer says so plainly: much of his best work is "
        "uncredited session work, present in the music and absent "
        "from the sleeves. The truer record is the log books, "
        "every session since he was nineteen, in his hand. "
        "Reputation says he mattered. The logs say how, and when, "
        "and for whom. The biography has followed the logs "
        "throughout, and states its method here so the reader can "
        "weigh its conclusions."
    ),
    "q093": (
        "His influence, as documented, runs through hands: the "
        "two engineers he taught now teach the log book habit to "
        "their own assistants, and rooms he has never seen run on "
        "session sheets copied from his. Influence of this kind "
        "does not announce itself. The record finds it the way he "
        "would: in other people's paperwork, done right. The "
        "doctrine's transmission is documented the same way, in "
        "day books and Bibles, three generations deep on both "
        "sides of his name."
    ),
    "q094": (
        "The material legacy the record can point to is a set of "
        "working objects: the Cold Room itself, rebuilt; the log "
        "books, complete; the rebuilt ribbon microphone on its "
        "shelf, still used on quiet songs; his mother's piano, "
        "still played; the family Bible, still being entered; "
        "Flint's toolbox, still carried. Nothing in the list is a "
        "monument. Everything in it works, which the biographer "
        "takes to be the point of the list, and of the life."
    ),
    "q095": (
        "The saying he is quoted by, in other people's studios "
        "now, is the rule of his room: tape does not care what you "
        "meant. He always credited it to his father, who said it "
        "first about radios, and the record supports the credit. "
        "Behind it stands the older sentence, his grandfather's, "
        "that the family quotes: a family keeps what it can fix, "
        "and fixes what it keeps. The biographer enters both "
        "correctly, as the subject would insist: the room's rule "
        "is his father's; the life's rule is the family's; he "
        "invented neither and kept both."
    ),
    "q096": (
        "What is misremembered about him, the record shows, is "
        "generous error: he is credited, in talk, with records he "
        "only repaired equipment for, and with sessions he "
        "attended as a boy with a broom. He corrects it when it "
        "happens, in writing, in the log, without embarrassment to "
        "anyone. The corrections are part of the archive, and the "
        "biographer has relied on them gratefully. A young "
        "reputation, corrected young: the record expects the "
        "errors to grow with the years and the corrections to "
        "keep pace."
    ),
    "q097": (
        "His own assessment of the life, given more than once and "
        "in nearly the same words, is that he is a tradesman of "
        "other people's best days, and that this is not modesty "
        "but bookkeeping. The record, weighed whole, supports the "
        "assessment and the spirit of it: he kept the books of his "
        "life the way he kept the session logs, and understated "
        "his own part in both. The biographer adds only the "
        "record's arithmetic: the life so far is twenty-six years, "
        "one studio, one fire, one marriage, and one drawer, "
        "still, of his own songs."
    ),
    "q098": (
        "The refusal he is most known for is the buyout: money "
        "enough to stop, offered for the room and its name, "
        "refused in one written sentence because the room was the "
        "work and not its price. Strangers tell that story about "
        "him more than any other. The record confirms the offer, "
        "the sentence, and the refusal, and notes that he never "
        "told the story himself if he could help it. It is, the "
        "biographer observes, the doctrine with the prices filled "
        "in: what the family keeps, it keeps at cost."
    ),
    "q099": (
        "What remains open in the record is his own album: the "
        "drawer's songs, years in the finishing, which he works "
        "on still in the studio's dark hours. The biographer "
        "cannot close the account and does not pretend to. The "
        "last reel, in the subject's own log entry on the matter, "
        "is not yet labelled. In a life whose every other object "
        "is catalogued, the unlabelled reel is the record's one "
        "deliberate blank, and the biography ends its evidence "
        "there, where he left it."
    ),
    "q100": (
        "The biographer's final assessment, on the whole record, "
        "is this: a life spent making rooms where other people's "
        "music could stay. The ear came from his mother, the hands "
        "from his father, the standard from both trades, and the "
        "room from all of it. What he added was the keeping: the "
        "log written down, the work done right, and the room left "
        "ready for whoever comes next. He is twenty-six. The "
        "record is open, the room is lit, and the biography, "
        "having followed the facts as far as the facts go, stops "
        "where the survey stops: at the present day, with the work "
        "continuing."
    ),
})

FACT_ANSWERS = {
    "subject_name": ("q001", NAME),
    "mother_name": ("q003", MOTHER),
    "father_name": ("q005", FATHER),
    "birth_year": ("q011", str(BIRTH_YEAR)),
    "birthplace": ("q012", BIRTHPLACE),
    "partner_name": ("q061", PARTNER),
}

YEAR_RE = re.compile(r"\b(1[0-9]{3}|20[0-9]{2})\b")


def main() -> int:
    problems = []
    if len(ANSWERS) != 100:
        problems.append(f"expected 100 answers, have {len(ANSWERS)}")
    for slot, (qid, value) in FACT_ANSWERS.items():
        if value not in ANSWERS.get(qid, ""):
            problems.append(
                f"character fact {slot}={value!r} missing from {qid}")
    first_year = YEAR_RE.search(ANSWERS["q011"])
    if not first_year or int(first_year.group(1)) != BIRTH_YEAR:
        problems.append(
            f"q011 must state the birth year {BIRTH_YEAR} first")
    if YEAR_RE.search(ANSWERS["q087"]):
        problems.append("q087 must contain no year (living subject)")
    for qid, text in ANSWERS.items():
        for match in YEAR_RE.finditer(text):
            if int(match.group(1)) not in ALLOWED_YEARS:
                problems.append(
                    f"{qid} mentions year {match.group(1)}, which "
                    "the canonical record does not support")
    for stale in ("Memphis", "Tennessee", "Evelyn", "Harold",
                  "Alice", "Hart", "Webb", "Calloway", "Veracruz",
                  "Night Clerks", "Static Bloom", "Beaumont",
                  "Saltmarsh", "1960"):
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
            "drawn from the canonical character record in "
            "demo/frozen-in-flames-character.json (record version "
            "2.0.0). The life described was invented as test data "
            "for the biography pack and is not a biography of any "
            "real person. Corrected edition: these answers supersede "
            "the answers shipped with release v0.2.0, which carried "
            "values the biography build had invented for the "
            "character's core facts before the author set the canon."
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
