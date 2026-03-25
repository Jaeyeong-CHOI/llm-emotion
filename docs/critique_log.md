# LLM-Emotion Paper Critique Log

---

## Critique [2026-03-25 11:05]
### Scores: Soundness 3/5 | Significance 2/5 | Presentation 3/5

---

### Context: What Changed Since 08:54 Critique

The paper has been substantially revised. The following issues raised in the prior critique are now resolved or improved:
- ✅ Data integrity: The N=1,336 full-dataset LME is now the authoritative analysis (`lme_analysis.json`); `lme_results.json` correctly flagged as legacy.
- ✅ Metric revised: Bag-of-words "semantic bias" replaced by sentence-transformer embedding cosine bias (`paraphrase-multilingual-MiniLM-L12-v2`). Paper explicitly acknowledges the legacy metric's limitation.
- ✅ N and condition counts now consistent: 503/402/431 for N/D/C in N=1,336.
- ✅ Limitations section substantially expanded (response length confound, two-model limitation, single annotator).
- ✅ H1 now explicitly declared as NOT confirmed by LME — framing is honest.
- ✅ Inter-rater reliability reported (κ=0.44, moderate).

The 08:54 critique's **Strong Reject** was appropriate for the prior state. The current version is meaningfully improved. This critique reassesses from scratch.

---

### Key Weaknesses

#### Soundness (3/5)

**Serious: The "semantic-layer dissociation" is the headline contribution but rests on a scale-incommensurable comparison.**
- The embedding regret bias (LME cond_D: β=0.150, z=4.12; cond_C: β=0.135, z=3.53) reflects a cosine-space difference, while the lexical markers are per-100-character token rates. These two measurement families are not on commensurable scales. The paper claims they "dissociate," but the non-significance of lexical LME coefficients is explicitly explained by between-scenario variance absorption — not by any principled psycholinguistic model. The claim that "counterfactual framing activates regret-associated semantic representations without triggering explicit regret vocabulary" is a theoretical interpretation imposed on what may simply be a measurement sensitivity difference (embedding features average over continuous distributional space; lexical counts are sparse discrete events with huge inter-scenario variance).
- The dissociation would be far more credible if both measurement layers were subject to the same random effects structure AND if the scenario variance absorption for lexical markers was specifically tested (e.g., what proportion of variance does the random intercept explain? An ICC should be reported).

**Serious: The ablation data exposes a critical inconsistency that weakens the main framing.**
- In the minimal-pair ablation (N=196), `cf_rate` (counterfactual expression rate) for the counterfactual condition is M=3.18 per 100 chars — far higher than deprivation (M=0.00, cf_rate_sd=0.00). Yet in the main dataset (N=1,336), counterfactual condition CF rate is M=0.12 vs deprivation M=0.70. These are directionally reversed. The paper frames the main result as "deprivation drives larger lexical increases," but the ablation shows CF framing dramatically outperforms deprivation on CF rate. This contradicts the framing of deprivation as the lexical-heavy condition. The paper does not resolve or even flag this reversal.
- The ablation's `semantic_regret_bias` values are in a completely different numeric range (0–5 range) than the main dataset embedding bias (−0.05 to +0.10 range), suggesting these are different metrics or parameterizations. The paper implies they measure the same construct. This is not explained.

**Serious: Prompt confound is incompletely controlled.**
- The deprivation prompt contains an explicit emotional instruction ("write... including what was lost and the emotions that remain"). The minimal-pair ablation was intended to address this, but: (a) the ablation uses only 3 topics with n≈10/cell — far too small for robust causal inference; (b) the ablation results show model heterogeneity (Gemini: d=0.73 pooled, GPT-4o: d=1.86 pooled) — a 2.5× difference that could reflect the response-length confound already identified. The ablation result does not cleanly isolate framing from content instruction.

**Moderate: Emotion/regret prototype set is not independently validated.**
- The embedding bias uses 3 Korean regret prototype sentences and 3 neutral prototype sentences chosen by the first author. These were not independently validated for prototypicality, breadth of regret expression, or orthogonality. With only 3 prototypes per pole, the metric is sensitive to the specific choice of prototypes. No ablation on prototype sensitivity is reported.

**Moderate: The "semantic-layer dissociation" N=36 human annotation appears insufficient for the claims made.**
- The annotation N=36 (12/condition) is too small to establish convergent validity for a metric claiming to detect subtle semantic-layer differences. The single-annotator design (first author) with κ=0.44 against a GPT-4o rater introduces experimenter bias risk. The paper reports d=4.49 for dep vs. neutral on human annotation — but this is trivially expected given the explicit emotion instruction and the annotator is aware of the condition (no blinding reported).

