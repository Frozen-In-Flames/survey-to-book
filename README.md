# survey-to-book

A system that converts a structured survey into a book. A respondent
answers 100 to 300 questions; each answer becomes exactly one page of
prose, generated sequentially by a local language model running
entirely offline. Pages are not generated independently: each page is
conditioned on the accumulated state of the book so far, and a
genre-specific framework controls how each answer is converted into
the literary form of its genre.

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
synopsis, the two most recent pages in full, and the current answer.
Because the bible and synopsis compress all earlier material, prompt
size stays bounded as book length grows: the context cost of page 300
is of the same order as page 30.

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

## Genre packs

One pack ships in this release:

- **memoir** (v1.0.0): 100 questions in 10 chapters of 10, ordered as
  a life arc (origins, childhood home, family, early world, first
  wounds, becoming, work and calling, love and partnership, losses
  and turning points, present day and legacy). Framework: first-person
  retrospective voice, twelve-device library, five typed facts.

Additional genre packs are added one at a time as updates to this
same application; the engine is genre-agnostic and loads any pack
that satisfies the schema in `engine/pack.py`.

## Proof of works

`books/memoir-first-book/` contains the first book produced by this
system, generated from the memoir pack and the demonstration answer
set in `demo/`:

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

Each future genre pack will ship with its own first book in the same
way, as evidence of the pack in operation.

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
- `packs/` — genre packs. `packs/memoir.json` is generated from
  `tools/build_memoir_pack.py`.
- `demo/` — the demonstration answer set for the memoir pack.
- `books/` — generated books published as proof of works.
- `tests/` — the test suite, including the negative controls.
- `tools/` — pack and demo-data builders.

## License

Apache-2.0. The demonstration model used for the first book,
Qwen2.5-3B-Instruct, is likewise Apache-2.0.
