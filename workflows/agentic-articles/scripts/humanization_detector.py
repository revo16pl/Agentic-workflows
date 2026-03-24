"""Open-source detector ensemble helpers for humanization QA."""
from __future__ import annotations

import os


def mean(values: list[float]) -> float:
    return (sum(values) / len(values)) if values else 0.0


def chunks(text: str, chunk_words: int) -> list[str]:
    words = text.split()
    if len(words) <= chunk_words:
        return [text]
    return [" ".join(words[i : i + chunk_words]) for i in range(0, len(words), chunk_words)]


def risk(label: str, score: float) -> float:
    lowered = label.lower()
    ai_labels = ["fake", "generated", "ai", "machine", "chatgpt", "gpt", "synthetic", "bot"]
    human_labels = ["real", "human"]
    if any(x in lowered for x in ai_labels):
        return score
    if any(x in lowered for x in human_labels):
        return 1.0 - score
    return 0.5


def detector_checks(text: str, model_ids: list[str]) -> dict[str, object]:
    max_ai = float(os.getenv("HUMAN_DETECTOR_MAX_AI_PROB", "0.58"))
    max_single = float(os.getenv("HUMAN_DETECTOR_MAX_SINGLE_AI_PROB", "0.70"))
    min_det = int(os.getenv("HUMAN_MIN_DETECTORS", "2"))
    allow_partial = os.getenv("HUMAN_ALLOW_PARTIAL_DETECTOR_SUCCESS", "false").lower() == "true"
    parts = chunks(text, int(os.getenv("HUMAN_DETECTOR_CHUNK_WORDS", "220")))
    out: list[dict[str, object]] = []
    errors: list[str] = []

    try:
        os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
        from transformers.utils import logging as hf_logging

        hf_logging.set_verbosity_error()
        hf_logging.disable_progress_bar()
        _ = torch.__version__
    except Exception as exc:
        return {
            "detector_ensemble_pass": False,
            "detectors_run": 0,
            "mean_ai_risk": 1.0,
            "max_single_ai_risk": 1.0,
            "max_ai_prob": max_ai,
            "max_single_ai_prob": max_single,
            "results": [],
            "errors": [f"Detector dependencies missing: {exc}"],
        }

    for model_id in [m.strip() for m in model_ids if m.strip()]:
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_id)
            model = AutoModelForSequenceClassification.from_pretrained(model_id)
            model.eval()
            chunk_risks: list[float] = []
            for part in parts:
                encoded = tokenizer(part, return_tensors="pt", truncation=True, max_length=512)
                with torch.no_grad():
                    logits = model(**encoded).logits
                    probs = torch.softmax(logits, dim=-1).detach().cpu().numpy()[0]
                idx = int(probs.argmax())
                label = str(model.config.id2label.get(idx, f"LABEL_{idx}"))
                chunk_risks.append(risk(label, float(probs[idx])))
            avg_risk = mean(chunk_risks)
            out.append({"model": model_id, "chunks": len(parts), "avg_ai_risk": avg_risk, "pass": avg_risk <= max_ai})
        except Exception as exc:
            errors.append(f"{model_id}: {exc}")

    detectors_run = len(out)
    mean_ai_risk = mean([float(x["avg_ai_risk"]) for x in out]) if out else 1.0
    max_single_risk = max([float(x["avg_ai_risk"]) for x in out], default=1.0)
    no_errors_needed = allow_partial or not errors
    pass_value = detectors_run >= min_det and no_errors_needed and mean_ai_risk <= max_ai and max_single_risk <= max_single
    return {
        "detector_ensemble_pass": pass_value,
        "detectors_run": detectors_run,
        "mean_ai_risk": mean_ai_risk,
        "max_single_ai_risk": max_single_risk,
        "max_ai_prob": max_ai,
        "max_single_ai_prob": max_single,
        "results": out,
        "errors": errors,
    }
