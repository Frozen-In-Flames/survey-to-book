#!/usr/bin/env python3
"""Build the GitHub Pages library site for the proof-of-works books.

The site is a library, not a single book page. It is data-driven over
every published book in the repo (books/*/manuscript.md together with
books/*/report.json):

- docs/index.html            the library index: every book listed with
                             its title, genre, demonstration character,
                             page and word counts, a Read button and a
                             Download button
- docs/<slug>/index.html     that book's reader: the entire book online,
                             page by page, with chapter navigation and
                             per-book position memory
- docs/<slug>/<slug>.md      verbatim manuscript copy, for download
                             (byte-identical to the book's manuscript)
- docs/<slug>/<slug>.txt     plain-text rendering, for download
- docs/.nojekyll             keeps Pages from running Jekyll

All pages are self-contained and make zero external requests. Adding
a book is a data entry: drop the finished book under books/ and, for
a curated slug and character line, add one BOOK_META entry below;
unregistered books are still listed with derived defaults.

Usage: python3 tools/build_reader_site.py [docs-dir]
Defaults: docs/ under the repo root.
"""

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Curated per-book metadata, keyed by the book's directory name under
# books/. Publication order is the dict order.
BOOK_META = {
    "memoir-first-book": {
        "slug": "the-porch-light",
        "genre": "Memoir",
        "character": ("June Calloway, a fictional demonstration "
                      "persona"),
    },
    "biography-first-book": {
        "slug": "the-cold-room",
        "genre": "Biography",
        "character": ("Frozen In Flames, a fictional demonstration "
                      "persona: the series' demonstration user"),
    },
    "family-history-first-book": {
        "slug": "the-keeping-book",
        "genre": "Family History",
        "character": ("Frozen In Flames, a fictional demonstration "
                      "persona: the series' demonstration user"),
    },
}

SERIES_NOTE = (
    "Each book in this library was generated locally and offline by "
    "survey-to-book from one fictional respondent's answers to a "
    "genre survey: proof of works for the genre pack named on the "
    "book. From the second book onward the respondent is the "
    "series' demonstration user, the fictional persona Frozen In "
    "Flames, drawn from one canonical character record, so the same "
    "character headlines every book. The first book's respondent is "
    "the fictional persona June Calloway."
)


def inline(text: str) -> str:
    """Escape HTML, then apply the manuscript's only inline markup: *em*."""
    out = html.escape(text)
    out = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", out)
    return out


def md_to_html(md: str) -> str:
    """Convert the manuscript's limited markdown (paragraphs, - lists,
    --- rules) to HTML."""
    blocks, para, items = [], [], []

    def flush_para():
        if para:
            blocks.append("<p>" + inline(" ".join(para)) + "</p>")
            para.clear()

    def flush_list():
        if items:
            lis = "".join("<li>" + inline(i) + "</li>" for i in items)
            blocks.append("<ul>" + lis + "</ul>")
            items.clear()

    for raw in md.splitlines():
        line = raw.strip()
        if not line:
            flush_para()
            flush_list()
        elif line == "---":
            flush_para()
            flush_list()
            blocks.append("<hr>")
        elif line.startswith("- "):
            flush_para()
            items.append(line[2:])
        else:
            flush_list()
            para.append(line)
    flush_para()
    flush_list()
    return "\n".join(blocks)


def parse_manuscript(md: str):
    """Split the manuscript into title, subtitle, and ## sections; split
    chapter sections into ### Page N units."""
    lines = md.splitlines()
    title = lines[0].lstrip("# ").strip()
    subtitle = ""
    sections = []  # (heading, body)
    heading, body = None, []
    for line in lines[1:]:
        if line.startswith("## "):
            if heading is not None:
                sections.append((heading, "\n".join(body)))
            heading, body = line[3:].strip(), []
        elif heading is None:
            if line.strip().startswith("*") and line.strip().endswith("*"):
                subtitle = line.strip().strip("*")
        else:
            body.append(line)
    if heading is not None:
        sections.append((heading, "\n".join(body)))
    return title, subtitle, sections


