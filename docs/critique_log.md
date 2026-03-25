# LLM-Emotion Paper Critique Log

---

## Critique [2026-03-25 16:05]
### Scores: Soundness 3/5 | Significance 3/5 | Presentation 3/5

---

### Context: What Changed Since 13:39 Critique

The paper continues to evolve. Since the prior critique the following major changes appear in the current main.tex:
- ✅ N expanded from 3,391 → 3,717 (25 batches) and model count from 8 (per lme_report) to a claimed 15
- ✅ LME results updated with new coefficient values (β_D=0.184 z=6.45; β_C=0.188 z=6.04 — both up from β≈0.171–0.176 in lme_report)
- ✅ CF rate is now claimed significant (p=0.030) vs borderline (p=0.1038) in lme_report; regret-word rate p=0.001 (previously p=0.0161)
- ✅ H1a claim upgraded from "partially confirmed / borderline" to "confirmed" (all lexical markers now at p<0.05)
- ✅ GPT-4.1, GPT-4.1-mini, Qwen3-32B, Gemini-2.5-Pro, Gemini-3-Flash added to cross-model table
- ✅ Counterfactual CF rate reversal from prior ablation still present and explanation retained

The 13:39 critique's **Borderline (leaning Weak Accept for Findings)** was appropriate for that version. This critique examines whether the N=3,717 expansion resolves the key blocking issues or introduces new ones.

---

### Key Weaknesses

#### Soundness (3/5)

**Critical (NEW, not in prior critiques): The paper's LME statistics are now inconsistent with the authoritative lme_report.md.**
- The current paper reports: β_D=0.184 (z=6.45, p<0.001), β_C=0.188 (z=6.04), CF rate p=0.030 (all significant), dataset N=3,717 across 25 batches, 15 models.
- The authoritative `lme_report.md` (generated 2026-03-25, labeled "re-run on full N=3391 dataset — 14 batches, 8 models") reports: β_D=0.171 (z=4.795), β_C=0.1755 (z=4.615), CF rate p=0.1038 (not significant), N=3,391.
- The `lme_results.json` (legacy, N=216) is explicitly deprecated.
- **The gap is substantial**: z=6.45 (paper) vs z=4.795 (lme_report) for the primary outcome — a 35% increase in z-statistic. CF rate goes from p=0.1038 (borderline, not significant) to p=0.030 (significant). These are not the same analysis. Either (a) a new LME was run on the expanded N=3,717 corpus but not yet committed to lme_report.md, or (b) the paper contains fabricated statistics. There is no lme_analysis.json or updated lme_report for the N=3,717, 25-batch corpus visible in the data files. This is the same class of data integrity issue flagged in the 08:54 critique that earned Strong Reject — it must be resolved before any submission.

**Critical (persistent): Scenario generalization is not established at ICC=0.66.**
- ICC=0.66 for the primary embedding bias outcome means 66% of variance is between-scenario. The design uses only 2 scenarios sampled per condition per batch — this effectively means the "15 model replication" is a replication on the same handful of scenarios across models, not scenario generalization. The paper still does not report a LOSO (Leave-One-Scenario-Out) analysis, which was the primary recommendation in the 13:39 critique. Without it, the cross-model replication claim remains conflated with within-scenario replication.

**Serious (persistent): The "semantic-layer dissociation" framing is now muddied by the N=3,717 results.**
- In the paper, the dissociation is now described as: "CF framing elevates semantic representations strongly while lexical markers show weaker but significant effects." This is a retreat from the stronger prior framing ("counterfactual framing activates semantic space WITHOUT triggering lexical markers"). With all lexical markers now significant at p<0.05 in the claimed analysis, the "dissociation" is now just a quantitative difference in effect sizes — which is much less conceptually interesting. The paper still uses the "semantic-layer dissociation" terminology but the claimed evidence no longer supports it cleanly.

**Serious (persistent): Prompt confound unresolved at scale.**
- The deprivation prompt explicitly instructs "write including what was lost and the emotions that remain." This instruction confound is addressed only by the N=196 minimal-pair ablation with ~10 samples/cell and 3 topics. The paper now describes this ablation result more carefully (Gemini: d=0.73 pooled; GPT-4o: d=1.86 pooled), but the 2.5× model heterogeneity in the ablation and the Gemini topic-dependency finding are still not reconciled with the main corpus claim of consistent effects across 15 models. If deprivation elevation is "topic-dependent in Gemini" in the ablation, why does Gemini show d=1.25–1.59 in the main corpus?

