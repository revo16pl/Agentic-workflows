#!/usr/bin/env python3
"""Pre-trained ML fluency signal for Polish text (no custom training)."""

from __future__ import annotations

import argparse
import json
import math
import os
import random
from pathlib import Path

from article_workflow_state import set_gate
from article_workflow_validate import clean_markdown_for_language_checks


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Polish fluency ML gate.")
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--input", default="article_draft_v2.md")
    parser.add_argument("--report", default="polish_fluency_ml_report.md")
    parser.add_argument(
        "--model",
        default=os.getenv("POLISH_FLUENCY_MODEL_ID", "dkleczek/bert-base-polish-cased-v1"),
        help="Hugging Face masked language model id.",
    )
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def pseudo_perplexity(text: str, model_id: str) -> tuple[float, int]:
    import torch
    from transformers import AutoModelForMaskedLM, AutoTokenizer
    from transformers.utils import logging as hf_logging

    os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
    hf_logging.disable_progress_bar()
    hf_logging.set_verbosity_error()

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForMaskedLM.from_pretrained(model_id)
    model.eval()

    encoded = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    input_ids = encoded["input_ids"][0]
    attention = encoded["attention_mask"][0]
    valid_positions = []
    special_ids = set(tokenizer.all_special_ids)
    for idx, token_id in enumerate(input_ids.tolist()):
        if attention[idx].item() == 0:
            continue
        if token_id in special_ids:
            continue
        valid_positions.append(idx)

    if len(valid_positions) < 8:
        raise RuntimeError("Text too short for ML fluency evaluation.")

    max_samples = int(os.getenv("POLISH_FLUENCY_MAX_TOKEN_SAMPLES", "220"))
    if len(valid_positions) > max_samples:
        random.seed(13)
        valid_positions = sorted(random.sample(valid_positions, k=max_samples))

    losses: list[float] = []
    with torch.no_grad():
        for pos in valid_positions:
            masked = input_ids.clone()
            original_id = masked[pos].item()
            masked[pos] = tokenizer.mask_token_id
            outputs = model(input_ids=masked.unsqueeze(0), attention_mask=attention.unsqueeze(0))
            logits = outputs.logits[0, pos]
            log_probs = torch.log_softmax(logits, dim=-1)
            losses.append(float(-log_probs[original_id].item()))

    mean_nll = sum(losses) / len(losses)
    ppl = float(math.exp(mean_nll))
    return ppl, len(losses)


def write_report(path: Path, payload: dict[str, object]) -> None:
    lines = [
        "# polish_fluency_ml_report.md",
        "",
        f"- model: {payload['model']}",
        f"- samples: {payload['samples']}",
        f"- pseudo_perplexity: {payload['pseudo_perplexity']:.4f}",
        f"- threshold: {payload['threshold']:.4f}",
        f"- polish_fluency_ml_pass: {'PASS' if payload['pass'] else 'FAIL'}",
    ]
    if payload.get("error"):
        lines.append(f"- error: {payload['error']}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    workspace = args.workspace.resolve()
    source = workspace / args.input
    if not workspace.exists() or not source.exists():
        print(f"ERROR: Missing workspace or source file: {workspace} / {source}")
        return 1

    threshold = float(os.getenv("POLISH_FLUENCY_MAX_PSEUDO_PERPLEXITY", "35.0"))
    text = clean_markdown_for_language_checks(source.read_text(encoding="utf-8"))
    payload: dict[str, object] = {
        "model": args.model,
        "samples": 0,
        "pseudo_perplexity": 999.0,
        "threshold": threshold,
        "pass": False,
        "error": "",
    }

    try:
        ppl, samples = pseudo_perplexity(text, args.model)
        passed = ppl <= threshold
        payload.update(
            {
                "samples": samples,
                "pseudo_perplexity": ppl,
                "pass": passed,
            }
        )
        set_gate(
            workspace,
            name="polish_fluency_ml_pass",
            passed=passed,
            source="check_polish_fluency_ml.py",
            severity="hard",
            details=f"ppl={ppl:.4f}, threshold={threshold:.4f}, model={args.model}, samples={samples}",
        )
    except Exception as exc:
        payload["error"] = str(exc)
        set_gate(
            workspace,
            name="polish_fluency_ml_pass",
            passed=False,
            source="check_polish_fluency_ml.py",
            severity="hard",
            details=f"ML fluency evaluation failed: {exc}",
        )

    report_path = workspace / args.report
    write_report(report_path, payload)
    payload["report_path"] = str(report_path.resolve())

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"ML fluency report: {report_path}")
        print(
            f"model={payload['model']}, ppl={float(payload['pseudo_perplexity']):.4f}, "
            f"threshold={threshold:.4f}, pass={'PASS' if payload['pass'] else 'FAIL'}"
        )
        if payload.get("error"):
            print(f"error={payload['error']}")
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