**Minor: Condition imbalance in N=1,336 dataset.**
- Neutral: 503, Deprivation: 402, Counterfactual: 431. The neutral condition has 25% more samples than deprivation. This imbalance is not addressed in the LME discussion and may affect random intercept estimation for scenario-level variance.

**Minor: Temperature effect null but included.**
- temp_z: β=0.0003, z=0.196, p=0.845 — the temperature factor adds no variance explained and inflates model complexity. Null is fine, but it should be dropped from the confirmatory model with a note.

---

#### Significance (2/5)

- **The core finding — that prompts instructing emotional content elicit emotional content — is trivially expected.** The paper's primary H1 is explicitly not confirmed by the confirmatory LME. The "dissociation" finding is the claimed contribution, but its novelty is limited: it essentially shows that a more sensitive (continuous embedding) measure detects what a sparse (discrete lexical) measure misses, which is a measurement methods observation rather than a substantive behavioral finding about LLMs.
- **The ruminative persona effect (z=14.61) is actually the most robust finding**, yet it receives less narrative emphasis than the condition effects. The actionable implication — that persona-level instructions are more reliable levers for affect-laden generation than prompt framing — is genuinely useful for alignment and safety, but is underemphasized.
- **The research question is framed as novel** ("few have examined whether affect-laden framing reliably shifts lexical distribution in a controlled cross-model fashion"), but this claim ignores a substantial body of work on persona-conditioned generation, tone adaptation, and sycophancy in RLHF-aligned models. The related work section is thin and does not engage with closest-neighbor work (e.g., Perez et al. on sycophancy, work on emotional tone injection in ChatGPT-style models).
- The safety motivation cited in the intro (emotionally sensitive applications) is never operationalized. What specific safety risk is quantified or mitigated by knowing that deprivation prompts produce regret-like language? Without this, the intro motivation is handwaving.
- Two LLM families is insufficient for "behavioral benchmarking" claims. With GPT-4o and Gemini only, the findings cannot be attributed to LLMs as a class.

---

#### Presentation (3/5)

- **Abstract is improved but contains statistical artifacts.** The abstract cites "exploratory Welch d≈2.0–2.2" alongside "confirmatory LME" results. Mixing exploratory and confirmatory statistics in the abstract, even with labels, sends a muddled signal. The abstract should foreground the LME results only.
- **The "semantic-layer dissociation" framing is repeated ~6 times.** By the conclusion, it reads like a rhetorical device rather than an empirically established finding. One clear statement in the abstract and one in the discussion is sufficient.
- **Figure 2 (bar chart) inconsistency.** The figure caption says "Condition-level marker means (N_total=1,156; GPT-4o and Gemini-2.5-Flash)." But the main dataset is N=1,336. The figure appears to use a subset; this is not explained. Also the EmbBias bar in Figure 2 shows values in the range −0.5 to +0.10, while the LME reports β=0.150 and Table 3 reports Emb. Bias means of +0.097 (D) and +0.092 (C). The Figure 2 bar for "Neutral" appears to be −0.047, consistent with Table 3's −0.049. The figure's N=1,156 vs paper's N=1,336 is unexplained discrepancy.
- **Table 4 (LME summary) omits the Intercept.** Reviewers cannot assess the baseline level of each marker without the intercept. This is non-standard.
- **The IEEEtran format** is inappropriate for an ACL/EMNLP/NeurIPS/ICLR submission. This suggests the target venue is unclear or the manuscript is not yet venue-formatted, which reviewers at top venues notice immediately.
- **The "8 batches" structure is never clearly explained.** The Methods section says N=1,336 across 8 batches, but the batch structure and what varied between batches is not described. The Reproducibility section lists batch names but no schema.
- **Hypothesis confirmation summary is missing.** A clear table showing H1/H2/H3 × confirmatory result (supported/not supported) would improve clarity. Currently the reader must infer from scattered subsections.

---

### Actionable Directions

1. **Resolve the ablation-main dataset inconsistency before resubmission (critical).** The reversal in CF rate ordering (CF > D in ablation; D > C in main corpus) is a direct contradiction that undermines the paper's causal story. Either the ablation uses different markers (explanation needed) or the main corpus CF condition responses are systematically off-topic (50% hallucination rate acknowledged for N=36 subsample — is this rate representative?). Measure and report the off-topic rate for the full CF condition in the main corpus. If it's high, the CF condition data is corrupted and should be re-collected with on-topic filtering.

2. **Report ICC for scenario random effect and add persona as crossed random effect.** The central claim that "lexical effects are absorbed by scenario variance" needs quantification: report the ICC for scenario in each lexical LME. If ICC > 0.3–0.4, the scenario-level design is underpowered for scenario generalization and this should be clearly stated as a limitation. Adding persona as a crossed random effect would also allow testing whether the ruminative persona effect is scenario-specific.

