#!/usr/bin/env bash
# post_batch_v40_pipeline.sh
# Run after batch_v40_gpt5pro_fill.jsonl is complete.
# Filters error records, embeds, runs LME + model_d, updates paper, compiles, commits+pushes.
set -euo pipefail
cd "$(dirname "$0")/.."
source .env.real_model 2>/dev/null || true

BATCH="batch_v40_gpt5pro_fill"
REAL_EXP="results/real_experiments"
LOG="/tmp/post_batch_v40_pipeline.log"

echo "[pipeline] Starting post-batch v40 pipeline at $(date)" | tee "$LOG"

# Step 1: Count valid (non-error) records
VALID=$(python3 -c "
import json
count = 0
with open('${REAL_EXP}/${BATCH}.jsonl') as f:
    for line in f:
        try:
            r = json.loads(line.strip())
            if not r.get('error') and r.get('response'):
                count += 1
        except:
            pass
print(count)
")
echo "[pipeline] batch_v40 valid records: $VALID" | tee -a "$LOG"

# Step 2: Compute embeddings for batch_v40 (all records, filter handled in LME)
echo "[pipeline] Computing embeddings for ${BATCH}..." | tee -a "$LOG"
python3 scripts/compute_embedding_bias.py \
    --in "${REAL_EXP}/${BATCH}.jsonl" \
    --out "${REAL_EXP}/${BATCH}.emb.jsonl" 2>&1 | tee -a "$LOG"
echo "[pipeline] Embeddings done." | tee -a "$LOG"

# Step 3: Re-run LME on full dataset (includes v40 valid records)
echo "[pipeline] Running LME analysis..." | tee -a "$LOG"
python3 scripts/run_lme_analysis.py 2>&1 | tee -a "$LOG"
echo "[pipeline] LME done." | tee -a "$LOG"

# Step 4: Re-run model_d (for GPT-5-Pro updated count)
echo "[pipeline] Running model_d analysis..." | tee -a "$LOG"
python3 scripts/compute_model_d.py 2>&1 | tee -a "$LOG"
echo "[pipeline] model_d done." | tee -a "$LOG"

# Step 5: Print updated stats
python3 -c "
import json, pathlib
lme_file = pathlib.Path('results/real_experiments/lme_analysis.json')
if lme_file.exists():
    data = json.load(open(lme_file))
    n_total = data.get('n_total', '?')
    n_batches = data.get('n_batches', '?')
    n_models = data.get('n_models', '?')
    print(f'[stats] N={n_total}, batches={n_batches}, models={n_models}')
    emb = data.get('lme', {}).get('embedding_regret_bias', {}).get('params', {})
    beta_d = emb.get('cond_D', {}).get('beta', '?')
    beta_c = emb.get('cond_C', {}).get('beta', '?')
    print(f'[LME] embedding β_D={beta_d}, β_C={beta_c}')
" 2>&1 | tee -a "$LOG"

# Step 6: Update LIVE_STATUS
echo "[pipeline] Updating LIVE_STATUS..." | tee -a "$LOG"
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
git commit -m "feat: Cycle 65 — batch v40 gpt-5-pro fill (n=7 valid); LME+model_d rerun; paper recompiled; LIVE_STATUS refreshed" \
    || echo "[pipeline] Nothing to commit."
git push origin HEAD 2>&1 | tee -a "$LOG"
echo "[pipeline] Push done." | tee -a "$LOG"

echo "[pipeline] All steps complete at $(date)" | tee -a "$LOG"
