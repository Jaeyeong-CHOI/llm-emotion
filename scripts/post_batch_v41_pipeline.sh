#!/usr/bin/env bash
# post_batch_v41_pipeline.sh
# Run after batch_v41_dep_balance collection is complete.
# Steps: validate → embed → LME → model_d → paper update → compile → commit+push
set -euo pipefail
cd "$(dirname "$0")/.."
source .env.real_model 2>/dev/null || true

BATCH="batch_v41_dep_balance"
REAL_EXP="results/real_experiments"
LOG="/tmp/post_batch_v41_pipeline.log"

echo "[pipeline] Starting post-batch v41 pipeline at $(date)" | tee "$LOG"

# Step 1: Count valid records
VALID=$(python3 -c "
import json
count = 0
with open('${REAL_EXP}/${BATCH}.jsonl') as f:
    for line in f:
        try:
            r = json.loads(line.strip())
            if not r.get('error') and r.get('output'):
                count += 1
        except:
            pass
print(count)
")
echo "[pipeline] batch_v41 valid records: $VALID" | tee -a "$LOG"

# Step 2: Compute embeddings
echo "[pipeline] Computing embeddings for ${BATCH}..." | tee -a "$LOG"
python3 scripts/compute_embedding_bias.py \
    --in "${REAL_EXP}/${BATCH}.jsonl" \
    --out "${REAL_EXP}/${BATCH}.emb.jsonl" 2>&1 | tee -a "$LOG"
echo "[pipeline] Embeddings done." | tee -a "$LOG"

# Step 3: Add batch to LME batch list (if not already there)
echo "[pipeline] Checking LME batch list..." | tee -a "$LOG"
python3 - << 'PYEOF'
import pathlib, re

lme_script = pathlib.Path("scripts/run_lme_analysis.py")
text = lme_script.read_text()

if "batch_v41_dep_balance" not in text:
    # Find the batch list and append
    old = '"batch_v40_gpt5pro_fill"'
    new = '"batch_v40_gpt5pro_fill", "batch_v41_dep_balance"'
    if old in text:
        text = text.replace(old, new)
        lme_script.write_text(text)
        print("[pipeline] Added batch_v41_dep_balance to LME batch list")
    else:
        print("[pipeline] WARNING: could not auto-insert batch into LME list — check manually")
else:
    print("[pipeline] batch_v41_dep_balance already in LME batch list")
PYEOF

# Step 4: Re-run LME on full dataset
echo "[pipeline] Running LME analysis..." | tee -a "$LOG"
python3 scripts/run_lme_analysis.py 2>&1 | tee -a "$LOG"
echo "[pipeline] LME done." | tee -a "$LOG"

# Step 5: Re-run model_d
echo "[pipeline] Running model_d analysis..." | tee -a "$LOG"
python3 scripts/compute_model_d.py 2>&1 | tee -a "$LOG"
echo "[pipeline] model_d done." | tee -a "$LOG"

# Step 6: Print updated stats
python3 -c "
import json, pathlib
d = json.loads(pathlib.Path('results/real_experiments/lme_analysis.json').read_text())
print()
print('=== Updated LME Stats ===')
print(f'N_total={d[\"n_total\"]}, models={d[\"n_models\"]}, batches={d[\"n_batches\"]}')
print(f'conditions: {d[\"conditions\"]}')
lme = d['lme']['embedding_regret_bias']['params']
print(f'emb β_D={lme[\"cond_D\"][\"beta\"]:.4f} z={lme[\"cond_D\"][\"z\"]:.3f}')
print(f'emb β_C={lme[\"cond_C\"][\"beta\"]:.4f} z={lme[\"cond_C\"][\"z\"]:.3f}')
" 2>&1 | tee -a "$LOG"

# Step 7: Update paper N stats and recompile
echo "[pipeline] Updating paper stats..." | tee -a "$LOG"
python3 scripts/update_paper_stats.py 2>&1 | tee -a "$LOG" || echo "[pipeline] update_paper_stats.py failed — manual update may be needed" | tee -a "$LOG"

echo "[pipeline] Compiling paper..." | tee -a "$LOG"
cd paper && bash compile.sh 2>&1 | tee -a "$LOG" && cd ..
echo "[pipeline] Paper compiled." | tee -a "$LOG"

# Step 8: Update LIVE_STATUS
echo "[pipeline] Updating LIVE_STATUS..." | tee -a "$LOG"
python3 scripts/update_live_status.py 2>&1 | tee -a "$LOG" || true

# Step 9: Commit and push
echo "[pipeline] Committing changes..." | tee -a "$LOG"
git add -A
git commit -m "feat: Cycle 70 — batch v41 dep balance (+163 dep samples); LME re-run; paper recompiled; LIVE_STATUS refreshed" 2>&1 | tee -a "$LOG"
git push 2>&1 | tee -a "$LOG"

echo "[pipeline] Done at $(date)" | tee -a "$LOG"
echo "[pipeline] Log: $LOG"
