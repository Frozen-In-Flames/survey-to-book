# Defect and correction log

This file is the public record of every defect found in this
system, per genre and per book, and of the correction applied to
the code to prevent its recurrence — or, where the behavior became
a controlled feature, the control that now bounds it. Each entry
states the defect as measured (numbers, not adjectives), its root
cause, the correction, and the control that now prevents or bounds
it (a test, a gate, a checker, or a parameter), with the commit
that carried the fix where practical.

The log is part of each genre build's delivery: a new genre adds
its own section, including a statement of no defects when none
occur.

## Engine

### E1. Verbatim sentence looping between consecutive pages

- **Measured:** in the first book (memoir, "The Porch Light"),
  90 of 100 pages shared at least one full sentence verbatim with
  the previous page.
- **Root cause:** earlier pages were fed forward into later page
  prompts as raw text; the model re-emitted their sentences.
- **Correction:** page prompts no longer carry earlier pages in
  full. Context is carried by the story bible and the rolling
  synopsis (compressed state), plus a short closing excerpt of the
  most recent page only.
- **Control:** the duplication checker (`engine/duplication.py`)
  measures verbatim sentence overlap for every build and records
  it in the build report; a page exceeding a small allowance is
  regenerated with the overlap named, a bounded number of times,
  and the outcome recorded. Commit `78477ec`.

### E2. Recurrence uncontrolled: the loop became the refrain parameter

- **Measured:** the E1 loop was the extreme of a real literary
  behavior: recurrence. Left unmeasured it looped verbatim; banned
  outright it would remove a legitimate device (a memoir's
  returning image, a family history's family saying).
- **Correction:** recurrence became a named framework parameter,
  `refrain`, set per pack and overridable at build time. A refrain
  is defined as recurrence *with development*: the anchor theme is
  carried in the prompt as a theme and must be restated, where a
  page calls it back, in fresh wording carrying material the story
  has established since.
- **Control:** two measurements in every build report — verbatim
  overlap (must stay low in both settings) and, with the parameter
  on, a development check that fails verbatim copies and passes
  thematic recurrences only when they demonstrably carry newer
  material. Commits `76c3e98`, `5073b19`.

### E3. Pack/answer ID misalignment shipped in the first pack commit

- **Measured:** the memoir pack's first commit used question ids
  `m001`–`m100` while its demo answers used `q001`–`q100`: the two
  sets did not intersect at all (0 of 100), so the pairing of pack
  and answers was never exercised by that commit.
- **Root cause:** pack and answers were authored in separate
  artifacts with no alignment check between them.
- **Correction:** ids unified on the `q001`–`q100` scheme.
- **Control:** every pack's test suite asserts exact set equality
  between question ids and answer ids, and that every answer is
  non-empty, before any generation is attempted. The biography and
  family-history suites carry this as their central test.

### E4. Continuity checker false positives (17 of 17)

- **Measured:** the first continuity check over the finished
  memoir flagged 17 candidate issues; inspection against the
  source answers showed all 17 were checker false positives, not
  text errors: 13 flagged the maternal grandfather in passages
  correctly naming him as grandfather, 2 flagged the grandmother
  likewise, 1 flagged a name in a list of the dead, and 1 flagged
  the plural family name "Calloways" as a misspelling of
  "Calloway".
- **Root cause:** trigger phrases matched as bare substrings, so
  "Father" matched inside "grandfather" and "Mother" inside
  "grandmother"; the name-drift scan had no plural rule.
- **Correction:** triggers match at word boundaries; plural forms
  of established names are excluded from drift, in
  `engine/continuity.py`.
- **Control:** regression tests cover the grandfather,
  grandmother, list, and plural cases, and negative controls
  (planted contradictions: a renamed parent, an altered birth
  year) are required to be flagged, proving the repaired checker
  still detects real errors. The book text was not edited; it was
  already correct. Commit `78477ec`.

### E5. Missing rolling synopsis after interruption (occurred twice)

- **Measured:** memoir chapter 9 and biography chapter 7 each lack
  a rolling synopsis in their shipped books — 1 of 10 chapters in
  each book. In both cases, later chapters were generated without
  that chapter's synopsis in their rolling context (the story
  bible and fixed facts were unaffected; continuity checks still
  reported 0 issues).
- **Root cause:** the same mechanism both times: generation was
  interrupted between a chapter's final page being saved and its
  synopsis being written, and the resumable build never revisited
  completed chapters, so the missing synopsis was never repaired.
- **Correction:** `BookBuilder.build()` now begins with a repair
  pass (`_repair_missing_synopses` in `engine/generate.py`): on
  resume, before any new page is generated, every chapter whose
  answered pages all exist in the saved state but whose synopsis
  is missing has its synopsis regenerated from the saved pages.
- **Control:** regression test
  `test_resume_repairs_missing_synopsis` in `tests/test_engine.py`
  deletes a chapter synopsis from a completed build's state,
  resumes, and asserts the synopsis is regenerated, no page is
  regenerated, and all page texts are byte-identical. Landed with
  the family-history build (v0.3.0). Production verification in
  that build: four interruptions, all 10 chapter synopses present
  in the finished book (see F3f).

### E6. Untraced bible facts (completeness gate)

- **Measured:** before the family-history build, no check proved
  that every fact in a book's story bible originated in a survey
  answer; the biography build demonstrated the failure mode by
  inventing core character facts (birth year, birthplace, parents'
  names) that no survey question had elicited (see B4).
