# Held-out mutation evaluation of the frozen delivery linter — results

Out-of-sample evaluation of `conformance/delivery_inspect.py` @ **305a3a8**
(delivery_inspect.py git-blob `6ef7b6de`), MP-SPDZ pin `9d809599`. The checker was
**not modified** before or after the run. Pre-registration commit:
**`d3d11e4d1fb93905f31cd319d28212fb7798dc23`** (PLAN.md + corpus + mutants + runner,
no results). This file and `results.json` are the execution-results commit. The run
is a **single** execution; nothing was tuned, deleted, or replaced afterward.

## TL;DR

- **All 22 mutants matched their pre-registered predictions** (18 linter PASS/REJECT
  calls + 2 provenance + 2 compile-invalid; **0 mismatches**).
- **Strict delivery detection: 2/3** (source-realizable structural mutants).
  **Inclusive: 10/12** (adds synthetic-manifest structural counterexamples).
- **Two false-accepts, both pre-registered:** **H-R2** (source-realizable recipient
  *permutation*) and **H-O3** (synthetic `call_arg` open — the checker's acknowledged
  gap). H-R2 is caught by the artifact's **runtime evidence layer**, not the linter.
- New in-scope structural leaks the linter had **never seen** — indirect (`ldmsi`)
  and gf2n (`gldms`) memory, socket/file/`print_int` sinks, vectorized public open —
  were **all caught** on the intended rule.
- Value-semantic mutants (incl. a genuine cross-party value leak) **pass the linter
  and fail the oracle**, as designed.

## Per-mutant: predicted vs actual

| ID | category | predicted | actual | match | classification |
|----|----------|-----------|--------|:----:|----------------|
| H-R1 | recipient | REJECT | REJECT | yes | structural |
| H-R2 | recipient | PASS | PASS / runtime-REJECT | yes | structural |
| H-R3 | recipient | REJECT | REJECT | yes | structural |
| H-O1 | open | REJECT | REJECT | yes | structural |
| H-O2 | open | REJECT | REJECT | yes | structural |
| H-O3 | open | PASS | PASS | yes | structural |
| H-T1 | topology | PASS | PASS | yes | benign |
| H-T2 | topology | REJECT | REJECT | yes | benign |
| H-T3 | topology | REJECT | REJECT | yes | structural |
| H-C1 | channel | REJECT | REJECT | yes | structural |
| H-C2 | channel | REJECT | REJECT | yes | structural |
| H-C3 | channel | PASS | PASS | yes | benign |
| H-V1 | value_semantic | PASS | PASS / oracle-FAIL | yes | semantic (out-of-scope) |
| H-V2 | value_semantic | PASS | PASS / oracle-FAIL | yes | semantic (out-of-scope) |
| H-V3 | value_semantic | PASS | PASS / oracle-FAIL | yes | semantic (out-of-scope) |
| H-P1 | transcript | REJECT | REJECT | yes | structural |
| H-P2 | transcript | REJECT | REJECT | yes | structural |
| H-P3 | transcript | REJECT | REJECT | yes | structural |
| H-E1 | provenance | validate-REJECT | validate=REJECT | yes | provenance |
| H-E2 | provenance | validate-REJECT | validate=REJECT | yes | provenance |
| H-X1 | compile_invalid | compile-FAIL | compile-FAIL | yes | compile-invalid |
| H-X2 | compile_invalid | compile-FAIL | compile-FAIL | yes | compile-invalid |


`match` = actual matched the pre-registered prediction. `runtime-REJECT` = caught by
the frozen `private_run` strict parser (the runtime evidence layer), not by the
delivery linter. `oracle-FAIL` = frozen oracle mismatch (value-semantic).

## Metrics (honest buckets — compile failures never counted as detections)

**delivery_inspect detection rate** (denominator = genuine gross-delivery-structure /
wrong-recipient violations that are compile-valid; semantic, benign, provenance, and
compile-invalid mutants are excluded):

| denominator | caught (REJECT) | n | rate | false-accepts |
|---|:---:|:---:|:---:|---|
| **strict** (source-realizable) | 2 | 3 | 0.67 | H-R2 |
| **inclusive** (+ synthetic manifests) | 10 | 12 | 0.83 | H-R2, H-O3 |

Other buckets (reported separately, **not** in the rate):

- **semantic / out-of-scope** (H-V1, H-V2, H-V3): linter **PASS** (3/3, by design) +
  oracle **FAIL** (3/3). The linter disclaims value semantics; these confirm it.
- **benign**: correct-accepts H-T1 (reorder), H-C3 (legit `call_arg` register use);
  one over-conservative **false-reject** H-T2 (extra well-formed masked tape — a
  non-leaking topology change rejected by the exact-multiset rule (f)).
- **provenance** (different frozen checker, `validate_evidence.py`): H-E1 (forged
  `delivery_sig`) and H-E2 (wrong `--repo`) both **rejected**.
- **compile-invalid**: H-X1, H-X2 both fail to compile (see below). Not detections.

## The two false-accepts