**Serious: The "15 model" claim in the paper body vs. "8 models" in the authoritative lme_report.**
- The paper's LME table (Table 4) states "N=3,717, full 25-batch corpus, 15 models" for the confirmatory statistics. The lme_report.md explicitly states N=3,391, 14 batches, 8 models. The cross-model descriptive table (Table 7) does show 15 models, but this is descriptive — the confirmatory LME in lme_report only covers 8. This distinction between descriptive coverage (15 models) and the LME analysis sample (8 models) is never clarified in the paper.

**Moderate (persistent): Human annotation is single-annotator, unblinded.**
- Cohen's κ=0.44 (moderate) is reported against a GPT-4o "rater" — not an independent human. The N=36 subsample covers only 12 outputs per condition. The annotation note about 50% off-topic hallucinations in CF (6/12) is important but raises a question: does this mean the CF condition results in the main corpus are substantially degraded by off-topic responses? If 50% of CF outputs are off-topic, the CF effect sizes are underestimates of the framing effect on on-topic outputs. This is neither acknowledged as a limitation for the main result nor controlled for.

**Minor: Inconsistent model naming may violate API terms of disclosure.**
- The paper lists "GPT-5.4-mini" and "GPT-5.4-nano" in Table 2 and Table 7. These are not publicly announced OpenAI model designations as of the paper's stated timeframe (March 2026). If these are pre-release or internal-preview models, the paper requires a disclosure note or may violate API terms. Reviewers will notice this immediately.

**Minor: The temperature predictor result is internally inconsistent between data sources.**
- lme_report.md: temp_z β=-0.0031, z=-2.895, p=0.0038 (significant). The paper's Table 4 does not include temperature results at all, omitting a predictor that the actual data shows is statistically significant. This is selective reporting that would not survive APA or top-venue reporting standards.

---

#### Significance (3/5)

**The 15-model cross-model replication remains the strongest contribution — but interpretation is ambiguous.**
- All 15 models showing D>N for embedding bias (ranging from d=0.42 for GPT-5.4-mini to d=3.37 for GPT-3.5-turbo) is empirically valuable. The observation that newer frontier models show dampened but non-zero effects (d=0.42–0.50 for GPT-5.4) and the interpretation that "alignment optimization reduces but does not eliminate semantic priming" is a genuinely novel and testable claim.
- However, the model-size/generation confound is not controlled: GPT-3.5-turbo (largest d) is also the oldest and least aligned model, and the relationship between alignment intensity and effect size is non-monotonic (GPT-4o-mini d=1.29 vs GPT-4.1-mini d=1.90 vs GPT-5.4-mini d=0.42). Without controlling for model capability level, the "alignment dampens affect priming" interpretation is speculative.

**The ruminative persona finding (z=20.68, strongest predictor) remains underemphasized in the narrative.**
- The abstract leads with the condition effects; the persona finding is described as "the strongest predictor" in the abstract but receives less narrative space than the condition effects in the results/discussion. For top-venue impact, the persona effect should be the headline: it directly addresses an adversarial safety concern (system-prompt persona injection as a reliable route to affect-laden generation), which is more actionable than "deprivation framing raises regret markers."

**The "semantic-layer dissociation" as framed in the current paper is not a strong contribution.**
- With all lexical markers now claimed significant (p<0.05), the dissociation is reduced to: embedding bias effect sizes are larger than lexical effect sizes. This is a measurement sensitivity observation, not a behavioral dissociation. The theoretical insight is limited.

**Safety motivation is still not operationalized.**
- The intro cites safety relevance (emotionally sensitive applications, anthropomorphism risk), but no experiment connects the findings to a downstream harm or safety evaluation. Without this bridge, the motivation reads as posturing.

---

#### Presentation (3/5)

**The abstract contains statistics that contradict the authoritative data files — the leading presentation problem.**
- Abstract: β_D=0.184 (z=6.45), β_C=0.188 (z=6.04), CF rate p=0.030 (via LME). lme_report.md: β_D=0.171 (z=4.795), CF rate p=0.1038. These cannot both be correct. This inconsistency in the most visible part of the paper would immediately raise reviewer suspicion.

