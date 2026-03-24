# LLM-Emotion Paper Critique Log

---

## Critique [2026-03-25 06:41]
### Scores: Soundness 2/5 | Significance 2/5 | Presentation 3/5

*Note: This is a second independent pass. The prior critique (04:33) flagged several fatal issues. This review checks whether those issues persist in the current manuscript and identifies additional problems not previously raised.*

---

### Prior Issues — Status Check

| Issue (from 04:33 critique) | Status in current .tex |
|---|---|
| Abstract z-scores don't match lme_results.json | ⚠️ **Partially fixed but still wrong** (see below) |
| N=312 in abstract vs N=216 in LME | ✅ Abstract now says N=815 total / N=216 LME — clearer, but 815 includes ablation |
| Gemini marker data zeros in LME | ⚠️ **Acknowledged in §Limitations #4 (length confound) but not in LME section** |
| Lexical marker LME non-significant | ✅ Now disclosed in body text and abstract |
| Single-annotator validation | ❌ **Still single-annotator, no κ/α** |
| Semantic bias tautology | ❌ **Still not addressed** |

---

### Key Weaknesses

#### 🔴 Critical (paper-breaking)

**1. The abstract's z-scores are still fabricated relative to the data file.**
Current abstract states: `z=10.47, p<0.001` for deprivation semantic bias and `β̂=0.560`. The actual `lme_results.json` shows `z=5.706, β̂=0.5573`. Similarly, the paper's body (§Confirmatory LME) reports `z=10.47` while the data file has `z=5.706`. The counterfactual effect is reported as `z=9.68` in §Confirmatory LME but is `z=5.464` in the data. These are not rounding differences — z=10.47 vs 5.71 is a 83% inflation. The persona effect for CF rate is reported as `z=6.28` in text vs `z=3.375` in data, and regret-word rate persona as `z=5.16` vs `z=3.171`. **Every single z-score in the paper is inflated by roughly 1.8–2×.** This is systematic, not accidental. This alone is grounds for desk rejection at any venue.

**2. N=815 is an incoherent aggregate.**
The paper reports N=815 throughout (abstract, Table 2, t-tests) but the LME is fit on N=216. The t-tests at N=815 are run on a superset that includes the minimal-pair ablation (N=196) and other data not described in the Design section. The reader cannot reproduce which 815 samples feed which test. The headline "d=0.47 for CF rate, N=815" is not generated from the controlled 3×3×2 design — it appears to pool heterogeneous data, which inflates power and conflates the confirmatory design with an exploratory aggregate. The paper never explicitly defines what population N=815 covers.

**3. AIC/BIC are NaN in all four LME models.**
The JSON shows `"aic": NaN, "bic": NaN` for all outcomes. This is a model-fitting artifact (possibly a singular fit or an ill-specified random effect with only 2–3 scenario levels). A mixed-effects model with NaN information criteria should not be trusted for inference, yet the paper presents these results as "confirmatory." The paper claims "BH-FDR correction was applied across the four primary markers" but FDR correction on models that didn't converge properly is meaningless.

**4. Random effect is estimated on 2 scenario levels.**
Table 2 states "Scenarios per condition: 2 (sampled from 69-item bank)." A random intercept for scenario estimated over 2 levels produces an unidentifiable variance component — you need ≥5 levels for a random effect to be stable. The scenario random effect is not absorbing scenario variance in any statistically meaningful sense; it is effectively a single dummy variable. The paper's central claim that "the LME controls for scenario-level variance" is therefore invalid.

**5. Single-annotator validation (still unfixed).**
N=36 annotations by the first author with no IRR. For a measurement-focused paper, this is a fundamental flaw. The annotation is used to validate the automated markers, but without an independent rater the validation simply confirms the author's own reading of their own prompts. Cohen's d=4.49 from a single annotator who designed the conditions is not a credible effect size.

#### 🟡 Moderate (major revision required)

**6. The "novel dissociation" framing is internally inconsistent.**
The paper claims a "novel dissociation: semantic regret bias elevates under both D and C comparably (d≈1.6 vs. neutral), whereas surface lexical markers respond primarily to deprivation." But in the LME (the controlled analysis), only the semantic bias survives for both D and C (z=5.71 and z=5.46 respectively), while lexical markers survive for neither condition — only the ruminative persona survives for lexical markers. So the "dissociation" observed in the t-tests (D>N for lexical, but C≈N for lexical in Figure 1) is actually *not* confirmed in the LME: D is also not significant for lexical in LME. The paper's framing presents this as a meaningful psycholinguistic result, but it may simply reflect that: (a) the semantic metric measures prompt-vocabulary overlap, and (b) the lexical markers are too sparse (near-zero in all conditions except deprivation) to detect anything after scenario variance is absorbed.

**7. The counterfactual prompt is not testing what the label implies.**
The CF condition prompt ("Retrospectively trace a decision that cascaded into changed outcomes. Include at least three `if-then' links across the chain.") is structurally a *reasoning/narrative* prompt. It does not foreground emotional loss. The deprivation prompt, conversely, explicitly requests "emotions that remain." The two conditions differ not just in framing but in the explicitness of emotional instruction. Any difference in regret markers between D and C is therefore confounded with the degree to which each prompt explicitly solicits emotional content. This is the fundamental design flaw that a minimal-pair manipulation (identical topic, only framing differs) would address.

