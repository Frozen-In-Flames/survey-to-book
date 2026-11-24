#!/usr/bin/env python3
"""Build the biography pack's demonstration answers.

The demonstration user of the series is Frozen In Flames, a fictional
persona. The canonical facts of the character's invented life live in
demo/frozen-in-flames-character.json; this script loads that record
and writes the character's answers to all 100 biography questions,
with the fact-bearing answers interpolated from the record so the
two cannot drift apart. A consistency check runs before anything is
written: every recorded fact must appear in its designated answer,
and the death-year question must contain no year (the character is
living; no death fact is established).
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

ANSWERS: dict[str, str] = {
    # Chapter 1 -- Before the Beginning
    "q001": (
        f"{NAME}. The name is given in full because it is the name "
        "the whole record uses: the subject of this biography, a "
        "musician and recording engineer of Memphis, Tennessee, "
        "known in daily life, and in every studio he ever worked in, "
        "simply as Frozen."
    ),
    "q002": (
        "What is known is modest and mostly kept in family memory. "
        "The Flames name came down the river: the subject's "
        "great-grandfather reached Memphis with a toolbox and stayed. "
        "On the other side, the Harts were western Tennessee people, "
        "farmers who became townspeople over two generations. No "
        "papers survive from before the Memphis years, and the "
        "family never claimed more ancestry than it could show."
    ),
    "q003": (
        f"{MOTHER}, born Evelyn Hart in 1934, a piano teacher and "
        "church organist. She is documented in the record first as a "
        "working musician: she taught lessons in the front room of "
        "the family house, played for services and weddings, and "
        "kept the household's books in the same careful hand she "
        "used for music."
    ),
    "q004": (
        "The subject's mother came from the Harts of western "
        "Tennessee. Her father, Samuel Hart, worked the railroad and "
        "was gone for days at a time; her mother kept a front room "
        "with a pump organ in it, and every Hart child learned some "
        "music whether inclined to it or not. The subject's ear, by "
        "all family testimony, came down this side."
    ),
    "q005": (
        f"{FATHER}. He is documented in the record as a repairman: "
        "for most of his working life he ran a small Memphis shop "
        "that repaired radios, televisions, and guitars, and he was "
        "known on the street as a man who could make a dead machine "
        "answer again. He taught his son the bench trade before any "
        "studio did."
    ),
    "q006": (
        "The subject's father came from the Flames side, the river "
        "people. His father, Emil Flames, was a toolmaker who "
        "settled in Memphis and raised his children on a single "
        "household doctrine: a family keeps what it can fix, and "
        "fixes what it keeps. The repair shop the subject grew up "
        "in was that doctrine with a cash register."
    ),
    "q007": (
        "His parents met over a broken piano pedal. Evelyn Hart was "
        "playing for a church social when the pedal failed; Harold "
        "Flames was the repairman the church called. He fixed the "
        "pedal, stayed for the singing, and, by the family's "
        "account, was engaged before he had heard her play a whole "
        "service through without stopping."
    ),
    "q008": (
        "He was born into Memphis in 1960: a river city where "
        "churches and recording studios stood streets apart and "
        "sometimes shared musicians, where a radio played in every "
        "kitchen, and where a working family could be poor in money "
        "and rich in standing if its work was respected. The record "
        "shows both institutions, church and studio, waiting for "
        "him from the start."
    ),
    "q009": (
        "The family's standing was that of respected working "
        "people. The repair shop was a known corner; the mother "
        "taught half the street's children their scales. They were "
        "not rich and were never hungry, and their credit, in the "
        "old sense of the word, was excellent: what the Flames "
        "family said it would do, it did."
    ),
    "q010": (
        "What he inherited was his mother's ear and his father's "
        "hands, and one conviction from both of them: anything "
        "broken can be understood, and most things understood can "
        "be mended. The witnesses disagree about which inheritance "
        "mattered more. The record suggests the biography is the "
        "story of the two becoming one trade."
    ),
    # Chapter 2 -- Birth and First Years
    "q011": (
        f"He was born in {BIRTH_YEAR}, on a March morning, in the "
        "city hospital in Memphis, the first child of Evelyn and "
        "Harold Flames. The year matters to the shape of the life: "
        "he was ten when the decade of the big studios ended, and "
        "old enough to have learned the old machines before the "
        "new ones arrived."
    ),
    "q012": (
        f"{BIRTHPLACE}, Tennessee, in a hospital a short ride from "
        "the river, and he was brought home to the rooms behind his "
        "father's repair shop. The record keeps him in that city, "
        "with travels, for the whole of the life that follows."
    ),
    "q013": (
        "The documented circumstances are plain. The birth was "
        "registered with the city within the week, the certificate "
        "names both parents and the father's trade, and a two-line "
        "notice in the church bulletin welcomed him by name. No "
        "family legend attaches to the day itself, which the "
        "subject, later, said was the right size of welcome."
    ),
    "q014": (
        "The household he entered was the flat behind the repair "
        "shop: two rooms and a kitchen, solder and piano music "
        "coming through the walls in about equal measure. His "
        "mother's students came and went through the front; his "
        "father's customers through the shop door; the child was "
        "raised, in effect, in the doorway between music made and "
        "music mended."
    ),
    "q015": (
        "His earliest surroundings, as the record reconstructs "
        "them, were the shop counter with its spools of wire, the "
        "guitars waiting in a row for repair, his mother's piano, "
        "and, at the end of the street, the old icehouse, a thick-"
        "walled building he would pass every day of his childhood "
        "without knowing it was waiting for him."
    ),
    "q016": (
        "His mother cared for him in the main, between students. "
        "When both parents were working, a neighbour, Mrs. Cole, "
        "watched him from her porch across the street. The record "
        "shows no institution and no hardship in the arrangement; "
        "it shows a street that regarded the child as partly its "
        "own."
    ),
    "q017": (
        "His early temperament, by the testimony of everyone who "
        "was asked, was quiet and listening. He talked late and "
        "listened early. He took his toys apart not to break them "
        "but, his mother insisted, to hear what was inside them; "
        "the family learned to give him broken things, which he "
        "preferred to new ones."
    ),
    "q018": (
        "The family story told about the child, the one his mother "
        "repeated all her life, is that before he could talk in "
        "sentences he would hum back the notes she played, exactly, "
        "from the next room. It cannot be verified and the "
        "biographer does not ask the reader to believe it. It is "
        "recorded because the family believed it, and organized "
        "his childhood around it."
    ),
    "q019": (
        "His own words enter the record early. At about seven, "
        "handed a radio his father had pronounced dead, he is "
        "reported to have said: it is not dead, it is just not "
        "answering yet. The sentence survives because his father "
        "wrote it in the shop's day book, under the date, without "
        "comment."
    ),
    "q020": (
        "The chapter turns on a child formed by two rooms: the "
        "front room where music was taught and the back room where "
        "machines were mended. Nothing in the record yet shows the "
        "two becoming one life. Everything in the record after "
        "this chapter is that becoming."
    ),
    # Chapter 3 -- The Making of the Child
    "q021": (
        "His schooling was the neighbourhood school, and the "
        "record of it is unremarkable except in one subject. His "
        "grades were ordinary; his music teacher, a Mr. Price, let "
        "him stay after school to play the school piano, and wrote "
        "on one report that the boy heard accurately and worked "
        "willingly, which the family kept as the truest sentence "
        "any school produced about him."
    ),
    "q022": (
        "The earliest work of his hands the record can fix is "
        "bench work: rewiring a lamp at nine, restringing guitars "
        "in his father's shop by eleven, unpaid and supervised. "
        "His father inspected every job and made him redo the "
        "careless ones, which the subject later described as the "
        "whole of his real education."
    ),
    "q023": (
        "His closest childhood friendship was with Danny Reyes, a "
        "boy two streets over who had a drum kit in a garage and "
        "ambitions neither of them could yet name. The friendship "
        "is documented in the ordinary way, in photographs and in "
        "Reyes's later testimony: the two of them, and a garage, "
        "and noise the street tolerated longer than it should have."
    ),
    "q024": (
        "The hardship of the childhood came the winter the shop's "
        "landlord raised the rent and work fell off together. His "
        "mother took extra students; his father took in sewing "
        "machines and anything else with a motor; nobody in the "
        "family called it hardship at the time. The subject learned "
        "from it the household's answer to worry, which was work, "
        "in both hands."
    ),
    "q025": (
        "The household's practice was church on Sundays, because "
        "his mother played the organ and the family sat where it "
        "could see her hands. The subject's own later account is "
        "that the music stayed with him longer than the sermons "
        "did, and that he considered this his mother's doing rather "
        "than his failing."
    ),
    "q026": (
        "His first instrument was his mother's piano, learned at "
        "her side in the front room. His second was a guitar his "
        "father repaired and gave him, an instrument a customer had "
        "brought in broken and never returned for. The record "
        "preserves the order because he insisted on it: the piano "
        "first, because she was first."
    ),
    "q027": (
        "The books and images that formed him were not, in the "
        "main, books. They were the radio catalogues and repair "
        "manuals of his father's trade, whose circuit diagrams he "
        "studied the way other children studied picture books, and "
        "the record sleeves in the shop's small front rack, which "
        "he handled like documents, because to him they were."
    ),
    "q028": (
        "The wider world reached him through the radio his family "
        "repaired for other people and tested at the bench. By "
        "night he could catch far stations fading in and out over "
        "the river, and he kept a list, in a school notebook, of "
        "the stations he had caught and the weather when he caught "
        "them: his first log book, though nobody called it that."
    ),
    "q029": (
        "His character in the record shows early in a small, "
        "documented act. At twelve he found a wallet with money in "
        "it on the street and returned it to its owner the same "
        "day, and was annoyed at being praised for it afterwards. "
        "It was not mine, he said. The biographer notes the story "
        "because it is the first instance of the exactness about "
        "other people's property that the whole later record shows."
    ),
    "q030": (
        "The chapter turns at fourteen, in 1974, when the unpaid "
        "help in his father's shop became paid work after school, "
        "and the boy who listened like it was a job was, in the "
        "plainest sense, employed. The making of the child was "
        "finished. The making of the tradesman began."
    ),
    # Chapter 4 -- Apprenticeship
    "q031": (
        "His first paid work, in 1974, was after-school bench work "
        "in his father's repair shop: radios, televisions, guitars, "
        "paid at a small man's wage for a boy's hours. The record "
        "is precise about it because his father was: the day book "
        "shows the first wage entered like any other job, with the "
        "work described and the amount paid."
    ),
    "q032": (
        "His first master was his father, at the bench. His second "
        "was Marcus Webb, who owned a recording studio across town "
        "and knew the family through the shop. Webb let the boy "
        "watch sessions from the corner, on the stated condition "
        "that he watch in silence and coil the cables afterwards "
        "better than he found them."
    ),
    "q033": (
        "The terms of the studio apprenticeship, from 1979, were "
        "that there were no wages. He was paid, in Webb's phrase, "
        "in tape and lessons: he swept, he coiled cable, he kept "
        "the session log, and in exchange he was taught the "
        "machines and allowed to stay for the music. The record "
        "shows he never missed a session he was permitted to attend."
    ),
    "q034": (
        "The standard the apprenticeship taught was Webb's, and it "
        "was absolute: a cable coiled wrong is a session ruined "
        "later; a log kept loosely is a record lost. Every session "
        "was written down to the minute, who played, what broke, "
        "what worked. The subject kept that standard, and that log "
        "book, for the rest of his working life."
    ),
    "q035": (
        "The tools of the apprenticeship were his father's "
        "soldering iron at the bench and, at the studio, the tape "
        "machine Webb taught him to align, patiently, by ear and by "
        "measurement together. The iron survives; it is in the "
        "record because the subject kept it all his life, and used "
        "it, and would not lend it."
    ),
    "q036": (
        "The failure of the apprenticeship, the one the record "
        "does not soften, is that he once mislabelled a reel and a "
        "singer's best take was erased. Webb made him tell the "
        "singer himself, in the room, before anyone else spoke. He "
        "did it, and he never mislabelled anything again; the log "
        "book's care dates, by his own account, from that afternoon."
    ),
    "q037": (
        "The discipline of the training was writing. Everything "
        "was entered: the session, the settings, the repairs, the "
        "failures with their causes. Webb's doctrine, which became "
        "the subject's, was that a thing not written down has not "
        "been learned, only survived. The log books of those years "
        "survive and are the spine of this biography's middle chapters."
    ),
    "q038": (
        "What he read, he read the way his father read: manuals. "
        "Studio manuals now, machine by machine, until he could "
        "align, bias, and repair the room he was learning to run. "
        "The record shows no other curriculum and the subject "
        "claimed no other; his education was a bench, a studio, "
        "and a shelf of other men's instructions, mastered."
    ),
    "q039": (
        "The apprenticeship ended the morning Webb let him run a "
        "session alone: a gospel group, a Sunday, a small budget "
        "and no rescue available. The recording came out clean. "
        "Webb's entry in the log that day, in Webb's hand, is four "
        "words long, and the biographer will not improve on them: "
        "he is ready now."
    ),
    "q040": (
        "The chapter turns on a completed tradesman. He had a "
        "trade, a standard, and a log book, and he had learned the "
        "thing his whole later life assumes: that music, which "
        "feels like weather, is made in rooms, by work, and can be "
        "kept. The young adult who follows was already formed; "
        "only his circumstances were about to change."
    ),
    # Chapter 5 -- The Young Adult
    "q041": (
        "He left home at nineteen, not in anger and not far in "
        "spirit: a rented room near the studio, a mattress, a hot "
        "plate, and his mother's piano still the place he went on "
        "Sundays. The record shows a leaving of the ordinary kind, "
        "a household becoming two households that shared a table "
        "every week."
    ),
    "q042": (
        "His first independent work was engineering sessions for "
        "local singers, hired by word of mouth. The first full "
        "album the record credits to him is by the Night Clerks, a "
        "Memphis band whose singer had heard what he did with a "
        "demo and asked for him by name. It is a modest credit. It "
        "is also the first time the name Frozen appears in print "
        "as the man behind the glass."
    ),
    "q043": (
        "The money of those years was by the session, and "
        "sometimes in trade, and he logged it like sessions: rent "
        "first, tape second, food third, which was his own joke "
        "about the order and also, the record suggests, roughly "
        "the truth. He was never, in these years, ahead. He was "
        "also never, the log shows, behind on the rent."
    ),
    "q044": (
        "The times he came of age in were changing under the "
        "trade: tape giving way, slowly, to newer machines, and "
        "studios arguing about it like a religion. The record "
        "shows him learning both and refusing the argument. A tool "
        "is a tool, he said; the log is the log. It was his "
        "father's doctrine, applied to a quarrel his father never had."
    ),
    "q045": (
        "His ambition in those years was stated plainly and often, "
        "to anyone who asked and some who did not: he wanted a room "
        "of his own where the work was done right. I want a room "
        "where it is done right. The sentence is recorded by three "
        "separate witnesses, which in this biography counts as a "
        "document."
    ),
    "q046": (
        "The setback of the young adult years was a studio closure: "
        "a room he depended on shut its doors with two weeks of his "
        "pay inside it. He worked a winter repairing televisions to "
        "stay even, his father's trade as the net under his own, "
        "and the record notes it without drama because he noted it "
        "without drama: one line in the log, and the winter's "
        "repairs itemized."
    ),
    "q047": (
        "Session work took him travelling, to other cities' rooms, "
        "for days and once for most of a season. The record is "
        "deliberately loose about the geography; what it keeps is "
        "the notebooks. He came home from every trip with a "
        "notebook full of other rooms' habits, what they did "
        "better, what they did worse, and what he meant to steal."
    ),
    "q048": (
        "His reputation formed in the way reputations in a trade "
        "actually form: singers asked for him by name. Get Frozen, "
        "the record shows them saying, because he listened before "
        "he touched a dial, and because a session with him ended "
        "with everything labelled. It was not fame. It was better "
        "than fame, in his own later judgment: it was repeat work."
    ),
    "q049": (
        "What the record leaves out of these years is his own "
        "music. He was engineering other people's records by day "
        "and writing his own songs at night, and the songs went "
        "into a drawer, unrecorded, while the drawer filled. The "
        "biographer flags the omission because the subject flagged "
        "it himself, later, as the central evasion of his young life."
    ),
    "q050": (
        "The chapter turns in 1988, when the old icehouse at the "
        "end of his childhood street, the thick-walled building he "
        "had passed every day as a boy, came up for lease. He took "
        "it. The young adult had found the room he had been "
        "describing for a decade, and it had been waiting at the "
        "end of the street where he started."
    ),
}

ANSWERS.update({
    # Chapter 6 -- The Work
    "q051": (
        "His principal work, from 1988, was the Cold Room: the "
        "small recording studio he founded in the converted "
        "icehouse at the end of his childhood street. The work was "
        "recording other people's music, done to his standard, and "
        "slowly, in the hours the studio was dark, his own. The "
        "record treats the founding as the life's hinge, and so "
        "does he."
    ),
    "q052": (
        "His method at the height of the work was his father's "
        "saying made into a studio rule: tape does not care what "
        "you meant. Listen first. Set the room before the artist "
        "arrives. Keep the log open on the desk. He held that a "
        "session is decided before the first note, in the "
        "preparation nobody applauds, and the record of the "
        "sessions supports him."
    ),
    "q053": (
        "The work he is best known for is the Night Clerks' album "
        "Static Bloom, the record most people name when his name "
        "comes up. The documentary record supports the association "
        "and complicates it: the log shows a band at its peak and "
        "an engineer who mostly stayed out of the way. He deflects "
        "the credit to the band to this day, and the deflection is "
        "also documented."
    ),
    "q054": (
        "A representative day at the height of it: up before the "
        "session, the machine aligned, coffee, the log open. The "
        "artists arrived to a room already listening. The day ended "
        "when the room was reset for tomorrow, the reels labelled, "
        "the failures written down with their causes. Witnesses "
        "describe the routine as unvarying, and the unvarying as "
        "the point."
    ),
    "q055": (
        "The object that best evidences the work is a ribbon "
        "microphone he rebuilt in his father's shop from a dead "
        "unit and spare parts, and used ever after on quiet songs. "
        "It sits on a shelf in the Cold Room still, with its log "
        "entry beside it: what was wrong, what he did, what it has "
        "recorded since. The biographer knows no cleaner summary "
        "of the man."
    ),
    "q056": (
        "His collaborators, as the record documents them, were "
        "Marcus Webb until Webb retired, a circle of Memphis "
        "players who came and went through the Cold Room's door, "
        "and, on early sessions, his younger sister Ruth, who sang "
        "harmony and kept the books for the studio's first two "
        "years. The work was solitary in method and crowded in fact."
    ),
    "q057": (
        "The recognition the record documents is modest and "
        "mostly in print small enough to miss: album credits, a "
        "newspaper profile that got his age wrong and his work "
        "right, and the trade's own currency, which is the repeat "
        "call. He kept the profile in the log book, the error "
        "uncorrected, as a reminder of what print is worth."
    ),
    "q058": (
        "The money the work made was enough, most years, and the "
        "record is honest about the mechanism: the studio paid its "
        "way, and in the thin years the repair bench at the back "
        "of the building, his father's trade carried on, covered "
        "what the sessions did not. He never separated the two "
        "trades in the accounts, because he never separated them "
        "in himself."
    ),
    "q059": (
        "The work he left unfinished is his own album: the songs "
        "from the drawer of his young years, begun as reels in the "
        "studio's dark hours, set aside for other people's records "
        "for the better part of two decades. The record does not "
        "excuse it. It notes that he finished other people's work "
        "first, every time, and that he knew the cost while he "
        "paid it."
    ),
    "q060": (
        "The chapter turns on a work with a place and a name: the "
        "Cold Room, its log books filling, its standard known. And "
        "in 1991 the work gained a witness, when the photographer "
        "hired to shoot a session stayed to argue about the light, "
        "and the household chapter of the life began."
    ),
    # Chapter 7 -- Love and Household
    "q061": (
        f"{PARTNER}, born Alice Verano, a photographer. She enters "
        "the documented record as a working artist in her own "
        "right: hired in 1990 to photograph a session at the Cold "
        "Room, married to the subject in 1991, and thereafter the "
        "person whose prints of his rooms hang in every room he "
        "worked in."
    ),
    "q062": (
        "They met at work, in 1990, when Alice Verano was hired to "
        "photograph a session and told the engineer, within the "
        "hour, that his studio had the best light of any room that "
        "was not supposed to have any. The session log for that day "
        "survives. Her name is in it, in his handwriting, spelled "
        "right the first time, which witnesses treat as evidence."
    ),
    "q063": (
        "The courtship survives in the record as letters, hers "
        "kept in a labelled box in the studio, written from the "
        "road when her work travelled, and in his log books, where "
        "her sessions and visits are entered with the same care as "
        "the music. They married in 1991. The biographer notes "
        "that this is the best-documented chapter of the life, and "
        "that the documentation is mostly hers."
    ),
    "q064": (
        "The household they made was a small house two streets "
        "from the studio: her darkroom in the back room, his bench "
        "in the shed, and, after his mother died, his mother's "
        "piano in the front room, where it stands in the record "
        "from then on. It was a working house. Both of them said "
        "so, as praise."
    ),
    "q065": (
        "The household held no children of their own; its children "
        "were his sister Ruth's, who were there on weekends and "
        "holidays and grew up, in effect, with two households. The "
        "record mentions it plainly because the witnesses do: the "
        "house was full, on the days it was full, and quiet in a "
        "way both of them defended on the others."
    ),
    "q066": (
        "His partner's work, as the record documents it, was "
        "photography: portraits, rooms, working people at their "
        "benches and instruments. The Cold Room's walls are her "
        "prints. Between them, the witnesses say, the two of them "
        "documented the same world twice, once in sound and once "
        "in light, and the archive of each is the other's index."
    ),
    "q067": (
        "The household's economy was two irregular incomes and one "
        "regular habit: the log. They kept a household book with "
        "the same rules as the session logs, everything entered, "
        "nothing rounded in their own favour. It is an "
        "unromantic document and the biographer recommends it as "
        "the truest portrait of the marriage that survives."
    ),
    "q068": (
        "The strain the record shows in the household came with "
        "money, in the thin years, and took the form of his "
        "silences, which she named in a letter the record keeps: "
        "he went quiet the way a room goes quiet, all at once and "
        "on purpose. What held them, by both accounts, was her "
        "refusal to let him sell his mother's piano, ever, for any "
        "bill. Some things were not the accounts' business."
    ),
    "q069": (
        "What the witnesses say of the household is consistent to "
        "the point of suspicion, until the biographer notes the "
        "source: most of them ate there. Friends describe a house "
        "where work and supper were the same conversation, where "
        "a session's failure and a soup's failure got the same "
        "post-mortem, and where both were usually fixed by morning."
    ),
    "q070": (
        "The chapter turns with the household proven: two trades, "
        "one house, a book kept honestly. What it had been built "
        "to hold against arrived in the next decade, when the "
        "standing he had earned met the years that tested it, and "
        "then, in a single night, the fire."
    ),
    # Chapter 8 -- Standing and Struggle
    "q071": (
        "His standing at its height, by the late nineteen-nineties, "
        "was that of a fixture: the man singers asked for, the "
        "room other engineers visited to see how it was done. The "
        "record shows it was built the slow way, on log books and "
        "clean sessions and reels labelled right, and that he "
        "trusted it exactly as far as it was built and no further."
    ),
    "q072": (
        "The institutional record of the standing is boring, which "
        "is its distinction: the studio's licences in order, its "
        "taxes paid, one bank loan taken for the roof and retired "
        "early. The biographer lists these because the subject "
        "listed them, among his achievements, without irony. "
        "Keeping the paperwork was keeping the room."
    ),
    "q073": (
        "The opposition the record documents came as an offer: a "
        "larger studio concern proposed to buy the Cold Room, its "
        "name and its book of work, and close it, the building "
        "being worth more to them dark than lit. He refused, in "
        "writing, in one sentence, which the record keeps and the "
        "legacy chapter will return to."
    ),
    "q074": (
        "The money trouble of the standing years came when "
        "recording budgets shrank and sessions thinned across the "
        "whole trade. The record shows the answer was the old one: "
        "the repair bench at the back of the building carried the "
        "studio through, radios and televisions paying for tape. "
        "He entered those years in the log without self-pity, "
        "itemized."
    ),
    "q075": (
        "The failure of his own the record keeps in this chapter "
        "is the album: his own record, shelved twice in these "
        "years, once for money and once, by his own entry in the "
        "log, for fear of finishing it. He called it the record of "
        "his cowardice and his standards in equal measure, and the "
        "biographer has found no witness who disagreed with either half."
    ),
    "q076": (
        "The public criticism the record preserves is a review "
        "that called his production old-fashioned, a decade behind "
        "the fashion. He kept the clipping, pinned inside the "
        "front cover of the current log book, where he would see "
        "it daily. Evidence, not injury, he said, when asked. It "
        "is still there in the record, and so, the biographer "
        "notes, is he."
    ),
    "q077": (
        "The private cost the record shows is his hearing: the "
        "left ear is not what it was, after years of loud rooms, "
        "and he mixes accordingly and says so to clients in "
        "advance, in writing. The biographer records it as he "
        "recorded it himself: a tradesman's wear, entered in the "
        "log like a machine's, with the adjustment noted beside it."
    ),
    "q078": (
        "What he refused, in these years, besides the buyout, was "
        "work he thought dishonest: most clearly, a session meant "
        "to copy another singer's record note for note and pass "
        "as an original. He declined it and sent the client, "
        "politely and in writing, to the very concern that had "
        "tried to buy him. The letter survives. It is courteous. "
        "It is final."
    ),
    "q079": (
        "The support the record documents around him in the "
        "struggle years was the household first, Alice and the "
        "house two streets away; his sister Ruth, who had kept "
        "the studio's books and now kept its spirits; and the "
        "players, who began bringing him their own students to "
        "teach, which he counted, correctly, as the trade's vote."
    ),
    "q080": (
        "The chapter turns in 2003, in one night: a fire in the "
        "building next door, and then in his. The Cold Room as "
        "first built, the room of his young ambition, burned. What "
        "the fire could not take is the subject of the rest of "
        "this biography: the log books were at the house, and the "
        "standard was in the man."
    ),
    # Chapter 9 -- Late Years and Death
    "q081": (
        "His late-life circumstances begin with the rebuilding: "
        "two years after the fire of 2003 in which the Cold Room "
        "rose again in the same thick walls, slower, smaller, and "
        "entirely his. The late years of the record are the rebuilt "
        "room and a calendar he finally chose himself: fewer "
        "sessions, each one wanted."
    ),
    "q082": (
        "His routine in the late years is documented by everyone "
        "who visited: mornings at the repair bench, afternoons in "
        "the studio, evenings at his mother's piano in the front "
        "room of the house. He kept the log. He answered letters "
        "from young engineers in full. Witnesses describe a man "
        "whose days had become the shape his young self had asked for."
    ),
    "q083": (
        "The late work the record shows is twofold: finishing, at "
        "last and in pieces, his own album, the drawer's songs "
        "becoming reels; and teaching, two young engineers taken "
        "on the old terms, no wages at first, paid in tape and "
        "lessons, who learned the log book habit at his bench the "
        "way he had learned it at Webb's."
    ),
    "q084": (
        "His health in the record is entered as he entered "
        "everything: the left ear, as documented; a knee that "
        "predicts weather, which was his joke and also, witnesses "
        "say, accurate; otherwise sound. He was impatient with "
        "sympathy and with questions about retirement, a word he "
        "treated as a rumour about other people."
    ),
    "q085": (
        "The deaths in his immediate family came in their order. "
        "His father died in 1998, at home, with his tools in reach "
        "in the shed, as he would have specified. His mother died "
        "in 2005; her piano was not sold, then or ever, and stands "
        "in the subject's front room in the record from that year "
        "forward. He wrote both entries in the log himself, in his "
        "ordinary hand."
    ),
    "q086": (
        "Among contemporaries, the death the record weighs most "
        "is Marcus Webb's, in 2011. The subject spoke at the "
        "service, about cable coiled right and logs kept honestly, "
        "and was given Webb's studio log books afterward, which he "
        "keeps still, shelved with his own. The apprenticeship's "
        "archive is complete, in one room, in his keeping."
    ),
    "q087": (
        f"{NAME} has not died. The survey reaches him alive, in "
        "his middle sixties, working shorter days in the room he "
        "rebuilt, and the pages that in another life would record "
        "an ending record instead what he has arranged: the log "
        "books to the studio's keeping, the rebuilt microphone to "
        "stay on its shelf, the piano to his sister's daughter. "
        "He is, by every account including his own, not finished."
    ),
    "q088": (
        "What he has said about his own end is said the way he "
        "says everything, in advance and in writing: he is to lie "
        "beside his parents in the Memphis ground where the Harts "
        "and the Flames family are, with no stone larger than "
        "theirs. The record notes the instruction exists, in the "
        "front of the current log book, where the right person "
        "will find it."
    ),
    "q089": (
        "The instructions he has left are kept with the log books "
        "and are practical: the studio to be offered first to the "
        "engineers he taught, at the value of its work and not its "
        "walls; the tapes catalogued and kept; his own album, "
        "finished or not, to be labelled honestly either way. It "
        "is less a will than a session log for an event he will "
        "not engineer."
    ),
    "q090": (
        "His most recent recorded words, given to a young engineer "
        "who asked him what all the work had been for, are these: "
        "so the room would be ready for whoever comes next. The "
        "biographer offers them without improvement, as the "
        "subject's own summary of the late years, and notes that "
        "the room, on the day the words were recorded, was ready."
    ),
    # Chapter 10 -- Legacy
    "q091": (
        "His reputation today, as the record documents it, lives "
        "in the trade's mouth: among the singers and engineers of "
        "his city he is a standard of comparison, and a session "
        "done the way Frozen does it is a phrase with a meaning "
        "everyone in that world can unpack. It is a local "
        "reputation. The record shows he never wanted a larger "
        "kind, and got the kind he wanted."
    ),
    "q092": (
        "The record against the reputation is incomplete, and the "
        "biographer says so plainly: much of his best work is "
        "uncredited session work, present in the music and absent "
        "from the sleeves. The truer record is the log books, a "
        "hundred sessions a year for decades, in his hand. "
        "Reputation says he mattered. The logs say how, and when, "
        "and for whom."
    ),
    "q093": (
        "His influence, as documented, runs through hands: the "
        "two engineers he taught now teach the log book habit to "
        "their own assistants, and rooms he has never seen run on "
        "session sheets copied from his. Influence of this kind "
        "does not announce itself. The record finds it the way he "
        "would: in other people's paperwork, done right."
    ),
    "q094": (
        "The material legacy the record can point to is a set of "
        "working objects: the Cold Room itself, rebuilt; the log "
        "books, complete; the rebuilt ribbon microphone on its "
        "shelf, still used on quiet songs; his mother's piano, "
        "still played. Nothing in the list is a monument. "
        "Everything in it works, which the biographer takes to be "
        "the point of the list."
    ),
    "q095": (
        "The saying he is quoted by, in other people's studios "
        "now, is the rule of his room: tape does not care what you "
        "meant. He always credited it to his father, who said it "
        "first about radios, and the record supports the credit. "
        "It is the closest thing the life has to a motto, and he "
        "would want it entered correctly: inherited, not invented."
    ),
    "q096": (
        "What is misremembered about him, the record shows, is "
        "generous error: he is credited, in talk, with records he "
        "only repaired equipment for, and with sessions he "
        "attended as a boy with a broom. He corrects it when it "
        "happens, in writing, in the log, without embarrassment to "
        "anyone. The corrections are part of the archive, and the "
        "biographer has relied on them gratefully."
    ),
    "q097": (
        "His own assessment of the life, given more than once and "
        "in nearly the same words, is that he is a tradesman of "
        "other people's best days, and that this is not modesty "
        "but bookkeeping. The record, weighed whole, supports the "
        "assessment and the spirit of it: he kept the books of "
        "his life the way he kept the session logs, and understated "
        "his own part in both."
    ),
    "q098": (
        "The refusal he is most known for is the buyout: money "
        "enough to stop, offered for the room and its name, "
        "refused in one written sentence because the room was the "
        "work and not its price. Strangers tell that story about "
        "him more than any other. The record confirms the offer, "
        "the sentence, and the refusal, and notes that he never "
        "told the story himself if he could help it."
    ),
    "q099": (
        "What remains open in the record is his own album: the "
        "drawer's songs, decades in the finishing, which he works "
        "on still in the studio's dark hours. The biographer "
        "cannot close the account and does not pretend to. The "
        "last reel, in the subject's own log entry on the matter, "
        "is not yet labelled."
    ),
    "q100": (
        "The biographer's final assessment, on the whole record, "
        "is this: a life spent making rooms where other people's "
        "music could stay. The ear came from his mother, the hands "
        "from his father, the standard from his master, and the "
        "room from all three. What he added was the keeping: the "
        "log written down, the work done right, and the room left "
        "ready for whoever comes next."
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


def main() -> int:
    problems = []
    if len(ANSWERS) != 100:
        problems.append(f"expected 100 answers, have {len(ANSWERS)}")
    for slot, (qid, value) in FACT_ANSWERS.items():
        if value not in ANSWERS.get(qid, ""):
            problems.append(
                f"character fact {slot}={value!r} missing from {qid}")
    if re.search(r"\b(1[0-9]{3}|20[0-9]{2})\b", ANSWERS["q087"]):
        problems.append("q087 must contain no year (living subject)")
    for stale in ("Brandt", "Calloway", "Pittsburgh", "Walter",
                  "Josef", "Clara", "Anna"):
        for qid, text in ANSWERS.items():
            if stale in text:
                problems.append(f"stale persona token {stale!r} in {qid}")
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
            "demo/frozen-in-flames-character.json. The life described "
            "was invented as test data for the biography pack and is "
            "not a biography of any real person."
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
