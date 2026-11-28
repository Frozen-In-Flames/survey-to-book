"""Book generation: sequential page production with accumulated context.

For each survey question, in pack order, the generator assembles a
prompt from five components:

1. the genre framework's controls (voice, point of view, tense, the
   global instructions, and the device instructions assigned to this
   question's slot),
2. the story bible (structured state folded from all answers so far),
3. the rolling synopsis (one model-written summary per finished
   chapter),
4. a short closing excerpt of the most recent page only, supplied as
   background so the prose can continue from where it stopped,
5. the respondent's answer to the current question, presented as the
   source material for this page.

Earlier pages reach the prompt as compressed state (bible and
synopses), not as raw text: the first book this system produced
showed that handing the model previous pages in full leads it to
re-emit their sentences verbatim (90 of 100 pages shared a full
sentence with the previous page). As a second guard, each generated
page is measured for verbatim sentence overlap against all earlier
pages (see engine/duplication.py); a page that repeats earlier
sentences is treated as failed and regenerated with the overlap
named in the retry prompt, a bounded number of times, and the
outcome is recorded in the build report.

Recurrence is also available as a selected device. The pack
framework's ``refrain`` parameter (boolean, default off, overridable
at build time) controls it. A refrain is recurrence with
development: the anchor theme returns changed by what the story has
established since its last appearance. With refrain on, the anchor
theme (the first page's opening sentences) is carried in the prompt
as a theme, and the model is directed to restate it, where the page
calls it back, as developed by the intervening facts, in fresh
wording. Verbatim copying is not the mechanism in either setting:
previous pages never reach the prompt in full, and a page that
copies earlier sentences verbatim is regenerated under the bounded
retry rule in both settings (with refrain on, the retry calls for
development, not merely fresh wording). The build report separates
the two measurements: verbatim overlap (the loop detector) and,
with refrain on, the development check (engine/duplication.py,
check_refrain): every thematic recurrence of the anchor must
demonstrably differ and carry newer material, and a book whose
refrain passages are near-identical copies fails that check by
name in the report.

A third guard runs after the duplication guard: the
subject-gender gate (see engine/gendergate.py). The series'
demonstration subject is male (canonical character record,
v2.0.0), and a book whose cast is mostly women showed the model
letting the narrator's own reference drift with theirs (The
Keeping Book, v0.3.0, page 79: the narrator counts himself
among "two women"). A page whose text trips the gate's
definite-pattern screen is treated as failed and regenerated
with the flagged sentences named, up to MAX_GENDER_RETRIES
times; the attempt with the fewest flagged sentences is kept
(ties broken by the duplication score), and the retry count
and any unresolved flags are recorded on the page and in the
build report. The gate is a referent screen, not a ban on
female pronouns: the women's pronouns are correct and remain.
The finished book is still audited after the build by
extraction and classification (the S7 failsafe); the gate is
the generation-time half of that control.

Two further screens run after the gender gate, added for the
devotional's corrected edition (see DEFECTS.md, V11--V13).
The spouse-term screen (engine/spousegate.py) is keyed to the
subject's recorded gender, which the pack elicits as a typed
fact (``subject_gender``) from the identity answer: a page
whose narrator possesses the wrong spouse in the first person
("my husband", for this series' male subject) is regenerated
under the same bounded rule. That construction is the
devotional's first edition's largest defect (62 of 100 pages)
and is invisible to the pronoun gate, because it attaches no
female marker to the narrator; the post-build audit now counts
spouse-term instances with the same code, so a gender result
is never reported clean on the pronoun audit alone. The
meta-narrative screen (engine/metagate.py) flags pages whose
prose names the generation machinery itself ("anchor
sentence", "carrying the newer facts", "story bible"): the
first devotional's prompts supplied those formulas, and the
model quoted them back on 68 of 100 pages. The prompt-side
half of that fix is below: the refrain block is now carried
only by pages whose slot assigns the return device (in the
first edition it was attached to all 100 prompts although
only 21 slots assign the device -- the saturation mechanism
behind that book's 53-of-100 duplication), and it directs the
return without naming the apparatus or supplying a quotable
formula.

With refrain on, the duplication guard's failure condition
also covers refrain development at generation time: a page
whose sentences restate the book's first-page sentences
without development -- verbatim copies, or thematic
recurrences carrying no material from the story since --
fails alongside verbatim duplication and is regenerated under
the same bounded rule, classified by the same code the
post-build development check (check_refrain) uses, so what
the build accepts and what the report measures are the same
judgement.

One craft standard is stated in every page prompt, for every
genre (set by the author, 2026-11-27): the beats of a page
connect by causation and contrast -- therefore, but, yet,
however, so -- never as a flat chain of "and then". The
standard is an instruction and a measurement, not a gate: the
build report counts chain markers against causal/contrast
connectors for the finished book (engine/connectors.py), and
the counts are reported as they fall.

One repair is applied to every produced page before any guard
runs: sentence completion. The 480-token page budget is the
standing cause of the series' truncation defect (10--25 of
100 pages per book ending mid-sentence). A page that does not
end at terminal punctuation is continued once, from its own
last token, with a small bounded budget, and only the words
that finish its final sentence are kept; if the continuation
does not reach a sentence end, the page stands as generated
and is measured as truncated. The completion is the model's
own continuation of its own sentence, never an editorial
finish, and the count of repaired pages is recorded in the
report alongside the truncation measurement.

One page is produced per non-empty answer. Empty answers produce no
page and are recorded in the build report; they are never padded or
invented. Build state is persisted after every page, so a build can
be interrupted and resumed without regenerating finished pages.

One interruption window is repaired explicitly: if a build stops
between a chapter's last page being saved and its synopsis being
written, the saved state holds the chapter's pages without its
synopsis, and a resumed build would otherwise skip the finished
pages and never revisit the chapter -- both of the first two books
shipped with exactly one such loss (memoir chapter 9, biography
chapter 7). On resume, before any new page is generated, chapters
whose answered pages are all present but whose synopsis is missing
have the synopsis regenerated from the saved pages.
"""

