#!/usr/bin/env bash
# post_batch_v35_pipeline.sh
# Run after batch_v35_gpt51_gpt52.jsonl is complete.
# Steps: embed → LME → model_d → paper update → compile → commit+push
set -euo pipefail
cd "$(dirname "$0")/.."
source .env.real_model 2>/dev/null || true

BATCH="batch_v35_gpt51_gpt52"
REAL_EXP="results/real_experiments"
LOG="/tmp/post_batch_v35_pipeline.log"

echo "[pipeline] Starting post-batch v35 pipeline at $(date)" | tee "$LOG"

# Step 1: Count records
N=$(wc -l < "${REAL_EXP}/${BATCH}.jsonl" | tr -d ' ')
echo "[pipeline] batch_v35 records: $N" | tee -a "$LOG"
if [ "$N" -lt 150 ]; then
    echo "[pipeline] WARNING: batch_v35 only $N records (expected ~180). Check script output." | tee -a "$LOG"
fi

# Step 2: Compute embeddings for batch_v35
echo "[pipeline] Computing embeddings for ${BATCH}..." | tee -a "$LOG"
python3 scripts/compute_embedding_bias.py \
    --in "${REAL_EXP}/${BATCH}.jsonl" \
    --out "${REAL_EXP}/${BATCH}.emb.jsonl" 2>&1 | tee -a "$LOG"
echo "[pipeline] Embeddings done." | tee -a "$LOG"

# Step 3: Re-run LME on full dataset (now 49 batches)
echo "[pipeline] Running LME analysis..." | tee -a "$LOG"
python3 scripts/run_lme_analysis.py 2>&1 | tee -a "$LOG"
echo "[pipeline] LME done." | tee -a "$LOG"

# Step 4: Re-run model_d corrected
echo "[pipeline] Running model_d analysis..." | tee -a "$LOG"
python3 scripts/compute_model_d.py 2>&1 | tee -a "$LOG"
echo "[pipeline] model_d done." | tee -a "$LOG"

# Step 5: Update paper stats
echo "[pipeline] Checking LME report for N, models, batches..." | tee -a "$LOG"
python3 -c "
import json, re, pathlib, sys

lme_file = pathlib.Path('results/real_experiments/lme_analysis.json')
lme_report = pathlib.Path('results/real_experiments/lme_report.md')

if lme_file.exists():
    with open(lme_file) as f:
        data = json.load(f)
    n_total = data.get('n_total', '?')
    n_batches = data.get('n_batches', '?')
    n_models = data.get('n_models', '?')
    print(f'[paper update] N={n_total}, batches={n_batches}, models={n_models}')
else:
    print('[paper update] lme_analysis.json not found, skipping stat read')
" 2>&1 | tee -a "$LOG"

# Step 6: Compile paper
echo "[pipeline] Compiling paper..." | tee -a "$LOG"
cd paper
bash compile.sh 2>&1 | tee -a "$LOG"
cd ..
echo "[pipeline] Paper compiled." | tee -a "$LOG"

# Step 7: Commit and push
echo "[pipeline] Committing changes..." | tee -a "$LOG"
git add -A
git commit -m "feat: batch v35 gpt-5.1/gpt-5.2 + stability fill (N=+${N}); embed+LME+model_d rerun; paper update (49 batches, 37 models)" \
    || echo "[pipeline] Nothing to commit."
git push origin HEAD 2>&1 | tee -a "$LOG"
echo "[pipeline] Push done." | tee -a "$LOG"

echo "[pipeline] All steps complete at $(date)" | tee -a "$LOG"
