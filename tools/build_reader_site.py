#!/usr/bin/env python3
"""Build the GitHub Pages reader site for a finished book.

Reads a book's manuscript.md and report.json and emits a self-contained
reader page under docs/:

- docs/index.html          the reader (no external requests; the full
                           book text is embedded at build time)
- docs/<slug>.md           verbatim manuscript copy, for download
- docs/<slug>.txt          plain-text rendering, for download
- docs/.nojekyll           keeps Pages from running Jekyll over the tree

Usage: python3 tools/build_reader_site.py [book-dir] [slug]
Defaults: books/memoir-first-book, the-porch-light.
"""

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


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


def build(book_dir: Path, slug: str):
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

    docs = ROOT / "docs"
    docs.mkdir(exist_ok=True)
    (docs / ".nojekyll").write_text("", encoding="utf-8")
    (docs / (slug + ".md")).write_text(manuscript, encoding="utf-8")

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
    (docs / (slug + ".txt")).write_text("\n".join(txt) + "\n", encoding="utf-8")

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
    page = TEMPLATE.replace("%%DATA%%", json.dumps(data, ensure_ascii=False)
                            .replace("</", "<\\/"))
    page = page.replace("%%TITLE%%", html.escape(title))
    (docs / "index.html").write_text(page, encoding="utf-8")
    print(f"screens: {len(screens)} ({len(chapters)} chapters), "
          f"index.html: {(docs / 'index.html').stat().st_size} bytes")


TEMPLATE = r"""<!DOCTYPE html>
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
  .download { display:inline-block; background:var(--accent); color:#fff;
              font-family: system-ui, sans-serif; font-weight:700;
              font-size:1.05rem; text-decoration:none;
              padding:.8rem 1.4rem; border-radius:.5rem; }
  .download:active, .download:hover { background:#5f3410; }
  .download.alt { background:transparent; color:var(--accent);
                  border:2px solid var(--accent); padding:.55rem 1rem;
                  font-size:.9rem; }
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
try { i = Math.min(parseInt(localStorage.getItem('reader-pos') || '0', 10) || 0,
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
  try { localStorage.setItem('reader-pos', String(i)); } catch (e) {}
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
    book = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "books/memoir-first-book"
    slug = sys.argv[2] if len(sys.argv) > 2 else "the-porch-light"
    build(book if book.is_absolute() else ROOT / book, slug)
