#!/usr/bin/env python3
"""Humanization QA gate: style checks + open-source detector ensemble."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from article_workflow_state import set_gate, set_many_gates
from article_workflow_validate import clean_markdown_for_language_checks
from humanization_detector import detector_checks
from humanization_style import parse_brief, style_checks, update_qa, write_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Humanization QA gate for article draft.")
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--input", default="article_draft_v2.md")
    parser.add_argument("--report", default="humanization_report.md")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--detector-models", default="")
    return parser.parse_args()


def resolve_models(raw: str) -> list[str]:
    if raw.strip():
        return [item.strip() for item in raw.split(",") if item.strip()]
    return [
        "openai-community/roberta-base-openai-detector",
        "Hello-SimpleAI/chatgpt-detector-roberta",
        "nbroad/openai-detector-base",
    ]


def main() -> int:
    args = parse_args()
    workspace = args.workspace.resolve()
    source = workspace / args.input
    if not workspace.exists() or not source.exists():
        print(f"ERROR: Missing workspace or input file: {workspace} / {source}", file=sys.stderr)
        return 1

    markdown = source.read_text(encoding="utf-8")
    style = style_checks(markdown, parse_brief(workspace / "article_brief.md"))
    detector = detector_checks(
        clean_markdown_for_language_checks(markdown),
        resolve_models(args.detector_models),
    )

    style_gates = dict(style["gates"])
    style_gates["rewrite_loop_pass"] = all(bool(v) for v in style_gates.values())
    detector_pass = bool(detector["detector_ensemble_pass"])
    gates = {**style_gates, "detector_ensemble_pass": detector_pass}
    payload = {
        "ok": all(bool(v) for v in style_gates.values()),
        "gates": gates,
        "style_metrics": style["metrics"],
        "detector": detector,
        "report_path": str((workspace / args.report).resolve()),
    }

    update_qa(workspace / "qa_report.md", gates)
    set_many_gates(
        workspace=workspace,
        gates=style_gates,
        source="check_humanization.py",
        severity="hard",
    )
    set_gate(
        workspace=workspace,
        name="detector_ensemble_pass",
        passed=detector_pass,
        source="check_humanization.py",
        severity="advisory",
        details=(
            f"mean_ai_risk={detector.get('mean_ai_risk', 1.0):.4f}, "
            f"max_single_ai_risk={detector.get('max_single_ai_risk', 1.0):.4f}"
        ),
    )
    write_report(workspace / args.report, payload)

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"Humanization report: {workspace / args.report}")
        for key, value in gates.items():
            print(f"- {key}: {'PASS' if value else 'FAIL'}")
        print("Humanization hard gate:", "PASS" if payload["ok"] else "FAIL")
        print(f"- detector_ensemble_pass (advisory): {'PASS' if detector_pass else 'FAIL'}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