**H-R2 — recipient permutation (source-realizable).** Delivering party *j*'s
`(accept,payload)` to player `(j+1) mod 3` keeps the MAIN `privateoutput`
destination **multiset** at `[0,0,1,1,2,2]`, and rule (a) checks only that multiset,
not the value→player *pairing* — so the linter **PASSES** a genuine wrong-recipient
delivery. This is the sharpest held-out finding because it is **source-realizable**
(unlike the synthetic counterexamples). It is **not** a hole in the artifact as a
whole: the frozen runtime layer catches it — `private_run.strict_parse_party` raised
`foreign verdict for party 2 in party 0 stream` on the executed build. (A variant
that also relabels the print would instead surface as an oracle value mismatch.) So:
the *delivery linter alone* does not certify recipient pairing; the *layered
artifact* does.

**H-O3 — `call_arg` open inside an existing masked subtape (synthetic).** Appending
`asm_open …, False` of a register-passed value to an existing `EQZ(3)_63` body trips
no rule: (c) needs the `True` flag, (h) needs a memory access, (f)'s multiset is
intact. The linter **PASSES**. This is the exact gap the checker's own docstring
names (`call_tape`/`call_arg` cannot be blocklisted because the honest subtapes use
it). **Realizability from source is unproven** — the paper's B6 shows the naive
source realization *adds a tape / spills to memory* and is caught. H-O3 demonstrates
the gap at the **manifest** level only.

## What the linter caught that it had never seen (in-scope, held-out)

Every REJECT fired on the intended rule, on assembly patterns absent from the B0–B6
design set:

- **memory forms** the memory regex generalized to: indirect `ldmsi` (H-C1) and gf2n
  `gldms` (H-C2) → rule (h). (B-series only used scalar `stms/ldms` and vectorized
  `vstms/vldms`.)
- **sink channels/opcodes**: `writesharestofile` (H-P1), network `writesocketshare`
  (H-P2), `print_int` (H-P3) → rule (d).
- **opens**: raw `True` (H-O1) and **vectorized** `vasm_open …,True` (H-O2) inside a
  subtape → rule (c).
- **topology**: off-pin but pattern-valid subtape name `EQZ(7)_63` (H-T3), extra
  masked tape (H-T2) → rule (f).
- **recipient set**: extra foreign recipient (H-R1), collapse-to-one (H-R3) → rule (a).

**Compiler defense-in-depth (H-X1):** the naive direct cross-tape reference
(`accept[1].reveal(False)` inside a `new_tape`) does not even compile —
`CompilerError: … "s749" … Register from other tape`. This is *why* B3/B5 needed a
memory hop, and it is a layer **below** the linter.

## Limitations / threats to validity

- **Not blind.** Same author built the checker and the mutants; predictions are
  static reasoning about the rules. Pre-registration + the no-tuning rule bound this
  (predictions were committed at `d3d11e4` before the run; the checker was unchanged;
  the run reproduced all predictions), but this is out-of-sample, **not**
  independent-adversary, and the perfect prediction match reflects that the author
  knows the rules — it is not evidence the rules are complete.
- **Synthetic realizability.** 12 mutants are manifest-level. A REJECT proves the
  rule fires on that pattern; a PASS (esp. **H-O3**) proves only that *no rule would*
  reject it, not that a source program can produce it without tripping another rule.
- **Small N, single backend/ring/query for linting** (22 mutants, pin only, `-R 64`,
  `p1_is_max`). Not a saturation study; the detection rates are over this corpus, not
  a universal claim.
- **Denominator dependence.** 2/3 vs 10/12 differ only by which structural mutants
  count; semantic/benign/provenance/compile-invalid are never folded in.

## Assessment: strengthen, weaken, or clarify?

**Primarily CLARIFIES; mildly STRENGTHENS the coverage/honesty story; does NOT
weaken the thesis.**

- **Clarifies.** With a pre-registered, out-of-sample corpus it pins down exactly
  what the delivery linter does and does not establish: it reliably rejects a broad
  range of gross-*structure* delivery leaks (opens, sinks, illicit memory/tapes,
  wrong-recipient *sets*) — including forms it had never seen — but it is blind, by
  construction, to (i) recipient *permutations* that preserve the destination
  multiset, (ii) the `call_arg` register-open channel at the manifest level, and
  (iii) *value* semantics. None of this contradicts a manuscript claim; the paper
  already states the linter is not a non-leakage proof.
- **Strengthens (mildly).** The linter's rules generalize to new in-scope patterns
  (held-out memory/sink/open/topology forms all caught), the acknowledged `call_arg`
  gap is now demonstrated concretely, and the *layered* defense is shown catching
  what the linter misses (H-R2 → runtime; H-X1 → compiler; H-E1/E2 → provenance).
- **Does not weaken.** No result falsifies any frozen claim.
- **One item worth the manuscript's attention (decision deferred to review, not
  acted on here):** the manuscript's current false-accept examples are *semantic*
  (S1). **H-R2 is a *source-realizable structural* false-accept** (a recipient
  permutation) that only the runtime layer catches — arguably worth a sentence in
  the limitations, precisely because it is structural yet passes the structural
  linter. Per the sprint rules we do **not** edit the manuscript or patch the linter.

## Reproduce

`bash paper/heldout/reproduce.sh` — checks out & verifies the 305a3a8 checker (fail
closed), verifies the MP-SPDZ pin, self-tests the harness on the public B-series,
then runs the single held-out evaluation. `run_heldout.py` additionally asserts the
`delivery_inspect.py` git-blob hash. Deterministic; `results.json` is the full
machine-readable record.