def discover_books() -> list[dict]:
    """All published books: books/*/ with manuscript.md + report.json,
    curated entries first (in BOOK_META order), then any others."""
    books_dir = ROOT / "books"
    found = {}
    for book_dir in sorted(books_dir.iterdir()):
        if not book_dir.is_dir():
            continue
        if not (book_dir / "manuscript.md").exists():
            continue
        if not (book_dir / "report.json").exists():
            continue
        meta = BOOK_META.get(book_dir.name, {})
        found[book_dir.name] = {
            "dir": book_dir,
            "slug": meta.get("slug", book_dir.name),
            "genre": meta.get(
                "genre", book_dir.name.split("-")[0].capitalize()),
            "character": meta.get(
                "character", "a fictional demonstration persona"),
        }
    ordered = [found[name] for name in BOOK_META if name in found]
    ordered += [book for name, book in found.items()
                if name not in BOOK_META]
    return ordered


def build_book(book: dict, docs: Path) -> dict:
    """Emit one book's reader + downloads; return its library entry."""
    book_dir, slug = book["dir"], book["slug"]
    manuscript = (book_dir / "manuscript.md").read_text(encoding="utf-8")
    report = json.loads((book_dir / "report.json").read_text(encoding="utf-8"))
    title, subtitle, sections = parse_manuscript(manuscript)

    screens = []   # {kind, label, chapter, html}
    chapters = []  # {name, first}  first = screen index of its first page
    for heading, body in sections:
        if heading == "Contents":
            continue
        if heading in ("Front matter", "Colophon"):
            screens.append({
                "kind": "meta", "label": heading, "chapter": "",
                "html": md_to_html(body),
            })
            continue
        first = len(screens)
        chapters.append({"name": heading, "first": first})
        parts = re.split(r"^### Page (\d+)\s*$", body, flags=re.M)
        # parts: [pre, num, text, num, text, ...]
        for i in range(1, len(parts), 2):
            screens.append({
                "kind": "page",
                "label": "Page " + parts[i],
                "chapter": heading,
                "html": md_to_html(parts[i + 1]),
            })

    out = docs / slug
    out.mkdir(parents=True, exist_ok=True)
    (out / (slug + ".md")).write_text(manuscript, encoding="utf-8")

    # Plain-text rendering for download.
    txt = [title]
    if subtitle:
        txt.append(subtitle)
    for heading, body in sections:
        if heading == "Contents":
            continue
        txt.append("\n\n" + heading.upper() + "\n")
        text = re.sub(r"^### Page (\d+)\s*$", r"Page \1", body, flags=re.M)
        text = text.replace("---", "")
        text = re.sub(r"\*", "", text)
        txt.append(text.strip())
    (out / (slug + ".txt")).write_text("\n".join(txt) + "\n",
                                       encoding="utf-8")

    data = {
        "title": title,
        "subtitle": subtitle,
        "pages": report["pages_built"],
        "words": report["total_words"],
        "model": report["model"],
        "chapters": chapters,
        "screens": screens,
        "slug": slug,
    }
    page = READER_TEMPLATE.replace(
        "%%DATA%%", json.dumps(data, ensure_ascii=False)
        .replace("</", "<\\/"))
    page = page.replace("%%TITLE%%", html.escape(title))
    (out / "index.html").write_text(page, encoding="utf-8")
    print(f"{slug}: {len(screens)} screens ({len(chapters)} chapters), "
          f"reader {(out / 'index.html').stat().st_size} bytes")
    return {
        "slug": slug,
        "title": title,
        "subtitle": subtitle,
        "genre": book["genre"],
        "character": book["character"],
        "pages": report["pages_built"],
        "words": report["total_words"],
    }


