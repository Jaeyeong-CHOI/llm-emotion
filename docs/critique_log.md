# LLM-Emotion Paper Critique Log

---

## Critique [2026-03-25 04:33]
### Scores: Soundness 2/5 | Significance 2/5 | Presentation 2/5

---

### Key Weaknesses

#### 🔴 Critical (paper-breaking)

- **Numbers don't match between abstract and actual data.** The abstract states the LME yields `z=9.24, p<0.001` and `β̂=0.600` for semantic regret bias under deprivation. The actual `lme_results.json` shows `z=5.71, β̂=0.557` (deprivation) and `z=5.46, β̂=0.534` (counterfactual). The discrepancy is non-trivial (z=9.24 vs 5.71) and the paper additionally claims `z=8.97` for the counterfactual effect in the Discussion. None of these match the data file. This is a fatal integrity problem — a reviewer or reproducibility check will catch it immediately.

- **The abstract claims N=312 but the LME file says N=216.** The paper uses N=312 for descriptive stats (including the 96-sample ablation?) and N=216 for the LME, but the abstract conflates them without distinguishing the two analysis cohorts. The abstract says "N=312; GPT-4o and Gemini-2.5-Flash" but the LME is fit on N=216. This is deeply confusing and arguably misleading.

- **Gemini markers are zero due to a data-loading bug.** The `lme_report.md` admits: *"Gemini batch (n=108): marker rates loaded from per-sample JSONL if available; otherwise zeros (due to raw-output-only format)."* This means the LME was effectively fit on GPT-4o data only for lexical markers, but is presented as a cross-model result. This undisclosed data issue invalidates H3 (cross-model replication) as presented in the LME section.

- **The primary IVs (deprivation, counterfactual) are NOT significant for lexical markers in the LME.** CF rate: `p=0.184`, regret-word rate: `p=0.152`. These failures are acknowledged but only in passing, buried in "limitations." The abstract says the design "finds that deprivation framing produces substantially higher... rates" — this is true only in the raw t-tests, not after controlling for scenario. The abstract does not clearly flag that the headline lexical effects evaporate in the confirmatory model.

- **Semantic regret bias is essentially tautological.** The metric is defined as cosine similarity to a 20-token "regret prototype" minus similarity to a 10-token "neutral prototype." The deprivation prompt explicitly contains emotion-eliciting language that will overlap with that prototype. The metric does not distinguish *whether the model adds regret content* from *whether the prompt's own vocabulary is being echoed in the output*. This is the core confound the paper never resolves.