- **Correction:** bible facts carry their source question id
  (`source_question`, recorded at extraction in
  `engine/bible.py`), and each genre pack is audited against the
  five interrogatives — who, what, when, where, how — for every
  core fact the book depends on; a core fact no question elicits
  is a pack gap, closed by adding the question and regenerating
  the answers under the clean-proof rule.
- **Control:** each pack's test suite includes a traceability test
  asserting, for every extracted fact, that its source question
  exists, declares that fact's slot, and has a non-empty answer;
  coverage (facts traced / total facts) must be 1.0 before
  generation. Family history: 18 of 18 facts traced. Biography
  (corrected edition): 6 of 6 established facts traced, the
  death_year slot declared and unestablished. Memoir (pack
  v1.1.0): 6 of 6 facts traced.

## Memoir — "The Porch Light" (v0.1.0)

### M1. Verbatim looping, 90 of 100 pages

See E1/E2. The shipped book retains the measured behavior; it was
generated before the feed-forward correction and the refrain
parameter existed. It stands as the baseline the later books are
compared against.

### M2. Narrator rendered contrary to a source answer

- **Measured:** the model rendered the narrator male ("boy", 33
  occurrences) although the source answer states the narrator was
  the first daughter; the sequential context then carried the
  rendering forward through the book.
- **Root cause:** the continuity checker constrains typed facts
  only; narrator attributes not declared as typed facts are
  outside its scope.
- **Status:** recorded as a known deviation in the book's README
  entry; not edited. The mitigation in force is declarative:
  attributes a book depends on must be declared as typed facts at
  the survey layer, where the checker can enforce them.

### M3. Final page ends mid-sentence

- **Measured:** page 100 is truncated mid-sentence at the
  480-token page budget.
- **Root cause:** the engine accepted a page that met the minimum
  length rather than extending generation to a sentence boundary.
- **Status:** recorded as a known deviation. The biography's final
  page ends on a complete sentence; the truncation behavior is
  unchanged in the engine and remains bounded by the page budget.

### M4. Chapter 9 rolling synopsis absent

See E5. Recorded in the shipped book; the root-cause correction
prevents recurrence in future builds.

### M5. Continuity checker false positives

See E4. All 17 flags were checker defects; the text was correct
and was not edited.

### M6. Pack/answer ID misalignment in the first commit

See E3.

### M7. Identity never asked: the narrator's name was build data

- **Measured:** the memoir pack (v1.0.0) contained no identity
  question and no narrator-name fact slot: none of its 100
  questions asks who the memoir's main character is. The
  narrator's name existed only as the demo answers file's
  persona metadata -- supplied by the build, not elicited from
  the respondent. The five-interrogative audit of the pack's
  core facts found every other fact elicited by a direct
  question (birth year q001, hometown q013, mother q021,
  father q024, partner q071); the single gap was the who of
  the book itself.
- **Root cause:** the survey was authored as if the respondent's
  identity were given by the act of responding. In this system
  identity is content, and content the survey does not elicit
  the build must supply -- the B4 mechanism, one level up (see
  F2, the same gap found in the family-history pack).
- **Correction:** pack v1.1.0 adds the identity question at the
  head of chapter 1, in the genre's form (who is the main
  character of this memoir, whose life is this book), declaring
  a subject_name fact. Published question ids are never
  renumbered (E3), so the added question takes the unused id
  q000 and stands first in the question list; the original 100
  questions are unchanged. The demo answers gained the
  corresponding answer, drawn from the persona the file already
  recorded (June Calloway). The shipped book was generated
  under pack v1.0.0 and stands as published; it does not
  contain the identity question's page.
- **Control:** tests in `tests/test_pack.py`: the identity
  question asks for the main character in terms, sits in
  chapter 1, and stands first in the list; the original 100
  question ids follow it unchanged and in order; pack and
  answers align exactly; traceability measures 6 of 6 facts
  traced to survey answers.

## Biography — "The Cold Room" (v0.2.0)

### B1. Duplication residue, 2 of 100 pages

