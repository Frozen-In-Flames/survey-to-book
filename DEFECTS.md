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
  the family-history build (v0.3.0).

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
  generation. Family history: 18 of 18 facts traced.

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
  v0.2.0 are unchanged; a corrected edition is a separate,
  queued decision.

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

### F2. Defects during generation

Recorded at build completion; see the book's entry in the README
and its `report.json`. (Updated as part of the v0.3.0 delivery.)