from __future__ import annotations

import json
from pathlib import Path

from .bible import Bible
from .connectors import check_connectors
from .continuity import check_continuity
from .duplication import check_duplication, check_refrain, \
    page_anchor_recurrences, page_overlap, split_sentences, \
    story_content_words
from .gendergate import subject_gender_flags
from .metagate import audit_meta_terms, meta_flags
from .pack import questions_by_chapter
from .spousegate import audit_spouse_terms, partner_term, \
    spouse_flags, wrong_spouse_term

WINDOW_PAGES = 1
WINDOW_EXCERPT_WORDS = 60
PAGE_MAX_TOKENS = 480
MAX_DUP_RETRIES = 2
MAX_GENDER_RETRIES = 2
MAX_SPOUSE_RETRIES = 2
MAX_META_RETRIES = 2
CONTINUATION_MAX_TOKENS = 64
_TERMINAL = '.!?"”’'


def _ends_complete(text: str) -> bool:
    """The series' uniform truncation test: a page is complete
    when its final character is terminal punctuation."""
    stripped = text.rstrip()
    return bool(stripped) and stripped[-1] in _TERMINAL


def _overlap_fails(overlap: dict) -> bool:
    """A page fails the duplication guard if it repeats any full
    sentence from the immediately previous page, or if more than a
    fifth of its sentences appear anywhere earlier in the book."""
    if overlap["shared_with_previous"] > 0:
        return True
    total = overlap["sentences"]
    return total > 0 and overlap["shared_with_any_earlier"] / total > 0.2


def _overlap_score(overlap: dict) -> int:
    """Lower is better; previous-page repetition weighs most."""
    return (overlap["shared_with_previous"] * 1000
            + overlap["shared_with_any_earlier"])


def _chat(system: str, user: str) -> str:
    return (f"<|im_start|>system\n{system}<|im_end|>\n"
            f"<|im_start|>user\n{user}<|im_end|>\n"
            f"<|im_start|>assistant\n")