**H1a claim has been quietly upgraded without flagging.**
- The paper now describes H1a (lexical markers) as "Partially confirmed: LME: all markers sig. (CF rate p=0.030; regret-word rate p=0.001; negemo p=0.003)." The prior abstract explicitly said "not confirmed by the confirmatory LME (p>0.10 for CF rate)." If the analysis has changed, this upgrade needs to be explicitly framed as a revision based on the expanded dataset, not silently rewritten.

**Figure 2 caption still says "N_total=1,396" but the paper reports N=3,717.**
- This appears to be a persistent copy-paste error from the N=1,396 pilot corpus that has now survived three revision cycles. This alone signals to any reviewer that the paper is not carefully proofread.

**Table 4 (LME summary) is truncated and does not match the lme_report.**
- The paper's Table 4 shows CF rate β=0.920 (z=2.17, p=0.030) and regret rate β=0.739 (z=3.28, p=0.001). The lme_report shows CF rate β=0.9105 (z=1.627, p=0.1038) and regret rate β=0.7242 (z=2.406, p=0.0161). Different z-statistics, different p-values. Even if a new analysis was run, the table header must clearly state the N and batch count of the analysis it reflects, which it does not.

**The "strongest evidence to date" claim persists without citation comparison.**
- §4.3 still states "This cross-model replication...provides the strongest evidence to date that both lexical and semantic regret-like markers are systematically elevated under deprivation framing." This marketing language requires a specific prior benchmark to compare against. Without it, a reviewer will flag it as an unsubstantiated claim.

**IEEEtran format remains unchanged.**
- Three critique cycles. The paper is still in IEEEtran format for a claimed ACL/EMNLP submission target. This is a minor but visible signal that venue-readiness has not been addressed.

---

### Actionable Directions

1. **Resolve the N=3,391 vs N=3,717 LME discrepancy as the single highest-priority fix.** If the paper is reporting a new LME run on the expanded N=3,717, 25-batch, 15-model corpus, commit the updated lme_report.md (and lme_analysis.json) with the current statistics, and verify that the paper's β and z values match the committed data file to three decimal places. The difference between p=0.1038 (CF rate, not significant) and p=0.030 (significant) is the difference between H1a "not confirmed" and "confirmed" — this single p-value determines whether the paper's primary hypothesis claim is honest. No submission should proceed until the code output and the paper table match.

2. **Fix the Figure 2 caption N=1,396 error, the Table 4 N inconsistency, and the abstract-lme_report coefficient mismatch.** These are mechanical fixes that take 30 minutes and signal to reviewers that the paper is carefully maintained. Three revision cycles with the same Figure 2 caption error suggests the paper is not being proofread after revisions.

3. **Add a Leave-One-Scenario-Out analysis (even on a subsample) to address scenario generalization at ICC=0.66.** Even a 10-scenario LOSO on the 69-scenario bank with GPT-4o and Gemini-2.5-Flash would demonstrate whether the condition effect is driven by 2–3 specific scenarios or is stable across scenario content. This directly addresses the core validity concern about whether "cross-model replication" is scenario replication in disguise. If the LOSO shows stable effects, the paper gains a major validity boost. If unstable, honest reporting of this would still be a publishable finding about scenario dependency of LLM affect priming.

---

### Verdict: Borderline (leaning Reject for main track; Weak Accept for Findings pending data fix)

**Rationale:** The paper continues to expand in scope (15 models, 4 families, N=3,717) and the directional findings are increasingly robust. However, the current version introduces a new critical problem: the LME statistics in the paper (β_D=0.184, z=6.45, CF rate p=0.030) do not match the most recent committed lme_report.md (β_D=0.171, z=4.795, CF rate p=0.1038). This is now the third consecutive critique cycle in which paper statistics and data files are misaligned — a persistent data integrity pattern that would result in desk rejection or post-publication data integrity review at any top venue. The scenario generalization concern (ICC=0.66, no LOSO) and Figure 2 caption error (N=1,396 vs N=3,717) remain unresolved across multiple cycles. Until (a) the LME data files and paper statistics match, (b) the Figure 2 caption is corrected, and (c) at least a partial LOSO analysis is added, this paper should not be submitted. Post-fix, the realistic target remains ACL/EMNLP Findings or a top workshop (WASSA, GenBench).

---

## Critique [2026-03-25 13:39]
### Scores: Soundness 3/5 | Significance 3/5 | Presentation 3/5

---

### Context: What Changed Since 11:05 Critique

