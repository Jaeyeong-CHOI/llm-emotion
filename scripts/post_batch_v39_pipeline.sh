#!/usr/bin/env bash
# post_batch_v39_pipeline.sh
# Run after batch_v39_new_models.jsonl is complete.
# Steps: embed → LME → model_d → paper update → compile → commit+push
set -euo pipefail
cd "$(dirname "$0")/.."
source .env.real_model 2>/dev/null || true

BATCH="batch_v39_new_models"
REAL_EXP="results/real_experiments"
LOG="/tmp/post_batch_v39_pipeline.log"

echo "[pipeline] Starting post-batch v39 pipeline at $(date)" | tee "$LOG"

# Step 1: Count records
N=$(wc -l < "${REAL_EXP}/${BATCH}.jsonl" | tr -d ' ')
echo "[pipeline] batch_v39 records: $N" | tee -a "$LOG"
if [ "$N" -lt 100 ]; then
    echo "[pipeline] WARNING: batch_v39 only $N records (expected ~162). Check script output." | tee -a "$LOG"
fi

# Step 2: Compute embeddings for batch_v39
echo "[pipeline] Computing embeddings for ${BATCH}..." | tee -a "$LOG"
python3 scripts/compute_embedding_bias.py \
    --in "${REAL_EXP}/${BATCH}.jsonl" \
    --out "${REAL_EXP}/${BATCH}.emb.jsonl" 2>&1 | tee -a "$LOG"
echo "[pipeline] Embeddings done." | tee -a "$LOG"

# Step 3: Re-run LME on full dataset
echo "[pipeline] Running LME analysis..." | tee -a "$LOG"
python3 scripts/run_lme_analysis.py 2>&1 | tee -a "$LOG"
echo "[pipeline] LME done." | tee -a "$LOG"

# Step 4: Re-run model_d
echo "[pipeline] Running model_d analysis..." | tee -a "$LOG"
python3 scripts/compute_model_d.py 2>&1 | tee -a "$LOG"
echo "[pipeline] model_d done." | tee -a "$LOG"

# Step 5: Check updated LME stats
python3 -c "
import json, pathlib
lme_file = pathlib.Path('results/real_experiments/lme_analysis.json')
if lme_file.exists():
    data = json.load(open(lme_file))
    n_total = data.get('n_total', '?')
    n_batches = data.get('n_batches', '?')
    n_models = data.get('n_models', '?')
    print(f'[stats] N={n_total}, batches={n_batches}, models={n_models}')
else:
    print('[stats] lme_analysis.json not found')
" 2>&1 | tee -a "$LOG"

# Step 6: Update LIVE_STATUS
python3 scripts/update_live_status.py 2>&1 | tee -a "$LOG" || echo "[pipeline] update_live_status.py not found, skipping"

# Step 7: Compile paper
echo "[pipeline] Compiling paper..." | tee -a "$LOG"
cd paper
bash compile.sh 2>&1 | tee -a "$LOG"
cd ..
echo "[pipeline] Paper compiled." | tee -a "$LOG"

# Step 8: Commit and push
echo "[pipeline] Committing changes..." | tee -a "$LOG"
git add -A
git commit -m "feat: batch v39 — gpt-5.3-chat-latest + gpt-5-pro (responses API); extends to 39 model variants; embed+LME+model_d rerun; paper update (55 batches)" \
    || echo "[pipeline] Nothing to commit."
git push origin HEAD 2>&1 | tee -a "$LOG"
echo "[pipeline] Push done." | tee -a "$LOG"

echo "[pipeline] All steps complete at $(date)" | tee -a "$LOG"
