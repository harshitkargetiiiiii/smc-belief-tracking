# Internal consistency audit (audit 3)

Cross-checked every repeated number/fact across `paper/main.tex`,
`paper/EXTERNAL_REVIEW_BRIEF.md`, `paper/REPRODUCIBILITY.md`, `paper/CROSS_VERSION.md`,
`paper/heldout/` (PLAN.md, README.md, results.json, corpus), and the mutation evidence
(`paper/mutations/README.md`, `detection_matrix.json`). Values below were also
re-derived live in audit 4.

## Cross-file value table

| Fact | main.tex | brief | REPRODUCIBILITY | CROSS_VERSION | heldout | mutations | Verdict |
|---|---|---|---|---|---|---|---|
| Conformance collected | **92** (46+46) | — | **92** (46+46) | — | — | — | ✅ consistent |
| Reference test functions → collected | **9 → 25** | — | **25** | — | — | — | ✅ consistent |
| Total collected pytest | **117** | — | **117 passed** | — | — | — | ✅ consistent (117 collected = 117 passed) |
| Adversarial matrix | **228** (216+12) | — | **228/228** (216+12) | — | — | — | ✅ consistent |
| Named-case harness | **4/4** | — | **4/4** | — | — | — | ✅ consistent |
| Executable negative controls | **five** (→B0–B3,B5) | 5 | **5** (leaky,subleak,namespoof,openfalse,openfalse_vec) | — | — | 5 committed | ✅ consistent |
| Mutation accounting | B0–B6 + S1; B4 synthetic, B6 reconstructed | ✓ | — | — | — | ✓ (detection_matrix) | ✅ consistent |
| Held-out corpus size | **22** | — | — | — | **22** | — | ✅ consistent |
| H-R1/H-R3 reject, H-R2 accept | ✓ | ✓ | — | — | results.json ✓ | — | ✅ consistent |
| H-V1/H-V2/H-V3 PASS/oracle-FAIL | ✓ | ✓ | — | — | results.json ✓ | — | ✅ consistent |
| H-O3 synthetic/manifest-level/unproven | ✓ | ✓ | — | — | ✓ | — | ✅ consistent |
| MP-SPDZ pin | `9d809599` | `9d809599` | `9d809599` | `9d809599` | `9d809599` | `9d809599…` | ✅ consistent |
| Cross-version revision | `26a60536` (v0.4.3) | `26a60536` | — | `26a60536` (v0.4.3) | — | — | ✅ consistent |
| Preregistration SHA | `d3d11e4` | `d3d11e4` | — | — | `d3d11e4…` | — | ✅ consistent |
| Results SHA | `9e22007` | `9e22007` | — | — | `9e22007` | — | ✅ consistent |
| Artifact baseline | `305a3a8` | `305a3a8` | `305a3a8` | — | `305a3a8` | `305a3a8` | ✅ consistent |

## Terminology / denominator checks

- **No aggregate detector-rate remnants.** `2/3`, `10/12`, `0.67`, `0.83`, and the
  phrase "detection rate" as a metric are **absent** from `main.tex`. The held-out
  README carries the withdrawn-metric note; the manuscript reports the recipient result
  only at exact strength ("rejected H-R1 and H-R3 and accepted … H-R2"). ✅
- **Synthetic vs source-realizable** terminology is used consistently: H-R1/2/3 and
  H-V1/2/3 are "source-realizable"; H-O1..3, H-T*, H-C*, H-P* are "synthetic /
  manifest-level"; the manuscript §4.3 wording ("The remaining *synthetic* mutants…")
  matches the corpus/README classification. ✅
- **"117 collected" (main.tex) vs "117 passed" (REPRODUCIBILITY).** Both are true and
  non-contradictory (117 collected, all 117 pass). Cosmetic only; **no action
  required**, though "117 collected (all pass)" would remove any reader doubt.
- **`\Sigma_T`** appears once (main.tex, "unimplemented and out of scope") — a scope
  statement, consistent with the brief and the hard rules; not a stale experiment.

## Findings

- **No contradiction, no stale count, no ambiguous denominator, no terminology drift
  found.** Every audited number is internally consistent across all six document sets
  and matches the live re-derivation in audit 4.
- Lone cosmetic note: "collected" vs "passed" for the 117 figure (both correct).
  **Non-blocking.**