- **Measured:** pages 38 and 39 each share one full sentence with
  the previous page (2 of 100, against the memoir's 90 of 100).
  The report records 27 regeneration retries across 22 pages.
- **Root cause:** on those two pages the bounded regeneration was
  exhausted; per policy the least-duplicative attempt was kept
  rather than discarding the page.
- **Control:** the outcome is recorded per page in `report.json`
  and named in the README; the bound (bounded retries, keep the
  least-duplicative attempt, record the exception) is the standing
  policy for every build.

### B2. Chapter 7 rolling synopsis absent

See E5. Recorded in the shipped book; chapters 8–10 were
generated without that chapter's synopsis in their rolling
context.

### B3. Opening-page meta-narrative mannerism

- **Measured:** page 1 describes its own act of introduction; the
  remaining 99 pages do not.
- **Status:** recorded as a known deviation; not edited.

### B4. Character canon invented outside the survey

- **Measured:** the biography build set the demonstration
  character's core facts itself — born 1960 in Memphis; mother
  Evelyn Flames; father Harold Flames; partner Alice Flames —
  because no survey question elicited them and the record was
  authored to fill the gap. On 2026-11-24 the author set the
  canon: born 2000 in Dallas, Texas; white American male, red
  hair, blue eyes; mother Ruby Flames; father Onyx Frozen (the
  family name splits into two lines, the mother's Flames and the
  father's Frozen, joined in the character's name); partner Amber
  Flames; and a naming law under which every family member's
  first name is a crystal or gem name.
- **Correction:** the canonical record
  (`demo/frozen-in-flames-character.json`, version 2.0.0) now
  carries the author's canon, with the supersession recorded in
  its provenance; the family-history pack and answers are built
  on the corrected record.
- **Control:** the clean-proof rule and the traceability gate
  (E6): a fact that had to be obtained outside the survey is a
  survey defect and becomes a survey question. The biography test
  suite pins the supersession mechanically — the shipped book's
  answers and the corrected record must diverge in exactly the
  five author-corrected fields.
- **Status of the shipped book:** "The Cold Room" and release
  v0.2.0 are unchanged in the release history. The corrected
  edition decided on 2026-11-24 shipped as v0.2.1 (see B5): the
  demo answers were regenerated from record version 2.0.0, and
  the library's copy of the book is the corrected edition.

### B5. Corrected edition and pack audit (v0.2.1)

The corrected edition decided on 2026-11-24, executed under the
clean-proof rule in the same pass as a five-interrogative audit
of the biography and memoir packs (for the memoir findings, see
M7).

- **Canon supersession resolved.** The demo answers were
  regenerated from the canonical record (version 2.0.0) by
  `tools/build_biography_demo_answers.py`, whose consistency
  checks now enforce the correction mechanically: every recorded
  fact must appear in its designated answer, the birth-year
  answer's first year must be the record's year, every year
  mentioned in any answer must be a year the record supports
  (an explicit whitelist drawn from the record), and no token of
  the superseded canon (Memphis, Evelyn, Harold, Alice, the 1960
  timeline) may appear. The bible extracted from the corrected
  answers equals the record fact for fact: 6 of 6 established
  facts (subject Frozen In Flames, born 2000 in Dallas; mother
  Ruby Flames; father Onyx Frozen; partner Amber Flames), the
  death_year slot declared and unestablished, the subject
  living. The biography test suite's supersession pin is
  inverted accordingly: answers and record must now agree
  exactly, and any future divergence fails the suite.
- **Five-interrogative audit of the pack.** Every core fact the
  book depends on is elicited by a direct question: who (subject
  q001, mother q003, father q005, partner q061), when (birth
  year q011, death year q087), where (birthplace q012), how
  (the parents' meeting q007, the making-of questions
  throughout). No fact was needed during answer-writing or
  generation that no question elicits.
- **Identity gap (the F2 class, found and closed).** q001 asked
  for the subject's full name as a name field; the survey
  nowhere asked, in terms, who the biography's subject is. The
  identity the book hangs on was therefore implied by the
  pack's structure rather than stated as respondent data.
  Correction, on the family-history pattern: q001 now asks the
  identity question explicitly in the genre's form (who is the
  subject of this biography, the person whose life this book
  tells). Question id, fact slot, devices, bible key, and the
  demo answer are unchanged in role; the pack diff is the
  prompt and narrative job of q001 alone. Control:
  `test_identity_question_asks_for_subject` in
  `tests/test_biography_pack.py`, with the traceability test
  beside it (6 of 6 facts traced, coverage 1.0).
- **Refrain unchanged:** off for this pack, per the author's
  explicit call of 2026-11-24.
- **Generation results.** The corrected edition: 100 pages, one
  per question, 30,356 words, 0 skipped, generated locally with
  the same model and settings as the other books. Duplication:
  1 of 100 pages (page 68) shares a full sentence verbatim with
  the previous page, against 2 of 100 in the first edition and
  90 of 100 in the memoir. All 10 chapter synopses are present.
  The build was interrupted five times (three runtime kills of
  build and server together, one dropped server connection, and
  one wedged server slot -- the orphaned request of a crashed
  build -- that required a server restart before a resume would
  generate); every resume continued from `state.json` with no
  pages regenerated and no progress lost. The defects found in
  the finished book are:

