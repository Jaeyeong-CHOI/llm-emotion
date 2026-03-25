#!/usr/bin/env python3
"""
Compute inter-rater reliability (Cohen κ) between human annotator and GPT-4o.
Uses annotation_subsample_50.json; GPT-4o acts as a second rater for regret binary.
"""

import json
import os
import pathlib
import sys
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
ANNOTATION_PATH = ROOT / "results" / "real_experiments" / "annotation_subsample_50.json"
OUTPUT_PATH = ROOT / "results" / "real_experiments" / "interrater_results.json"


def call_gpt4o_rater(text: str, api_key: str) -> int:
    """Ask GPT-4o to rate whether text expresses regret-like language (0 or 1)."""
    prompt = (
        "You are annotating whether this LLM-generated text expresses regret-like language.\n"
        "Score 1 if the text contains counterfactual thinking, self-blame, regret words, or loss-focused content. "
        "Score 0 otherwise.\n"
        f"Text: {text}\n"
        "Answer with just: 0 or 1"
    )
    payload = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "max_tokens": 5,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode())
            answer = result["choices"][0]["message"]["content"].strip()
            return int(answer)
        except Exception as e:
            if attempt < 2:
                time.sleep(2 ** attempt)
            else:
                print(f"  WARNING: GPT-4o call failed after 3 attempts: {e}", file=sys.stderr)
                return -1


def main():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set. Run: source .env.real_model", file=sys.stderr)
        sys.exit(1)

    samples = json.loads(ANNOTATION_PATH.read_text(encoding="utf-8"))
    print(f"Loaded {len(samples)} annotated samples")

    # Derive human binary label from annotation_regret_intensity
    human_labels = []
    gpt4o_labels = []
    details = []

    for s in samples:
        human_binary = 1 if s["annotation_regret_intensity"] > 0 else 0
        human_labels.append(human_binary)

        text = s["output_first200"]
        gpt4o_score = call_gpt4o_rater(text, api_key)
        gpt4o_labels.append(gpt4o_score)

        details.append({
            "sample_id": s["sample_id"],
            "condition": s["condition"],
            "human_label": human_binary,
            "gpt4o_label": gpt4o_score,
            "human_intensity": s["annotation_regret_intensity"],
        })
        print(f"  Sample {s['sample_id']:2d} ({s['condition']:15s}): human={human_binary}, gpt4o={gpt4o_score}")

    # Filter out any failed calls
    valid = [(h, g) for h, g in zip(human_labels, gpt4o_labels) if g >= 0]
    if not valid:
        print("ERROR: No valid GPT-4o ratings obtained", file=sys.stderr)
        sys.exit(1)

    h_valid, g_valid = zip(*valid)

    from sklearn.metrics import cohen_kappa_score, confusion_matrix, accuracy_score

    kappa = cohen_kappa_score(h_valid, g_valid)
    acc = accuracy_score(h_valid, g_valid)
    cm = confusion_matrix(h_valid, g_valid).tolist()

    result = {
        "n_total": len(samples),
        "n_valid": len(valid),
        "cohen_kappa": round(kappa, 4),
        "accuracy": round(acc, 4),
        "confusion_matrix": cm,
        "labels": {"rows": "human", "cols": "gpt4o", "classes": [0, 1]},
        "details": details,
    }

    OUTPUT_PATH.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nResults saved to {OUTPUT_PATH}")
    print(f"Cohen's κ = {kappa:.4f}")
    print(f"Accuracy  = {acc:.4f}")
    print(f"Confusion matrix (human × gpt4o):\n{cm}")


if __name__ == "__main__":
    main()