def build_library(entries: list[dict], docs: Path) -> None:
    cards = []
    for e in entries:
        cards.append(
            '<article class="book">'
            f"<h2>{html.escape(e['title'])}</h2>"
            + (f"<p class=\"subtitle\">{html.escape(e['subtitle'])}</p>"
               if e["subtitle"] else "")
            + f"<p class=\"meta\">{html.escape(e['genre'])} · "
              f"{e['pages']} pages · {e['words']:,} words</p>"
            + f"<p class=\"character\">Demonstration character: "
              f"{html.escape(e['character'])}.</p>"
            + '<p class="actions">'
              f"<a class=\"read\" href=\"{e['slug']}/\">Read</a>"
              f"<a class=\"download\" href=\"{e['slug']}/{e['slug']}.md\" "
              f"download>↓ Download (.md)</a>"
              f"<a class=\"txt\" href=\"{e['slug']}/{e['slug']}.txt\" "
              f"download>plain text (.txt)</a>"
              "</p></article>"
        )
    page = LIBRARY_TEMPLATE.replace("%%CARDS%%", "\n".join(cards))
    page = page.replace("%%SERIES_NOTE%%", html.escape(SERIES_NOTE))
    page = page.replace("%%COUNT%%", str(len(entries)))
    (docs / "index.html").write_text(page, encoding="utf-8")
    print(f"library index: {len(entries)} book(s), "
          f"{(docs / 'index.html').stat().st_size} bytes")


def build(docs: Path) -> None:
    docs.mkdir(parents=True, exist_ok=True)
    (docs / ".nojekyll").write_text("", encoding="utf-8")
    books = discover_books()
    if not books:
        raise SystemExit("no published books found under books/")
    entries = [build_book(book, docs) for book in books]
    build_library(entries, docs)