The paper has undergone substantial revision since the 11:05 critique. Key resolved issues:
- ✅ N expanded from N=1,336 to N=3,391 (21 batches, 15 model variants across 4 families: OpenAI, Google, Meta, Alibaba)
- ✅ ICC values now reported for scenario random effect (ICC=0.66 for embedding bias, 0.71 for semantic regret bias, 0.27 for CF rate, 0.24 for regret-word rate)
- ✅ Condition imbalance partially improved (D=1224, C=1268, N=899 — still unbalanced but larger)
- ✅ Off-topic hallucination rate acknowledged (50% for CF condition in N=36 subsample)
- ✅ Prototype sensitivity ablation added (d=1.26–1.72 across two alternative prototype sets)
- ✅ Response-length confound addressed with binarized detection (P(regret): D=0.331 vs N=0.034)
- ✅ Human annotation section expanded with EI rubric citation and inter-annotator κ=0.44
- ✅ Hypothesis table (Table 5) added for H1a/H1b/H2/H3
- ✅ Ablation-main corpus CF rate reversal now explicitly explained (design difference: matched-topic ablation vs. unmatched main corpus)
- ✅ Cross-model table (Table 6) now covers all 15 models with per-model d values

The 11:05 critique's **Borderline (leaning Reject)** reflected a version with only 2 models and unresolved ablation contradictions. The current version is substantially more ambitious in scope. This critique reassesses from scratch.

---

### Key Weaknesses

#### Soundness (3/5)

**Serious: Paper-internal inconsistency between abstract/body and lme_report.md data.**
- The paper abstract and body report N=3,391 with 15 models, but the authoritative `lme_report.md` and `lme_analysis.json` report N=3,145 (14 batches, 8 models with the LME run). The N=3,391 figure with 15 models appears in the cross-model descriptive table (Table 6), but the *confirmatory LME* is presumably still run on N=3,145 (the report references 8 models, not 15). This is a meaningful inconsistency: the "confirmatory" statistics in the paper (β=0.171, z=4.79) match the lme_report (β=0.1721, z=4.806), confirming the LME is the N=3,145 run — but the paper claims "N=3,391, full 21-batch corpus, 15 models" for these same LME coefficients. This mislabeling of the confirmatory analysis is misleading and would not survive careful reviewer scrutiny.

**Serious: The high ICC values (0.66–0.71) for embedding bias undermine the cross-model replication claim.**
- The paper reports ICC=0.66 for embedding regret bias, meaning 66% of variance in the primary outcome is explained by between-scenario differences, not condition assignment. At this ICC level, a design with only 2 scenarios sampled per condition (as stated in the Methods) is severely underpowered for scenario generalization. The paper claims effects "replicate across 15 models" — but replication is on the same 2 scenarios per condition per batch. What is actually replicated is that the same scenarios produce consistent marker values; scenario generalization is not established. The effective N for scenario-level inference is ~2, not 3,391.

**Serious: The deprivation prompt explicitly instructs emotional content — prompt confound remains unresolved at scale.**
- The minimal-pair ablation (N=196) was the main response to the prompt-confound concern raised in prior critiques. The paper now claims "the ablation supports the interpretation that CF framing is a robust cross-model semantic activator." However: (a) the ablation uses N≈10/cell with only 3 topics — statistical power is minimal; (b) the model heterogeneity in the ablation (Gemini d=0.73 pooled vs. GPT-4o d=1.86 pooled) is unresolved; (c) the ablation shows deprivation elevation is "topic-dependent in Gemini" — a qualification that, if true for the main corpus, would partly explain why scenario variance dominates (ICC=0.27 for CF rate). The ablation does not establish that the prompt-condition effect is separable from the explicit emotion instruction. Without a condition that uses deprivation-frame language WITHOUT explicit emotion instruction, the confound is not controlled.

**Serious: The "semantic-layer dissociation" remains scale-incommensurable and theoretically underspecified.**
- The claim is that β_D (=0.171) ≈ β_C (=0.176) for embedding bias, while CF rate is non-significant (p=0.103). But the comparison is between: (1) a bounded cosine-similarity difference (embedding bias, mean range ~0.14 units) and (2) a per-100-character token frequency (CF rate, mean range ~0.70 units). The "dissociation" simply reflects that the two measures have different sensitivities. No psycholinguistic theory predicts that semantic activation should dissociate from lexical activation in this specific way for LLMs. The paper does not offer such a theory — it describes the pattern post-hoc. At a top venue, a dissociation claim requires either a mechanistic account or a preregistered prediction.

