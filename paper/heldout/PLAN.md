# PLAN — pre-registered held-out evaluation of the frozen delivery linter

**This document and everything it references (the corpus, the mutant sources, the
transforms, the runner) are committed BEFORE the evaluation runs.** The results
(`results.json`, `README.md`) are added in a SEPARATE later commit. The
pre-registration commit SHA and the execution-results commit SHA are reported
separately in the final report.

## 0. Goal and hard rules

Produce an **out-of-sample** evaluation of `conformance/delivery_inspect.py` — the
frozen delivery linter — measuring how it behaves on mutants that were **never used
to design it**. The checker is frozen at artifact baseline **`305a3a8`**
(delivery_inspect.py git-blob `6ef7b6de`) and is **not modified** in this sprint,
before or after seeing any result. We add only `paper/heldout/`; we do not touch
`conformance/`, `mpc/`, `reference/`, `.github/`, or the manuscript. If a mutant
exposes a new bypass we **document and stop** — we do not patch the linter.

## 1. What the frozen checker is (so predictions are grounded, not guessed)

`delivery_inspect.is_private_manifest(manifest, EXPECTED_SUBTAPES)` inspects the
compiled per-tape assembly of a build and returns PASS iff ALL hold (paraphrased
from the frozen docstring):

- **(a)** exactly one MAIN tape; its `privateoutput` destination-player **multiset**
  is exactly `[0,0,1,1,2,2]`; MAIN performs **no open**; MAIN's only sinks are
  `privateoutput` + guarded `cond_print`; **(g)** MAIN performs no memory STORE.
- **(b)** no `privateoutput` in any non-main tape.
- **(c)** no public open-to-all (`open …, True`) in any tape.
- **(d)** no cleartext/file/socket sink (`print_*`/`intoutput`/`rawoutput`/
  `writesocket*`/`write*file*`/…) in any tape.
- **(e)** every non-main tape name matches `^(EQZ|LTZ)\(\d+\)_\d+$`.
- **(f)** the non-main tape base **multiset** equals the pinned
  `{EQZ(3)_63, EQZ(81)_63, LTZ(36)_64}` exactly.
- **(h)** every non-main tape performs **no memory access** at all.

It is an **opcode-identity / channel-blocklist linter**. Its own docstring states it
is **not** a non-leakage proof and that the `call_tape`/`call_arg` register channel
cannot be blocklisted (the honest comparison subtapes use it). This is the design
the held-out corpus probes.

## 2. Mutation taxonomy (principled, not B0–B6 renamed)

Grounding:

- **Our history (B0–B6/S1).** B0 public reveal in MAIN; B1 separate-tape
  reveal+print; B2 name-spoofed subtape with wrong-player `privateoutput`+file sink;
  B3 `reveal(False)` in a duplicate `EQZ(3)_63` via **scalar** memory; B5 the
  **vectorized** memory variant; B6 `call_arg` that ADDS a tape (caught); S1 correct
  structure / wrong value. The held-out corpus deliberately avoids these exact
  channels and instead moves **along** each axis to new points.
- **Security mutation testing** (Just et al.; PIT/`mutmut` operator families): apply
  systematic, category-defined operators; separate **stillborn/equivalent**
  (here: compile-invalid, and benign structure-preserving) mutants from killed ones;
  never count a stillborn mutant as a kill.
- **Information-flow / static analysis** (ct-verif, Binsec/Rel, Securify;
  explicit-secrecy): leakage is an **operand/dataflow** property, not an
  opcode-identity property — so a checker keyed on opcode/channel identity is
  expected to miss value-routed and permutation leaks. We include those as the
  out-of-scope pole.
- **MP-SPDZ compiler mechanisms:** tapes and subtapes (`new_tape`, `@function_tape`),
  the `call_tape`/`call_arg` register-argument channel, the `asm_open`/`vasm_open`
  open family (`True`/`False` flag), memory forms (`stm*/ldm*`, vectorized `v…`,
  indirect `…si`, gf2n `g…`), sink opcodes (`print_*`, `intoutput`,
  `writesocket*`, `write*file*`), and the cross-tape-register **compile error** that
  forces any main→subtape value transfer through memory or `call_arg`.

