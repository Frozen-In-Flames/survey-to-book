# survey-to-book

A system that converts a structured survey into a book. A respondent
answers 100 to 300 questions; each answer becomes exactly one page of
prose, generated sequentially by a local language model running
entirely offline. Pages are not generated independently: each page is
conditioned on the accumulated state of the book so far, and a
genre-specific framework controls how each answer is converted into
the literary form of its genre.

## Method

The survey is the origin of everything the book legitimately
contains; the model's role is transformation of supplied material
into book form. Each genre has its own survey, written to draw out
the material a real book in that genre is made of — scenes, facts,
voices, turning points, and the who, what, when, where, and how of
its subject — in the respondent's own substance. The model performs
the editorial work on that material: assembly into pages under the
genre framework, continuity against the accumulated state, and
polish of expression. It does not originate the book's facts,
people, or events: the engine's prompts state this role explicitly,
the story bible's typed facts each carry the id of the survey
answer they were extracted from, and a fact with no source answer
fails validation before generation. A pack is therefore judged by
how completely its questions elicit the book; when a needed fact
has to be obtained outside the survey, that is a defect of the
survey, and the correction is a new question (see the
completeness gate in `DEFECTS.md`, entry E6).

## Mechanism

The pipeline has four components.

**Genre pack.** A genre is data, not code: a JSON document containing
a framework and a question set. Each question carries, beside the
prompt shown to the respondent, four machine-readable declarations:
its `narrative_job` (the structural role of the page it will produce),
its `position` in the book's arc, the `devices` to apply when
converting the answer, and the `bible_keys` its answer creates or
updates in the story bible. A question may also declare a typed
`fact` (a person's name, a place, a year) that the rest of the book
is required to keep consistent.

**Framework as control layer.** The framework specifies voice, point
of view, tense, page length, and a library of named literary devices,
each defined as an instruction (scene rendering, sensory palette,
motif planting and payoff, then-and-now contrast, object memory,
dialogue reconstruction, and others). During generation, the device
instructions assigned to a question's slot are inserted into the
prompt as explicit controls. Genre method is therefore applied by
construction rather than left to the model's improvisation: the same
answer, submitted to two different genre packs, is converted by two
different, inspectable control sets.

**Story bible and rolling synopsis.** State is maintained in two
compressed forms. The story bible is a structured record (people,
places, timeline, motifs, promises to the reader) folded
deterministically from the answers under the questions' `bible_keys`
declarations, together with the typed facts. After each chapter, the
model writes a short synopsis of that chapter, and the synopses
accumulate into a rolling synopsis. A page prompt is assembled from
the framework controls for the slot, the bible (rendered under a word
budget, most relevant entries first), the fixed facts, the rolling
synopsis, a short closing excerpt of the most recent page, and the
current answer. Because the bible and synopsis compress all earlier
material, prompt size stays bounded as book length grows: the
context cost of page 300 is of the same order as page 30. Earlier
pages are deliberately not fed forward in full: the first book this
system produced showed that a model handed previous pages as raw
text re-emits their sentences verbatim (in that book, 90 of 100
pages shared a full sentence with the previous page).

**Continuity verification.** After generation, a deterministic
checker scans the finished pages against the bible's typed facts.
Trigger phrases associated with each fact are located in later pages
and the value appearing in the value position is compared with the
established fact; near-miss spellings of established names are
flagged as possible drift. Trigger phrases match at word boundaries,
so a kinship word does not match inside a longer one ("Father" does
not match inside "grandfather"), and plural forms of established
names are not treated as drift. The checker ships with negative
controls in the test suite: fixtures with deliberately planted
contradictions (a renamed parent, an altered birth year) are
required to be flagged, and consistent fixtures are required to
pass; regression tests cover the grandfather, grandmother, list, and
plural cases that the first book exposed.

**Duplication measurement and the refrain parameter.** A sibling
checker measures verbatim sentence overlap between each page and
the pages before it; its headline metric (pages sharing a full
sentence with the previous page) is recorded in every build report.
A page that repeats earlier sentences beyond a small allowance is
treated as failed and regenerated with the overlap named, a bounded
number of times, and the outcome is recorded. Recurrence itself is
a writer's control, not an error: the framework's `refrain`
parameter (a boolean in each pack, overridable at build time with
`--refrain` / `--no-refrain`) selects it. A refrain is recurrence
with development. With the parameter on, the book's anchor theme —
the first page's opening sentences — is carried in the prompt as a
theme, and the model is directed to restate it, where a page calls
it back, as developed by everything the story has established
since: newer facts and shifted understanding, in fresh wording.
Verbatim copying is not the mechanism in either setting, and the
report separates the two measurements: verbatim overlap (the loop
detector, which must stay low in both settings) and, with the
parameter on, a development check that classifies each recurrence
of the anchor — verbatim copies fail it, and thematic recurrences
pass only when they demonstrably carry material drawn from the
story since the anchor. The check's verdict and any failing pages
are named in the report and the book's colophon.

**Generation.** Inference is fully local and offline, served by
llama.cpp from a GGUF model file on the same machine. No network
service, account, or API is involved at any stage. Builds are
resumable: state is persisted after every page, and an interrupted
build continues from the first ungenerated page.

## What is novel in the approach

- **Structural isomorphism between survey and book.** The survey is
  the book's architecture, not an intake form: question order is
  chapter order, and each question's declared narrative job fixes the
  function of its page before any prose exists.
- **The framework as an explicit, inspectable control layer** between
  raw answers and prose, mapping answer types to literary devices per
  genre. The transformation rules are data that can be audited,
  versioned, and reused across respondents.
- **State compression in place of context accumulation.** The story
  bible plus rolling synopsis replace re-reading the full manuscript
  at each step, which is what makes a 300-page book generable on a
  lightweight local model with a bounded context window.
- **Typed facts with mechanical enforcement.** Facts declared at the
  survey layer become constraints verified over the finished text,
  with negative controls proving the verification can fail.
- **Recurrence as a measured parameter.** The refrain is a named,
  togglable framework control whose two failure modes — verbatim
  looping and undeveloped restatement — are each measured by a
  deterministic checker, so the selected behavior is verified in
  the build report rather than asserted.

## Genre packs

Six packs ship in this release:

- **memoir** (v1.1.0): 101 questions in 10 chapters (chapter 1
  carries 11), ordered as a life arc (origins, childhood home,
  family, early world, first wounds, becoming, work and calling,
  love and partnership, losses and turning points, present day
  and legacy). Framework: first-person retrospective voice,
  twelve-device library, six typed facts. Refrain default: on
  (its first book was generated with recurrence in effect, before
  the parameter existed; the pack now records the setting
  explicitly). Version 1.1.0, added in the biography
  corrected-edition audit, opens the survey with an explicit
  identity question (who is the main character of this memoir)
  declaring the narrator's name as a typed fact: the original
  survey never asked, and the narrator's identity had entered
  the build only as answer-file metadata (see `DEFECTS.md`, M7).
  The pack's first book was generated under v1.0.0 and stands as
  published.

- **biography** (v1.0.0): 100 questions in 10 chapters of 10, ordered
  cradle to present (before the beginning, birth and first years,
  the making of the child, apprenticeship, the young adult, the
  work, love and household, standing and struggle, late years and
  death, legacy). Framework: third-person retrospective voice — the
  pack's defining difference from memoir — a thirteen-device library
  (scene reconstruction, period detail, documentary anchor, voice of
  record, the subject's own words, contextual frame, character
  portrait, testimony weave, object evidence, turning point,
  reputation against the record, legacy lens, chapter turn), and
  seven typed fact slots kept about the subject (name, birth year,
  birthplace, mother, father, partner, death year). Refrain default:
  off; in a third-person chronological life, recurrence reads as
  error rather than voice. The survey opens by asking, in terms,
  who the biography's subject is: the identity question the
  clean-proof rule requires, put in terms by the corrected-edition
  audit (see `DEFECTS.md`, B5).

- **family-history** (v1.0.0): 100 questions in 10 chapters of 10,
  whose subject is a family across generations rather than one
  life. The pack models two family lines — the respondent's
  mother's line and father's line — each traced separately
  (founding ancestor, origin place, migration, matriarch,
  patriarch, trades, records) and converging in the parents'
  joining and in the respondent. Framework: first-person voice,
  thirteen-device library (including the doctrine: a family saying
  carried as an explicit device), and eighteen typed fact slots —
  two line names, the respondent's name, both parents' names, five
  facts per line (founding ancestor, origin place, migration year,
  matriarch, patriarch), the respondent's birth year and
  birthplace, and the partner's name. Every fact slot is elicited
  by a direct question, and the pack's test suite proves each
  extracted fact traces to its source answer (18 of 18).
  Refrain default: on; a family saying returning across
  generations, developed in each era, is this genre's native
  structure, bounded by the verbatim guard and the development
  check.

- **cookbook** (v1.0.0): 100 questions in 10 chapters of 10,
  whose subject is a practice rather than a life or a lineage:
  one cook's cooking, inherited from two family lines' kitchens
  and practiced in his household and in his recording studio.
  The structure is the genre's own: the cook and the two
  kitchens (their matriarchs, origins, and rules), the working
  kitchen (pantry, techniques), the table (ten signature
  dishes rendered whole as cookable recipes, the studio's
  feeding, occasions), and keeping and handing on
  (preservation, teaching). Framework: first-person cook's
  voice, a thirteen-device library (recipe rendering,
  technique lesson, provenance note, preservation method,
  substitution craft, failure and repair, pantry inventory,
  among them), and thirteen typed fact slots — the two line
  names, the cook, both parents, the two matriarchs and the
  two origin places, the cook's birth year and birthplace,
  the studio's founding year, and the partner. Every fact
  slot is elicited by a direct question, and the pack's test
  suite proves each extracted fact traces to its source
  answer (13 of 13). Refrain default: off, chosen
  deliberately: a cookbook's pages are modular, one recipe or
  food memory per answer, and its native recurrence is the
  dish, the technique, or the house rule returning in new
  material — content carried by the answers themselves, not
  an anchor theme the prompt restates. The family's doctrine
  appears in the book as answer content (planted at q009,
  restated by the respondent at q094), and the verbatim
  duplication guard applies in full.

- **short-story-collection** (v1.0.0): 100 questions in 10
  chapters of 10, whose subject is a teller and his material:
  one hundred standalone stories drawn from one life — the
  front room where his mother taught, his father's repair
  shop, the recording studio he founded, the road, the
  family's inherited tales — each story answerable on its own
  and the whole held together by cast, place, and voice
  rather than by plot. The structure follows the telling:
  the teller, the shop, and the front room; the work (first
  work, the studio, the fire and the rebuilding); the world
  (the road, strangers, the family telling); and last
  stories. Framework: first-person storyteller's voice (past
  tense for the stories, present for the teller's frame), a
  thirteen-device library (story rendering, scene opening,
  character sketch, dialogue beats, object anchor, turning
  point, ending line, inherited tale, frame voice, sensory
  palette, place portrait, time frame, chapter turn), and
  ten typed fact slots — the two line names, the subject's
  name, both parents' names, the subject's birth year and
  birthplace, the sister's name, the partner's name, and the
  studio's founding year. Every fact slot is elicited by a
  direct question, and the pack's test suite proves each
  extracted fact traces to its source answer (10 of 10). The
  survey opens its first chapter by asking, in terms, who the
  main character of the collection is (q003). Refrain
  default: off, chosen deliberately: a collection's stories
  stand alone, and its native recurrence is the cast, the
  places, and the voice returning in new material — content
  carried by the answers themselves. The engine's anchor
  mechanism takes the first page's opening sentences as its
  theme, and this pack's first page is a fact-fixing
  family-name page, not a theme, so an imposed anchor would
  weld standalone stories into a false arc. The family's
  doctrine appears in the book as answer content (planted at
  q010, restated by the respondent in chapter 10), and the
  verbatim duplication guard applies in full.

- **devotional** (v1.0.0): 100 questions in 10 chapters of
  10, whose subject is a practice kept daily: one keeper's
  disciplines of naming, gratitude, work, hardship,
  intercession, silence, and the night watch, drawn from his
  household, his family lines, and his recording studio.
  The structure follows the keeping: the keeper and the
  first light; the kept table; work as practice; the hard
  hours; other people; gratitude counted; silence and
  listening; the night watch; and the practice handed on.
  The pack is religion-agnostic in structure: the questions
  ask about the respondent's own practices, sources of
  strength, gratitude, hardship, hope, and daily disciplines
  in the respondent's own terms, never presuming a tradition
  or correcting the respondent's vocabulary, and a pack test
  enforces that no question prompt contains a
  tradition-presuming term. Framework: first-person keeper's
  voice, a thirteen-device library (anchor return, practice
  rendering, moment opening, gratitude naming, hardship
  witness, intercession, silence rendering, listening, day
  examen, kept object, place portrait, sensory palette,
  sending), and ten typed fact slots — the two line names,
  the subject's name, both parents' names, the subject's
  birth year and birthplace, the sister's name, the
  partner's name, and the studio's founding year. Every fact
  slot is elicited by a direct question, and the pack's test
  suite proves each extracted fact traces to its source
  answer (10 of 10). The survey opens its first chapter by
  asking, in terms, who the main character of the devotional
  is (q003). Refrain default: on, chosen deliberately — the
  opposite call from the story collection, and for the
  genre's own reason: a devotional is refrain-shaped, one
  anchor sentence returned to daily and changed by the day,
  where a collection's standalone stories made the same
  mechanism a false arc. The family's doctrine appears in
  the book as answer content (planted at q010, restated by
  the respondent in chapter 10), and the verbatim
  duplication guard applies in full. What the refrain cost
  this book in practice is recorded without softening in
  `DEFECTS.md` (V2, V4, V5, V6).

Additional genre packs are added one at a time as updates to this
same application; the engine is genre-agnostic and loads any pack
that satisfies the schema in `engine/pack.py`.

## Proof of works

Each genre pack ships with a first book generated from the pack and
a demonstration answer set in `demo/`, as evidence of the pack in
operation. The demonstration user of the series is Frozen In
Flames, a fictional persona: the canonical record of the
character's invented life is `demo/frozen-in-flames-character.json`,
and each pack's demonstration answers are that character's answers,
drawn from the single record so the same character headlines every
book. (The first book predates the shared-character rule; its
respondent is a separate fictional persona, as its entry states.)

- **The Porch Light** — 100 pages, one per question, 38,261 words,
  generated locally with Qwen2.5-3B-Instruct (Q4_K_M GGUF, Apache-2.0;
  file SHA-256 `626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d`)
  via llama.cpp build b12651 (temperature 0.8, top-p 0.95, repeat
  penalty 1.1, 480-token page budget, single inference slot). The
  respondent, June Calloway, is a fictional demonstration persona; the
  answers are fabricated test data written to exercise the pack end to
  end, and the book's front matter states this. `report.json` records
  the page and word counts and the continuity check outcome for the
  run.

- **The Cold Room** (`books/biography-first-book/`) — the biography
  pack's first book, corrected edition (survey-to-book v0.2.1):
  100 pages, one per question, 30,356 words, generated locally
  with the same model and settings as the other books
  (Qwen2.5-3B-Instruct Q4_K_M GGUF via llama.cpp build b12651;
  temperature 0.8, top-p 0.95, repeat penalty 1.1, 480-token page
  budget, single inference slot). The subject is Frozen In Flames,
  the series' demonstration user: a fictional persona whose
  fabricated survey answers are drawn from the canonical character
  record in `demo/frozen-in-flames-character.json` (record version
  2.0.0, carrying the author's canon: born 2000 in Dallas; mother
  Ruby Flames; father Onyx Frozen; partner Amber Flames), and the
  book's front matter states this. The story bible extracted from
  the answers agrees with the character record fact for fact, and
  every one of the pack's six established facts traces to its
  source survey answer (6 of 6; the death-year slot is declared
  but unestablished, the character living). This edition
  supersedes the edition released as v0.2.0 (28,415 words), which
  was generated from answers carrying a character canon the
  biography build had invented (born 1960 in Memphis; mother
  Evelyn Flames; father Harold Flames; partner Alice Flames)
  because the survey had never asked the author; v0.2.0 stands
  unchanged in the release history, and the correction is
  recorded in `DEFECTS.md` (B4, B5). The pack's refrain parameter
  was off for this build. Duplication: 1 of 100 pages shares a
  full sentence verbatim with the previous page (page 68, where
  the bounded regeneration was exhausted and the least-duplicative
  attempt was kept, as recorded in `report.json`), against 2 of
  100 in the first edition and 90 of 100 in the first book. All
  10 chapter synopses are present, across the five interruptions
  the build survived (see `DEFECTS.md`, B5). Continuity check:
  4 candidate issues flagged at build time; inspection against
  the source answers showed all 4 were checker false positives
  (kinship triggers matching the parents' own parents, whose
  names the text states correctly), and reader-level sampling
  found the genuine errors recorded in the deviations below.

- **The Keeping Book** (`books/family-history-first-book/`) — the
  family-history pack's first book, corrected edition
  (survey-to-book v0.3.1): 100 pages, one per question, 29,037
  words, generated locally with the same model and settings as
  the other books (Qwen2.5-3B-Instruct Q4_K_M GGUF via llama.cpp
  build b12651; temperature 0.8, top-p 0.95, repeat penalty 1.1,
  480-token page budget, single inference slot). The respondent
  is Frozen In Flames, the series' demonstration user: a
  fictional persona whose fabricated survey answers are drawn
  from the canonical character record in
  `demo/frozen-in-flames-character.json` (record version 2.0.0,
  carrying the author's canon: born 2000 in Dallas; mother Ruby
  Flames; father Onyx Frozen; partner Amber Flames), and the book's
  front matter states this. The story bible extracted from the
  answers agrees with the record fact for fact, and every one of
  the pack's 18 typed facts traces to its source survey answer
  (18 of 18). This edition supersedes the edition released as
  v0.3.0 (29,655 words), which the author read and found
  gendering the subject female: the full classification of that
  text (394 marker sentences; one definite subject instance, on
  page 79) is recorded in `DEFECTS.md` (F4). The corrected
  edition was regenerated from the same pack, the same answers,
  and the same bible with a generation-time subject-gender gate
  in the engine; the post-build audit of the new text (352
  marker sentences) finds zero definite and zero probable
  subject instances (F5). The pack's refrain parameter was on
  for this build. Duplication: 3 of 100 pages share a full
  sentence verbatim with the previous page (v0.3.0: 0 of 100),
  5 pages share a sentence with some earlier page, and 2 pages
  carry an intra-page duplicated sentence. All 10 chapter
  synopses are present, across the six interruptions and one
  wedged server slot the build survived (see `DEFECTS.md`,
  F5). Continuity check: 7 candidate issues flagged at build
  time; inspection showed 1 was a checker false positive and 6
  were genuine surface garbles of the family name ("Flamers",
  once "Flamels"). The refrain development check passes: 3
  recurrences of the anchor theme, all 3 developed, and no
  verbatim anchor copies (v0.3.0 failed it: 13 recurrences, 6
  developed, 1 verbatim copy).

- **The Keeping Table** (`books/cookbook-first-book/`) — the
  cookbook pack's first book: 100 pages, one per question,
  30,488 words, generated locally with the same model and
  settings as the other books (Qwen2.5-3B-Instruct Q4_K_M
  GGUF via llama.cpp build b12651; temperature 0.8, top-p
  0.95, repeat penalty 1.1, 480-token page budget, single
  inference slot). The respondent is Frozen In Flames, the
  series' demonstration user: a fictional persona whose
  fabricated survey answers are drawn from the canonical
  character record in `demo/frozen-in-flames-character.json`
  (record version 2.0.0, carrying the author's canon: born
  2000 in Dallas; mother Ruby Flames; father Onyx Frozen;
  partner Amber Flames), and the book's front matter states
  this. The story bible extracted from the answers agrees
  with the record fact for fact, and every one of the pack's
  13 typed facts traces to its source survey answer (13 of
  13; the studio's founding year, 2022, traces to the
  record's defining events). The pack's refrain parameter
  was off for this build. Duplication: 5 of 100 pages share
  a full sentence verbatim with the previous page (pages 7,
  12, 48, 88, 91, one sentence each, after the bounded
  regeneration was exhausted; 20 regeneration retries across
  15 pages), against 0 of 100 in the third book, 1 of 100 in
  the second, and 90 of 100 in the first. No page repeats a
  sentence within itself. All 10 chapter synopses are
  present, across the five interruptions the build survived
  (see `DEFECTS.md`, C7). Continuity check: 1 candidate
  issue flagged at build time; inspection showed it was a
  checker false positive (the verb "Rub" in the brisket
  recipe, flagged as a drift of the name "Ruby"). The ten
  signature-dish pages render as cookable recipes —
  ingredients with quantities, method in order, yield — and
  reader-level sampling found the genuine errors recorded
  in the deviations below.

- **The Day Book** (`books/short-story-collection-first-book/`) —
  the short story collection pack's first book: 100 pages, one
  per question, 30,972 words, generated locally with the same
  model and settings as the other books (Qwen2.5-3B-Instruct
  Q4_K_M GGUF via llama.cpp build b12651; temperature 0.8,
  top-p 0.95, repeat penalty 1.1, 480-token page budget,
  single inference slot). The respondent is Frozen In Flames,
  the series' demonstration user: a fictional persona whose
  fabricated survey answers are drawn from the canonical
  character record in `demo/frozen-in-flames-character.json`
  (record version 2.0.0, carrying the author's canon: born
  2000 in Dallas; mother Ruby Flames; father Onyx Frozen;
  partner Amber Flames), and the book's front matter states
  this. The story bible extracted from the answers agrees
  with the record fact for fact, and every one of the pack's
  10 typed facts traces to its source survey answer (10 of
  10). The pack's refrain parameter was off for this build,
  deliberately (see the pack entry above). Duplication: 0 of
  100 pages share a full sentence verbatim with the previous
  page, against 5 of 100 in the fourth book, 0 of 100 in the
  third, 1 of 100 in the second, and 90 of 100 in the first;
  measured against any earlier page, 7 pages share at least
  one sentence with an earlier page (the front-room setting
  description recurring), and 3 pages repeat a sentence
  within the page (see `DEFECTS.md`, S2). 10 regeneration
  retries across 10 pages. All 10 chapter synopses are
  present, across the five interruptions the build survived
  (see `DEFECTS.md`, S8). Continuity check: 0 candidate
  issues flagged at build time, the first book in the series
  with none. Subject-gender audit (the new permanent check
  recorded at `DEFECTS.md`, S7): of 458 sentences carrying a
  female pronoun or role word, 1 refers to the narrator with
  a female role word (page 100) and 2 more are probable
  instances; the rest refer to the female cast or other
  women. Reader-level sampling found the genuine errors
  recorded in the deviations below.

- **The Kept Hours** (`books/devotional-first-book/`) — the
  devotional pack's first book: 100 pages, one per question,
  31,962 words, generated locally with the same model and
  settings as the other books (Qwen2.5-3B-Instruct Q4_K_M
  GGUF via llama.cpp build b12651; temperature 0.8, top-p
  0.95, repeat penalty 1.1, 480-token page budget, single
  inference slot). The respondent is Frozen In Flames, the
  series' demonstration user: a fictional persona whose
  fabricated survey answers are drawn from the canonical
  character record in `demo/frozen-in-flames-character.json`
  (record version 2.0.0, carrying the author's canon: born
  2000 in Dallas; mother Ruby Flames; father Onyx Frozen;
  partner Amber Flames), and the book's front matter states
  this. The story bible extracted from the answers agrees
  with the record fact for fact, and every one of the pack's
  10 typed facts traces to its source survey answer (10 of
  10). The pack's refrain parameter was on for this build,
  deliberately (see the pack entry above). This is the first
  book in the series whose headline results are failures,
  and they are reported here as plainly as the earlier books'
  passes. The generated narrator is cast as a wife from page
  1 ("The family name of my husband's line is Flames"),
  against the record's male respondent with a wife: "my
  husband" appears on 62 of 100 pages, and because the
  refrain takes its anchor from the first page, the error
  recurs through the whole book (see `DEFECTS.md`, V2).
  Duplication: 53 of 100 pages share a full sentence verbatim
  with the previous page, against 0 of 100 in the fifth book,
  5 of 100 in the fourth, 0 of 100 in the corrected third,
  1 of 100 in the second, and 90 of 100 in the first; measured
  against any earlier page, 76 pages share at least one
  sentence with an earlier page, and 10 pages repeat a
  sentence within the page (see `DEFECTS.md`, V5). The
  refrain analysis records 20 recurrences, 12 developed, and
  its development check fails (see `DEFECTS.md`, V4). All 10
  chapter synopses are present, across the eight interruptions
  the build survived (see `DEFECTS.md`, V10). Continuity
  check: 0 candidate issues flagged at build time, the second
  book in the series with none; its scope does not cover the
  narrator inversion (see `DEFECTS.md`, V8). Subject-gender:
  the generation-time gate recorded its heaviest activity in
  the series (23 retries, 7 pages flagged, 12 flagged
  sentences), and the post-build audit classified all 218
  female-marker sentences in the finished text with 0
  definite and 0 probable instances referring to the narrator
  — while the book's actual gender failure, recorded at V2,
  uses a spouse-term construction neither check screens. The
  gap is named, and the prescribed screen extension is
  recorded, at `DEFECTS.md`, V3. Reader-level sampling found
  the further genuine errors recorded in the deviations below.

- Live library: all six books can be read in a browser at
  https://frozen-in-flames.github.io/survey-to-book/, which is now a
  library index: every published book is listed with its title,
  genre, demonstration character, and page and word counts, a Read
  button opening that book's full text page by page with chapter
  navigation, and a Download button for the book file (Markdown,
  byte-identical to the book's manuscript, or plain text). The site
  is static and self-contained; it is generated from the books'
  manuscripts and reports by `tools/build_reader_site.py` and
  served from `docs/`. Adding the next book is a data entry in
  that generator, not a rewrite.

- Continuity: the first check of the finished book flagged 17
  candidate issues. Inspection against the source answers showed all
  17 were false positives of the checker's trigger matching, not
  errors in the text: thirteen flagged the maternal grandfather Tomas
  Delgado in passages where the text correctly names him as
  grandfather, two flagged the grandmother Odette in passages where
  the text correctly names her as grandmother, one flagged the name
  Eli in a list of the dead, and one flagged the plural family name
  "Calloways" as a misspelling of "Calloway". The defects were in the
  checker: bare triggers matched as substrings, so "Father" matched
  inside "grandfather" and "Mother" inside "grandmother", and the
  drift scan had no plural rule. Both were fixed in
  `engine/continuity.py` — triggers now match at word boundaries and
  plural forms of established names are excluded from drift — with
  regression tests proving the fixed checker still flags planted
  contradictions. The checker was re-run over the finished book and
  reports 0 issues. The book text was not edited; it was already
  correct, and the colophon records the post-fix result.

- Known deviations in this first book, recorded rather than edited
  away: (1) the chapter-9 rolling synopsis is absent. The generation
  process was interrupted between the chapter's final page being
  saved and its synopsis being written, and the resumable build does
  not revisit completed chapters; chapters 1–8 and 10 have synopses.
  (2) The model rendered the narrator male ("boy", 33 occurrences)
  despite the source answer stating the narrator was the first
  daughter; the sequential context then carried that rendering
  forward. The continuity checker constrains typed facts only and
  does not catch this class of deviation. (3) The final page ends
  mid-sentence: the 480-token page budget truncated generation, and
  the engine accepts a page that meets the minimum length rather than
  extending it to a sentence boundary.

- Known deviations in the second book (corrected edition),
  recorded on the same terms: (1) the final page writes the
  subject's death ("By 2023, when he died"), contradicting the
  living-subject frame and page 87 of the same book; the checker
  could not flag it, the death-year slot being unestablished.
  (2) Page 20 misassigns a relation ("Onyx Frozen, her father",
  of Ruby; he is her husband and the subject's father).
  (3) Page 17 places John Glenn's 1962 orbital flight in the
  subject's birth year, 2000; page 96 dates a passage to 2034, a
  year the record does not support; page 2 sends Flint Frozen to
  Dallas "to join his father", a relation the record does not
  contain. (4) Ten pages (10, 45, 47, 61, 71, 72, 77, 93, 96,
  97) end mid-sentence at the 480-token page budget; the final
  page's prose ends on a complete sentence. (5) Page 68 shares
  one full sentence with the previous page after the bounded
  duplication retries were exhausted. The first edition's
  deviations are recorded at `DEFECTS.md` B1–B3.

- Known deviations in the third book, recorded on the same terms:
  (1) page 28 calls the paternal grandparents by the parents'
  titles: "my father Jasper's words" (Jasper Frozen is the
  narrator's grandfather; his father is Onyx Frozen) and "My
  mother Coral's amendment" (Coral Frozen is his grandmother; his
  mother is Ruby Flames). The continuity checker flagged both;
  the text was not edited. (2) Page 28 repeats one paragraph
  verbatim within the page ("Jasper's doctrine taught my father
  Onyx patience and skill ..."); the duplication checker measures
  sharing between pages only, so this intra-page repetition is
  outside its scope. (3) The refrain development check failed
  (see the book's entry above): the anchor theme returns partly as
  instruction echo — page 4 quotes the prompt's refrain block
  verbatim, pages 2 and 5 frame the return as "The book's anchor
  theme ...", and pages 53–54 echo the instruction's wording about
  "carrying the newer facts and shifting understanding in fresh
  wording". (4) Page 4 ends mid-sentence at the 480-token page
  budget. (5) Page 4 dates the parents' joining to 2000; the
  record has the marriage in 1999 and the respondent's birth in
  2000. The final page ends on a complete sentence.

- Known deviations in the fourth book, recorded on the same
  terms: (1) 25 of 100 pages end mid-sentence at the 480-token
  page budget (pages 9, 12, 13, 15, 21, 26, 28, 29, 45, 46,
  47, 49, 54, 55, 59, 63, 65, 66, 75, 81, 82, 83, 93, 97, 98)
  — the truncation class of the first book's M3 at the
  highest rate in the series; the cookbook's dense recipe
  and list pages reach the budget most often. The final page
  ends on a complete sentence. (2) Page 53 renders the
  brisket rub as six pounds of coarse salt and six pounds of
  coarse black pepper for a twelve-pound brisket — the
  answer's "equal parts" of salt and pepper misread as
  halves of the meat's weight — substitutes an oven for the
  answer's oak-fired pit, and appends an unrelated technique
  section (knife work) after the recipe. (3) Page 100
  attributes the pot beans to Ruby's teaching; the dish is
  Pearl Frozen's, the Frozen line's matriarch, and the same
  page gives the narrator a first memory from Pearl's
  kitchen although the record states she died in 1999, the
  year before he was born. (4) Twenty of 100 pages open with
  chapter-or-book meta phrasing ("In this chapter…", "In
  this book…"), the opening mannerism of the second book's
  B3 at a higher rate.

- Known deviations in the fifth book, recorded on the same
  terms: (1) 25 of 100 pages end mid-sentence at the
  480-token page budget (pages 2, 3, 6, 8, 9, 15, 16, 23, 24,
  39, 41, 44, 50, 54, 55, 58, 60, 61, 70, 71, 90, 91, 92, 98,
  99), tying the fourth book's rate as the highest in the
  series; the final page ends on a complete sentence.
  (2) Seven pages share at least one full sentence with some
  earlier page (the front-room setting description recurring
  on non-adjacent pages, which the previous-page duplication
  guard cannot see), and 3 pages repeat a sentence within
  the page. (3) Page 100 genders the narrator female once —
  "Ruby's son and Onyx's daughter" — the instance class the
  author found in the third book, caught here by the new
  subject-gender audit (`DEFECTS.md`, S7), which also records
  2 probable instances (pages 76 and 94). (4) Page 24 places
  the narrator, aged three, at the 1998 pedal incident, two
  years before his birth; page 100 brings him to the same
  evening and scrambles his parents' relation ("my mother
  played the organ again, this time as her wife"). (5)
  Page 30 gives the narrator a daughter the record does not
  contain (the answer's pupil, a drummer's daughter, becomes
  "my daughter"); page 46 reassigns Amber's line about the
  room to the narrator and invents a proposal scene; page 51
  inverts the fire's survival facts (the office and the metal
  cabinet the answers say stood and saved the record are
  rendered as taken by the fire). (6) Page 10 echoes the
  build's framing language ("This sentence is planted as
  content in every story of this book…"), and page 1 invents
  a year (a fire in 1916) the record does not contain.

- Known deviations in the sixth book, recorded on the same
  terms: (1) The narrator is cast as a wife from page 1 —
  "The family name of my husband's line is Flames" — against
  the record's male respondent with a wife; "my husband"
  appears on 62 of 100 pages (about 109 instances), the
  refrain's anchor is drawn from the corrupted page, and the
  book contradicts itself elsewhere ("my wife" on pages 9,
  17, and 54). Neither the generation-time subject-gender
  gate nor the post-build audit screens this construction;
  the gap and the prescribed fix are recorded at
  `DEFECTS.md`, V2–V3. (2) The refrain's development check
  fails: 20 recurrences, 12 developed, 4 verbatim anchor
  copies (V4). (3) Duplication is the heaviest since the
  first book: 53 of 100 pages share a sentence with the
  previous page, 76 with some earlier page, and 10 repeat a
  sentence within the page, the late chapters saturating
  with refrain boilerplate (V5). (4) The generation
  machinery's vocabulary saturates the prose — "anchor
  sentence" named on 60 pages (V6). (5) 22 of 100 pages end
  mid-sentence at the 480-token page budget (V7). (6) Pages
  31 and 46 date the studio's third year against the book's
  own later timeline; page 45 opens on other material before
  the ruin; one sentence lowercases the Flames line into a
  common noun (V9).

Each future genre pack will ship with its own first book in the same
way, as evidence of the pack in operation. Every defect found in
any book, and the correction applied to the code for each, is
recorded in [`DEFECTS.md`](DEFECTS.md).

## Running it

Requirements: Python 3.11 or later (standard library only), and a
llama.cpp `llama-server` binary plus a GGUF model for real
generation. The deterministic stub model used by the tests requires
neither.

```bash
# validate a genre pack against the schema
python -m engine.cli validate --pack packs/memoir.json

# run the test suite (includes all negative controls)
python -m unittest discover -s tests

# start a local model server (offline; loopback only)
# -np 1: generation is strictly sequential, so one slot is
# sufficient, and it keeps the KV cache near 1 GB. Four slots
# allocated a multi-gigabyte KV cache that pushed the model into swap
# on the 8 GB machine used for the first book; measured generation
# fell to ~0.6 tokens per second under that load, and a single slot
# restored ~1.8 tokens per second under the same contention.
llama-server -m models/qwen2.5-3b-instruct-q4_k_m.gguf \
    -c 8192 -np 1 -t 4 --port 8080

# build a book from an answers file
python -m engine.cli build --pack packs/memoir.json \
    --answers demo/memoir-demo-answers.json \
    --model llama --out books/memoir-first-book \
    --title "The Porch Light" --persona-note "..." --colophon "..."
```

Answers are supplied as a JSON object mapping question ids to answer
text (optionally wrapped in an `answers` key, as in `demo/`). An
empty or missing answer produces no page and is listed in the build
report; the engine never pads an unanswered question with invented
material.

## Repository layout

- `engine/` — the genre-agnostic engine (pack validation, story
  bible, prompt assembly and sequential generation, continuity
  checking, Markdown export, CLI).
- `packs/` — genre packs. `packs/memoir.json`,
  `packs/biography.json`, `packs/family-history.json`, and
  `packs/cookbook.json` are
  generated from the builders in `tools/`.
- `DEFECTS.md` — the defect-and-correction log: every defect found
  per genre and per book, as measured, with its root cause, the
  correction applied, and the control that now prevents or bounds
  it.
- `demo/` — the demonstration answer sets, and the canonical
  character record (`frozen-in-flames-character.json`) they are
  drawn from.
- `books/` — generated books published as proof of works.
- `tests/` — the test suite, including the negative controls.
- `tools/` — pack and demo-data builders.

## License

Apache-2.0. The demonstration model used for the first book,
Qwen2.5-3B-Instruct, is likewise Apache-2.0.