3. **Reframe the contribution around persona > framing and expand to 4+ models.** The most reproducible, non-trivial finding is that ruminative persona instructions outperform prompt framing as a regret-marker predictor (z=14.61 vs z=4.12). This has clear implications for LLM safety (jailbreak via persona), alignment evaluation, and persona-conditioned generation. Reframe the paper around this, add open-weight models (Llama-3-8B, Mistral-7B) with the same protocol, and the contribution becomes publication-worthy at a workshop or findings venue. Adding a 4th finding about what makes personas vs. framing differentially effective (hypothesis about RLHF fine-tuning depth) would elevate to main track consideration.

---

### Verdict: Borderline (leaning Reject)

**Rationale:** The revised paper has resolved the critical data integrity and metric validity issues identified in the prior critique. The confirmatory LME is now run on the correct N=1,336, the metric is upgraded from bag-of-words to sentence-transformer embedding similarity, and limitations are honestly stated. However, several new issues emerge on close reading: (a) the ablation-main corpus CF rate contradiction is unaddressed; (b) the "dissociation" framing is theoretically underspecified; (c) the significance bar for a top venue is not met — the strongest finding (persona effect) is underemphasized, and the main finding (condition framing) is primarily negative (H1 not confirmed). For ACL/EMNLP main track: Reject. For ACL Findings or a targeted workshop (e.g., WASSA, EmotionX): Borderline / Weak Accept with the ablation inconsistency resolved.

---

## Critique [2026-03-25 08:54]
### Scores: Soundness 2/5 | Significance 2/5 | Presentation 3/5

---

### Key Weaknesses

#### Soundness (2/5)

**Critical: The paper's actual LME data contradicts its primary headline claims.**
- The paper claims (abstract, conclusion) LME results of $\hat{\beta}=0.500$, $z=11.28$ for deprivation and $\hat{\beta}=0.481$, $z=10.43$ for counterfactual, with $N_\text{total}=1084$. However, the actual `lme_results.json` and `lme_report.md` show an LME run on $N=216$ (not 1084) with deprivation effect on semantic regret bias of $\hat{\beta}=0.557$, $z=5.71$ — different coefficients, different sample size. The reported $z$-statistics in the paper (~11, ~10) are not reproducible from any data file found in the repository. **This is a data integrity / reproducibility crisis.**

**Critical: Gemini marker data is partially zeros/unreliable.**
- `lme_report.md` explicitly states: "Gemini batch (n=108): marker rates loaded from per-sample JSONL if available; otherwise zeros (due to raw-output-only format)." This means up to half the dataset may have zero-imputed marker values, which would severely inflate effect sizes for the combined analysis. The paper does not disclose this.

**Critical: The "semantic regret bias" metric is a bag-of-words cosine, not a validated semantic similarity measure.**
- The metric computes `sim(output, R) - sim(output, N)` where both $\mathcal{R}$ (20 tokens) and $\mathcal{N}$ (10 tokens) are simple token sets, using bag-of-words cosine. Any prompt that literally contains the prototype tokens (which the deprivation prompt by design asks for) will produce high similarity. This is not semantic similarity; it's token overlap detection. The $d=2.31$–$2.47$ "large" effects on this metric are therefore a near-tautology: prompts instructing the model to use regret vocabulary get outputs with more regret vocabulary.

**Serious: Exploratory tests reported without correction, alongside "confirmatory" framing.**
- Section 4.1 reports uncorrected Welch $t$-tests as primary evidence and labels them "exploratory" — but the abstract and conclusion present these effect sizes as the headline contribution. The actual LME (which IS the correct test) finds no significant effect on lexical markers ($p=0.18$–$0.92$ for all lexical outcomes). The paper frames this as an interesting dissociation, but it actually means **the primary H1 claim (deprivation raises CF/regret word rates) is not supported by the confirmatory analysis.**

**Serious: The N=1084 figure is contested.**
- The paper reports $N_\text{total}=1084$ with 299/378/407 per condition, but the LME is run on $N=216$ with balanced 72/72/72. The six-batch expansion is only partially analyzed. Which dataset the claimed $z=11.28$ result comes from is not reproducible.

**Moderate: Single annotator human validation.**
- The $N=36$ human annotation subsample is annotated solely by the first author. No inter-rater reliability (Cohen's κ, Krippendorff's α) is reported. The claimed $d=4.49$ is therefore not a validated measure — it could reflect annotator bias aligned with experimental expectations.

**Moderate: Prompt confound inadequately addressed.**
- The deprivation prompt explicitly says "write... including what was lost and the emotions that remain." This is not a framing manipulation — it is a direct emotional-content instruction. The paper acknowledges this but argues the minimal-pair ablation addresses it; however, the ablation shows deprivation effects are model-heterogeneous and topic-dependent, which undermines rather than supports the causal claim.