Seven categories (+ a compile-invalid bucket), 3 mutants each where applicable:

1. **recipient/destination** — who receives which verdict (MAIN `privateoutput`).
2. **public/private open** — raw/`False`/vectorized opens placed via the register
   channel inside existing masked subtapes.
3. **subtape/topology** — reorder, add, or rename subtapes.
4. **secret-transfer/channel** — memory FORMS not exercised by B3/B5 (indirect,
   gf2n) and the legitimate `call_arg` register use.
5. **output/value-semantic** — correct structure, wrong VALUE (needs the oracle).
6. **transcript/output-channel** — file/socket/numeric-print sinks and placements.
7. **evidence/provenance** — forged/replayed evidence (targets the SEPARATE frozen
   checker `validate_evidence.py`, not `delivery_inspect`).

## 3. The complete corpus (22 mutants) — predictions locked here

`kind`: `source` = a real `.mpc` compiled then linted; `synthetic` = a
manifest-level transform of the honest compiled manifest (a B4-style counterexample;
**source-realizability is NOT claimed** and is recorded per-mutant); `provenance` =
an evidence transform scored against `validate_evidence.py`. Exact per-mutant
mechanism, intended violation, and predicted rule are in `corpus.json`; the sources
are in `mutants/`; the transforms in `synthetic_transforms.py`.

| ID | cat | kind | genuine? | realizable | pred compile | pred linter | oracle? | bucket | denom |
|----|-----|------|----------|-----------|--------------|-------------|---------|--------|-------|
| H-R1 | recipient | source | yes | source | valid | REJECT | no | structural_security | strict |
| H-R2 | recipient | source | yes | source | valid | PASS | yes | structural_security | strict |
| H-R3 | recipient | source | yes | source | valid | REJECT | no | structural_security | strict |
| H-O1 | open | synthetic | yes | synthetic-manifest | n/a | REJECT | no | structural_security | inclusive |
| H-O2 | open | synthetic | yes | synthetic-manifest | n/a | REJECT | no | structural_security | inclusive |
| H-O3 | open | synthetic | yes | synthetic-manifest | n/a | PASS | no | structural_security | inclusive |
| H-T1 | topology | synthetic | no | synthetic-manifest | n/a | PASS | no | benign | none |
| H-T2 | topology | synthetic | no | synthetic-manifest | n/a | REJECT | no | benign | none |
| H-T3 | topology | synthetic | yes | synthetic-manifest | n/a | REJECT | no | structural_security | inclusive |
| H-C1 | channel | synthetic | yes | synthetic-manifest | n/a | REJECT | no | structural_security | inclusive |
| H-C2 | channel | synthetic | yes | synthetic-manifest | n/a | REJECT | no | structural_security | inclusive |
| H-C3 | channel | synthetic | no | synthetic-manifest | n/a | PASS | no | benign | none |
| H-V1 | value_semantic | source | yes | source | valid | PASS | yes | semantic_out_of_scope | none |
| H-V2 | value_semantic | source | yes | source | valid | PASS | yes | semantic_out_of_scope | none |
| H-V3 | value_semantic | source | yes | source | valid | PASS | yes | semantic_out_of_scope | none |
| H-P1 | transcript | synthetic | yes | synthetic-manifest | n/a | REJECT | no | structural_security | inclusive |
| H-P2 | transcript | synthetic | yes | synthetic-manifest | n/a | REJECT | no | structural_security | inclusive |
| H-P3 | transcript | synthetic | yes | synthetic-manifest | n/a | REJECT | no | structural_security | inclusive |
| H-E1 | provenance | provenance | yes | provenance | n/a | n/a | no | provenance_other_checker | none |
| H-E2 | provenance | provenance | yes | provenance | n/a | n/a | no | provenance_other_checker | none |
| H-X1 | compile_invalid | source | yes | source(compile-fail) | invalid | n/a | no | compile_invalid | none |
| H-X2 | compile_invalid | source | no | source(compile-fail) | invalid | n/a | no | compile_invalid | none |