class BookBuilder:
    def __init__(self, pack: dict, answers: dict[str, str], model,
                 state_path: str | Path) -> None:
        self.pack = pack
        self.answers = answers
        self.model = model
        self.state_path = Path(state_path)
        self.state = self._load_state()
        self.refrain = bool(pack.get("framework", {}).get("refrain", False))
        self.report: dict = {"skipped_empty": [], "pages_built": 0,
                             "refrain": self.refrain}
        # The subject's recorded identity, folded from the full
        # answer set rather than the incremental bible: the
        # screens keyed to it (spouse-term, and the subject line
        # every prompt carries) must hold from the first page,
        # before the identity answers have been folded in page
        # order. A pack that does not elicit a subject_gender
        # fact leaves the spouse screen inert.
        full_bible = Bible()
        for q in pack["questions"]:
            answer = answers.get(q["id"], "")
            if answer.strip():
                full_bible.update_from_answer(q, answer)
        self.subject_facts = full_bible.facts
        gender_fact = full_bible.facts.get("subject_gender")
        self.subject_gender = (gender_fact["value"]
                               if gender_fact else None)
        partner_fact = full_bible.facts.get("partner_name")
        self.partner_name = (partner_fact["value"]
                             if partner_fact else None)

    # -- state -----------------------------------------------------------

    def _load_state(self) -> dict:
        if self.state_path.exists():
            with open(self.state_path, encoding="utf-8") as fh:
                return json.load(fh)
        return {"pages": {}, "synopses": {}}

    def _save_state(self) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_path, "w", encoding="utf-8") as fh:
            json.dump(self.state, fh, indent=1)

    # -- context assembly -------------------------------------------------

    def _bible_upto(self, upto_index: int) -> Bible:
        bible = Bible()
        for q in self.pack["questions"][: upto_index + 1]:
            answer = self.answers.get(q["id"], "")
            if answer.strip():
                bible.update_from_answer(q, answer)
        return bible

    def _synopsis_text(self, before_chapter: str | None) -> str:
        parts = []
        for chapter in self.pack["chapters"]:
            if chapter["id"] == before_chapter:
                break
            syn = self.state["synopses"].get(chapter["id"])
            if syn:
                parts.append(f"[{chapter['title']}] {syn}")
        return "\n".join(parts) if parts else "(no chapters completed yet)"

    def _window_text(self) -> str:
        pages = self.ordered_pages()
        if not pages:
            return "(this is the first page of the book)"
        last = pages[-WINDOW_PAGES:]
        page = last[-1]
        words = page["text"].split()
        excerpt = " ".join(words[-WINDOW_EXCERPT_WORDS:])
        return (f"[Closing lines of page {page['index'] + 1}. These "
                f"lines are background only, supplied so the prose "
                f"can continue from where it stopped. Do not repeat "
                f"them, or any earlier sentence, verbatim.]\n"
                f"... {excerpt}")

    def _anchor_text(self) -> str | None:
        """The book's refrain anchor: the first page's opening
        sentences, carried as a theme (never as pages in full)."""
        pages = self.ordered_pages()
        if not pages:
            return None
        sentences = split_sentences(pages[0]["text"])
        if not sentences:
            return None
        return " ".join(sentences[:2])

    def ordered_pages(self) -> list[dict]:
        pages = list(self.state["pages"].values())
        return sorted(pages, key=lambda p: p["index"])

    # -- page production ---------------------------------------------------

    def _produce(self, prompt: str) -> tuple[str, bool]:
        """Generate one page candidate. Returns the text and
        whether its final sentence had to be completed."""
        text = self.model.complete(prompt, max_tokens=PAGE_MAX_TOKENS)
        if len(text.split()) < 50:
            text = self.model.complete(
                prompt, max_tokens=PAGE_MAX_TOKENS)
        return self._finish_sentence(text)

    def _finish_sentence(self, text: str) -> tuple[str, bool]:
        """Sentence completion: if the page's token budget ran
        out mid-sentence, continue the page from its own last
        token once, with a small bounded budget, and keep only
        the words that finish the final sentence. If the
        continuation never reaches a sentence end, the page
        stands as generated and is measured as truncated. The
        completion is the model's own continuation, never an
        editorial finish."""
        stripped = text.rstrip()
        if not stripped or stripped[-1] in _TERMINAL:
            return text, False
        continue_text = getattr(self.model, "continue_text", None)
        if continue_text is None:
            return text, False
        continuation = continue_text(
            text, max_tokens=CONTINUATION_MAX_TOKENS)
        if not continuation:
            return text, False
        end = -1
        for i, ch in enumerate(continuation):
            if ch in ".!?":
                end = i
                break
        if end < 0:
            return text, False
        piece = continuation[:end + 1]
        if not piece.strip(" .!?"):
            return text, False
        return text + piece, True

    # -- prompt construction ----------------------------------------------

    def page_prompt(self, question: dict, index: int, bible: Bible,
                    retry_note: str | None = None) -> str:
        fw = self.pack["framework"]
        device_lines = []
        for dev_id in question["devices"]:
            dev = fw["devices"][dev_id]
            device_lines.append(f"- {dev['name']}: {dev['instruction']}")
        subject_line = ""
        if self.subject_gender in ("male", "female"):
            who = ("man" if self.subject_gender == "male"
                   else "woman")
            poss = ("his" if self.subject_gender == "male"
                    else "her")
            role = partner_term(self.subject_gender)
            subject_line = f"The respondent is a {who}."
            if self.partner_name and role:
                subject_line += (
                    f" {self.partner_name} is {poss} {role}; the "
                    f"respondent's spouse is always {poss} {role}, "
                    f"never a "
                    f"{wrong_spouse_term(self.subject_gender)}.")
            subject_line += " "
        system = (
            f"You are the writing engine for a {self.pack['genre']} book. "
            f"{fw['global_instructions']} "
            f"{subject_line}"
            f"Voice: {fw['voice']} Point of view: {fw['pov']}. "
            f"Tense: {fw['tense']}. "
            f"Write exactly one page of prose, about "
            f"{fw['page_target_words']} words. Output only the page's "
            f"prose: no title, no heading, no commentary about the task. "
            f"Your role is transformation, not origination: everything "
            f"the page contains must come from the source answer and "
            f"the established state supplied below; do not invent "
            f"facts, people, places, or events beyond them. "
            f"Connect the beats of the page by causation and "
            f"contrast, not by sequence alone: what happens should "
            f"happen therefore, but, yet, however, or so -- never "
            f"as a flat chain of \"and then\" following \"and "
            f"then\", which makes a list instead of a story."
        )
        refrain_block = ""
        # The return is carried only by pages whose slot assigns
        # the return device. The first devotional attached this
        # block, with the anchor quoted, to every one of its 100
        # prompts although only 21 slots assign the device; the
        # model, told on every page to consider a return, filled
        # the book with near-verbatim boilerplate (53 of 100
        # pages sharing a sentence with the previous page). The
        # block also names no apparatus: it does not say
        # "anchor", "theme", or "refrain", the words the first
        # edition's prose then repeated on 68 pages (see
        # engine/metagate.py). An earlier wording of this block
        # did supply a quotable formula ("let it arrive changed
        # by the days since...") and the corrected edition
        # quoted it back as narration on pages 50, 53 and 94
        # (DEFECTS V17); the directive below is worded as plain
        # instruction, and the old formula's phrases are on the
        # meta screen so an echo costs a retry.
        if self.refrain and "anchor_return" in question["devices"]:
            anchor = self._anchor_text()
            if anchor:
                refrain_block = (
                    f"The first page said: \"{anchor}\" Write "
                    f"today's entry -- the day, the people, the "
                    f"practice. Never copy an earlier sentence "
                    f"word for word. Where today truly returns "
                    f"to the first page's sentence, write it as "
                    f"today has remade it, in today's own words, "
                    f"and say nothing about the sentence itself "
                    f"or its returning.\n\n")
        user = (
            f"STORY BIBLE (established state; do not contradict it):\n"
            f"{bible.render(question['bible_keys'])}\n\n"
            f"FIXED FACTS (must remain exactly as stated):\n"
            f"{bible.render_facts()}\n\n"
            f"ROLLING SYNOPSIS (chapters so far):\n"
            f"{self._synopsis_text(question['chapter'])}\n\n"
            f"PREVIOUS PAGE, CLOSING LINES (background only):\n"
            f"{self._window_text()}\n\n"
            f"{refrain_block}"
            f"QUESTION_ID: {question['id']}\n"
            f"NARRATIVE JOB OF THIS PAGE: {question['narrative_job']}\n"
            f"POSITION IN THE BOOK: {question['position']}\n"
            f"DEVICES TO APPLY:\n" + "\n".join(device_lines) + "\n\n"
            f"SOURCE ANSWER (the respondent's own words; transform this "
            f"material into the page, do not quote it verbatim at "
            f"length):\n{self.answers[question['id']]}\n\n"
            + (f"{retry_note}\n\n" if retry_note else "")
            + f"Write the page now."
        )
        return _chat(system, user)

    def synopsis_prompt(self, chapter: dict, pages: list[dict]) -> str:
        body = "\n\n".join(p["text"] for p in pages)
        system = ("You summarize one chapter of a book in about 120 "
                  "words, preserving names, places, dates, and turning "
                  "points exactly as written. Output only the summary.")
        user = (f"TASK: SUMMARIZE_CHAPTER\nCHAPTER_ID: {chapter['id']}\n\n"
                f"{body}\n\nWrite the chapter summary now.")
        return _chat(system, user)

    # -- build -------------------------------------------------------------

    def _repair_missing_synopses(self, grouped: dict) -> None:
        """Regenerate synopses for chapters whose pages all exist
        but whose synopsis is missing (the interruption window
        between a chapter's last page save and its synopsis write).
        Runs on resume, before any new page is generated, so later
        chapters are never conditioned on a rolling synopsis with a
        silent gap."""
        for chapter in self.pack["chapters"]:
            chapter_id = chapter["id"]
            if chapter_id in self.state["synopses"]:
                continue
            answered = [q for q in grouped[chapter_id]
                        if self.answers.get(q["id"], "").strip()]
            if not answered:
                continue
            if not all(q["id"] in self.state["pages"]
                       for q in answered):
                continue
            chapter_pages = [self.state["pages"][q["id"]]
                             for q in answered]
            syn = self.model.complete(
                self.synopsis_prompt(chapter, chapter_pages),
                max_tokens=220)
            self.state["synopses"][chapter_id] = syn
            self._save_state()

    def build(self) -> dict:
        questions = self.pack["questions"]
        grouped = questions_by_chapter(self.pack)
        chapter_of = {q["id"]: q["chapter"] for q in questions}
        self._repair_missing_synopses(grouped)

        for index, question in enumerate(questions):
            qid = question["id"]
            answer = self.answers.get(qid, "")
            if not answer.strip():
                if qid not in self.report["skipped_empty"]:
                    self.report["skipped_empty"].append(qid)
                continue
            if qid in self.state["pages"]:
                continue
            bible = self._bible_upto(index)
            prompt = self.page_prompt(question, index, bible)
            text, repaired = self._produce(prompt)
            # Duplication guard (both refrain settings): a page
            # that re-emits earlier sentences verbatim is treated
            # as failed and regenerated with the overlap named, up
            # to MAX_DUP_RETRIES times. Verbatim copying is never
            # the mechanism. With refrain on, the failure
            # condition also covers development: a sentence that
            # restates the book's first-page sentences without
            # carrying anything the story has established since
            # (classified by the same code as the post-build
            # development check) fails alongside a verbatim copy,
            # because in the first devotional exactly that
            # near-verbatim boilerplate -- not the anchor alone
            # -- saturated the book's final third. The
            # least-duplicative attempt is kept; the outcome is
            # recorded on the page and in the build report. The
            # retry note names the repeated sentences without
            # supplying a quotable formula of its own (the first
            # edition's note language, "carrying the newer
            # facts", is itself among the phrases its prose
            # leaked; see engine/metagate.py).
            earlier = self.ordered_pages()
            earlier_texts = [p["text"] for p in earlier]
            previous_text = earlier[-1]["text"] if earlier else None
            best_overlap = page_overlap(text, earlier_texts,
                                        previous_text)
            anchor_sentences = (
                split_sentences(earlier[0]["text"])
                if self.refrain and earlier else [])
            refrain_story_words = (
                story_content_words(earlier_texts[1:])
                if anchor_sentences else set())

            def refrain_failures(candidate_text: str) -> list[dict]:
                if not anchor_sentences:
                    return []
                return [r for r in page_anchor_recurrences(
                    split_sentences(candidate_text), anchor_sentences,
                    refrain_story_words) if not r["developed"]]

            def dup_score(overlap: dict, failures: list) -> int:
                return (_overlap_score(overlap)
                        + 500 * len(failures))

            best_refrain_failures = refrain_failures(text)
            retries = 0
            while ((_overlap_fails(best_overlap)
                    or best_refrain_failures)
                   and retries < MAX_DUP_RETRIES):
                retries += 1
                named_parts = []
                if best_overlap["shared_sentences"]:
                    named_parts.append(
                        "sentences copied word for word from "
                        "earlier in the book: " + "; ".join(
                            f'"{s[:120]}"'
                            for s in
                            best_overlap["shared_sentences"][:3]))
                if best_refrain_failures:
                    named_parts.append(
                        "sentences that restate the book's "
                        "first-page sentences unchanged: "
                        + "; ".join(
                            f'"{r["sentence"][:120]}"'
                            for r in best_refrain_failures[:3]))
                retry_note = (
                    f"RETRY {retries}: the previous attempt at "
                    f"this page repeated earlier material -- "
                    + "; ".join(named_parts)
                    + ". Write the page again from the source "
                    f"answer in entirely fresh sentences. A "
                    f"sentence that comes back from earlier in "
                    f"the book must come back changed by what "
                    f"has happened since, in words of its own, "
                    f"or not come back at all. Do not repeat any "
                    f"sentence that has already appeared in the "
                    f"book, and do not restart the previous "
                    f"page's wording.")
                candidate, cand_repaired = self._produce(
                    self.page_prompt(question, index, bible,
                                     retry_note=retry_note))
                cand_overlap = page_overlap(candidate, earlier_texts,
                                            previous_text)
                cand_failures = refrain_failures(candidate)
                if dup_score(cand_overlap, cand_failures) < \
                        dup_score(best_overlap,
                                  best_refrain_failures):
                    text, best_overlap, best_refrain_failures, \
                        repaired = candidate, cand_overlap, \
                        cand_failures, cand_repaired
            # Subject-gender gate: a page whose text attaches a
            # female pronoun or role word to the subject/narrator
            # (definite-pattern screen, engine/gendergate.py) is
            # treated as failed and regenerated with the flagged
            # sentences named, up to MAX_GENDER_RETRIES times.
            # The attempt with the fewest flagged sentences is
            # kept, ties broken by the duplication score and then
            # the refrain-failure count; the outcome is recorded
            # on the page and in the report.
            gender_flags = subject_gender_flags(text)
            gender_retries = 0
            while (gender_flags
                   and gender_retries < MAX_GENDER_RETRIES):
                gender_retries += 1
                named = "; ".join(
                    f'"{f["sentence"][:120]}"'
                    for f in gender_flags[:3])
                retry_note = (
                    f"RETRY {gender_retries} (subject-gender gate): "
                    f"the previous attempt at this page attached a "
                    f"female pronoun or female role word to the "
                    f"respondent himself, or left a female pronoun "
                    f"without a named referent, in: {named}. The "
                    f"respondent, Frozen In Flames, is a man: refer "
                    f"to him only with male pronouns and male role "
                    f"words (he, his, son, husband, father). The "
                    f"women of his family — his mother Ruby, his "
                    f"sister Opal, his wife Amber, and the "
                    f"matriarchs Jet, Pearl, Coral, and Topaz — "
                    f"keep their own pronouns, but name the woman "
                    f"in the sentence itself wherever a pronoun "
                    f"refers to her, so no female reference can be "
                    f"read as the respondent's.")
                candidate, cand_repaired = self._produce(
                    self.page_prompt(question, index, bible,
                                     retry_note=retry_note))
                cand_flags = subject_gender_flags(candidate)
                cand_overlap = page_overlap(candidate, earlier_texts,
                                            previous_text)
                if (len(cand_flags), _overlap_score(cand_overlap),
                        len(refrain_failures(candidate))) < \
                        (len(gender_flags),
                         _overlap_score(best_overlap),
                         len(best_refrain_failures)):
                    text, gender_flags, best_overlap, repaired = \
                        candidate, cand_flags, cand_overlap, \
                        cand_repaired
                    best_refrain_failures = refrain_failures(text)
            # Spouse-term screen (engine/spousegate.py): a page
            # whose narrator possesses the wrong spouse in the
            # first person, keyed to the subject's recorded
            # gender, is regenerated under the same bounded rule.
            # Inert for packs that record no subject gender.
            spouse_page_flags = spouse_flags(text, self.subject_gender)
            spouse_retries = 0
            while (spouse_page_flags
                   and spouse_retries < MAX_SPOUSE_RETRIES):
                spouse_retries += 1
                named = "; ".join(
                    f'"{f["sentence"][:120]}"'
                    for f in spouse_page_flags[:3])
                wrong = wrong_spouse_term(self.subject_gender)
                right = partner_term(self.subject_gender)
                who = ("man" if self.subject_gender == "male"
                       else "woman")
                poss = ("his" if self.subject_gender == "male"
                        else "her")
                if self.partner_name:
                    marriage = (f"{self.partner_name} is {poss} "
                                f"{right}")
                else:
                    marriage = f"{poss} spouse is {poss} {right}"
                retry_note = (
                    f"RETRY {spouse_retries} (spouse-term screen): "
                    f"the previous attempt at this page gave the "
                    f"respondent a {wrong}, in: {named}. The "
                    f"respondent is a {who}: {marriage}, and the "
                    f"respondent's spouse is always {poss} "
                    f"{right}, never a {wrong}. Write the page "
                    f"again with the respondent's marriage as "
                    f"recorded.")
                candidate, cand_repaired = self._produce(
                    self.page_prompt(question, index, bible,
                                     retry_note=retry_note))
                cand_flags = spouse_flags(candidate,
                                          self.subject_gender)
                cand_overlap = page_overlap(candidate, earlier_texts,
                                            previous_text)
                if (len(cand_flags), _overlap_score(cand_overlap),
                        len(refrain_failures(candidate))) < \
                        (len(spouse_page_flags),
                         _overlap_score(best_overlap),
                         len(best_refrain_failures)):
                    text, spouse_page_flags, best_overlap, \
                        repaired = candidate, cand_flags, \
                        cand_overlap, cand_repaired
                    best_refrain_failures = refrain_failures(text)
            # Meta-narrative screen (engine/metagate.py): a page
            # whose prose names the generation machinery itself
            # is regenerated under the same bounded rule.
            meta_page_flags = meta_flags(text)
            meta_retries = 0
            while (meta_page_flags
                   and meta_retries < MAX_META_RETRIES):
                meta_retries += 1
                phrases = "; ".join(sorted(
                    {p for f in meta_page_flags
                     for p in f["phrases"]}))
                retry_note = (
                    f"RETRY {meta_retries} (meta-narrative "
                    f"screen): the previous attempt at this page "
                    f"talked about the book's own construction, "
                    f"in phrases including: {phrases}. Write the "
                    f"page itself: the scene, the people, the "
                    f"events, what was done and what was said. "
                    f"Never mention sentences returning, "
                    f"material supplied for the page, or the "
                    f"bookkeeping behind the book.")
                candidate, cand_repaired = self._produce(
                    self.page_prompt(question, index, bible,
                                     retry_note=retry_note))
                cand_flags = meta_flags(candidate)
                cand_overlap = page_overlap(candidate, earlier_texts,
                                            previous_text)
                if (len(cand_flags), _overlap_score(cand_overlap),
                        len(refrain_failures(candidate))) < \
                        (len(meta_page_flags),
                         _overlap_score(best_overlap),
                         len(best_refrain_failures)):
                    text, meta_page_flags, best_overlap, \
                        repaired = candidate, cand_flags, \
                        cand_overlap, cand_repaired
                    best_refrain_failures = refrain_failures(text)
            self.state["pages"][qid] = {
                "question_id": qid,
                "chapter": question["chapter"],
                "index": len(self.state["pages"]),
                "text": text,
                "word_count": len(text.split()),
                "duplication_retries": retries,
                "gender_retries": gender_retries,
                "gender_flags": len(gender_flags),
                "spouse_retries": spouse_retries,
                "spouse_flags": len(spouse_page_flags),
                "meta_retries": meta_retries,
                "meta_flags": len(meta_page_flags),
                "truncation_repaired": repaired,
                "refrain_undeveloped":
                    len(refrain_failures(text)),
                "shared_with_previous":
                    best_overlap["shared_with_previous"],
                "shared_with_any_earlier":
                    best_overlap["shared_with_any_earlier"],
            }
            self._save_state()

            # Chapter finished? Write its rolling synopsis.
            chapter_id = chapter_of[qid]
            chapter_qs = grouped[chapter_id]
            answered = [q for q in chapter_qs
                        if self.answers.get(q["id"], "").strip()]
            if (answered and answered[-1]["id"] == qid
                    and chapter_id not in self.state["synopses"]):
                chapter_pages = [self.state["pages"][q["id"]]
                                 for q in answered
                                 if q["id"] in self.state["pages"]]
                chapter = next(c for c in self.pack["chapters"]
                               if c["id"] == chapter_id)
                syn = self.model.complete(
                    self.synopsis_prompt(chapter, chapter_pages),
                    max_tokens=220)
                self.state["synopses"][chapter_id] = syn
                self._save_state()

        pages = self.ordered_pages()
        # Re-index pages in true question order.
        order = {q["id"]: i for i, q in enumerate(questions)}
        pages.sort(key=lambda p: order[p["question_id"]])
        for i, p in enumerate(pages):
            p["index"] = i
        bible = self._bible_upto(len(questions) - 1)
        issues = check_continuity(pages, bible.facts)
        self.report.update({
            "pages_built": len(pages),
            "total_words": sum(p["word_count"] for p in pages),
            "continuity_issues": issues,
            "duplication": check_duplication(pages),
            "connectors": check_connectors(pages),
            "gender_gate": {
                "retries": sum(p.get("gender_retries", 0)
                               for p in pages),
                "pages_flagged": sum(1 for p in pages
                                     if p.get("gender_flags", 0)),
                "flagged_sentences": sum(p.get("gender_flags", 0)
                                         for p in pages),
            },
            "spouse_gate": {
                "retries": sum(p.get("spouse_retries", 0)
                               for p in pages),
                "pages_flagged": sum(1 for p in pages
                                     if p.get("spouse_flags", 0)),
                "flagged_sentences": sum(p.get("spouse_flags", 0)
                                         for p in pages),
            },
            "meta_gate": {
                "retries": sum(p.get("meta_retries", 0)
                               for p in pages),
                "pages_flagged": sum(1 for p in pages
                                    if p.get("meta_flags", 0)),
                "flagged_sentences": sum(p.get("meta_flags", 0)
                                         for p in pages),
            },
            "spouse_audit": audit_spouse_terms(
                pages, self.subject_gender),
            "meta_audit": audit_meta_terms(pages),
            "truncation": {
                "pages_repaired": sum(
                    1 for p in pages
                    if p.get("truncation_repaired")),
                "pages_ending_mid_sentence": sum(
                    1 for p in pages
                    if not _ends_complete(p["text"])),
            },
            "model": getattr(self.model, "name", "unknown"),
        })
        if self.refrain:
            self.report["refrain_analysis"] = check_refrain(pages)
        self._save_state()
        return self.report
