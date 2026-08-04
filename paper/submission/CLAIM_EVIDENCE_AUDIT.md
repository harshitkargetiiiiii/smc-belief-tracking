# Claim → evidence audit (audit 1)

Scope: every empirical, security, reproducibility, backend, mutation, and functional
claim in `paper/main.tex` at HEAD `4081a95`. "Reproduced this gate" = re-executed in
audit 4 (`paper/reproduce.sh` / `paper/heldout/reproduce.sh`, both EXIT 0). Evidence
paths are relative to the repo root and were confirmed present at HEAD.

## A. Functional / artifact claims

| # | Claim (main.tex) | Evidence at HEAD | Supports wording? | Note |
|---|---|---|---|---|
| A1 | Fixture (2 invocations) + 2 further states reproduce the pseudo-oracle | `conformance/harness.py`, `results-*.txt` | yes | harness **4/4** reproduced this gate |
| A2 | Bounded **228-case** matrix (216 single + 12 carried) all match the oracle | `conformance/coverage.py`, `results-coverage.txt` | yes | **228/228** reproduced this gate; wording says "constructed test matrix, not general coverage" — accurate |
| A3 | Conformance package **92 tests** (46 functional + 46 delivery-gate) + **9 reference test functions (25 collected)** = **117 collected** | `pytest reference/ conformance/` | yes | Collection **92 + 25 = 117** verified this gate; wording now exact |
| A4 | **Five** committed executable negative controls rejected | `conformance/mpc/threshold_smc_{leaky,subleak,namespoof,openfalse,openfalse_vec}.mpc`, `private_run.py` gate | yes | all 5 rejected this gate |
| A5 | Recomputed, hash-bound evidence (source hash + delivery sig + oracle case-table) | `conformance/validate_evidence.py` | yes (as *self-consistency under trusted CI*, not adversarial integrity — the text says exactly this) | `--recompute` OK this gate |

## B. Mutation-study claims

| # | Claim | Evidence | Supports wording? | Note |
|---|---|---|---|---|
| B1 | B0–B6/S1 detection matrix; five controls map to B0–B3,B5; **B4 synthetic**, **B6 reconstructed**, **S1 semantic** | `paper/mutations/detection_matrix.json`, `README.md` | yes | matrix recomputed this gate |
| B2 | **B6 is REJECTED** (naive `call_arg` realization caught) — *not a bypass of the final linter* | `detection_matrix.json` (B6), `reproduce_mutations.py` | yes | reproduced (B6 caught) |
| B3 | Honest build passes secret operands via `call_tape`/`call_arg`, no memory | `detection_matrix.json` meta; `reproduce_mutations.py` honest-channel check | yes | reproduced (call_tape×3 / call_arg×3, no subtape memory) |
| B4 | **S1** passes the linter, fails the oracle **end-to-end** at the pin; mismatch `[0,1,2]` on `(0,0,0)/p1_is_max` | `paper/mutations/s1_runtime_evidence.json` | yes | reproduced (S1 lint-PASS + runtime mismatch) |
| B5 | The studied opcode-identity/channel-blocklist linter **cannot be promoted to a general non-leakage checker** | argument grounded in B6 + the shared-open-instruction fact | yes — **interpretive conclusion, correctly scoped** | Not a single measurement; it is a reasoned claim from B6 + backend facts, and the text hedges it precisely ("*studied* … cannot be *promoted*"). Acceptable. |

## C. Held-out evaluation claims (§3.2, §4.3)

| # | Claim | Evidence | Supports wording? | Note |
|---|---|---|---|---|
| C1 | Pre-registered, out-of-sample, run once; **not** independent-adversary | `paper/heldout/PLAN.md`; prereg `d3d11e4` → results `9e22007` (both in-branch history) | yes | two-phase history present; wording hedged correctly |
| C2 | **H-R1, H-R3 rejected; H-R2 (multiset-preserving permutation) accepted** | `paper/heldout/results.json` | yes | reproduced this gate |
| C3 | **H-R2** = source-realizable *structural* false accept; transcript parser caught **this concrete build** (foreign `PRIV j`); *no general permutation claim* | `results.json` (`runtime_layer_reject`), `README.md` | yes | reproduced (`runtime_rejects=[H-R2]`); generality explicitly disclaimed |
| C4 | **H-V1/H-V2/H-V3** semantic: linter PASS, oracle FAIL | `results.json` | yes | reproduced (`semantic PASS + oracle_fail`) |
| C5 | **H-O3** and synthetics = manifest-level rule-coverage probes, unproven realizability, no detector rate | `results.json`, `README.md` | yes | H-O3 always labelled synthetic/manifest-level |
| C6 | Compiler blocks the naive direct cross-tape reference (H-X1) | `results.json` compile_error ("Register from other tape") | yes | reproduced (compile-invalid) |

## D. Reproducibility / backend claims (§3.2)

| # | Claim | Evidence | Supports wording? | Note |
|---|---|---|---|---|
| D1 | Frozen artifact reproduces from a fresh checkout + fresh pinned build (117, 4/4, 228, evidence recompute, B4/B6/S1) | `paper/REPRODUCIBILITY.md` | yes | reproduced this gate (fresh clone) |
| D2 | **Normalized per-tape `manifest_signature` values recompute** — *not* raw binaries/assembly byte-for-byte | `REPRODUCIBILITY.md`, `detection_matrix.json` | yes — exact-strength wording; the negative ("not raw bytes") is stated | reproduced |
| D3 | Backend observations **replicate on v0.4.3 `26a60536`** (shared open family, honest `call_tape`/`call_arg`, B6, S1); **two versions only, not version-independent** | `paper/CROSS_VERSION.md` | yes | ⚠ **relies on archived evidence** — the v0.4.3 build was **not re-executed in this gate** (`reproduce.sh` builds only the pin). The claim rests on `CROSS_VERSION.md`. Flagged, not a defect: the wording is already hedged to "two versions". |

## Findings

- **No unsupported claim** and **no wording stronger than its evidence** was found; every empirical statement maps to a committed file that exists at HEAD, and all but one (D3) were re-reproduced this gate.
- **Interpretation-reliant (but correctly scoped):** B5 (the "cannot be promoted" boundary conclusion) is an argument, not a measurement — appropriately hedged. Acceptable.
- **Archived-evidence-only this gate:** D3 (cross-version v0.4.3) — the manuscript's citation `paper/CROSS_VERSION.md` is correct and the claim is hedged to two versions, but a cold reviewer should note the v0.4.3 result is not re-run by `reproduce.sh`. **Non-blocking.**
- **Evidence pointers checked:** all `\repo{}` targets cited for empirical claims (`REPRODUCIBILITY.md`, `CROSS_VERSION.md`, `paper/heldout/*`, `paper/mutations/*`, `conformance/*`) exist at HEAD. No stale/wrong pointer found. (Appendix B's claim→evidence table matches this audit.)