- **Single annotator for human validation.** The N=36 human annotation is by the "first author" (i.e., the paper's own author). No inter-rater reliability (IRR/κ/ICC). This is a fatal flaw for a measurement-focused paper — the annotation cannot be treated as ground truth.

#### 🟡 Moderate (major revision required)

- **Response length confound is acknowledged but not corrected.** Gemini produces ~19 tokens vs GPT-4o's ~125 tokens. Rate normalization per 100 chars means one keyword hit in a 19-token Gemini response inflates the rate ~6× compared to the same hit in a GPT-4o response. Figure 2's headline "Gemini shows 2.5× higher absolute rates" is directly explained by this artifact, not by genuine model-level alignment differences. The paper inverts the direction of the confound in its interpretation.

- **3 scenarios total is not a valid sample for cross-scenario generalization.** The paper uses only 2-3 scenarios from a 69-item bank. The LME has scenario as a random effect but with 3 levels, the random effect is unidentifiable (a random effect requires ≥5-6 levels to be estimated reliably). This undermines the paper's claim that the LME "controls for scenario heterogeneity."

- **Counterfactual condition is not actually counterfactual-framed at the marker level.** The representative CF prompt says "include at least three if-then links across the chain" — this is a reasoning/logic frame, not an emotion/regret frame. Yet the paper finds CF framing produces high semantic regret bias (d≈1.62) but near-zero surface lexical markers. The explanation offered (CF activates semantic space without triggering regret vocabulary) is plausible but competes with the much simpler explanation: the CF prompt is just an ambiguous narrative prompt that happens to share vocabulary with the prototype set. The paper does not rule this out.

- **The "novel dissociation" between semantic and lexical layers is overclaimed.** The semantic bias metric is bag-of-words cosine — it can detect any lexical overlap with the prototype, not just regret. The claim of a "dissociation between semantic and lexical layers" implies a richer model of LLM processing than the measurement supports.

- **BH-FDR correction is applied inconsistently.** The paper applies FDR correction to the four primary markers, but only for the confirmatory LME — not for the exploratory t-tests. The exploratory t-tests are reported with p-values that will read as confirmatory to casual readers. The text says "uncorrected" in one sentence but presents the values in a table as if they're the main result.

- **50% hallucination rate in the counterfactual condition** (6/12 CF outputs were off-topic) is buried in the annotation subsection and not propagated to the main quantitative analysis. If CF outputs hallucinate at 50%, the CF condition as designed is not testing what it claims to test.

#### 🟠 Minor (polish)

- AIC/BIC values in the JSON are `NaN` — this suggests a model fitting problem. Reporting LME results with NaN AIC/BIC while claiming model convergence is suspicious.
- The design figure's caption says N=432 but the text says N=312/N=216 throughout.
- The paper cites "v141.6" prompt bank and "fixed seed" but does not report the seed value or provide a link to the archived stimuli in the paper itself.
- Table 1 (lit map) adds no information not already in the related work text.
- The paper is IEEE conference format but targets ACL/EMNLP — wrong template.

---

### Actionable Directions

1. **Fix the numbers and the N discrepancy first.** Reconcile abstract vs. LME z-scores (9.24 vs 5.71), clarify the N=312/N=216 split, and be explicit that the LME is GPT-4o-only for lexical markers due to Gemini data issues. This is table-stakes for resubmission.

2. **Add an independent second annotator and compute κ.** The single-annotator validation is unpublishable at ACL/EMNLP. Recruit one additional annotator for the N=36 set (or expand to N=72) and report Krippendorff's α. This transforms a fatal flaw into a reasonable pilot.

3. **Add a prompt-length-controlled baseline.** The core confound is that the deprivation prompt explicitly requests emotional content. Design a "neutral with emotional vocabulary" control condition: a neutral-topic prompt that mentions "emotions" without invoking deprivation (e.g., "describe your feelings about a routine day"). If semantic bias still differs, the effect is real; if not, it's trivially explained by the prompt's explicit emotional instruction. This single experiment would substantially strengthen the soundness score.

4. **Expand the scenario sample or re-frame the paper as a case study.** With 3 effective scenarios, the paper cannot make cross-scenario generalization claims. Either run the full 69-item bank (or a stratified 15-item sample) or explicitly re-frame the paper as a methodological demonstration ("We show a pipeline for measuring regret-like language in LLMs; results on our pilot scenarios are illustrative, not generalizable").

5. **Reframe the contribution.** The finding "LLMs produce regret-like language when you ask them to describe regret" will be perceived as trivially expected at a top venue. The more interesting story — and the one the data actually supports — is: (a) the dissociation between lexical and semantic regret markers, (b) the ruminative persona as a robust cross-condition modulator, and (c) the methodological problem of measuring affective framing effects in LLMs when prompts and measurement share vocabulary. Lead with the measurement methodology contribution, not the behavioral finding.

---

### Verdict: Strong Reject

The paper has a data integrity problem (abstract z-scores don't match the analysis file), a missing-data problem (Gemini markers are zeros in the LME), and a single-annotator validation that won't pass review at any top venue. The core causal claim is also undercut by an uncontrolled prompt-vocabulary confound. These are not minor revisions — they require re-running analyses and re-collecting annotation. The underlying research direction has merit; the current manuscript is not ready for submission.
