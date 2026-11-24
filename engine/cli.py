"""Command-line interface for the survey-to-book engine.

Usage:

    python -m engine.cli validate --pack packs/memoir.json
    python -m engine.cli build --pack packs/memoir.json \
        --answers demo/memoir-demo-answers.json \
        --model llama --out books/memoir-first-book \
        --title "The Porch Light" --persona-note "..."

``--model stub`` runs the deterministic test double (no model file
needed); ``--model llama`` uses a local llama.cpp server, which must
already be running on the loopback address given by ``--llama-url``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .export import export_markdown
from .generate import BookBuilder
from .model import LlamaServerModel, StubModel
from .pack import PackError, load_pack


def _load_answers(path: str) -> dict[str, str]:
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if isinstance(data, dict) and "answers" in data:
        return data["answers"]
    return data


def cmd_validate(args: argparse.Namespace) -> int:
    try:
        pack = load_pack(args.pack)
    except PackError as exc:
        print(exc)
        return 1
    print(f"pack OK: genre={pack['genre']} version={pack['version']} "
          f"chapters={len(pack['chapters'])} "
          f"questions={len(pack['questions'])}")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    try:
        pack = load_pack(args.pack)
    except PackError as exc:
        print(exc)
        return 1
    answers = _load_answers(args.answers)
    known = {q["id"] for q in pack["questions"]}
    unknown = set(answers) - known
    if unknown:
        print(f"answers reference unknown questions: {sorted(unknown)}")
        return 1

    if args.model == "stub":
        model = StubModel()
    else:
        model = LlamaServerModel(
            base_url=args.llama_url, model_label=args.model_label)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    builder = BookBuilder(pack, answers, model, out_dir / "state.json")
    report = builder.build()
    with open(out_dir / "report.json", "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=1)

    meta = {
        "title": args.title,
        "subtitle": args.subtitle,
        "provenance": args.persona_note,
        "colophon": args.colophon,
    }
    manuscript = export_markdown(pack, builder.state, report, meta)
    book_path = out_dir / "manuscript.md"
    with open(book_path, "w", encoding="utf-8") as fh:
        fh.write(manuscript)
    print(json.dumps({
        "pages_built": report["pages_built"],
        "total_words": report["total_words"],
        "skipped_empty": report["skipped_empty"],
        "continuity_issues": len(report["continuity_issues"]),
        "pages_sharing_sentence_with_previous":
            report["duplication"]["pages_sharing_sentence_with_previous"],
        "manuscript": str(book_path),
    }, indent=1))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="survey-to-book")
    sub = parser.add_subparsers(dest="command", required=True)

    p_validate = sub.add_parser("validate")
    p_validate.add_argument("--pack", required=True)
    p_validate.set_defaults(func=cmd_validate)

    p_build = sub.add_parser("build")
    p_build.add_argument("--pack", required=True)
    p_build.add_argument("--answers", required=True)
    p_build.add_argument("--model", choices=("stub", "llama"),
                         default="llama")
    p_build.add_argument("--llama-url", default="http://127.0.0.1:8080")
    p_build.add_argument("--model-label",
                         default="Qwen2.5-3B-Instruct (Q4_K_M GGUF) "
                                 "via llama.cpp, local")
    p_build.add_argument("--out", required=True)
    p_build.add_argument("--title", required=True)
    p_build.add_argument("--subtitle", default="")
    p_build.add_argument("--persona-note", required=True)
    p_build.add_argument("--colophon", required=True)
    p_build.set_defaults(func=cmd_build)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
