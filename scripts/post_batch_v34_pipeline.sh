#!/usr/bin/env bash
# post_batch_v34_pipeline.sh
# Run after batch_v34_gpt5_family.jsonl is complete (243 records).
# Steps: embed → LME → model_d → paper update → compile → commit+push
set -euo pipefail
cd "$(dirname "$0")/.."
source .env.real_model 2>/dev/null || true

BATCH="batch_v34_gpt5_family"
REAL_EXP="results/real_experiments"
LOG="/tmp/post_batch_v34_pipeline.log"

echo "[pipeline] Starting post-batch v34 pipeline at $(date)" | tee "$LOG"

# Step 1: Count records
N=$(wc -l < "${REAL_EXP}/${BATCH}.jsonl" | tr -d ' ')
echo "[pipeline] batch_v34 records: $N" | tee -a "$LOG"
if [ "$N" -lt 200 ]; then
    echo "[pipeline] WARNING: batch_v34 only $N records (expected ~243). Proceeding anyway." | tee -a "$LOG"
fi

# Step 2: Compute embeddings for batch_v34
echo "[pipeline] Computing embeddings for ${BATCH}..." | tee -a "$LOG"
python3 scripts/compute_embedding_bias.py \
    --in "${REAL_EXP}/${BATCH}.jsonl" \
    --out "${REAL_EXP}/${BATCH}.emb.jsonl" 2>&1 | tee -a "$LOG"
echo "[pipeline] Embeddings done." | tee -a "$LOG"

# Step 3: Re-run LME on full dataset (now 48 batches)
echo "[pipeline] Running LME analysis..." | tee -a "$LOG"
python3 scripts/run_lme_analysis.py 2>&1 | tee -a "$LOG"
echo "[pipeline] LME done." | tee -a "$LOG"

# Step 4: Re-run model_d corrected
echo "[pipeline] Running model_d analysis..." | tee -a "$LOG"
python3 scripts/compute_model_d.py 2>&1 | tee -a "$LOG"
echo "[pipeline] model_d done." | tee -a "$LOG"

# Step 5: Compile paper
echo "[pipeline] Compiling paper..." | tee -a "$LOG"
cd paper
bash compile.sh 2>&1 | tee -a "$LOG"
cd ..
echo "[pipeline] Paper compiled." | tee -a "$LOG"

# Step 6: Commit and push
echo "[pipeline] Committing changes..." | tee -a "$LOG"
git add -A
git commit -m "feat: batch v34 gpt-5 base family (N=+${N}); rerun LME/model_d; paper update (48 batches)" \
    || echo "[pipeline] Nothing to commit."
git push origin HEAD 2>&1 | tee -a "$LOG"
echo "[pipeline] Push done." | tee -a "$LOG"

echo "[pipeline] All steps complete at $(date)" | tee -a "$LOG"
