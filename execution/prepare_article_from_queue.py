#!/usr/bin/env python3
"""Create article workspace from approved RUN_QUEUE row."""

from __future__ import annotations

import argparse
import csv
import re
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PLANNING_ROOT = PROJECT_ROOT / "Agentic Articles" / "planning"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare article workspace from run_queue row.")
    parser.add_argument("--queue-row-id", required=True, help="Queue row id, e.g. rq-0001")
    parser.add_argument("--queue-file", type=Path, default=None, help="Optional explicit run_queue.csv path")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def find_queue_file(explicit: Path | None, queue_row_id: str) -> Path:
    if explicit:
        return explicit.resolve()
    candidates = sorted(PLANNING_ROOT.glob("*_sprint/run_queue.csv"), reverse=True)
    for path in candidates:
        with path.open("r", encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                if row.get("queue_row_id", "").strip() == queue_row_id:
                    return path.resolve()
    raise FileNotFoundError(f"Queue row {queue_row_id} not found in planning sprints.")


def load_row(queue_file: Path, queue_row_id: str) -> dict[str, str]:
    with queue_file.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            if row.get("queue_row_id", "").strip() == queue_row_id:
                return {k: str(v).strip() for k, v in row.items()}
    raise ValueError(f"queue_row_id not found: {queue_row_id}")


def update_brief(brief_path: Path, row: dict[str, str]) -> None:
    text = brief_path.read_text(encoding="utf-8")
    match = re.search(r"```yaml\s*(.*?)```", text, flags=re.S)
    if not match:
        return

    yaml_text = match.group(1)

    replacements = {
        "topic": row.get("article_title_working") or row.get("primary_keyword", ""),
        "company": row.get("company", ""),
        "target_intent": row.get("intent", "informational"),
        "target_length_words": row.get("target_length_words", "1600"),
        "word_count_min": str(max(900, int(float(row.get("target_length_words", "1600") or 1600)) - 300)),
        "word_count_max": str(max(1300, int(float(row.get("target_length_words", "1600") or 1600)) + 500)),
        "cta_type": row.get("cta_type", "consultation"),
    }

    for key, value in replacements.items():
        if re.search(rf"^{re.escape(key)}:\s*.*$", yaml_text, flags=re.M):
            yaml_text = re.sub(
                rf"^{re.escape(key)}:\s*.*$",
                f'{key}: "{value}"' if key in {"topic", "company", "target_intent", "cta_type"} else f"{key}: {value}",
                yaml_text,
                flags=re.M,
            )

    text = text[: match.start(1)] + yaml_text + text[match.end(1) :]

    service_url = row.get("target_service_url", "")
    if service_url:
        text = re.sub(
            r"(Priority service pages do podlinkowania \(1-3\):\n)",
            r"\1- " + service_url + "\n",
            text,
            count=1,
        )

    brief_path.write_text(text, encoding="utf-8")


def extract_workspace(stdout: str) -> Path:
    match = re.search(r"Workspace ready:\s*(.+)", stdout)
    if not match:
        raise RuntimeError("Cannot parse workspace path from article_workflow_init output.")
    return Path(match.group(1).strip()).resolve()


def main() -> int:
    args = parse_args()
    queue_file = find_queue_file(args.queue_file, args.queue_row_id)
    row = load_row(queue_file, args.queue_row_id)

    if row.get("workflow_b_ready", "").lower() != "yes":
        print(f"ERROR: Queue row {args.queue_row_id} is not ready: {row.get('reason_if_no', 'unknown reason')}")
        return 1

    topic = row.get("article_title_working") or row.get("primary_keyword", "")
    company = row.get("company", "")
    if not topic or not company:
        print("ERROR: queue row missing topic/company")
        return 1

    cmd = [
        "python3",
        str(PROJECT_ROOT / "execution" / "article_workflow_init.py"),
        "--topic",
        topic,
        "--company",
        company,
        "--planning-sprint-id",
        row.get("source_sprint", ""),
        "--planning-topic-id",
        row.get("topic_id", ""),
        "--planning-row-status",
        "approved",
        "--planning-queue-path",
        str(queue_file),
    ]

    if args.dry_run:
        print("DRY RUN:", " ".join(cmd))
        return 0

    run = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True)
    if run.returncode != 0:
        print(run.stdout)
        print(run.stderr)
        return run.returncode

    workspace = extract_workspace(run.stdout)
    brief_path = workspace / "article_brief.md"
    if brief_path.exists():
        update_brief(brief_path, row)

    print(f"Queue row: {args.queue_row_id}")
    print(f"Workspace ready: {workspace}")
    print(f"Brief prefilled from queue row: {brief_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
