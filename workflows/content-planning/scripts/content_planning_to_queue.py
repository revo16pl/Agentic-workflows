#!/usr/bin/env python3
"""Publish approved backlog topics to RUN_QUEUE file."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


QUEUE_HEADERS = [
    "queue_row_id",
    "topic_id",
    "company",
    "topic_cluster_name",
    "article_title_working",
    "primary_keyword",
    "target_length_words",
    "intent",
    "target_service_url",
    "cta_type",
    "workflow_b_ready",
    "reason_if_no",
    "source_sprint",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Move approved topics to run_queue.csv")
    parser.add_argument("--sprint", type=Path, required=True, help="Planning sprint path")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing queue rows from this sprint")
    return parser.parse_args()


def load_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return [dict(row) for row in csv.DictReader(fh)]


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=QUEUE_HEADERS)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in QUEUE_HEADERS})


def is_ready(row: dict[str, str]) -> tuple[str, str]:
    secondary = [x.strip() for x in row.get("secondary_keywords", "").split("|") if x.strip()]
    required = [
        row.get("topic_id", "").strip(),
        row.get("company", "").strip(),
        row.get("article_title_working", "").strip(),
        row.get("primary_keyword", "").strip(),
        row.get("intent", "").strip(),
        row.get("target_service_url", "").strip(),
        row.get("cta_type", "").strip(),
    ]
    if not all(required):
        return "no", "missing required topic/intent/service/cta fields"
    if len(secondary) < 8:
        return "no", "secondary_keywords < 8"
    return "yes", ""


def target_word_count(row: dict[str, str]) -> str:
    try:
        low = int(float(row.get("recommended_length_min", "0") or 0))
        high = int(float(row.get("recommended_length_max", "0") or 0))
    except ValueError:
        return "1600"
    if low > 0 and high > 0 and high >= low:
        return str((low + high) // 2)
    return "1600"


def main() -> int:
    args = parse_args()
    sprint = args.sprint.resolve()

    backlog_path = sprint / "content_plan_backlog.csv"
    gate_path = sprint / "planning_gate.json"
    queue_path = sprint / "run_queue.csv"

    if not backlog_path.exists():
        print(f"ERROR: missing backlog file: {backlog_path}")
        return 1
    if not gate_path.exists():
        print(f"ERROR: missing planning_gate.json: {gate_path}")
        return 1

    gate = json.loads(gate_path.read_text(encoding="utf-8"))
    if not bool(gate.get("planning_hard_block_pass", False)):
        print("ERROR: planning_hard_block_pass is FAIL. Queue publication blocked.")
        return 1

    backlog = [row for row in load_csv(backlog_path) if row.get("status", "").strip().lower() == "approved"]
    if not backlog:
        print("ERROR: no approved rows in content_plan_backlog.csv")
        return 1

    existing = load_csv(queue_path)
    if args.overwrite:
        existing = [row for row in existing if row.get("source_sprint", "") != sprint.name]

    rows_to_add: list[dict[str, str]] = []
    offset = len(existing)
    for idx, row in enumerate(backlog, start=1):
        ready, reason = is_ready(row)
        rows_to_add.append(
            {
                "queue_row_id": f"rq-{offset + idx:04d}",
                "topic_id": row.get("topic_id", "").strip(),
                "company": row.get("company", "").strip(),
                "topic_cluster_name": row.get("topic_cluster_name", "").strip(),
                "article_title_working": row.get("article_title_working", "").strip(),
                "primary_keyword": row.get("primary_keyword", "").strip(),
                "target_length_words": target_word_count(row),
                "intent": row.get("intent", "").strip(),
                "target_service_url": row.get("target_service_url", "").strip(),
                "cta_type": row.get("cta_type", "").strip(),
                "workflow_b_ready": ready,
                "reason_if_no": reason,
                "source_sprint": sprint.name,
            }
        )

    final_rows = [*existing, *rows_to_add]
    write_csv(queue_path, final_rows)

    print(
        json.dumps(
            {
                "ok": True,
                "queue_path": str(queue_path),
                "rows_added": len(rows_to_add),
                "ready_rows": sum(1 for row in rows_to_add if row["workflow_b_ready"] == "yes"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