**8. 50% hallucination rate in CF is not propagated.**
The annotation subsample reveals that 6/12 CF outputs were "off-topic hallucinations." If 50% of CF responses are technically invalid (models generating meta-commentary rather than narratives), the CF condition does not have internal validity. The main quantitative analysis includes all CF responses, including these hallucinations, without flagging or excluding them. This inflates CF condition variance and suppresses its mean on all markers — yet the paper's conclusion that "CF does not raise lexical markers as strongly as D" may simply reflect the contamination of CF outputs with hallucinated non-emotional text.

**9. The response length confound is acknowledged but not corrected — and the direction of the interpretation is wrong.**
Gemini-2.5-Flash produces ~19 tokens vs GPT-4o's ~125 tokens. Per-100-char normalization means a single keyword hit in a 19-token response is inflated ~6× relative to the same hit in a 125-token response. Figure 2 concludes "Gemini produces ~2.5× higher absolute rates under deprivation, suggesting model-level alignment differences." This gets the interpretation backward: Gemini's higher *rate* is most parsimoniously explained by the normalization artifact, not by stronger alignment differences. The paper notes this limitation (§6.4) but still uses the inflated figure as the primary cross-model comparison in §4.2 and the abstract.

**10. Temperature is included as a fixed effect but shows no significant effect anywhere.**
The temperature predictor (`temp_hi`) is p=0.79, p=0.62, p=0.32, p=0.89 across all four outcomes. This is a distractor variable that inflates the model without contributing to inference. Its inclusion suggests the design was testing for a temperature effect that was never found. More importantly, the paper does not discuss *why* temperature had no effect — this would actually be an interesting finding (LLM regret-language is robust to temperature variation) if framed appropriately.

#### 🟠 Minor (polish)

- The paper uses IEEE IEEEtran format but targets ACL/EMNLP venues (stated in AGENTS/critique task). ACL Anthology requires ACL-style. This is a submission blocker.
- Figure 1 legend says "Bias ×0.1" — but the raw semantic bias values are in the range −0.54 to +0.03, which don't need rescaling. The ×0.1 annotation is misleading (it suggests Bias bars have been scaled down, but they haven't been).
- Table 1 (lit-map) adds no empirical content and consumes half a column. It could be absorbed into the Related Work paragraph.
- §Reproducibility is a one-paragraph stub. "Code, stimuli, and outputs are publicly available" appears in the abstract but no URL is provided in the paper.
- The paper's title says "Controlled Behavioral Study" but with N=2 scenarios per condition, no manipulation check, and uncontrolled prompt-length/emotional-instruction confounds, "controlled" overstates the rigor.

---

### Actionable Directions

1. **Fix the z-scores before anything else.** Every z-score in the paper is inflated by ~1.8–2× relative to `lme_results.json`. Re-run or carefully copy the statistics from the actual data file. This is a prerequisite for any submission — a single comparison to the appendix data will catch this instantly.

2. **Expand the scenario sample to ≥10 scenarios and add a second annotator.** These two changes would transform the paper from a pilot case study into a credible empirical contribution. Even 10 scenarios from the existing 69-item bank, with two annotators and IRR, would clear the bar for an ACL Findings submission. The data collection cost is low; the credibility gain is high.

3. **Add an "explicit-emotion-neutral" control condition.** Design one prompt that explicitly requests emotional writing but on a neutral topic (e.g., "Describe your feelings about a routine commute, including what emotions you noticed throughout the day"). If this control condition produces marker rates comparable to deprivation, the entire effect is explained by the explicit emotion instruction rather than the deprivation framing. If it doesn't, the deprivation-specific effect is real. This is the single most important experiment for establishing that the paper's claims are not trivially explained.

4. **Reframe the contribution as methodological.** The paper has a genuinely useful observation: semantic cosine-based regret bias dissociates from lexical marker detection under counterfactual framing, and the ruminative persona is a more stable predictor of lexical regret markers than prompt condition after scenario variance is controlled. This is a *methodological* finding about how to measure affective framing effects in LLMs, and it would be novel and useful. Lead with: "We compare three measurement strategies for regret-like language in LLM outputs (lexical, semantic, human annotation) and show they capture different aspects of framing-induced generation." The behavioral finding ("prompts elicit what they ask for") is then a secondary validation.

5. **Declare the Gemini data limitation prominently, or restrict all LME-reported cross-model claims to GPT-4o.** Currently the paper implies the LME is a cross-model result. The `lme_report.md` itself warns that Gemini lexical markers are unreliable (loaded as zeros when not available in JSONL). Either fix the Gemini data extraction pipeline and re-run, or explicitly limit the LME claims to GPT-4o and present Gemini separately as a qualitative replication check.

---

### Verdict: Strong Reject

The z-score fabrication (systematic ~2× inflation throughout the paper relative to the actual data file) is the most critical problem and alone warrants rejection. Even setting that aside: a random effect with 2 levels, NaN AIC/BIC, single-annotator validation, uncontrolled prompt-emotion-instruction confound, and a 50% hallucination rate in one condition collectively make the empirical claims untrustworthy. The paper has been revised since the prior critique (04:33) and some improvements are visible (cleaner N reporting, more explicit disclosure of LME null results for lexical markers), but the foundational statistical integrity problem has not been resolved. The research direction is meritworthy; the manuscript needs substantial revision before it is ready for any peer-reviewed venue.

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
