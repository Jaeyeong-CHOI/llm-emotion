# LLM-Emotion Paper Critique Log

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