LIBRARY_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>survey-to-book — proof-of-works library</title>
<style>
  :root { --ink:#1d1a16; --paper:#faf7f1; --accent:#7a4416; --muted:#6d655b; }
  * { box-sizing: border-box; }
  body { margin:0; background:var(--paper); color:var(--ink);
         font-family: Georgia, "Iowan Old Style", "Times New Roman", serif; }
  main { max-width:44rem; margin:0 auto; padding:2rem 1.1rem 3rem; }
  h1 { font-size:1.9rem; margin:.2rem 0 .4rem; }
  .series { color:var(--muted); font-size:1.02rem; line-height:1.6;
            margin:0 0 2rem; }
  .book { border:1px solid #ddd3c3; border-radius:.6rem; background:#fff;
          padding:1.2rem 1.3rem 1.3rem; margin:0 0 1.4rem; }
  .book h2 { margin:.1rem 0 .2rem; font-size:1.45rem; }
  .book .subtitle { margin:0 0 .5rem; font-style:italic; color:var(--muted); }
  .book .meta { margin:0 0 .4rem; font-family:system-ui, sans-serif;
                font-size:.92rem; color:var(--muted);
                text-transform:uppercase; letter-spacing:.05em; }
  .book .character { margin:0 0 1rem; line-height:1.55; }
  .actions { display:flex; flex-wrap:wrap; gap:.6rem; align-items:center;
             margin:0; font-family:system-ui, sans-serif; }
  .actions a.read, .actions a.download { display:inline-block;
      text-decoration:none; font-weight:700; border-radius:.5rem;
      padding:.8rem 1.4rem; font-size:1.05rem; }
  .actions a.read { background:var(--accent); color:#fff; }
  .actions a.read:hover { background:#5f3410; }
  .actions a.download { background:transparent; color:var(--accent);
      border:2px solid var(--accent); padding:.68rem 1.2rem; }
  .actions a.txt { color:var(--accent); font-size:.95rem; }
  footer { border-top:1px solid #ddd3c3; padding:1rem; text-align:center;
           font-family: system-ui, sans-serif; font-size:.82rem;
           color:var(--muted); }
  footer a { color:var(--accent); }
</style>
</head>
<body>
<main>
  <h1>survey-to-book: the proof-of-works library</h1>
  <p class="series">%%SERIES_NOTE%%</p>
  %%CARDS%%
</main>
<footer>%%COUNT%% book(s) published · Generated locally and offline ·
  <a href="https://github.com/Frozen-In-Flames/survey-to-book">Source repository</a></footer>
</body>
</html>
"""


READER_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%%TITLE%% — a survey-to-book proof of works</title>
<style>
  :root { --ink:#1d1a16; --paper:#faf7f1; --accent:#7a4416; --muted:#6d655b; }
  * { box-sizing: border-box; }
  body { margin:0; background:var(--paper); color:var(--ink);
         font-family: Georgia, "Iowan Old Style", "Times New Roman", serif; }
  #progress { position:fixed; top:0; left:0; height:4px; background:var(--accent);
              width:0; z-index:20; transition:width .2s; }
  header { position:sticky; top:0; z-index:10; background:var(--paper);
           border-bottom:1px solid #ddd3c3; padding:.6rem 1rem;
           display:flex; flex-wrap:wrap; gap:.6rem; align-items:center;
           justify-content:space-between; }
  header .book { font-size:1.05rem; font-weight:bold; }
  header .book span { display:block; font-size:.78rem; font-weight:normal;
                      color:var(--muted); font-style:italic; }
  header .lib { font-family:system-ui, sans-serif; font-size:.9rem;
                color:var(--accent); text-decoration:none; }
  .download { display:inline-block; background:var(--accent); color:#fff;
              font-family: system-ui, sans-serif; font-weight:700;
              font-size:1.05rem; text-decoration:none;
              padding:.8rem 1.4rem; border-radius:.5rem; }
  .download:active, .download:hover { background:#5f3410; }
  main { max-width:40rem; margin:0 auto; padding:1.2rem 1.1rem 2rem;
         font-size:1.13rem; line-height:1.65; }
  main h2 { font-size:1.35rem; margin:.4rem 0 .2rem; }
  main h3.pagelabel { font-size:.95rem; color:var(--muted); font-weight:normal;
                      font-family: system-ui, sans-serif; margin:0 0 1rem;
                      text-transform:uppercase; letter-spacing:.06em; }
  main p { margin:0 0 1em; }
  main hr { border:none; border-top:1px solid #ddd3c3; margin:1.6em 0; }
  .controls { max-width:40rem; margin:0 auto; padding:0 1.1rem 2.5rem;
              font-family: system-ui, sans-serif; }
  .controls .row { display:flex; gap:.6rem; align-items:stretch;
                   justify-content:space-between; }
  .controls button, .controls select { font:inherit; font-size:1rem;
      padding:.75rem 1rem; border-radius:.5rem; border:1px solid #c9bda6;
      background:#fff; color:var(--ink); cursor:pointer; }
  .controls button:disabled { opacity:.35; cursor:default; }
  .controls select { flex:1; min-width:0; }
  #pos { text-align:center; color:var(--muted); font-size:.9rem;
         margin:.7rem 0; }
  .endmatter { text-align:center; margin-top:2rem; }
  .endmatter p { font-family: system-ui, sans-serif; font-size:.95rem;
                 color:var(--muted); }
  footer { border-top:1px solid #ddd3c3; padding:1rem; text-align:center;
           font-family: system-ui, sans-serif; font-size:.82rem;
           color:var(--muted); }
  footer a { color:var(--accent); }
</style>
</head>
<body>
<div id="progress"></div>
<header>
  <div class="book">%%TITLE%%<span id="subtitle"></span></div>
  <a class="lib" href="../index.html">← Library</a>
  <a class="download" id="dl-top" href="#" download>↓ Download the book</a>
</header>
<main id="main"></main>
<div class="controls">
  <div class="row">
    <button id="prev" type="button">← Previous</button>
    <select id="chapter" aria-label="Chapter"></select>
    <button id="next" type="button">Next →</button>
  </div>
  <div id="pos"></div>
  <div class="endmatter" id="endmatter" hidden>
    <p>Keep the book offline:</p>
    <a class="download" id="dl-end" href="#" download>↓ Download the book</a>
    <p><a id="dl-txt" href="#" download>Also available as plain text (.txt)</a></p>
  </div>
</div>
<footer id="footer"></footer>
<script>
const DATA = %%DATA%%;
const main = document.getElementById('main');
const posEl = document.getElementById('pos');
const prevBtn = document.getElementById('prev');
const nextBtn = document.getElementById('next');
const sel = document.getElementById('chapter');
const endEl = document.getElementById('endmatter');
const POSKEY = 'reader-pos-' + DATA.slug;
document.getElementById('subtitle').textContent = DATA.subtitle;
for (const id of ['dl-top', 'dl-end']) {
  const a = document.getElementById(id);
  a.href = DATA.slug + '.md';
}
document.getElementById('dl-txt').href = DATA.slug + '.txt';
document.getElementById('footer').innerHTML =
  'Generated by survey-to-book from a structured survey: ' + DATA.pages +
  ' pages, ' + DATA.words.toLocaleString() + ' words, produced locally and ' +
  'offline (' + DATA.model + '). The respondent is a fictional ' +
  'demonstration persona; see the front matter. ' +
  '<a href="../index.html">Back to the library</a> · ' +
  '<a href="https://github.com/Frozen-In-Flames/survey-to-book">Source repository</a>';
const opt0 = document.createElement('option');
opt0.value = 0; opt0.textContent = 'Front matter';
sel.appendChild(opt0);
for (const ch of DATA.chapters) {
  const o = document.createElement('option');
  o.value = ch.first; o.textContent = ch.name;
  sel.appendChild(o);
}
const optEnd = document.createElement('option');
optEnd.value = DATA.screens.length - 1; optEnd.textContent = 'Colophon';
sel.appendChild(optEnd);
let i = 0;
try { i = Math.min(parseInt(localStorage.getItem(POSKEY) || '0', 10) || 0,
                   DATA.screens.length - 1); } catch (e) { i = 0; }
function render() {
  const s = DATA.screens[i];
  let head = '';
  if (s.kind === 'page') {
    head = '<h2>' + s.chapter + '</h2><h3 class="pagelabel">' + s.label +
           '</h3>';
  } else {
    head = '<h2>' + s.label + '</h2>';
  }
  main.innerHTML = head + s.html;
  const pages = DATA.screens.filter(x => x.kind === 'page').length;
  posEl.textContent = s.kind === 'page'
    ? s.label + ' of ' + pages + ' · ' + s.chapter
    : s.label;
  prevBtn.disabled = i === 0;
  nextBtn.disabled = i === DATA.screens.length - 1;
  endEl.hidden = !(i === 0 || i === DATA.screens.length - 1);
  let v = 0;
  for (const o of sel.options) if (parseInt(o.value, 10) <= i) v = o.value;
  sel.value = v;
  document.getElementById('progress').style.width =
    (100 * i / (DATA.screens.length - 1)) + '%';
  try { localStorage.setItem(POSKEY, String(i)); } catch (e) {}
  window.scrollTo(0, 0);
}
prevBtn.onclick = () => { if (i > 0) { i--; render(); } };
nextBtn.onclick = () => { if (i < DATA.screens.length - 1) { i++; render(); } };
sel.onchange = () => { i = parseInt(sel.value, 10); render(); };
document.addEventListener('keydown', e => {
  if (e.key === 'ArrowLeft') prevBtn.onclick();
  if (e.key === 'ArrowRight') nextBtn.onclick();
});
render();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    docs = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs"
    build(docs if docs.is_absolute() else ROOT / docs)