**Moderate: Response length confound acknowledged but not corrected.**
- Gemini produces ~19 token responses vs. GPT-4o's ~125 tokens. Per-100-character normalization amplifies single keyword matches 6x in short responses. The $2.5\times$ Gemini/GPT-4o rate difference is likely substantially explained by this artifact, yet it is presented as evidence of "alignment differences."

**Minor: Temperature as a factor is included but never analyzed meaningfully.**
- Temperature (0.2 vs. 0.7) is in the LME but shows no effect anywhere ($p=0.62$–$0.89$). This factor adds design complexity and dilutes cell sizes with no apparent payoff.

---

#### Significance (2/5)

- **The core finding — that prompts asking for regret produce regret-like outputs — is trivially expected.** The paper's own limitations section acknowledges this. Advancing this to a top-tier venue requires either (a) a surprising failure of this expectation, (b) a mechanistic explanation, or (c) actionable safety/alignment implications with clear empirical grounding. None of these are adequately delivered.
- The "novel dissociation" between semantic bias and lexical markers is potentially interesting but is undermined by the artifact concern with the semantic bias metric (token overlap ≠ semantic similarity).
- The cross-model replication result (H3) is directionally supported but magnitude heterogeneity (2.5×) is unexplained and may be a measurement artifact.
- No comparison to a baseline LLM that was NOT prompted with emotional framing is made against a realistic use case. The practical implication for "safety" (cited in intro) is gestured at but not demonstrated.
- Prior work that substantially overlaps is not adequately discussed: studies on prompt injection of emotional tone (e.g., RLHF-aligned models' sycophantic affect matching, persona-conditioned generation studies).

---

#### Presentation (3/5)

- The abstract is dense and contains statistical claims ($z=11.28$) that cannot be verified from the repository data files — this is a significant credibility issue at review time.
- Figure 1 (design diagram) is clear and well-constructed.
- Figure 2 (bar chart) shows "Bias ×0.1" in the caption, but the y-axis label says "Mean rate" with no indication of the scaling. The neutral bar for "Bias" shows −0.475 which already seems to be the un-scaled value; the caption's ×0.1 note is confusing.
- The paper presents two separate LME specifications (Eq. 1 in §4.3 vs. Eq. 2 in §4.5) with different formulas and different reported results. This is confusing and suggests the analysis evolved without cleanup.
- The "Confirmatory LME analysis" subsection (§4.5) appears to repeat results already reported in §4.3 with slightly different framing. This redundancy inflates the apparent rigor.
- The limitations section is genuinely honest and well-written — this is a strength.
- Table 3 (results) has SD values with inconsistent formatting (e.g., neutral regret SD=0.00 but actual data shows non-zero variance in some batches).
- The IEEEtran format is unusual for an NLP/AI venue; target venue formatting would be expected (ACL style, EMNLP style).

---

### Actionable Directions

1. **Fix the data integrity issue first.** Reconcile the $N=216$ LME (in the actual data files) with the $N=1084$ LME claimed in the paper. Rerun the confirmatory LME on the full, properly analyzed dataset with verified Gemini marker values (not zero-imputed). Report honest $z$-statistics. If the LME on the full dataset doesn't replicate $z\approx11$, revise claims accordingly.

2. **Replace the bag-of-words "semantic bias" metric with an actual embedding-based semantic similarity.** Use a Korean sentence encoder (e.g., KoSBERT, KoBERT, or multilingual-e5) to compute cosine similarity against regret/neutral prototype sentences rather than token bags. This would address the tautology concern and make the "semantic layer dissociation" finding credible. Additionally, validate this metric against the human annotation subsample with an independent rater.

3. **Reframe the contribution around the dissociation finding, not the trivial H1.** The potentially interesting result is that counterfactual framing (which does NOT explicitly ask for regret) elevates semantic regret space comparably to deprivation framing — IF the metric is valid. This is a non-obvious finding with implications for how models represent counterfactual reasoning. Reframing around this, with a proper semantic metric, could produce a genuine contribution. Add at least one independent rater for the N=36 annotation subsample and report Cohen's κ.

---

### Verdict: Strong Reject

**Rationale:** The paper's primary quantitative claims in the abstract and conclusion are not reproducible from the provided data files. The semantic bias metric is potentially a measurement artifact rather than a genuine measure of semantic similarity. The confirmatory LME does not support the primary hypothesis (lexical markers) and the headline effect sizes appear to come from either an undisclosed analysis version or a different N. The research question, while stated carefully, produces findings that are largely expected. These are not issues of polish — they are fundamental to the paper's validity. The authors should rerun the full analysis with verified data, correct the metric, and resubmit with honest claims aligned with what the confirmatory analysis actually shows.

---
