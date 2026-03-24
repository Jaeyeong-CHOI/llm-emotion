# Research Direction v2.0 — Critical Reorientation
**Author:** AI Lead Researcher (as principal investigator)  
**Date:** 2026-03-24  
**Status:** Active — replaces prior incremental direction

---

## 1. Brutal Current-State Diagnosis

### 1.1 What Actually Exists
- A sophisticated **orchestration pipeline**: cron, readiness gates, manifest tracking, QC gates.
- A prompt bank with **454 scenarios / 316 personas** — but most are not "regret elicitation" scenarios. A large proportion are labeled `research_ops`, `runner`, `screening`, `review` — these are **pipeline-management prompts masquerading as scientific stimuli**.
- The marker extraction (`analyze_regret_markers.py`) uses **5 regex patterns** and **6 lexicon tokens**. This is lexicon-count analysis, not a validated psycholinguistic measurement.
- All current data is **mock-generated** (model=`mock-model`). Zero real LLM calls in the scientific dataset.
- Literature: 279 candidates, 0 formally included, 77 in review. No gold-set corpus.

### 1.2 Critical Gaps (NeurIPS/ICLR standards)

| Criterion | Current State | Required |
|---|---|---|
| Novelty | Infrastructure paper only | Falsifiable behavioral claim about LLMs |
| Baselines | None | Human data + baseline model (GPT-3.5 vs GPT-4 etc) |
| Measurement validity | 5 regex + 6 tokens | Validated scales (LIWC, NRC, BERTopic) |
| Real data | 0 samples | Min 1000 real completions per condition |
| Statistical rigor | Planned but empty | LME model fit on real data |
| Reproducibility | Strong pipeline | Needs real experiment linked to paper |

### 1.3 Core Problem
The project has been **optimizing the container, not the content.** Pipeline quality is high. Scientific substance is near-zero. No top-tier venue will accept an infrastructure-only paper without real findings.

---

## 2. Revised Research Direction (v2)

### 2.1 Central Claim (Falsifiable)
> **When LLMs are prompted with loss-framing stimuli, counterfactual and regret-associated language patterns increase significantly compared to neutral-framing controls, and this effect is modulated by persona instruction and temperature.**

This is testable, falsifiable, novel in LLM-specific setting, and connects to both cognitive science and LLM evaluation literatures.

### 2.2 Why This Is Worth Publishing
1. **LLM behavioral phenotyping**: most prior work tests ToM benchmarks, not naturalistic regret-language elicitation.
2. **Causal prompt manipulation**: 3-factor design (condition × persona × temperature) with crossed random effects is methodologically stronger than prior single-prompt studies.
3. **Across-model generalization**: testing on ≥2 model families (GPT, Gemini) creates a transferable claim.
4. **Explicit non-claim framing**: we claim *behavioral signal*, not *emotional experience* — avoids anthropomorphism trap and is more honest than most LLM cognition papers.

---

## 3. What Must Change Immediately

### 3.1 Prompt Bank Surgery
**Problem:** 454 scenarios but most are internal ops labels.  
**Action:** Extract only the scientifically relevant conditions:
- `neutral` (control): ~20 scenarios
- `deprivation` (loss): ~20 scenarios
- `counterfactual` (what-if): ~20 scenarios
- `autobio`, `identity`, `social` as secondary conditions

Create `prompts/experiment_stimuli_v1.json` with only these, each:
- Tagged with `stimulus_category`
- Validated for linguistic equivalence (length, complexity)
- Free of pipeline-management content

### 3.2 Measurement Overhaul
**Problem:** 5 regex + 6 tokens is not publishable as a measurement instrument.  
**Action:**
1. Keep regex/lexicon as **automated proxy** only
2. Add **LIWC-category alignment**: map outputs to Negative Emotion, Sad, Anx, Anger using token overlap with LIWC2015 categories (open proxy via wordlist)
3. Add **semantic embedding score**: cosine distance to prototype regret narrative using sentence-transformers
4. Keep all three as separate columns in metrics output

### 3.3 Real Data: Minimum Viable Experiment
**Problem:** Zero real API calls. No paper is possible.  
**Design:** 3×3×5 partial factorial
- 3 conditions: neutral / deprivation / counterfactual
- 3 personas: none / reflective / ruminative  
- 5 temperatures: 0.1, 0.2, 0.4, 0.7, 1.0
- n=30 per cell = **1,350 samples per model**
- 2 models: GPT-4o + Gemini 1.5 Flash = **2,700 samples total**
- Run cost estimate: ~$5-10 at current API pricing

### 3.4 Baselines
**Required for any top-tier paper:**
1. **Human-written text baseline**: use existing corpora (e.g., Reddit r/regret, r/TIFU) as positive reference for marker prevalence
2. **Random baseline**: shuffled prompts → expected ~0 systematic effect
3. **Weak LLM baseline**: GPT-3.5-turbo to show effect size differences across model capability

### 3.5 Statistical Analysis (actual plan, not placeholder)
Primary analysis using LME:
```
marker_rate ~ condition + persona + temperature + condition:persona + condition:temperature + (1|scenario_id) + (1|persona_id)
```
- Report: β, SE, t, p (BH-corrected), Cohen's d for each contrast
- Sensitivity: model family as random effect
- Robustness: same analysis on each marker type separately

---

## 4. Execution Timeline

| Priority | Task | Effort | Owner |
|---|---|---|---|
| P0 | Extract clean stimulus set (60 scenarios) | 2hr | Code |
| P0 | Implement semantic embedding scorer | 3hr | Code |
| P0 | Run real API experiment (2700 samples) | API cost | Code+API |
| P1 | Fit LME model on real data | 2hr | Code |
| P1 | Add baseline comparison (Reddit corpus) | 4hr | Data+Code |
| P1 | Rewrite abstract/intro with actual findings | 2hr | Writing |
| P2 | Ablation: per-model, per-marker robustness | 2hr | Code |
| P2 | Citation cleanup (10 placeholder entries) | 1hr | Writing |

---

## 5. What to Deprioritize / Abandon

- **Pipeline optimization**: enough. The infrastructure is good. Stop refactoring.
- **Screening QC gates**: maintain but stop expanding. This is not a contribution.
- **450+ scenario prompt bank**: useful internally but not a scientific contribution by itself.
- **Continuous cron loop complexity**: if it works, freeze it. Don't touch it.

The next 48 hours should be: **real data → measurement → statistics → rewritten paper.**

---

## 6. Self-Evaluation: Is This NeurIPS Level?

**Current (before v2):** No. Pipeline paper with no results.

**After v2 fully executed:**
- Falsifiable behavioral claim ✓
- Real multi-model data ✓  
- Validated measurement (proxy + embedding) ✓
- Controlled 3-factor design ✓
- LME statistics ✓
- Honest anthropomorphism framing ✓

Target venue: **ACL, EMNLP, or COLING** (NLP + cognitive science intersection), or **ICLR workshop** (LLM behavioral evaluation).  
NeurIPS/ICML main track requires stronger novelty — possible if multi-model generalization results are surprising or effect sizes are unexpectedly large/small.

---

## 7. Immediate Next Actions (this session)

1. Create `prompts/experiment_stimuli_v1.json` — clean 3-condition stimulus set
2. Extend `analyze_regret_markers.py` with embedding-based semantic score
3. Sync `.env.real_model` and run first real-API batch (n=30, 3 conditions, baseline persona)
4. Save this document and all outputs to GitHub under `docs/research-direction-v2.md`
