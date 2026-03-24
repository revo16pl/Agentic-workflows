#!/usr/bin/env python3
"""Shared state helpers for Agentic Articles workflow JSON artifacts."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


QUALITY_GATE_FILENAME = "quality_gate.json"
RESEARCH_EVIDENCE_FILENAME = "research_evidence_manifest.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def quality_gate_path(workspace: Path) -> Path:
    return workspace / QUALITY_GATE_FILENAME


def research_evidence_path(workspace: Path) -> Path:
    return workspace / RESEARCH_EVIDENCE_FILENAME


def load_json_or_default(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return dict(default)
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass
    return dict(default)


def default_quality_gate() -> dict[str, Any]:
    return {
        "version": "3.0",
        "updated_at": now_iso(),
        "overall_pass": False,
        "hard_gates": [],
        "gates": {},
    }


def ensure_quality_gate(workspace: Path) -> dict[str, Any]:
    payload = load_json_or_default(quality_gate_path(workspace), default_quality_gate())
    payload.setdefault("version", "3.0")
    payload.setdefault("updated_at", now_iso())
    payload.setdefault("overall_pass", False)
    payload.setdefault("hard_gates", [])
    payload.setdefault("gates", {})
    return payload


def write_quality_gate(workspace: Path, payload: dict[str, Any]) -> Path:
    payload["updated_at"] = now_iso()
    if "hard_gates" in payload and isinstance(payload["hard_gates"], list):
        hard = payload["hard_gates"]
        gates = payload.get("gates", {})
        payload["overall_pass"] = all(
            str((gates.get(name, {}) or {}).get("status", "")).upper() == "PASS" for name in hard
        )
    path = quality_gate_path(workspace)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def set_gate(
    workspace: Path,
    *,
    name: str,
    passed: bool,
    source: str,
    severity: str = "hard",
    details: str = "",
) -> dict[str, Any]:
    payload = ensure_quality_gate(workspace)
    gates = payload.setdefault("gates", {})
    gates[name] = {
        "status": "PASS" if passed else "FAIL",
        "severity": severity,
        "source": source,
        "details": details,
        "updated_at": now_iso(),
    }

    hard_gates = payload.setdefault("hard_gates", [])
    if severity == "hard" and name not in hard_gates:
        hard_gates.append(name)
    if severity != "hard" and name in hard_gates:
        hard_gates.remove(name)
    write_quality_gate(workspace, payload)
    return payload


def set_many_gates(
    workspace: Path,
    *,
    gates: dict[str, bool],
    source: str,
    severity: str = "hard",
    details: dict[str, str] | None = None,
) -> dict[str, Any]:
    payload = ensure_quality_gate(workspace)
    data = payload.setdefault("gates", {})
    hard_gates = payload.setdefault("hard_gates", [])
    details = details or {}

    for name, passed in gates.items():
        data[name] = {
            "status": "PASS" if passed else "FAIL",
            "severity": severity,
            "source": source,
            "details": details.get(name, ""),
            "updated_at": now_iso(),
        }
        if severity == "hard" and name not in hard_gates:
            hard_gates.append(name)
        if severity != "hard" and name in hard_gates:
            hard_gates.remove(name)

    write_quality_gate(workspace, payload)
    return payload


def set_hard_gate_set(workspace: Path, hard_gate_names: list[str]) -> dict[str, Any]:
    payload = ensure_quality_gate(workspace)
    payload["hard_gates"] = list(dict.fromkeys(hard_gate_names))
    write_quality_gate(workspace, payload)
    return payload


def recompute_hard_block_gate(workspace: Path) -> dict[str, Any]:
    payload = ensure_quality_gate(workspace)
    gates = payload.get("gates", {})
    hard = payload.get("hard_gates", [])
    hard_without_self = [name for name in hard if name != "hard_block_export_pass"]
    hard_ok = all(str((gates.get(name, {}) or {}).get("status", "")).upper() == "PASS" for name in hard_without_self)
    gates["hard_block_export_pass"] = {
        "status": "PASS" if hard_ok else "FAIL",
        "severity": "hard",
        "source": "article_workflow_state",
        "details": "Derived from all hard gates.",
        "updated_at": now_iso(),
    }
    if "hard_block_export_pass" not in hard:
        hard.append("hard_block_export_pass")
    payload["hard_gates"] = list(dict.fromkeys(hard))
    write_quality_gate(workspace, payload)
    return payload
