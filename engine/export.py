"""Manuscript export.

Assembles generated pages into a single Markdown manuscript: front
matter (including a factual provenance note), a chapter table of
contents, the pages in order grouped under chapter headings, and a
colophon recording the generation parameters and the continuity
check outcome.
"""

from __future__ import annotations

from .pack import questions_by_chapter


def export_markdown(pack: dict, state: dict, report: dict, meta: dict) -> str:
    grouped = questions_by_chapter(pack)
    pages_by_qid = state["pages"]
    chapter_titles = {c["id"]: c["title"] for c in pack["chapters"]}

    lines: list[str] = []
    lines.append(f"# {meta['title']}")
    lines.append("")
    lines.append(f"*{meta.get('subtitle', '')}*")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Front matter")
    lines.append("")
    lines.append(meta["provenance"])
    lines.append("")
    lines.append(f"- Genre pack: {pack['genre']} (version {pack['version']})")
    lines.append(f"- Questions in pack: {len(pack['questions'])}")
    lines.append(f"- Pages in this book: {report['pages_built']}")
    lines.append(f"- Total words: {report['total_words']}")
    if report.get("skipped_empty"):
        lines.append(
            f"- Questions left unanswered (no page generated): "
            f"{len(report['skipped_empty'])}")
    lines.append("")
    lines.append("## Contents")
    lines.append("")
    for chapter in pack["chapters"]:
        lines.append(f"- {chapter['title']}")
    lines.append("")
    lines.append("---")
    lines.append("")

    page_number = 0
    for chapter in pack["chapters"]:
        chapter_pages = []
        for q in grouped[chapter["id"]]:
            page = pages_by_qid.get(q["id"])
            if page:
                chapter_pages.append(page)
        if not chapter_pages:
            continue
        lines.append(f"## {chapter['title']}")
        lines.append("")
        for page in sorted(chapter_pages, key=lambda p: p["index"]):
            page_number += 1
            lines.append(f"### Page {page_number}")
            lines.append("")
            lines.append(page["text"])
            lines.append("")
        lines.append("---")
        lines.append("")

    issues = report.get("continuity_issues", [])
    lines.append("## Colophon")
    lines.append("")
    lines.append(meta["colophon"])
    lines.append("")
    lines.append(f"- Generating model: {report.get('model', 'unknown')}")
    lines.append(f"- Generation: fully local and offline; no network "
                 f"services were used at any stage.")
    if issues:
        lines.append(f"- Continuity check: {len(issues)} candidate "
                     f"issue(s) flagged for human review:")
        for issue in issues:
            lines.append(
                f"  - page {issue['page_index'] + 1}: "
                f"{issue['type']} on {issue.get('fact_slot') or 'name'}: "
                f"expected {issue.get('expected')!r}, "
                f"found {issue.get('found')!r}")
    else:
        lines.append("- Continuity check: no candidate contradictions "
                     "found against the story bible's fixed facts.")
    lines.append("")
    return "\n".join(lines)
