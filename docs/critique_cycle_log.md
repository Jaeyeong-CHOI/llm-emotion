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
