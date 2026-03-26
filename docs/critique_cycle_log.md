## Critique Cycle 43 [2026-03-27 02:00] — Stale Unresidualised d Values (849795e)

**Issue:** In the Response Length Confound limitation, unresidualised d comparison values were stale (hardcoded in script as 1.886/2.208 from earlier dataset). With N=7440, actual unresidualised dep d=2.032, CF d=2.401 — nearly identical to residualised values (2.033, 2.386), confirming length is not driving condition effects.

**Fix:** Updated comparison from 'd=1.89 and d=2.21 unresidualised' to 'd=2.03 and d=2.40 unresidualised' with note that length adjustment changes d by <0.02. This strengthens the claim.

**Commit:** 849795e
