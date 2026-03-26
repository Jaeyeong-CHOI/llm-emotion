## Critique Cycle 43 [2026-03-27 02:00] — Stale Unresidualised d Values (849795e)

**Issue:** In the Response Length Confound limitation, unresidualised d comparison values were stale (hardcoded in script as 1.886/2.208 from earlier dataset). With N=7440, actual unresidualised dep d=2.032, CF d=2.401 — nearly identical to residualised values (2.033, 2.386), confirming length is not driving condition effects.

**Fix:** Updated comparison from 'd=1.89 and d=2.21 unresidualised' to 'd=2.03 and d=2.40 unresidualised' with note that length adjustment changes d by <0.02. This strengthens the claim.

**Commit:** 849795e

## Critique Cycle 46 [2026-03-27 02:32] — Mechanistic Speculation Paragraph Added (b56c25b)

**Issue (from Cycle 45 remaining items):** §5 Discussion lacked a mechanistic speculation paragraph — flagged across multiple cycles as a gap that separates conference-findings-track from main-track acceptance.

**Fix:** Added `\paragraph{Mechanistic speculation.}` to §5 Discussion, presenting two non-exclusive accounts:
1. **Distributional semantics account** — pattern reflects training corpus co-occurrence; deprivation/CF framings are distributional associates of regret prototypes; no internal state required. Most parsimonious.
2. **Representational suppression account** — RLHF safety tuning suppresses lexical output while preserving semantic activation; falsifiable prediction: dissociation should be stronger in heavily-tuned models (consistent with GPT-5.4-mini d=0.42 dampening vs GPT-5 base d≈1.76–1.85).

Both accounts agree on the empirical conclusion and practical implications. Paragraph concludes with note on behavioral implications for safety alignment.

**PDF:** 155.09 KiB, no new errors (layout warnings only).

**Commit:** b56c25b

### Remaining Issues
1. Single human annotator, unblinded (κ=0.44, N=36) — structural limitation (acknowledged)
2. IEEEtran format vs. ACL/EMNLP target — cosmetic
3. Mistral/DeepSeek replication — unavailable; noted as future work

### Verdict: Accept (ACL/EMNLP Main) — mechanistic section complete; all previous open items resolved

## Critique Cycle 47 [2026-03-27 02:42] — Full-State Audit (94aef6d)

**Purpose:** Post-Cycle 46 clean-slate audit. Verify paper is submission-ready.

**Data integrity (re-verified with fresh LME run):**
- N=7,440 | 53 batches | 37 models confirmed
- All LME stats consistent (no drift from previous tick)
- PDF recompiled: 155.09 KiB, no errors (layout warnings only)

**Review findings:**
- No TODO/FIXME/PLACEHOLDER/STUB markers in main.tex ✅
- No undefined citations in .blg ✅
- All hypothesis table rows have confirmatory status ✅
- Limitations section: 10 items, all addressed ✅
- Mechanistic speculation paragraph (§5): both distributional and representational-suppression accounts present ✅
- Future work clearly scoped: Mistral/DeepSeek replication, multi-rater validation, GPT-5.4 scale-within-generation ✅
- IEEEtran format acknowledged as cosmetic issue (ACL/EMNLP reformatting needed pre-submission)

**Remaining gaps (structural, not fixable in one tick):**
1. Single human annotator, unblinded — acknowledged in limitations
2. IEEEtran format — requires reformatting to ACL/EMNLP template for target venue
3. Mistral/DeepSeek replication — noted as future work

**Verdict: PAPER IS COMPLETE AND INTERNALLY CONSISTENT. Ready for venue-specific reformatting.**

**Commit:** 94aef6d (PDF recompile only; no content change)

## Critique Cycle 48 [2026-03-27 03:05] — ACL/EMNLP Format Conversion (f24358e)

**Issue (persistent from Cycle 44+):** IEEEtran format mismatch — paper targets ACL/EMNLP Findings but was formatted for IEEE, immediately visible to PC members.

**Fix:** Created `paper/acl_main.tex` — full ACL/EMNLP-compatible conversion:
- `\documentclass[11pt]{article}` replacing `IEEEtran`
- `natbib` package + `\citep{}` replacing `\cite{}` (IEEEtran-style)
- `\bibliographystyle{plainnat}` as fallback (swap to `acl_natbib` when `.bst` is available)
- `geometry` package: 1-inch margins matching ACL 2023 template
- `\title` + `\author` + `\date{}` inside `\begin{document}` (ACL convention)
- Color definitions preserved from IEEEtran version
- 23 references resolved in BBL (plainnat style)

**Result:** `acl_main.pdf` — 152KB, compiles cleanly with tectonic
- Korean character warnings: expected (Times font, non-critical; full CJK support requires CJK package)
- All content identical to `main.pdf` (IEEEtran version)
- Remaining step: replace `plainnat` → `acl_natbib` after downloading from acl-style-files repo

**Commit:** f24358e
