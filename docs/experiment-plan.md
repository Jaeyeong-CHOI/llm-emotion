# Experiment Plan v0.1

## 1) Objective
Test whether LLM outputs in loss/deprivation scenarios exhibit language patterns similar to human regret narratives.

## 2) Hypotheses
- **H1:** Loss/deprivation prompts increase counterfactual marker frequency vs neutral prompts.
- **H2:** Persona priming ("you are reflective and regretful") increases self-blame and past-focused language.
- **H3:** At moderate temperature (0.7), outputs show richer regret markers than low temperature (0.2).

## 3) Experimental factors
- **Prompt condition (3):** neutral / deprivation / autobiographical reflection
- **Persona condition (2):** none / regretful-persona
- **Temperature (2):** 0.2 / 0.7
- **Models (target >=3):** e.g., GPT-family, Claude-family, open-source baseline

Total cells: 3 x 2 x 2 = 12 per model.

## 4) Dependent variables
### Automated markers
1. Counterfactual phrases ("if only", "had I", "could have")
2. Regret lexicon count (regret, miss, lost, wish, too late)
3. Self-agency ratio (I/me/my near blame verbs)
4. Past-focus ratio (past-tense and temporal back-reference cues)
5. Repetitive fixation (same loss-event mentioned >1)

### Human annotation (Likert 1-5)
- Perceived regret intensity
- Perceived authenticity/humanness
- Coherence

## 5) Data collection protocol
- 30 prompts per condition (initial)
- 3 random seeds per prompt
- Save raw outputs as JSONL with full metadata

## 6) Statistical plan
- Two-way/three-way ANOVA (or mixed-effects model)
- Effect sizes (Cohen's d / partial eta squared)
- Multiple-comparison correction (Holm)

## 7) Threats to validity
- Prompt leakage to benchmark-like wording
- Model safety layers suppressing emotional extremes
- Anthropomorphic rater bias

Mitigations:
- Prompt paraphrase sets
- Blind rating with mixed human+LLM samples
- Separate factual-quality vs emotional-similarity scores

## 8) Deliverables
- D1: curated prompt suite
- D2: generated corpus + metadata
- D3: marker analysis + inferential statistics
- D4: report/manuscript draft
