"""Beat-connection measurement: causation and contrast vs
sequence.

The craft standard (set by the author, 2026-11-27): a story's
beats connect by causation and contrast -- therefore, but,
yet, however, so -- never by flat sequence alone, the "and
then" chain that makes a page a list instead of a story. The
instruction half of the standard lives in the generation
prompt (engine/generate.py, every genre); this module is the
measurement half, part of the standard audit set reported for
every book.

The metric counts, across a finished book:

* **chain markers**: occurrences of "and then", the flat
  sequence joiner the standard prohibits as a chain;
* **causal/contrast connectors**: occurrences of therefore,
  but, yet, however, thus, hence, consequently, because, and
  "so" in its causal use -- sentence-initial ("So we left.")
  or after a comma ("It rained, so we left.") -- the bare
  word's intensifier use ("so tired") is not a connector and
  is not counted.

The headline quantities are the two totals and their ratio:
chain markers per causal/contrast connector. The standard is
an instruction and a measurement, not a gate: no page is
regenerated on this count, and the numbers are reported as
they fall, like the truncation count.
"""

from __future__ import annotations

import re

_CHAIN_RE = re.compile(r"\band then\b", re.IGNORECASE)
_CONNECTORS = (
    "therefore", "but", "yet", "however", "thus", "hence",
    "consequently", "because",
)
_CONNECTOR_RE = re.compile(
    r"\b(?:" + "|".join(_CONNECTORS) + r")\b", re.IGNORECASE)
_SO_CAUSAL_RE = re.compile(
    r"(?:^|[.!?]\s+)so\b|,\s+so\b", re.IGNORECASE | re.MULTILINE)


def count_connectors(text: str) -> dict:
    """Count chain markers and causal/contrast connectors in
    one page's text."""
    return {
        "chain_markers": len(_CHAIN_RE.findall(text)),
        "causal_contrast": (len(_CONNECTOR_RE.findall(text))
                            + len(_SO_CAUSAL_RE.findall(text))),
    }


def check_connectors(pages: list[dict]) -> dict:
    """Measure beat connection across a finished book.

    ``pages`` is an ordered list of dicts with ``index``,
    ``question_id`` and ``text``, as in the duplication check.
    """
    per_page = []
    chain = 0
    causal = 0
    for page in pages:
        counts = count_connectors(page["text"])
        chain += counts["chain_markers"]
        causal += counts["causal_contrast"]
        per_page.append({
            "page_index": page["index"],
            "question_id": page["question_id"],
            "chain_markers": counts["chain_markers"],
            "causal_contrast": counts["causal_contrast"],
        })
    return {
        "chain_markers": chain,
        "causal_contrast_connectors": causal,
        "chain_per_connector": (chain / causal) if causal else None,
        "pages_with_chain_markers": sum(
            1 for p in per_page if p["chain_markers"]),
        "per_page": per_page,
    }