Predicted (from the rules in §1, not from running the linter): **11 REJECT, 7 PASS,
4 n/a**. Predicted **false-accepts** (genuine violation, linter PASS): **H-R2**
(source-realizable recipient permutation), **H-O3** (synthetic `call_arg` open —
the acknowledged gap), and the three **value-semantic** mutants **H-V1/H-V2/H-V3**
(out of the linter's stated scope). Predicted **benign**: H-T1 correct-accept,
H-C3 correct-accept, H-T2 over-conservative false-reject.

## 4. Oracle classification (pre-registered case set)

Value-semantic and permutation mutants are executed at the pin over a FIXED case set
and compared to the frozen oracle (`mpc_run.oracle_expect`) via the frozen strict
parser (`private_run.strict_parse_party`):

```
CASES_FOR_ORACLE = [((0,0,1),"sum_even"), ((0,0,1),"p1_is_max"),
                    ((2,0,0),"p1_is_max"), ((1,2,0),"sum_even"), ((0,0,0),"p1_is_max")]
```

`oracle_fail` = any case where parsed delivery ≠ oracle. `runtime_layer_reject` =
any case where a party's stream raises in the frozen strict parser (e.g. a foreign
`PRIV j` record) — this is the **runtime evidence layer**, reported separately from
the linter.

## 5. Counting rules and metrics (pre-registered)

Buckets: `structural_security` (genuine gross-delivery-structure / wrong-recipient
violation the linter targets; detection = REJECT), `semantic_out_of_scope` (genuine
value error, correct structure; PASS by design; needs oracle; **not** counted
against the linter), `benign` (non-violating; a REJECT here is a false-reject), 
`provenance_other_checker` (scored vs `validate_evidence.py`), `compile_invalid`
(never a detector success).

Denominators for a `delivery_inspect` detection rate:

- **strict** = `structural_security` mutants that are **source-realizable &
  compile-valid** (H-R1, H-R2, H-R3). The conservative, defensible denominator.
- **inclusive** = strict + synthetic-manifest `structural_security` counterexamples,
  reported **with** the realizability caveat.

Hard counting rules: a compile failure is never a kill; semantic mutants are in no
delivery denominator; a benign REJECT is a precision (false-reject) datum, not a
detection; provenance mutants are scored against `validate_evidence.py`.

Metrics produced: per-mutant predicted-vs-actual table; strict & inclusive detection
rates; the false-accept list; the semantic bucket (linter-PASS count + oracle-FAIL
count); compile-invalid count; provenance results; benign correct-accepts and
false-rejects.

## 6. Threats to validity (declared up front)

- **Not blind.** The mutants and predictions are authored by the same party who
  built the checker. Pre-registration + the no-tuning rule bound the damage
  (predictions are fixed in git before the run; the checker cannot be edited after),
  but this is an out-of-sample, **not** an independent-adversary, evaluation.
- **Synthetic realizability.** The `synthetic` mutants are manifest-level
  counterexamples. A REJECT proves the rule fires on that assembly pattern; a PASS
  (esp. **H-O3**) proves only that no rule *would* reject it — whether a **source**
  program can realize that exact manifest without tripping another rule is a separate
  question the paper's B6 shows is nontrivial. Recorded per-mutant.
- **Small N, single backend, single ring/query for linting.** 22 mutants, MP-SPDZ
  pin only, `-R 64`, linter probed on `p1_is_max`. Not a saturation study.
- **Denominator dependence.** The headline rate depends on which bucket is the
  denominator; we therefore report strict and inclusive separately and never fold in
  semantic/compile-invalid/provenance mutants.

## 7. Reproduction

`bash paper/heldout/reproduce.sh` (from a checkout of the evaluation branch). It
checks out the frozen checker at **305a3a8** into a worktree and **fails closed** if
that is not the exact commit; verifies the MP-SPDZ pin; runs a self-test on the
public B-series (`selftest_bseries.py`) to validate the harness; then runs the
single held-out evaluation (`run_heldout.py`), which additionally asserts the
`delivery_inspect.py` git-blob hash and writes `results.json`. The run is
deterministic.