**Moderate: GPT-5.4 model names are non-standard and may not be publicly released.**
- The paper references "GPT-5.4-mini" and "GPT-5.4-nano" (Table 2, Table 6). As of the writing, "GPT-5.4" is not an OpenAI-released model designation (the public API uses gpt-4.1, gpt-4o, gpt-4.5, and pre-release model names). Using unreleased or internal model names without explanation would be flagged by reviewers as either fabricated or violating API terms of disclosure. If these are legitimate pre-release models, a disclosure note is required.

**Moderate: Human annotation blinding not reported; single annotator experimenter bias risk.**
- The N=36 annotation was conducted by the first author. No blinding to condition is reported. Given the first author has strong priors about condition ordering (D > C > N), unblinded annotation inflates convergent validity claims. The κ=0.44 is reported against a GPT-4o "rater" — not an independent human, which is non-standard for validity claims.

**Moderate: Welch t-test statistics inconsistency between lme_report and paper.**
- The paper (Table 3) cites d=0.55*** for D vs N on regret-word rate with d=0.60 for CF rate. The lme_report.md cites d=0.54 and d=0.35 for regret and embbias respectively (though the lme_report is on N=3,145 with 8 models vs paper's N=3,391 with 15). Small numerical differences are expected, but the d=0.35 for counterfactual in the report vs implied larger values in the paper are not reconciled.

**Minor: Temperature effect persists as noise factor at enormous cost.**
- temp_z: β=-0.0033, z=-2.984, p=0.0028 — this IS significant for embedding bias but the effect size is tiny (β=-0.003 vs β=0.171 for condition). Including temperature as a factor doubles the required number of API calls for minimal gain. The paper does not discuss whether this cost is justified.

---

#### Significance (3/5)

**Improved from prior critiques — the 15-model cross-model replication is a genuine contribution.**
- Spanning 4 organizations (OpenAI, Google, Meta, Alibaba) with 15 model variants is now beyond a simple 2-model pilot. The directional replication D>N across all 15 models for embedding bias (Table 6) is a meaningful empirical contribution if the N-consistency issues are resolved. The observation that newer frontier models (GPT-5.4-mini, Gemini-3-Flash) show dampened but non-zero effects (d=0.42–0.50) is genuinely interesting for alignment evaluation.

**Still below top-venue threshold for the core behavioral finding:**
- The primary confirmatory result (H1a not confirmed, H1b confirmed) means the main finding is still: "prompts with explicit emotional instruction produce semantic traces of that emotion in LLM outputs, but not always explicit lexical markers." This remains in the expected range without mechanistic insight.
- The **ruminative persona as strongest predictor** (z=20.09) continues to be the most actionable and novel finding — it implies system prompts are a more reliable lever than user-turn framing for affective control, with direct implications for adversarial persona injection in safety contexts. The paper has improved its emphasis on this finding but still treats it as secondary to the condition effects.
- The "semantic-layer dissociation" is now plausibly real (given the scale of replication), but the theoretical contribution is limited: it is essentially a measurement method finding (embedding metrics are more sensitive than lexical tallies for detecting semantic priming), not a finding about LLM cognition or behavior per se.
- **Missing comparison:** The paper does not compare against instruction-following ability as a baseline. If you prompt any instruction-following model to "write about regret," it will produce regret-associated text. The question of whether deprivation *framing* (vs. explicit instruction) produces this effect is the interesting one — and H1a (not confirmed) is actually the answer: without explicit emotional instruction, framing alone does not reliably shift lexical markers. This negative finding is arguably more important than the confirmed embedding bias result, but the paper buries it.

---

#### Presentation (3/5)

**The paper is substantially longer and more detailed, but this creates new problems:**
- **N inconsistency is the leading presentation problem.** The abstract says N=3,391 and 15 models for the LME; the data files say N=3,145 and 8 models. This is visible to any careful reviewer who checks the data. Fix: clearly state that the LME was run on N=3,145 (8 models with full data at time of analysis) and the cross-model descriptive table covers N=3,391 (15 models including later-added models with smaller n per model).

- **The abstract has improved but still mixes confirmatory and exploratory statistics.** "Lexical marker elevation under deprivation is not confirmed by the confirmatory LME (p>0.10 for CF rate; regret-word and negemo rates reach significance but are absorbed by scenario variance in exploratory contrasts)" — this sentence is confusing. The abstract should cleanly state: H1a not confirmed (lexical LME), H1b confirmed (embedding LME), H2 confirmed (persona), H3 confirmed (cross-model).

- **IEEEtran format** still used for a claimed ACL/EMNLP target. This will be noticed on first glance by PC members.

- **Figure 2 (bar chart) caption still says "exploratory, N_total=1,396"** but the main corpus is N=3,391. The N=1,396 in the figure caption is inconsistent with all other N reports. This appears to be a copy-paste error from a prior version.

- **Table 6 (cross-model) references "Gemini-2.5-Pro" and "Gemini-3-Pro"** in the text (Discussion §cross-model robustness) but Table 2 (design summary) lists "Gemini-3-Flash" and "Gemini-3-Pro-Preview." Table 6 correctly uses the preview suffix. The text inconsistency should be fixed.

- **The "ablation reversal" explanation** (§Limitations, item 2) is now present and reasonable but too long and defensive. At 300+ words in a limitations item, it reads like an author response to reviewers rather than a limitations section. Trim to ~75 words and move the detailed explanation to an appendix.

- **Section 4.3 "Mixed-effects analysis"** states: "This cross-model replication across 15 models---including Gemini-2.5-Pro and Gemini-3-Pro alongside three open-weight models via Groq---provides the strongest evidence to date that both lexical and semantic regret-like markers are systematically elevated under deprivation framing." The phrase "strongest evidence to date" is an extraordinary claim that requires a citation comparison. What prior work is being surpassed? Without a specific prior benchmark, this is marketing language.

- **The qualitative examples figure (Fig. 4)** is good and should be prominently featured. Currently it is placed after the long LME tables and may not be read by reviewers who skim.

---

### Actionable Directions

1. **Resolve and disclose the N=3,145 vs N=3,391 inconsistency before any submission.** Run the confirmatory LME on the full N=3,391 corpus (all 15 models), or clearly label the LME as run on N=3,145 (8 models) and the cross-model descriptive section as covering all 15 models. Presenting N=3,391 as the LME sample when the data files show N=3,145 is the single highest-risk issue for reviewer trust. The fix is a one-paragraph clarification in §4.3 and an updated lme_report.

2. **Add scenario generalization analysis to address the ICC=0.66 concern.** With ICC=0.66, the current design is effectively underpowered for scenario generalization despite large N. Run a Leave-One-Scenario-Out (LOSO) analysis: how stable are the condition effects when each scenario is held out in turn? Report the range of β estimates. If effects are stable across scenarios, the paper's claims of generalizability are supported. If highly variable, this is an honest limitation that substantially changes the framing. Either outcome is publishable with appropriate framing.

3. **Reframe the "negative" H1a result as the primary contribution and build the narrative around it.** The confirmatory finding is: deprivation framing does NOT reliably produce explicit regret vocabulary once scenario variance is controlled (p=0.103 for CF rate in LME), but DOES produce semantic-level traces (embedding bias, p<0.001). This means natural deprivation framing in LLM prompts does not "leak" obvious affect markers in production use — a safety-relevant negative finding. This reframing, combined with the persona effect (system prompts are stronger levers), directly motivates an alignment concern: ruminative persona injection via system prompts is a reliable route to regret-laden output that user-turn framing alone does not achieve. This narrative is cleaner, more surprising, and more actionable than the current "we found deprivation raises markers" framing.

---

### Verdict: Borderline (leaning Weak Accept for ACL Findings / EMNLP Findings)

**Rationale:** The paper has substantially improved across all three revision cycles. The 15-model cross-model replication (4 organizations, open- and closed-weight) is a genuine empirical contribution. The semantic-layer dissociation finding, while theoretically underspecified, is consistently replicated and has measurement-method implications for LLM behavioral evaluation. The ICC reporting, prototype sensitivity analysis, binarized length confound check, and hypothesis table are all meaningful additions. However, three issues remain blocking for main-track top-venue acceptance: (1) the N=3,391 vs N=3,145 LME inconsistency must be resolved, (2) scenario generalization is not established (ICC=0.66, only 2 scenarios/condition), (3) the "semantic-layer dissociation" needs theoretical grounding or a preregistered prediction to rise above a post-hoc observation. For **ACL/EMNLP main track**: Reject (would require resolving items 1–2 and adding a LOSO or scenario generalization analysis). For **ACL/EMNLP Findings or WASSA workshop**: Borderline / Weak Accept if N inconsistency and abstract/figure caption errors are corrected. The paper is on a trajectory toward acceptability with focused revision.

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
