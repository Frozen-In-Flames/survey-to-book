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

One page is produced per non-empty answer. Empty answers produce no
page and are recorded in the build report; they are never padded or
invented. Build state is persisted after every page, so a build can
be interrupted and resumed without regenerating finished pages.
"""

from __future__ import annotations

import json
from pathlib import Path

from .bible import Bible
from .continuity import check_continuity
from .duplication import check_duplication, page_overlap
from .pack import questions_by_chapter

WINDOW_PAGES = 1
WINDOW_EXCERPT_WORDS = 60
PAGE_MAX_TOKENS = 480
MAX_DUP_RETRIES = 2


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
        self.report: dict = {"skipped_empty": [], "pages_built": 0}

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

    def ordered_pages(self) -> list[dict]:
        pages = list(self.state["pages"].values())
        return sorted(pages, key=lambda p: p["index"])

    # -- prompt construction ----------------------------------------------

    def page_prompt(self, question: dict, index: int, bible: Bible,
                    retry_note: str | None = None) -> str:
        fw = self.pack["framework"]
        device_lines = []
        for dev_id in question["devices"]:
            dev = fw["devices"][dev_id]
            device_lines.append(f"- {dev['name']}: {dev['instruction']}")
        system = (
            f"You are the writing engine for a {self.pack['genre']} book. "
            f"{fw['global_instructions']} "
            f"Voice: {fw['voice']} Point of view: {fw['pov']}. "
            f"Tense: {fw['tense']}. "
            f"Write exactly one page of prose, about "
            f"{fw['page_target_words']} words. Output only the page's "
            f"prose: no title, no heading, no commentary about the task."
        )
        user = (
            f"STORY BIBLE (established state; do not contradict it):\n"
            f"{bible.render(question['bible_keys'])}\n\n"
            f"FIXED FACTS (must remain exactly as stated):\n"
            f"{bible.render_facts()}\n\n"
            f"ROLLING SYNOPSIS (chapters so far):\n"
            f"{self._synopsis_text(question['chapter'])}\n\n"
            f"PREVIOUS PAGE, CLOSING LINES (background only):\n"
            f"{self._window_text()}\n\n"
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

    def build(self) -> dict:
        questions = self.pack["questions"]
        grouped = questions_by_chapter(self.pack)
        chapter_of = {q["id"]: q["chapter"] for q in questions}

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
            text = self.model.complete(prompt, max_tokens=PAGE_MAX_TOKENS)
            if len(text.split()) < 50:
                text = self.model.complete(
                    prompt, max_tokens=PAGE_MAX_TOKENS)
            # Duplication guard: a page that re-emits earlier
            # sentences verbatim is treated as failed and regenerated
            # with the overlap named, up to MAX_DUP_RETRIES times.
            # The least-duplicative attempt is kept; the outcome is
            # recorded on the page and in the build report.
            earlier = self.ordered_pages()
            earlier_texts = [p["text"] for p in earlier]
            previous_text = earlier[-1]["text"] if earlier else None
            best_overlap = page_overlap(text, earlier_texts,
                                        previous_text)
            retries = 0
            while _overlap_fails(best_overlap) and retries < MAX_DUP_RETRIES:
                retries += 1
                named = "; ".join(
                    f'"{s[:120]}"'
                    for s in best_overlap["shared_sentences"][:3])
                retry_note = (
                    f"RETRY {retries}: the previous attempt at this "
                    f"page repeated sentences verbatim from earlier "
                    f"in the book, including: {named}. Write the page "
                    f"again from the source answer in entirely fresh "
                    f"sentences. Do not repeat any sentence that has "
                    f"already appeared in the book, and do not restart "
                    f"the previous page's wording.")
                candidate = self.model.complete(
                    self.page_prompt(question, index, bible,
                                     retry_note=retry_note),
                    max_tokens=PAGE_MAX_TOKENS)
                cand_overlap = page_overlap(candidate, earlier_texts,
                                            previous_text)
                if _overlap_score(cand_overlap) < _overlap_score(best_overlap):
                    text, best_overlap = candidate, cand_overlap
            self.state["pages"][qid] = {
                "question_id": qid,
                "chapter": question["chapter"],
                "index": len(self.state["pages"]),
                "text": text,
                "word_count": len(text.split()),
                "duplication_retries": retries,
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
            "model": getattr(self.model, "name", "unknown"),
        })
        self._save_state()
        return self.report