**B5a. Continuity flags: 4 candidates, all false positives.**
- **Measured:** the build-time continuity check flagged 4
  candidate issues: mother_name on pages 18, 20, and 85 (found
  "Opal Reyes", "Opal Reyes", and "Onyx" against the expected
  "Ruby Flames") and father_name on page 17 (found "Slate
  Flames" against "Onyx Frozen").
- **Inspection:** all four are checker false positives of the
  E4 family. On pages 18 and 85 the text names the subject's
  maternal grandmother correctly ("her mother Opal Reyes" --
  Ruby's mother, born Opal Reyes); on page 17 it names Ruby's
  father correctly ("her father, Slate Flames"); on page 20
  the flagged "Onyx" begins the clause after "her mother," and
  names no relation. The kinship triggers ("her mother", "her
  father") cannot distinguish the subject's parents from the
  parents' own parents, and the text states the grandparents'
  names correctly in each case. The book text was not edited.
- **Status:** recorded. No checker change was made in this
  build: separating the two readings requires antecedent
  resolution, not a matching rule, and a wider scan would trade
  these flags for false positives elsewhere (the F3g trade).

**B5b. Genuine errors found by reader sampling (recorded, not
edited).**
- **Page 100** closes the life by writing the subject's death:
  "By 2023, when he died, he left instructions for The Cold
  Room's future." The subject is living; the record establishes
  no death year, and page 87 of the same book states he has not
  died. The checker did not flag it: with death_year
  unestablished there is no value to contradict, and the
  lowercase "he died" falls outside the trigger set's casing.
  This is the largest single error in the book.
- **Page 20** misassigns a relation: "Onyx Frozen, her father"
  (of Ruby) -- Onyx is Ruby's husband and the subject's father.
  The checker's flag on this page (B5a) was on a different
  sentence.
- **Page 17** misplaces an era event: John Glenn's orbital
  flight (1962) is given as the backdrop of the subject's birth
  year, 2000. The continuity checker constrains bible facts
  only; public-era detail is outside its scope.
- **Page 96** dates a passage to 2034, a year the record does
  not support; **page 2** sends Flint Frozen to Dallas "to join
  his father", a relation the record does not contain.

**B5c. Mid-sentence truncation, 10 of 100 pages.**
- **Measured:** pages 10, 45, 47, 61, 71, 72, 77, 93, 96, and
  97 end mid-sentence at the 480-token page budget -- the M3
  class, at ten times the rate of the two previous books (1 of
  100 each). The final page's prose ends on a complete
  sentence.
- **Status:** recorded as known deviations; the engine's page
  budget behavior is unchanged.

**B5d. Duplication residue, 1 of 100 pages.**
- **Measured:** page 68 shares one full sentence with page 67
  after the bounded regeneration was exhausted; the
  least-duplicative attempt was kept, per the standing policy
  recorded at B1.

## Family history — v0.3.0

### F1. Survey-completeness catches under the clean-proof rule

- **Measured:** applying the five-interrogative audit (who, what,
  when, where, how) to the family-history pack before generation
  found the core facts that the biography build had needed to
  obtain outside its survey. The family-history pack was authored
  with direct questions for each: the two family lines' names
  (q001, q002), the respondent's own name (q003), the naming
  tradition (q004), the mother's name and line (q005), the
  father's name and line (q006), each line's founding ancestor,
  origin place, migration year, matriarch, and patriarch (q011–
  q014, q018, q021–q024, q027), the respondent's birth year and
  birthplace (q041, q042), and the partner's name (q081).
- **Control:** the traceability test measures coverage at 18 of
  18 facts traced to survey answers; no fact was needed during
  answer-writing or generation that no question elicits.

### F2. Main character implied by the pack, not asked

- **Measured:** the pack's central-identity fact (subject_name)
  was elicited by q003, but as a name field ("What is your full
  name, and how does it come from the two lines?"): the survey
  nowhere asked, in terms, who the book's main character is. The
  identity the whole book hangs on was therefore implied by the
  pack's structure rather than stated as respondent data — the
  same class of gap as B4, one level up.
- **Root cause:** the five-interrogative audit checked the book's
  facts for a who, but did not check the book's premise: that the
  respondent is the central figure is itself a fact, and it was
  the one fact the build, not the respondent, was supplying.
- **Correction:** q003 now asks the identity question explicitly,
  in the genre's form: who is the main character of this family
  history, the person in whom the two lines join, through whose
  life the family's story is told. Question id, fact slot,
  narrative job, and the demo answer are unchanged; the answer
  still comes from the canonical record, and subject_name still
  traces to q003. (The correction is to the survey prompt only;
  generation does not consume prompt text, so the in-progress
  build was not disturbed.)
- **Control:** test
  `test_identity_question_asks_for_main_character` in
  `tests/test_family_history_pack.py` requires the question
  declaring subject_name to sit in the first chapter and to ask
  for the main character in terms. Standing pattern for every
  pack: an explicit identity question early in the survey, in the
  genre's form (main character, subject, whose family), with the
  central-identity fact tracing to its answer.

### F3. Defects during generation

The build ran 100 pages in 29,655 words with 0 of 100 pages
sharing a full sentence verbatim with the previous page (against
90 of 100 in the memoir and 2 of 100 in the biography) and all 10
chapter synopses present. The defects found are:

**F3a. Continuity checker false positives (8 of 10 flags).**
- **Measured:** the build-time continuity check flagged 10
  issues. Eight were checker false positives: seven flagged the
  ordinary English word "Yet" as a one-letter drift of the
  established name "Jet" (pages 2, 3, 9, 67, 94, 96, 97), and one
  flagged "Flame" as a drift of "Flames" (page 15, "This is the
  Flame family line").
- **Root cause:** the name-drift scan flagged any capitalized
  token at edit distance 1 from an established name token. "Yet"
  is capitalized only because it opens a sentence, and "Flame" is
  the singular of the plural established name, used as an
  attributive noun.
- **Correction:** two rules in `engine/continuity.py`. A token is
  the same name in singular form when it is an established name
  minus its plural "s" (mirroring the existing plural rule), and a
  token counts as a near-miss spelling only when it shares the
  established name's first letter or appears capitalized
  mid-sentence. The drift excerpt now shows the flagged
  occurrence's context instead of the page's first 120 characters.
- **Control:** four regression tests in
  `tests/test_continuity.py` (sentence-initial common word,
  singular family name, genuine drift still flagged, mid-sentence
  drift with a different first letter still flagged). Re-running
  the repaired checker over the finished book's pages reports 2
  issues, both genuine (F3b).

**F3b. Genuine continuity errors on page 28 (recorded, not edited).**
- **Measured:** page 28 (q028, the doctrine page) calls Jasper
  Frozen "my father Jasper" and Coral Frozen "My mother Coral".
  Jasper and Coral are the narrator's paternal grandparents; his
  father is Onyx Frozen and his mother is Ruby Flames. The same
  page elsewhere states the relations correctly ("Jasper's
  doctrine taught my father Onyx"), so the page contradicts
  itself. The checker caught both; the book text was not edited,
  per the standing rule.
- **Status:** recorded as known deviations in the README and in
  this log.

**F3c. Refrain development check failed.**
- **Measured:** with the refrain on, the development check
  recorded 13 recurrences of the anchor theme: 6 developed, 6
  thematic but undeveloped (pages 2, 4, 5, 54, 78), and 1 verbatim
  copy (page 4). Verdict: FAIL. Verbatim sentence overlap against
  the previous page stayed 0 of 100; the failure is in
  development, not in looping.
- **Root cause:** the anchor returns partly as instruction echo
  rather than developed restatement. Page 4 quotes the prompt's
  refrain block verbatim ("The book's anchor theme was first
  stated thusly: ..."); pages 2 and 5 frame the return as "The
  book's anchor theme ..."; pages 53–54 echo the instruction's own
  wording ("carrying the newer facts and shifting understanding
  in fresh wording that means something new").
- **Status:** recorded as a known deviation. The refrain
  parameter's measurement worked as designed (the failure is
  visible in the report and colophon); the generation-side
  correction — keeping the anchor out of the model's quotable
  text, or instructing against meta-commentary on the theme — is
  open work for a later build, not applied to the shipped book.

**F3d. Page 4 ends mid-sentence.**
- **Measured:** page 4 is truncated mid-sentence at the 480-token
  page budget ("...carry a legacy from Mississippi to"). Same
  truncation class as the memoir's final page (M3), here mid-book.
- **Status:** recorded as a known deviation; the engine's page
  budget behavior is unchanged.

**F3e. Intra-page paragraph duplication on page 28.**
- **Measured:** one paragraph on page 28 ("Jasper's doctrine
  taught my father Onyx patience and skill ...") appears twice
  verbatim within the same page.
- **Root cause:** the duplication checker measures sharing
  between pages only; repetition inside one page is outside its
  scope. This is a metric blind spot, not a missed flag.
- **Status:** recorded as a known deviation.

**F3f. Generation interrupted four times; no data lost.**
- **Measured:** the build was killed four times before completion
  (runtime restarts and process reaping; twice the model server
  died with it, once the build crashed on a dropped server
  connection). Each resume continued from `state.json` with no
  pages regenerated and no progress lost. All 10 chapter synopses
  are present in the finished book, including chapters completed
  across interruptions — the first production evidence for the
  E5 resume-repair.
- **Root cause (environmental):** the interruptions were runtime
  restarts and sandbox teardown, not engine defects. One
  contributing pattern was established by measurement:
  builds started from a cron worker's session died within ~30
  minutes (twice) or ~67 seconds (once), while builds started
  from an interactive session survived for hours; the completed
  build ran in the foreground from an interactive session, with
  the watchdog cron as backstop only.
- **Control:** the resumable build plus the E5 repair pass; the
  watchdog cron (temporary, removed at cleanup). A diagnostic gap
  was also logged: the build prints nothing until its final
  report, so a stalled build is indistinguishable from a dead one
  by its log alone; `state.json` is the only progress signal.
  Per-page progress output is open work for a later engine pass.

**F3g. Unflagged date slip on page 4.**
- **Measured:** page 4 says "My parents chose to unite their
  families in 2000"; the record has the parents married in 1999
  and the respondent born in 2000. The year 2000 is the birth,
  not the joining.
- **Root cause:** the year-contradiction scan only checks years
  appearing next to its triggers ("born in", "I was born"); a
  year attached to another verb is outside its scope.
- **Status:** recorded as a known deviation; no checker change
  was made in this build, since widening the year scan to every
  year in the text would trade this one catch for false positives
  on every legitimate year.

## Cookbook — "The Keeping Table" (v0.4.0)

The build ran 100 pages in 30,488 words with all 10 chapter
synopses present. The pack's refrain parameter was off for this
build, by the pack's deliberate default: a cookbook's pages are
modular (one recipe or food memory per answer), and its native
recurrence is the dish, technique, or house rule returning in
new material — content carried by the answers, not an anchor
theme the prompt restates. The family's doctrine appears in
the book as answer content (planted at q009, restated by the
respondent at q094). The verbatim duplication guard applied in
full. The defects found are:

### C1. Survey-completeness under the clean-proof rule (no gaps found)

- **Measured:** the cookbook pack was authored under the
  completeness gate from the start. The five-interrogative
  audit (who, what, when, where, how) over the core facts the
  book depends on found each elicited by a direct question:
  who (the cook, by the identity question q003 in the genre's
  form — who is the main character of this cookbook, the cook
  whose kitchen this book comes from; the mother q004; the
  father q005; the two lines' matriarchs q011, q021; the
  partner q071), what (the practice itself: doctrine q009,
  purpose q010, the dishes and techniques throughout), when
  (birth year q006; the studio's founding year q061), where
  (birthplace q007; the two lines' origin places q012, q022),
  how (the techniques chapter and the method questions
  throughout). The identity corollary was satisfied by
  construction: q003 asks for the main character in terms,
  sits in chapter 1, and declares subject_name.
- **Control:** the traceability test measures coverage at 13
  of 13 facts traced to survey answers; no fact was needed
  during answer-writing or generation that no question
  elicits. The studio_year fact (2022) traces to q061 and
  agrees with the canonical record's defining events.

### C2. Duplication residue, 5 of 100 pages

- **Measured:** pages 7, 12, 48, 88, and 91 each share one
  full sentence verbatim with the previous page (5 of 100,
  against 0 of 100 in the family history, 1 of 100 in the
  corrected biography, and 90 of 100 in the memoir). The
  report records 20 regeneration retries across 15 pages.
  The five surviving shared sentences are generic connective
  sentences (one is a recipe-instruction fragment on page
  48); none carries a fact.
- **Root cause:** on those five pages the bounded
  regeneration was exhausted; per policy the
  least-duplicative attempt was kept rather than discarding
  the page.
- **Control:** the outcome is recorded per page in the
  build's state and named here and in the README; the bound
  (bounded retries, keep the least-duplicative attempt,
  record the exception) is the standing policy recorded at
  B1. A related measurement came back clean for the first
  time in the series: no page repeats a sentence within
  itself (0 of 100), so the intra-page blind spot recorded
  at F3e did not occur in this book.

### C3. Mid-sentence truncation, 25 of 100 pages

- **Measured:** 25 of 100 pages end mid-sentence at the
  480-token page budget (pages 9, 12, 13, 15, 21, 26, 28,
  29, 45, 46, 47, 49, 54, 55, 59, 63, 65, 66, 75, 81, 82,
  83, 93, 97, 98) — the M3 class, at the highest rate in the
  series (memoir 1 of 100, corrected biography 10 of 100,
  family history 1 of 100). The final page ends on a
  complete sentence.
- **Root cause:** the engine accepts a page that meets the
  minimum length rather than extending generation to a
  sentence boundary (as at M3); the cookbook's dense pages
  — recipes with ingredient lists, inventories, technique
  enumerations — consume the token budget faster than prose
  pages, so this genre reaches the budget most often.
- **Status:** recorded as known deviations; the engine's
  page budget behavior is unchanged.

### C4. Continuity checker false positive (1 of 1 flags)

- **Measured:** the build-time continuity check flagged 1
  candidate issue: name drift on page 53, expected "Ruby",
  found "Rub" — the verb that opens the brisket recipe's
  second step ("Rub the brisket with equal parts coarse
  salt and pepper").
- **Root cause:** the drift scan's near-miss rule (F3a)
  admits a token that shares an established name's first
  letter at edit distance 1; "Rub" is "Ruby" minus its
  final letter, and it stands capitalized at a list step's
  start. The text is correct; the flag is the checker's.
- **Status:** recorded. No checker change was made in this
  build: distinguishing an imperative verb from a name
  requires part-of-speech context, not a matching rule, and
  narrowing the rule would trade this flag for missed
  genuine drift elsewhere (the B5a/F3g trade).

### C5. Genuine errors found by reader sampling (recorded, not edited)

- **Page 53 (the brisket recipe)** renders the rub as "6
  pounds coarse salt, 6 pounds coarse black pepper" for a
  twelve-pound brisket: the answer's "coarse salt and
  coarse black pepper, equal by weight, and nothing else"
  — equal to each other, as a rub — misread as halves of
  the meat's weight. The same page substitutes an oven for
  the answer's oak-fired pit, and appends an unrelated
  section ("Technique Lesson: Knife Work", drawn from
  q041's material) after the recipe's yield. The other
  nine signature-dish pages render as single cookable
  recipes.
- **Page 100** attributes the closing dish, the pot beans,
  to "Ruby Flames' teachings"; the dish is Pearl Frozen's,
  established at q052 as the Frozen matriarch's recipe,
  and the same page gives the narrator a "first memory
  from her kitchen" although the record states Pearl died
  in 1999, the year before the narrator was born. The
  continuity checker did not flag either: dish attribution
  and remembered acquaintance are not typed facts, the
  same scope limit recorded at M2 and B5b.

### C6. Meta-narrative openings, 20 of 100 pages

- **Measured:** 20 of 100 pages open with chapter-or-book
  meta phrasing ("In this chapter…", "In this book…",
  "This chapter…"), including page 1 — the mannerism
  recorded at B3 (there measured on 1 page of 100) at a
  higher rate in this genre. Several such openings restate
  the question's narrative job nearly verbatim (page 50:
  "we close the techniques chapter with our family's
  doctrine as kitchen method").
- **Root cause:** the page prompt carries the slot's
  narrative job and position, and the model echoes them as
  an opening frame; recipe and technique pages, whose jobs
  are the most formulaic, echo most.
- **Status:** recorded as a known deviation; not edited.

### C7. Generation interrupted five times; no data lost

- **Measured:** the build was killed five times before
  completion (runtime restarts killing build and server
  together), at state checkpoints of 16, 41, 60, 69, and 90
  pages. Each resume continued from `state.json` with no
  pages regenerated and no progress lost; the state file's
  page sequence was verified contiguous (q001–q100) at the
  end. All 10 chapter synopses are present in the finished
  book, including chapters completed across interruptions —
  further production evidence for the E5 resume-repair. One
  additional resume attempt failed before starting: the
  first restart had wiped /tmp, taking the build's runner
  script with it, and the relaunched command failed on the
  missing file while the server sat healthy; the loss cost
  one monitoring cycle (~28 minutes) and no data.
- **Root cause (environmental):** the interruptions were
  runtime restarts and sandbox teardown, not engine
  defects. The /tmp failure is a placement defect: a
  resumable build's runner is part of the build and belongs
  in durable storage.
- **Control:** the resumable build plus the E5 repair pass;
  the runner script now lives in the goal workspace
  (`~/workspace/goals/survey-to-book-generator/hidden_files/`),
  outside /tmp, and this log records the rule for future
  genre builds.

## Short story collection — "The Day Book" (v0.5.0)

The fifth book was audited on completion (Nov 26, 2026) the
same way as the first four: report figures first, then
reader-level sampling of pages against their source answers,
then the new subject-gender audit recorded at S7. The refrain
parameter was off for this build, deliberately: a short story
collection's stories stand alone, and its native recurrence is
the shared cast, the shared places, and the teller's voice,
all carried by the answers themselves; the engine's anchor
mechanism takes the first page's opening sentences as the
theme, and this book's first page is a fact-fixing family-name
page, not a theme, so an imposed anchor would have welded
standalone stories into a false arc. The family's doctrine
appears in the book as answer content (planted at q010,
restated by the respondent in chapter 10) and surfaces in the
generated text on 4 pages (q010, q056, q085, q099) without any
anchor being imposed. No generated page was edited; the
genuine errors found are recorded, not fixed.

- **S1. Completeness audit: no gaps.** The five-W audit of the
  pack found every W covered by direct questions: who (the
  teller's identity and family in chapter 1, the cast of the
  front room, shop, and studio across chapters 2–5), what (the
  telling and the work, carried by the thirteen-device
  library), when (story-time frames in chapters 1, 6, and 9
  and the record's years throughout), where (the Dallas house,
  the repair shop, the Cold Room studio, the road, Chicago,
  Fort Worth), and how (the device library and the frame
  voice). No question had to be asked outside the survey, so
  the clean-proof rule added nothing. The identity question
  the rule requires is q003 in chapter 1, asking who the main
  character of the collection is, in terms. Traceability gate:
  the pack declares ten typed facts (the two line names, the
  subject's name, both parents' names, the subject's birth
  year and birthplace, the sister's name, the partner's name,
  the studio's founding year), each elicited by a direct
  question, and the pack's test suite proves each extracted
  fact traces to its source answer: 10 of 10. The story bible
  extracted from the answers agrees with the character record
  (v2.0.0) fact for fact, and the 100 demonstration answers
  passed their own consistency check against the record
  (names, record-supported years only, the crystal/gem naming
  law, the doctrine verbatim) before generation.

- **S2. Duplication: the previous-page measure is clean; the
  non-adjacent measure is not.** 0 of 100 pages share a full
  sentence verbatim with the previous page — the headline
  measure, against 90 of 100 in the first book, 1 of 100 in
  the second (corrected edition), 0 of 100 in the third, and
  5 of 100 in the fourth. Measured against any earlier page
  rather than only the previous one, 7 pages share at least
  one full sentence with an earlier page (q045: 1, q056: 1,
  q060: 4, q070: 1, q078: 1, q093: 2, q099: 2; 12 shared
  instances in all). The recurrent material is the front-room
  setting description, the collection's shared place: two
  sentences each appear on 3 pages ("My mother inherited the
  room where she fed pupils like me while teaching them, her
  hands steady as if carved from stone against the rhythmic
  keys." and "Ruby Flames set this layout when she taught
  generations of children, ensuring teaching and feeding were
  interwoven."). This is the non-adjacent form of the
  repetition the verbatim guard was built against: the guard
  compares each page to its predecessor only, so a setting
  re-described in the same words twenty pages later passes.
  Bounded regeneration: 10 duplication retries across 10
  pages (the cookbook needed 20 across 15). Intra-page
  repetition, the F3e blind spot, recurs: 3 pages repeat a
  sentence within the page (q022 repeats two sentences twice
  each; q027 and q032 repeat one each). The cookbook had
  none; the family history had one page. **Control:**
  recorded, not repaired in the text. The candidate engine
  control — extend the duplication measurement to any earlier
  page and to within-page repetition, with bounded
  regeneration keyed to both — is noted for the engine
  backlog and was not built in this release.

- **S3. Truncation: 25 of 100 pages end mid-sentence.** The
  M3/F3d/C3 class, unchanged: pages 2, 3, 6, 8, 9, 15, 16, 23,
  24, 39, 41, 44, 50, 54, 55, 58, 60, 61, 70, 71, 90, 91, 92,
  98, and 99 end without terminal punctuation at the
  480-token page budget (verified by reading the page ends;
  page 2 ends "each story's details se", page 99 ends "As").
  The rate ties the cookbook's 25 of 100 as the highest in
  the series (memoir 1, corrected biography 10, family
  history 1). The final page ends on a complete sentence.
  The budget was left at 480 tokens for series comparability.
  **Control:** none applied in this release beyond recording;
  the class remains the top open engine defect, and its
  candidate controls (sentence-boundary completion at the
  budget, or a larger budget with the comparability cost
  stated) stay as recorded at C3.

- **S4. Continuity: no flags, and the scope limit stated.**
  The build's continuity check flagged 0 candidate issues —
  the first book in the series with none (memoir 17 flagged
  pre-repair, biography 4, family history 10, cookbook 1; all
  but two of those, across the series, were checker false
  positives). There were therefore no flags to inspect. The
  clean report is not evidence of a clean book: the checker
  constrains typed facts and kinship triggers, and the
  reader sampling at S5 found genuine errors of classes
  outside its scope — timeline presence, invented relations,
  inverted survival facts — as did the new gender audit at
  S7. **Control:** no checker change in this release; the
  scope statement is the control, so no future release reads
  a zero-flag report as a correctness claim.

- **S5. Genuine errors found by reader sampling (recorded,
  not edited).** Sampling read pages against their source
  answers across all ten chapters, and the S7 extraction read
  doubled as a whole-book skim. Genuine deviations: (1)
  page 10 echoes the build's own framing language ("This
  sentence is planted as content in every story of this
  book…") — an instruction echo of the same class as the
  family history's refrain echoes. (2) Page 24 places the
  narrator at the pedal incident "only three years old"; the
  record dates the incident to 1998, two years before his
  birth in 2000, and the answer frames it as the founding
  story of his parents' meeting, before he existed. Page 100
  repeats the error, bringing him to the social "later" that
  same evening. (3) Page 30 turns the drummer's daughter,
  enrolled for lessons in the answer, into "my daughter" —
  the narrator is given a child the record does not contain.
  (4) Page 46 gives the narrator the line the answer gives
  Amber (that the room "had a face"), renders her dismissive
  of it, and invents a proposal scene at the first session's
  end; the answer's courtship is gradual, the marriage the
  following year. (5) Page 51 inverts the fire's survival
  facts: the page has the fire take the office and the metal
  cabinet; the answers and the record have the office stand
  and the cabinet save the log and the gospel tape. (6)
  Page 82 merges the founder's arrival into the narrator's
  ("she began the family Bible in 1949, the year of my
  arrival"); page 84 garbles Pearl Frozen's dates ("I was
  born after she died in the same year"; the record: she
  died in 1999, he was born in 2000). (7) Page 100 scrambles
  the parents' relation ("my mother played the organ again,
  this time as her wife"). (8) Page 1's grandmother's tale
  mentions "that big fire in 1916", a year the record does
  not contain: the answers' year discipline does not bind
  the generated text. Against these, many pages track their
  answers closely — pages 77, 95, and 99 follow theirs
  nearly word for word — and the deviations concentrate in
  the frame and retelling pages, where the model composes
  transitions the answers do not supply.

- **S6. Meta-narrative openings: absent in the strict form.**
  0 of 100 pages open with the chapter-or-book meta formula
  ("In this chapter…", "This chapter…") that marked 20 of
  100 cookbook pages (see C-section deviations and the second
  book's B3). A broader scan finds 3 first sentences that
  mention the collection at all: page 10's mention is a
  subordinate clause inside a scene opening ("…I remember
  why this collection exists"), page 96 opens "In 2023, as
  we neared the end of our collection, …" (the year is also
  unsupported by its answer, which dates the story only to
  the studio's first year), and page 99's opening mirrors
  its own answer's stated frame ("What This Collection Is
  For"), by the answer's design. **Control:** none needed;
  recorded so the mannerism's rate is on the series record
  book by book.

- **S7. Subject pronoun/gender consistency: a new permanent
  failsafe, and this book does not clear it at zero.** Origin:
  the author read the third book, The Keeping Book, and found
  the text gendering the subject Frozen In Flames female in
  places (Nov 25, 2026). The canonical record is unambiguous
  that the character is male (record v2.0.0; the family-
  history book's own front matter says "his"), and the
  continuity checker has no subject-gender check, which is
  how the instances shipped; the same class in reverse was
  recorded in the first book (the model rendered its narrator
  male against a female source answer) as outside the
  checker's scope. The check, now permanent for the series:
  extract every sentence of the finished manuscript that
  contains a female pronoun (she, her, hers, herself) or a
  female role word (daughter, sister, wife, mother, woman,
  girl, and their kin), classify each by referent against the
  book's cast, and report how many attach a female reference
  to the subject or narrator, with samples. The extractor
  lives with the build tooling
  (`~/workspace/goals/survey-to-book-generator/hidden_files/audit_subject_gender.py`);
  classification is the auditor's, sentence by sentence. This
  book: 458 marker sentences extracted across 100 pages; 455
  refer to the female cast (the mother, the sister, the
  partner, the lines' matriarchs) or to other women in the
  stories. Definite subject instances: 1 — page 100: "When I,
  Ruby's son and Onyx's daughter, arrived later at the social
  to see what damage my mother had caused, she smiled with
  pride…" The narrator names himself his father's daughter
  in the same breath as his mother's son, on the book's
  final page. Probable instances: 2 — page 76: "In the
  studio, where she was known for dates kept, I learned the
  hard way that not everything could be fixed in a day or
  even a week." (being known for dates kept is the narrator's
  own established trait, from his answer; no female referent
  in the passage fits it); page 94: "That night, I sat at my
  father's bench in the front room of our house, a piano
  teacher and church organist herself." (the appositive
  grammatically attaches the mother's female-marked roles to
  "I"). **Control:** the audit runs on every future book
  before release and its result is a required line in the
  release report alongside duplication, continuity, and
  traceability; no generated text is edited under it. The
  follow-up the check prescribes for the third book: run the
  same extraction and full classification over The Keeping
  Book (extraction yields 394 marker sentences; targeted
  scans did not isolate the author's instances, which sit in
  mixed company among the legitimately female cast, so the
  full classification is the required next step; the author's
  reader finding stands as this failsafe's origin).

- **S8. The build was interrupted five times; nothing was
  lost.** The generation process was killed by runtime
  restarts at saved-state checkpoints of 30, 55, 77, 91, and
  99 pages — the last one page short of completion. Each
  resume reloaded `state.json` and continued with the next
  unanswered question; no page was generated twice, no
  chapter synopsis is missing, and the final book is complete
  at 100 pages. The runner script lived in the goal workspace
  throughout, per the C7 rule, and the only scratch at risk
  was the S7 extraction in /tmp, which the audit tool
  regenerates from the manuscript. **Control:** the C7
  control held under five interruptions; no change.
