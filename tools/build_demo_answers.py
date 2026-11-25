"""Builds demo/memoir-demo-answers.json.

The respondent is a fictional demonstration persona, June Calloway,
invented as test data for the memoir pack. Every biographical detail
in these answers is fabricated for demonstration. The answers are
internally consistent with the pack's fixed facts: birth year 1962,
mother Rosa Calloway, father Henry Calloway, hometown Saltmarsh,
partner Daniel Reyes.

The q000 answer was added with memoir pack v1.1.0 (2026-11-25),
when the clean-proof audit put the identity question into the
survey: before that, the narrator's name existed only as this
file's persona metadata. The shipped book ("The Porch Light",
v0.1.0) was generated under pack v1.0.0 and does not contain the
identity question's page; the answer is recorded here so the pack
and its demonstration answers stay paired for future builds.
"""

import json
from pathlib import Path

A = {}
A["q000"] = (
    "June Calloway. That is my full name, and the main character "
    "of this memoir is me: the life in this book is my own. "
    "Calloway is my father's name, Louisiana people who repaired "
    "engines along the coast; my mother was a Delgado from "
    "Veracruz before she was a Calloway, so both of the family's "
    "coasts are in the name I sign. I married a Reyes and kept "
    "Calloway, which tells you something about me that the rest "
    "of this book will spend a hundred pages confirming."
)
A["q001"] = (
    "I was born in 1962, in Beaumont, Texas, in the spring. The world "
    "that year was holding its breath over Cuba, and my father said the "
    "radio in the cafe never really got turned off until November. I "
    "was the second child and the first daughter, born into a family "
    "that measured time by tides and tourist seasons more than by "
    "calendars."
)
A["q002"] = (
    "My mother's people came from Veracruz, crossing to Texas when my "
    "grandfather Tomas Delgado was nineteen, with a net, a skillet, and "
    "strong opinions about both. My father's people were Louisiana "
    "Calloways who drifted west along the coast repairing engines. The "
    "two families met, as everyone in Saltmarsh eventually did, at the "
    "harbor, over fish and weather."
)
A["q003"] = (
    "The oldest relative I have a clear story about is my grandfather "
    "Tomas Delgado. During a storm in 1948 he rowed out to bring in two "
    "men whose boat had swamped, and he refused all thanks, saying the "
    "sea keeps accounts and he was only paying his. My mother told that "
    "story whenever one of us claimed we had done something generous."
)
A["q004"] = (
    "We believed we were the people who fed Saltmarsh, and that feeding "
    "people was a kind of covenant. If someone was hungry, the reason "
    "did not matter. My mother said a town is just the people who will "
    "feed each other without being asked, and she ran the Harbor Cafe "
    "for forty years on exactly that doctrine."
)
A["q005"] = (
    "We were working people who were sometimes poor and never once "
    "called it that. The cafe made money in summer and lost it in "
    "winter. My father's mechanic work filled the gaps. I understood "
    "early that the good china and the cracked mugs came out for the "
    "same guests, and that pride in our house had nothing to do with "
    "money."
)
A["q006"] = (
    "Nobody said out loud that my grandfather Tomas had a first family "
    "in Veracruz, a wife who died before he crossed. I pieced it "
    "together at thirty from a photograph and an aunt's slip of the "
    "tongue. It explained his silences at certain songs. The secret was "
    "never shame, I think. It was grief that had never been given a "
    "room in the house."
)
A["q007"] = (
    "My mother's cast-iron skillet. It crossed the Gulf in 1919 in my "
    "grandmother's luggage, it cooked in the cafe every day of my "
    "childhood, and it sits on my stove now, black as a well. When I "
    "lift it I am lifting the exact weight my grandmother lifted. Some "
    "families hand down jewelry. Mine handed down a pan and expected "
    "you to understand."
)
A["q008"] = (
    "We were Catholic in a town that was mostly Baptist, and we spoke "
    "Spanish at home and English everywhere else, switching mid-sentence "
    "without noticing. On Fridays the cafe served fish whether you "
    "ordered it or not. Neighbors thought the statues in our windows "
    "were decoration. They were not decoration. They were the "
    "management, my mother said, and she only half meant it as a joke."
)
A["q009"] = (
    "We feed people. It was on no sign and in no frame, but it decided "
    "everything: who got hired, who got credit, who got the last piece "
    "of pie. If a stranger came in broke, the motto answered before "
    "anyone could think. I have tried to live by other rules since, "
    "simpler and more selfish ones, and they never once held."
)
A["q010"] = (
    "I wish I had known that the silences were grief and not coldness, "
    "and that my grandfather's whole first life was sitting at our "
    "table every night, unmentioned. As a child I thought the adults "
    "were simply complete, like furniture. Knowing they were carrying "
    "things would not have lightened the carrying, but it would have "
    "changed how I judged the carriers."
)
A["q011"] = (
    "A white frame house on low stilts on Harbor Street, two streets "
    "from the water, with a porch that ran the whole front and a roof "
    "my father patched so often he called it the quilt. From outside "
    "it looked like every other house in Saltmarsh, which was the "
    "point. Inside, it was unmistakably ours, and I could have found "
    "it blindfolded by smell alone."
)
A["q012"] = (
    "You came in through the screen door, which slapped shut behind "
    "every person who ever entered, and the house announced you. It "
    "smelled of coffee, floor wax, and whatever was in my mother's "
    "skillet, over a base note of salt and mildew that no cleaning "
    "ever defeated. It sounded like the radio, the clock over the "
    "stove, and gulls complaining outside the kitchen window."
)
A["q013"] = (
    "Saltmarsh, my hometown, a town of about four thousand on the Texas "
    "Gulf Coast, known for shrimp, for the ferry landing, and for "
    "being the place people passed through on the way to somewhere "
    "with a bigger name. It had one school, three churches, two cafes "
    "counting ours, and a harbor that employed half the town and fed "
    "the other half."
)
A["q014"] = (
    "The kitchen, without argument. It was the largest room, it held "
    "the stove, the long table, the tide chart nailed by the door, and "
    "every important conversation of my childhood. Homework happened "
    "there, and discipline, and celebrations, and the nightly council "
    "where my parents divided the world into what could be fixed and "
    "what had to be weathered."
)
A["q015"] = (
    "The porch first, then Harbor Street, then the marsh itself, which "
    "began where the mowed grass gave up. At high tide the water "
    "silvered under the houses. We had a yard of sand and stubborn "
    "grass, a fig tree my grandfather planted, and a clear view of the "
    "sky doing its enormous evening performance over the bay."
)
A["q016"] = (
    "Under the roof: my parents, my older brother Tomas, my younger "
    "sister Lily, and me. Nearly under it: my grandmother Odette, who "
    "took Sunday dinner and most weekdays with us; Uncle Ray, who "
    "appeared between boats; and Willa Brandt from next door, who had "
    "her own key before she had her own bicycle."
)
A["q017"] = (
    "The screen door. Not its slam, everyone remembers a slam, but the "
    "particular two-note complaint of its spring, a creak and then a "
    "catch, that told you someone was coming in before they were in. I "
    "hear it in dreams with total fidelity. When the house was repaired "
    "after the hurricane they replaced that door, and I grieved it "
    "like a person."
)
A["q018"] = (
    "The roof, perpetually. The porch step that dipped. A window in my "
    "brother's room that had to be persuaded with a butter knife. My "
    "father fixed things with what the harbor discarded, and some of "
    "his repairs were better than the original construction and some "
    "were acts of optimism. Nothing in that house was new except the "
    "food."
)
A["q019"] = (
    "Supper at six, because the cafe closed at five-thirty and my "
    "mother cooked twice every day of her life, once for the town and "
    "once for us. Then dishes, then the radio, then my father on the "
    "porch with the tide chart and the weather, deciding tomorrow. We "
    "children did homework at the kitchen table and were sent to bed "
    "in order of age, oldest last, which I resented on principle."
)
A["q020"] = (
    "I last saw it in 2019, after my mother's death, before we sold it. "
    "The fig tree was gone. The porch had been rebuilt straight and "
    "level, which made it a stranger. Someone had painted the kitchen "
    "a color called Seaside that my mother would have described "
    "accurately and unkindly. It was a good house. It was no longer "
    "the house, and I understood the difference is the people."
)
A["q021"] = (
    "Rosa Calloway. She was born Rosa Delgado, and everyone who knew "
    "her called her Rosie, except my father, who called her Rosa in a "
    "tone that ended arguments and started dances. She ran the Harbor "
    "Cafe from the age of twenty-six until the hurricane took it, and "
    "she was the fixed point of Saltmarsh in a way the town only "
    "admitted after she was gone."
)
A["q022"] = (
    "Her hands were never still and never idle. At the cafe they "
    "rolled tortillas, wrote the day's menu in chalk, made change "
    "without looking, and rested, briefly, on the shoulders of anyone "
    "sitting alone too long. At home they mended, kneaded, shelled, "
    "and pointed, and the pointing alone could stop my brother "
    "mid-sentence from another room, or so it felt."
)
A["q023"] = (
    "The morning the health inspector came in 1974, my mother served "
    "him coffee, asked after his mother by name, fed him pie, and then "
    "walked him through her kitchen like a general reviewing troops "
    "she was proud of. He found two violations and apologized for "
    "both. Walking out he said, 'Rosie, this kitchen is cleaner than "
    "my hospital,' and she said, 'Then eat here, baby, it's safer.'"
)
A["q024"] = (
    "Henry Calloway. The town called him Hank, and the harbor called "
    "him when an engine mattered. He was a shrimp-boat mechanic with "
    "a Louisiana drawl he never lost and a belief that any machine "
    "honestly examined would confess its problem. He was quieter than "
    "my mother in every register, and his silences were a language "
    "the whole family learned to read."
)
A["q025"] = (
    "He worked bent over other men's engines in heat that shimmered, "
    "and the work wrote itself on him: hands permanently lined with "
    "grease at the knuckles, a back that stiffened every winter of his "
    "fifties, hearing worn thin on the left side. He never complained "
    "about the work itself. He complained about men who neglected "
    "engines, the way priests complain about sin."
)
A["q026"] = (
    "One October evening a boat came in dead and my father stayed at "
    "the harbor past midnight, working by lantern while the crew "
    "waited. I brought him coffee at ten, being twelve and trusted "
    "with the thermos. He never looked up, just said, 'Set it where I "
    "can reach it, June,' and I understood I had been given a post in "
    "the operation. I have rarely felt so employed since."
)
A["q027"] = (
    "They gave each other loyalty so complete it was almost a country. "
    "What they withheld was words. My father never said he was afraid, "
    "my mother never said she was tired, and each protected the other "
    "from the information at some cost to themselves. They were a "
    "good marriage. They were also a demonstration that love and "
    "candor are separate virtues, and a house can run on one."
)
A["q028"] = (
    "My brother Tomas is three years older, built like our father, "
    "with our mother's temper kept in a locked drawer he opens "
    "rarely. My sister Lily is five years younger, the only one of us "
    "who left Saltmarsh for good and the only one who calls every "
    "Sunday without fail. We were a triangle: Tomas the anchor, me "
    "the narrator, Lily the escape artist we all quietly envied."
)
A["q029"] = (
    "My grandmother Odette, my father's mother. She taught me cards, "
    "French hymns, and the management of grief, in that order. What "
    "passed between us without words was a complete understanding "
    "that the family's emotional weather would be handled by the "
    "women quietly, and that this was both an honor and a theft. She "
    "died when I was sixteen and I still set a place for her in my "
    "head."
)
A["q030"] = (
    "We never said that we were struggling, and we never said that "
    "anyone was forgiven. Both subjects were handled by food. If my "
    "mother made your favorite dish, the matter was closed, whatever "
    "the matter was. It took me forty years and one failed business "
    "to learn to say 'I am sorry' in plain words to a living person, "
    "and I learned it from watching the cost of the other way."
)
A["q031"] = (
    "Saltmarsh Elementary, a brick building with windows that opened "
    "with a crank and a flagpole we saluted in the heat. On my first "
    "day I wore a dress my grandmother had altered and I carried a "
    "tin lunchbox with a dent I can still describe. I cried at the "
    "door, was handed a crayon by a girl named Willa Brandt, and "
    "stopped. That was the whole negotiation."
)
A["q032"] = (
    "Willa Brandt, from the house next door, who decided on the first "
    "day of school that we were friends and simply never revisited "
    "the decision. She was braver than me, funnier than me, and the "
    "first person who ever made me laugh until it hurt. Sixty years "
    "later she is still the first person I call, and she still "
    "answers like no time has passed."
)
A["q033"] = (
    "Down Harbor Street in a line of children that dissolved and "
    "re-formed like a flock, past the cafe where my mother would "
    "appear at the screen door exactly as we passed, which we "
    "pretended was coincidence for years. The route smelled of salt "
    "and diesel and, near the school, of the mimosa tree by the "
    "fence, sweet enough to make you stop."
)
A["q034"] = (
    "Mrs. Okafor, my fourth-grade teacher, who found me reading under "
    "the desk during arithmetic and, instead of punishing me, began "
    "leaving books on my desk with notes in them. She told my mother, "
    "'This one is going to teach,' in my hearing, on purpose. It was "
    "the first time an adult outside my family described me as a "
    "future, and I have been walking toward her sentence ever since."
)
A["q035"] = (
    "Kickball on the packed sand behind the school at low tide, with "
    "bases that had to be re-established every day because the sea "
    "took the field back every night. The impermanence was the point, "
    "though we did not know it. Rules were renegotiated each "
    "afternoon like a small parliament, and Willa was, by acclamation "
    "and by force of personality, the parliament."
)
A["q036"] = (
    "I was the one who read. Among the children this meant I was "
    "consulted about plots, excuses, and the wording of notes, and "
    "teased with an affection I only recognized later as respect. "
    "Tomas was the strong one, Willa was the brave one, and I was the "
    "one who would remember, which turned out to be a job with "
    "duties nobody warns you about."
)
A["q037"] = (
    "Sunday dinner at my grandmother Odette's, where the gumbo took "
    "two days and the roux was a subject of theology. She cooked "
    "Louisiana into a Texas town one pot at a time. I remember the "
    "dark shine of that roux, the okra cut thin as coins, and being "
    "given the spoon to stir exactly once, under supervision, like "
    "handling a relic."
)
A["q038"] = (
    "The water. I nearly drowned at eight, caught by an undertow at "
    "the public beach while the adults were twenty feet and one "
    "conversation away. After that I managed the fear by learning the "
    "tide chart the way other children learned catechism. If I knew "
    "when the water would move, I believed it could not surprise me. "
    "I was wrong about the logic and right about the comfort."
)
A["q039"] = (
    "I kept a tide journal, a composition book where I recorded the "
    "tides, the weather, and one sentence a day about what had "
    "happened, from the age of nine. It was the first thing I made "
    "that was entirely mine and entirely useless to anyone else, "
    "which is to say it was the first draft of this book, sixty years "
    "early."
)
A["q040"] = (
    "A day in the summer I was ten, when the tide, the light, my "
    "father's rare free afternoon, and a string of fish all arrived "
    "at once. We stayed on the water until the sky went the color of "
    "the inside of a shell. Nothing since has been perfect in that "
    "unargued way. I stopped expecting it to be. That day is my "
    "evidence that perfection is a thing that happens, briefly, and "
    "is not a standard."
)
A["q041"] = (
    "The drowning that nearly was, at eight. I remember the green "
    "light, the sand leaving under my feet, and the specific shame, "
    "as I was pulled out coughing, of having caused a scene. Before "
    "that day I believed the world was supervised. After it I "
    "understood that love and attention are not the same thing, and "
    "that a child can be adored and still go under."
)
A["q042"] = (
    "My grandmother Odette, who held me that night and did not say it "
    "was nothing, which is what the other adults said. She said, 'The "
    "water took your breath. It did not take you.' I have used that "
    "sentence, adjusted, on frightened children for fifty years. Who "
    "failed to comfort me was my father, who could not come into the "
    "room, because his fear had nowhere to sit down."
)
A["q043"] = (
    "Our dog Biscuit, run over on Harbor Street when I was nine, was "
    "the first death I attended. We buried him under the fig tree "
    "with a ceremony my brother conducted in a borrowed cassock of "
    "seriousness. I learned that grief is not proportional to the "
    "size of the lost, and that a family that buries a dog properly "
    "is practicing for harder work."
)
A["q044"] = (
    "My father's silence. When Tomas and I broke the harbor master's "
    "skiff loose through carelessness, my father did not raise his "
    "voice. He repaired the damage with us over two weekends and "
    "spoke only about the work, and the absence of his ordinary words "
    "was a weight I have never forgotten. I decided then that I would "
    "rather be shouted at by anyone than silenced by him."
)
A["q045"] = (
    "I was eleven when a neighbor's boat was repossessed and the man's "
    "children, my classmates, were told at school by other children "
    "before their parents could tell them at home. I watched the "
    "adults of the town, including mine, arrange their faces into "
    "helplessness. I understood that grown people could see a wrong "
    "clearly and still choose the dignity of doing nothing."
)
A["q046"] = (
    "I wrote it down. Anger and grief went into the tide journal in "
    "code, one flat sentence each, because the feelings were too big "
    "for the house's rules about volume. 'Wind from the north. "
    "Nobody apologized.' Reading them now I can decode every one "
    "instantly. The code was never to hide the feelings from others. "
    "It was to make them small enough to keep."
)
A["q047"] = (
    "The drowning divided it, but the formal before-and-after was the "
    "winter I was twelve, when my father crushed two fingers in an "
    "engine and the cafe carried us entirely. He sat at the kitchen "
    "table with his hand bandaged like a parcel, learning to be "
    "helped, which was the hardest work of his life. We were all "
    "different after that winter: quicker to sit down with each other."
)
A["q048"] = (
    "I blamed myself for my brother's broken arm. I was thirteen; I "
    "had dared Tomas to walk the ridge of the harbor warehouse roof, "
    "and he fell, and for years I carried it as my injury done to "
    "him. He never blamed me, which somehow made it heavier. At forty "
    "I finally told him. He said, 'June, I was showing off. You were "
    "just the audience I chose.'"
)
A["q049"] = (
    "I have never fully told anyone that in the year after the "
    "drowning I was afraid of my father, not of anything he did, but "
    "of his fear, which filled rooms. It felt like disloyalty to "
    "notice it, so I noticed it alone for decades. I am telling it "
    "now because he is beyond being hurt by it, and because some "
    "reader's child is noticing the same thing tonight, alone."
)
A["q050"] = (
    "They taught me to go quiet and write it down. To this day, when "
    "I am hurt, my first move is silence and my second is a notebook, "
    "and only much later, sometimes, a voice. It made me a writer and "
    "a difficult wife and a careful friend. The pattern is not the "
    "worst inheritance. But I have spent the second half of my life "
    "learning to reverse the order."
)
A["q051"] = (
    "The first day of high school, when Willa was put in a different "
    "homeroom and I ate lunch with the tide journal open like a "
    "shield. Nothing terrible happened. That was the knowledge: the "
    "world would now proceed by administration, in rooms assigned by "
    "other people, and childhood, which had been a place, was "
    "replaced by a schedule."
)
A["q052"] = (
    "At fifteen I wore my brother's castoff shirts and my hair cut "
    "short against orders, listened to my father's radio stations "
    "because we had one radio, and kept a room whose walls were "
    "covered in tide charts and one photograph of a library in a city "
    "I had never seen. My ambition was enormous and completely "
    "unfunded, and I guarded it like a second secret heart."
)
A["q053"] = (
    "I rebelled against the expectation that I would work in the cafe "
    "forever and marry locally and in order. The rebellion looked "
    "small from outside: a haircut, a library card used like a "
    "weapon, applications to colleges my parents had not heard of, "
    "filled out at the kitchen table in silence. My mother watched "
    "me go about it and said nothing, which I now know was her form "
    "of blessing."
)
A["q054"] = (
    "I wanted to become a teacher in a place with seasons, an idea I "
    "had assembled entirely from novels. The picture came from Mrs. "
    "Okafor's classroom and from books where women had rooms of their "
    "own and snow on the windowsill. I had never seen snow. The "
    "wanting was not really about weather. It was about a life whose "
    "terms I had chosen myself."
)
A["q055"] = (
    "Eli Navarro, the summer I was seventeen, who worked the ferry and "
    "read poetry he pretended not to read. What belongs in the book "
    "is this: he was the first person who kissed me like I was an "
    "argument he agreed with, and when he left for the Navy in the "
    "fall I grieved with a completeness that embarrassed me and "
    "taught me my own capacity."
)
A["q056"] = (
    "I hid the college applications, the poems, and the depth of my "
    "intention to leave. Not from cruelty. From arithmetic: my "
    "leaving would cost my mother her daughter at the cafe counter "
    "and cost me, I thought, her blessing. I was wrong about the "
    "blessing. She had been saving it, the way she saved everything, "
    "for when it was needed."
)
A["q057"] = (
    "Willa, again and always, and the harbor kids who gathered at the "
    "ferry landing: Tomas when he deigned, Eli, and a rotating crew "
    "united by boats and boredom. Willa formed me most because she "
    "refused every smallness the town offered her and made refusal "
    "look like a form of gaiety. She taught me that leaving and "
    "staying are both just addresses; the point is not to shrink."
)
A["q058"] = (
    "At sixteen I took my father's skiff out past the jetties in "
    "weather I had no business in, to prove the drowning had not "
    "marked me. The engine died. I was towed in by a shrimper who "
    "knew my father and, mercifully, told him only that the engine "
    "was at fault. The risk taught me the difference between courage "
    "and theater, mostly by the shaking of my own hands."
)
A["q059"] = (
    "A poem printed in the school paper when I was sixteen, about the "
    "porch light at the cafe, was the first thing entirely mine that "
    "existed in the world without my hands on it. People I did not "
    "know quoted it back at me at the counter. I understood that "
    "words could go where I could not, and I have organized my life "
    "around that discovery ever since."
)
A["q060"] = (
    "At eighteen I believed I would never live in Saltmarsh again, "
    "that love and geography were enemies, and that my mother's life "
    "at the cafe was a cautionary tale. I was certain about all of it "
    "with the clean certainty of a girl packing a suitcase. The "
    "reader of this book already knows how the town and I settled "
    "it. The girl would not believe me, and I forgive her."
)
A["q061"] = (
    "Washing dishes at the Harbor Cafe, starting the summer I was "
    "sixteen, at a wage my mother set and my father pretended to "
    "approve. The first money felt less like payment than like "
    "citizenship: I had a place in the economy of the house. I spent "
    "the first check on a hardback dictionary and a bus ticket to "
    "Galveston, which tells you everything about the citizen."
)
A["q062"] = (
    "Mrs. Okafor taught me the work ethic of teaching: prepare like "
    "an engineer, perform like an actor, forgive like a grandmother. "
    "But my father taught me how to work, full stop: show up, "
    "diagnose honestly, finish the job, and never blame the tool you "
    "were handed. Between the two of them I was fully educated. "
    "College added information."
)
A["q063"] = (
    "Teaching a child to read. You begin with the letter sounds laid "
    "out like tools, you watch where the child's eye stalls, you lend "
    "them your voice for the hard word without making them feel lent "
    "to, and one ordinary Tuesday the whole machine catches and runs "
    "on its own power. My hands know the weight of a primer and the "
    "exact patience required, which is more than I think I have, "
    "daily, for forty years."
)
A["q064"] = (
    "The school year after the flood of 1993, when we taught in a "
    "borrowed church hall with half our books gone and a third of my "
    "students living in trailers and motels. I nearly broke that "
    "spring, not from the work but from the arithmetic of need: "
    "thirty children, one of me, and a town pretending normal was a "
    "place we still lived."
)
A["q065"] = (
    "In 1998 I started a catering business with a friend, June's "
    "Table, and it failed in fourteen months, taking my savings and "
    "nearly the friendship. The failure rearranged me: I learned "
    "that loving the work and running the business are different "
    "trades, and that I had been confusing my mother's genius at "
    "both for a single gift. I went back to teaching with my eyes "
    "open and a respect for ledgers."
)
A["q066"] = (
    "I knew in a portable classroom in 1985, when a boy named Marcus "
    "read his first full sentence aloud and then looked up at me with "
    "an expression I can only call sovereignty. I did not so much "
    "choose the calling as recognize it, the way you recognize your "
    "own house in fog. Everything since, including the bakery, has "
    "been the same work in different aprons: feeding, teaching, "
    "witnessing."
)
A["q067"] = (
    "The Porch Light, the bakery I opened in 2010 on Harbor Street, "
    "two doors from where the cafe stood. It carries my name in the "
    "town's mouth if not on the sign: people say 'June's' and mean "
    "the building. Every loaf that leaves it is stamped, in the only "
    "way bread can be, with my mother's motto and my father's "
    "standard: honestly made, and finished."
)
A["q068"] = (
    "The school board, in the person of a superintendent who thought "
    "my reading program was an extravagance, and later a landlord who "
    "doubled the bakery's rent in its second year, betting I would "
    "fold. I did with opposition what my grandfather did with "
    "weather: noted it, dressed for it, and went out anyway. Being "
    "underestimated is a resource if you can stand to spend it "
    "slowly."
)
A["q069"] = (
    "Success cost me my mother's last good years at the cafe counter, "
    "some of them. The bakery succeeded in the same seasons she was "
    "failing, and every hour the ovens took was an hour not spent "
    "beside her. She would have called the trade correct and did, "
    "loudly. The cost was real anyway. Both things are true, and "
    "holding both is most of what I know about success."
)
A["q070"] = (
    "Four-thirty in the morning, the bakery dark except the oven "
    "light, my hands in the first dough, the tide chart by the door, "
    "and the porch light switched on before anything else, before "
    "coffee, before thought. That scene has repeated ten thousand "
    "times with variations of grief and weather. If my working life "
    "is a film, it is that frame, held."
)
A["q071"] = (
    "Daniel Reyes. I met him in the summer of 1989 at a teachers' "
    "conference in Galveston, where he was arguing with a vending "
    "machine with great dignity. He taught mathematics two districts "
    "away and had my mother's laugh exactly, which I noticed before "
    "I noticed anything else and should have taken as the warning "
    "and the promise it was."
)
A["q072"] = (
    "He was the first person who asked about the tide journal and then "
    "waited, in real silence, for the whole answer. Previous loves "
    "had wanted the edited version of me, the cafe daughter, the "
    "teacher. Daniel wanted the archive. I knew it was different "
    "because for the first time I did not tidy a single fact before "
    "handing it over."
)
A["q073"] = (
    "Saturdays in the good years: the market, his terrible pancakes, "
    "the two of us grading papers and lesson plans at the kitchen "
    "table like a small university of two, and the evening walk to "
    "the ferry landing to watch the boats come in with my father's "
    "old commentary running in my head. Ordinary days are the "
    "load-bearing walls of a marriage. Ours held."
)
A["q074"] = (
    "We argued about money, which meant we argued about fear. His "
    "fear was scarcity, learned in a house where the lights were once "
    "turned off by the city. Mine was waste, learned at a cafe "
    "counter. Underneath every budget fight of thirty years stands "
    "two children at two different tables, both certain the food "
    "might stop."
)
A["q075"] = (
    "Love asked me to give up the Austin job, a real promotion, in "
    "1996, because Daniel's work and my mother's health were both "
    "anchored to the coast. I gave it up. I have never pretended it "
    "cost nothing, and I have never once, even in our worst season, "
    "believed I chose wrong. The two statements sit together in me "
    "without fighting, which took practice."
)
A["q076"] = (
    "In 2003 Daniel drank his way through the winter of his father's "
    "death and I moved into the bakery's back room for four months. "
    "It was the breaking point and we both knew it standing in it. "
    "What I will say here is that he stopped, entirely, without being "
    "rescued, and that my leaving was the least loving and most "
    "necessary thing I have ever done. We rebuilt on different terms."
)
A["q077"] = (
    "The tide chart. The one from my parents' kitchen wall, which "
    "Daniel rescued from the flooded house in 2008, dried page by "
    "page on the bakery's racks like pastry. It hangs by our door "
    "now, warped and salt-stained, still consulted daily by a man "
    "who taught mathematics and consults it anyway. It is the "
    "constitution of both my families."
)
A["q078"] = (
    "That I go quiet and write things down instead of saying them, in "
    "love exactly as in childhood. Daniel taught me by surviving it "
    "and then, in our rebuilt years, refusing it: 'Say the ugly "
    "sentence, June. I can carry a sentence. I cannot carry a "
    "silence.' It is the most useful sentence anyone has ever given "
    "me, and I have been practicing it, imperfectly, since."
)
A["q079"] = (
    "One child: Ana, born in 1994, who has her grandfather's hands "
    "and her grandmother's authority and a laugh that reorganizes "
    "rooms. She teaches now, two districts away, which the family "
    "treats as both a tradition and a joke at my expense. I had "
    "wanted three children. I got the one the arithmetic allowed, "
    "and she is not a consolation. She is the point."
)
A["q080"] = (
    "Whether I chose right in 2003 by leaving, and right again by "
    "returning. I believe both, and the belief has a seam in it that "
    "aches in certain weather. Daniel says the question is closed. "
    "For him it is. A marriage, I have learned, is two people "
    "carrying the same events in different editions, and ours differ "
    "on that chapter."
)
A["q081"] = (
    "My father, in 2011. A heart attack at the harbor, between one "
    "engine and the next, which is the death he would have ordered. "
    "I learned of it from Tomas, who called the bakery and said only, "
    "'Come to the dock, June,' in a voice with the bottom out of it. "
    "I drove with flour on my hands. I remember the flour more "
    "clearly than the drive."
)
A["q082"] = (
    "Grief looked like inventory. I catalogued his tools, his "
    "notebooks, the coffee cans of sorted bolts, because my hands "
    "needed a list when my mind could not hold a thought. I cried in "
    "the truck, at red lights, on a schedule as regular as the "
    "tides, and taught my classes dry-eyed and competent. People "
    "said I was strong. I was indexed. It is not the same thing."
)
A["q083"] = (
    "The cafe. Hurricane Della took its roof in 2008 and the water "
    "took the rest, and though the building was technically rebuilt "
    "by strangers into a shop selling candles, the place, the actual "
    "place where my mother fed a town for forty years, was lost as "
    "completely as any person in this book. I grieve it in the "
    "present tense."
)
A["q084"] = (
    "September 13, 2008, the day Della came in. By dark the cafe was "
    "gone, the house was full of the sea, and my mother stood in the "
    "bakery-that-wasn't-yet's doorway, doing arithmetic in her head. "
    "Everything in my life is dated from that day or from my "
    "father's death, the two hinges. Saltmarsh people still say "
    "'before the storm' the way other people say 'before the war.'"
)
A["q085"] = (
    "I walked away from teaching in 2009, a year before I had planned, "
    "with the storm damage still unrepaired and my mother aging out "
    "of her own kitchen. It cost me the pension arithmetic I had "
    "counted on and a piece of my identity I had worn since Mrs. "
    "Okafor's classroom. I have never regretted it. Regret requires "
    "believing the other road existed. It did not."
)
A["q086"] = (
    "Hurricane Della, again. Disaster in my life has a single name "
    "and a date. It rearranged the map of Saltmarsh, the family "
    "finances, my mother's remaining years, and my occupation. But I "
    "want it recorded that the weeks after were also the town's "
    "finest: nobody in Saltmarsh ate alone that September unless "
    "they hid. We fed people. The motto held under water."
)
A["q087"] = (
    "I failed Tomas. During his divorce in 2015 I was consumed by my "
    "mother's decline and I did not go to Houston, not once, though "
    "he had driven down for every crisis of mine for fifty years. He "
    "has forgiven me in the family's way, completely and without "
    "words, which means I carry it in the family's way too: I show "
    "up now, early and with food, and say nothing."
)
A["q088"] = (
    "I survived the winter of 2003, my marriage on the back-room cot, "
    "my mother watching me decide. I had thought the limit of my "
    "endurance was a fixed coastline. It turned out to be a tide "
    "line, farther out than I believed. I do not romanticize it. "
    "Surviving cost me a kind of softness I have never recovered, "
    "and I still think the price was worth paying."
)
A["q089"] = (
    "The last breakfast with my mother, in her kitchen, in the spring "
    "of 2019. She made coffee too strong and criticized the bakery's "
    "cinnamon rolls with professional precision, and I laughed and "
    "washed the cups. She died in her sleep three weeks later. I did "
    "not know it was the last ordinary morning. They never announce "
    "themselves. That is the whole of the cruelty and the mercy."
)
A["q090"] = (
    "Loss left me the skillet, the ledger, and the habit of the porch "
    "light. The ledger is the one nobody expects: forty years of my "
    "mother's handwriting, who owed, who was forgiven, who was fed "
    "free in which hard winter. It is the true history of Saltmarsh, "
    "and I use it the way other people use scripture, to check what "
    "we owe each other."
)
A["q091"] = (
    "I live above the bakery on Harbor Street, in an apartment that "
    "smells of bread the way the first house smelled of my mother's "
    "skillet, which is to say completely and forever. From the window "
    "I see the harbor my father worked and the water that nearly took "
    "me. The marsh still begins where the grass gives up. Some "
    "geographies you do not leave. You ripen in them."
)
A["q092"] = (
    "Up at four-thirty. Porch light on, ovens lit, dough, coffee, the "
    "tide chart consulted like an oracle I pretend not to believe "
    "in. The bakery opens at seven. Ana calls at nine on teaching "
    "days. Afternoons are for the ledger I keep now, my own, and for "
    "the memoirs I write at the kitchen table in the back, one honest "
    "sentence at a time, most days."
)
A["q093"] = (
    "Still here: Daniel, across the table as I write this. Ana, two "
    "districts away and in my kitchen every Sunday. Lily, calling "
    "from Oregon. Willa, next door in every way that matters, sixty "
    "years on. Gone: my parents, my grandmother, Eli, and the "
    "versions of my brother and myself that we were before the "
    "storm. The roll gets shorter and the table, somehow, stays set."
)
A["q094"] = (
    "I believe now that certainty is a luxury of the young and the "
    "unbereaved, and that a life is not a thesis but a practice. The "
    "eighteen-year-old packing her suitcase believed leaving was the "
    "same as becoming. She would argue fiercely. I would let her "
    "win the argument and then show her the bakery, the ledger, the "
    "light, and let the evidence do what arguments cannot."
)
A["q095"] = (
    "The silence. I have interrupted it, mostly, in the important "
    "rooms: I say the ugly sentence now, to Daniel, to Ana, to "
    "Tomas, while there is still time for the sentence to do its "
    "work. What I have not interrupted is the writing-it-down-first. "
    "Every hard thing still passes through a notebook before it "
    "reaches my mouth. Perhaps that is not a wound anymore. Perhaps "
    "that is just the shape of the tool."
)
A["q096"] = (
    "The bakery, and the reading program, if I am allowed two. The "
    "Porch Light still stands on Harbor Street, and Ana is learning "
    "its ovens whether or not she admits that is what she is doing. "
    "The reading program outlived my superintendent and my "
    "retirement; children I taught are teaching their children from "
    "it. Work that survives you in other people's hands is the only "
    "monument I trust."
)
A["q097"] = (
    "I want to finish the family cookbook, the real one, with the "
    "ledger's stories in it, before my hands give out. I want Ana to "
    "want the bakery, and I want to be able to bear it gracefully if "
    "she does not. I want ten more years of four-thirty mornings. "
    "Plainly stated: I want more of exactly this, and time to hand "
    "it over properly."
)
A["q098"] = (
    "I would stand in the kitchen doorway of the first house and tell "
    "her: the water will take your breath and not take you. The "
    "silences are grief, not coldness, and you are allowed to say so. "
    "Keep the journal. Forgive the carriers. And when you are "
    "sixty-four and they ask you what it all meant, you will say: we "
    "fed people, and it was enough, and it was everything."
)
A["q099"] = (
    "The skillet goes to Ana, with its history told to her properly, "
    "not discovered in pieces as I discovered my grandfather's. The "
    "ledger goes to the town library, where it belongs, being the "
    "town's own record. My tide journals go to whoever asks first "
    "and means it. My name should be on nothing except the bakery "
    "sign, and they may paint over that when the time comes."
)
A["q100"] = (
    "The porch light, at dusk, on Harbor Street. It has burned for "
    "the boats, for the lost, for my mother's customers and my "
    "father's engines and my own worst winter, and it burns now for "
    "whoever is still out on the water. If the reader holds one "
    "image, let it be that: a light left on, deliberately, by people "
    "who knew exactly how dark it gets."
)


def main() -> None:
    out = Path(__file__).resolve().parent.parent / "demo" / \
        "memoir-demo-answers.json"
    data = {
        "persona": "June Calloway (fictional demonstration persona)",
        "note": ("All biographical details in these answers are "
                 "fabricated demonstration data, written to exercise "
                 "the memoir genre pack end to end. Any resemblance "
                 "to a real person is unintended."),
        "answers": A,
    }
    out.write_text(json.dumps(data, indent=1), encoding="utf-8")
    words = sum(len(v.split()) for v in A.values())
    print(f"wrote {out}: {len(A)} answers, {words} words")


if __name__ == "__main__":
    main()
