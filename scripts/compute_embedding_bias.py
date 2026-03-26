#!/usr/bin/env python3
"""
Compute embedding-based regret bias using sentence-transformers.
Replaces the bag-of-words cosine metric with real semantic similarity.

Usage:
    python3 scripts/compute_embedding_bias.py --in results/real_experiments/batch_v1_pilot_openai.jsonl --out results/real_experiments/batch_v1_pilot_openai.emb.jsonl
    python3 scripts/compute_embedding_bias.py --all   # process all batches
"""

import argparse
import json
import pathlib
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "results" / "real_experiments"

BATCH_FILES = [
    "batch_v1_pilot_openai",
    "batch_v1_gemini_v2",
    "batch_v3_expand",
    "batch_v4_expand_gpt4o",
    "batch_v5_expand_both",
    "batch_v6_expand",
    "batch_v7_expand",
    "batch_v8_neutral_balance",
    "batch_v9_gpt35",
    "batch_gemini25flashlite",
    "batch_gpt54mini",
    "batch_gpt54nano",
    "batch_llama33_70b",
    "batch_llama4_scout",
    "batch_qwen3_32b",
    "batch_gemini25pro",
    "batch_gemini3pro",
    "batch_gpt41",
    "batch_gpt41mini",
    "batch_gpt4omini",
    "batch_gemini3flash",
    "batch_v10_neutral_expand",
    "batch_v11_neutral_balance2",
    "batch_v12_gemini3pro_cf",
    "batch_v13_openai_balance",
    "batch_v14_balance",
    "batch_v15_new_models",
    "batch_v16_oss_small",
    "batch_v17_groq_compound",
    "batch_v18_new_groq",
    "batch_v19_groq_fill",
    "batch_v20_safeguard",
    "batch_v21_gemini_new",
    "batch_v22_cf_fill",
    "batch_v23_new_openai",
    "batch_v24_fill_cells",
    "batch_v25_groq_compound_balance",
    "batch_v26_lowcount_fill",
]

# Regret prototype sentences (Korean)
REGRET_PROTOS = [
    "정말 후회스럽고 미안한 마음이 든다",
    "그때 다른 선택을 했더라면 좋았을 텐데",
    "아쉽고 자책하는 감정이 계속 남는다",
]

# Neutral prototype sentences (Korean)
NEUTRAL_PROTOS = [
    "오늘 날씨가 맑고 기온이 적당했다",
    "일상적인 하루가 평범하게 지나갔다",
    "특별한 감정 없이 평온하게 지냈다",
]


def load_model():
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    return model


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))


def compute_bias(model, text: str, regret_embs: np.ndarray, neutral_embs: np.ndarray) -> dict:
    """Compute embedding_regret_bias = mean_cos(text, regret_protos) - mean_cos(text, neutral_protos)."""
    if not text.strip():
        return {"embedding_regret_bias": 0.0, "embedding_regret_sim": 0.0, "embedding_neutral_sim": 0.0}

    text_emb = model.encode(text, normalize_embeddings=True)

    regret_sims = [cosine_sim(text_emb, r) for r in regret_embs]
    neutral_sims = [cosine_sim(text_emb, n) for n in neutral_embs]

    regret_mean = float(np.mean(regret_sims))
    neutral_mean = float(np.mean(neutral_sims))

    return {
        "embedding_regret_bias": round(regret_mean - neutral_mean, 6),
        "embedding_regret_sim": round(regret_mean, 6),
        "embedding_neutral_sim": round(neutral_mean, 6),
    }


def process_file(model, regret_embs, neutral_embs, in_path: pathlib.Path, out_path: pathlib.Path):
    lines = [l for l in in_path.read_text(encoding="utf-8", errors="replace").splitlines() if l.strip()]
    results = []
    for line in lines:
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        text = row.get("output") or row.get("text", "")
        bias = compute_bias(model, text, regret_embs, neutral_embs)
        row.update(bias)
        results.append(row)

    out_path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in results) + "\n",
        encoding="utf-8",
    )
    print(f"  {in_path.name} -> {out_path.name}: {len(results)} samples")
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", help="Input JSONL file")
    ap.add_argument("--out", help="Output JSONL file")
    ap.add_argument("--all", action="store_true", help="Process all batch files")
    args = ap.parse_args()

    print("Loading sentence-transformer model...")
    model = load_model()

    # Pre-encode prototypes
    regret_embs = model.encode(REGRET_PROTOS, normalize_embeddings=True)
    neutral_embs = model.encode(NEUTRAL_PROTOS, normalize_embeddings=True)

    if args.all:
        all_results = []
        for fname in BATCH_FILES:
            in_path = DATA_DIR / f"{fname}.jsonl"
            out_path = DATA_DIR / f"{fname}.emb.jsonl"
            if not in_path.exists():
                print(f"  SKIP {fname} (not found)")
                continue
            results = process_file(model, regret_embs, neutral_embs, in_path, out_path)
            all_results.extend(results)

        # Write combined per_sample_analyzed.jsonl with embedding bias
        combined_path = DATA_DIR / "per_sample_analyzed.jsonl"
        combined_path.write_text(
            "\n".join(json.dumps(r, ensure_ascii=False) for r in all_results) + "\n",
            encoding="utf-8",
        )
        print(f"\nCombined output: {combined_path} ({len(all_results)} samples)")

        # Print summary by condition
        from collections import defaultdict
        by_cond = defaultdict(list)
        for r in all_results:
            by_cond[r.get("condition", "?")].append(r["embedding_regret_bias"])
        print("\n=== Embedding Regret Bias by Condition ===")
        for cond in ["neutral", "deprivation", "counterfactual"]:
            vals = by_cond.get(cond, [])
            if vals:
                print(f"  {cond:16s}: mean={np.mean(vals):.4f}, sd={np.std(vals):.4f}, n={len(vals)}")
    else:
        if not args.inp or not args.out:
            ap.error("Provide --in and --out, or use --all")
        process_file(model, regret_embs, neutral_embs, pathlib.Path(args.inp), pathlib.Path(args.out))


if __name__ == "__main__":
    main()
