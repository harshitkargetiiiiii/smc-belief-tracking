# Held-out mutation evaluation of the frozen delivery linter — results

Out-of-sample evaluation of `conformance/delivery_inspect.py` @ **305a3a8**
(delivery_inspect.py git-blob `6ef7b6de`), MP-SPDZ pin `9d809599`. The checker was
**not modified** before or after the run. Pre-registration commit:
**`d3d11e4d1fb93905f31cd319d28212fb7798dc23`** (PLAN.md + corpus + mutants + runner,
no results). The run is a **single** execution; nothing was tuned, deleted, or
replaced afterward.

> **Interpretation update (Codex review, post-run).** This README was revised after
> a Codex review of the interpretation. **The pre-registration commit `d3d11e4`,
> `corpus.py`/`corpus.json`, the runner, the checker, and the raw `results.json` are
> unchanged** — only this reporting file was edited. The revisions: (1) the synthetic
> manifest transforms are reframed as **manifest-level rule-coverage probes**, not
> executable security violations, and are **no longer aggregated into a
> "detection rate"** (the pre-registered `denominator: inclusive` label in
> `corpus.json` is therefore **not** reported as a security metric); (2) the
> source-realizable recipient result is stated at exact strength (three mutants, not
> a rate); (3) **H-O3** is a manifest-level **rule-gap PASS** with unproven source
> realizability — **H-R2** is the one *demonstrated source-realizable* structural
> false accept; (4) the H-R2 runtime-catch claim is narrowed to this concrete mutant;
> (5) the raw `prediction_matches: 18` field is explained; (6) the provenance probes
> are downgraded to non-isolated supporting checks; (7) "byte-deterministic" →
> "outcome-deterministic".

## TL;DR

- **Every mutant behaved as pre-registered** (see the accounting of the raw
  `prediction_matches: 18` field below).
- **Source-realizable recipient-structure result (exact strength):** among the three
  pre-registered source-realizable recipient-structure mutants, the frozen linter
  **rejected H-R1 and H-R3** and **accepted the multiset-preserving H-R2
  permutation**. We do **not** treat "2 of 3" as an estimate of general detector
  effectiveness.
- **H-R2 is the one demonstrated source-realizable *structural* false accept**: a
  compiled, executable build whose delivery the linter passes but which delivers a
  party's verdict to the wrong recipient. The **synthetic** probe **H-O3** is a
  *manifest-level rule-gap* (a PASS with no rule to reject it), whose realizability
  from source is **unproven**, not a demonstrated executable attack.
- **Synthetic transforms are manifest-level rule probes**, reported per-rule (below),
  **without** an aggregate security-detection percentage. On the patterns probed,
  rules (c)/(d)/(f)/(h) each fired as intended — including forms absent from the
  B-series (indirect `ldmsi`, gf2n `gldms`, `writesocketshare`, `print_int`,
  vectorized open).
- **Value-semantic** source mutants (H-V1/H-V2/H-V3): linter **PASS** + oracle
  **FAIL** (out of scope, by design; H-V3 is a genuine cross-party value leak).

## Per-mutant: predicted vs actual

`kind`: **source (exec)** = a real `.mpc` compiled and (where relevant) executed;
**synthetic (manifest)** = a manifest-level transform that probes whether a rule
fires on an assembly pattern (not a demonstrated executable attack);
**provenance** = scored against `validate_evidence.py`.

| ID | kind | category | predicted | actual | match |
|----|------|----------|-----------|--------|:----:|
| H-R1 | source (exec) | recipient | REJECT | REJECT | yes |
| H-R2 | source (exec) | recipient | PASS | PASS / runtime-REJECT(this mutant) | yes |
| H-R3 | source (exec) | recipient | REJECT | REJECT | yes |
| H-O1 | synthetic (manifest) | open | REJECT | REJECT | yes |
| H-O2 | synthetic (manifest) | open | REJECT | REJECT | yes |
| H-O3 | synthetic (manifest) | open | PASS | PASS | yes |
| H-T1 | synthetic (manifest) | topology | PASS | PASS | yes |
| H-T2 | synthetic (manifest) | topology | REJECT | REJECT | yes |
| H-T3 | synthetic (manifest) | topology | REJECT | REJECT | yes |
| H-C1 | synthetic (manifest) | channel | REJECT | REJECT | yes |
| H-C2 | synthetic (manifest) | channel | REJECT | REJECT | yes |
| H-C3 | synthetic (manifest) | channel | PASS | PASS | yes |
| H-V1 | source (exec) | value_semantic | PASS | PASS / oracle-FAIL | yes |
| H-V2 | source (exec) | value_semantic | PASS | PASS / oracle-FAIL | yes |
| H-V3 | source (exec) | value_semantic | PASS | PASS / oracle-FAIL | yes |
| H-P1 | synthetic (manifest) | transcript | REJECT | REJECT | yes |
| H-P2 | synthetic (manifest) | transcript | REJECT | REJECT | yes |
| H-P3 | synthetic (manifest) | transcript | REJECT | REJECT | yes |
| H-E1 | provenance | provenance | validate-REJECT | validate=REJECT | yes |
| H-E2 | provenance | provenance | validate-REJECT | validate=REJECT | yes |
| H-X1 | source (exec) | compile_invalid | compile-FAIL | compile-FAIL | yes |
| H-X2 | source (exec) | compile_invalid | compile-FAIL | compile-FAIL | yes |

`runtime-REJECT(this mutant)` = the frozen `private_run` strict parser rejected
**this specific** executed build (not a general property — see H-R2 below).
`oracle-FAIL` = frozen oracle mismatch (value-semantic).

## Results by kind

### A. Source-realizable, executable (the mutants that support security claims)

- **Recipient structure (H-R1, H-R2, H-R3).** Exact outcome: the linter **rejected
  H-R1** (extra foreign recipient → destination multiset `[0,0,1,1,1,2,2]`, rule (a))
  and **H-R3** (collapse to one player → `[0,0,0,0,0,0]`, rule (a)), and **accepted
  H-R2** (permutation preserving `[0,0,1,1,2,2]`). This is the concrete result for
  three mutants, **not** a detector-effectiveness rate.
- **Value-semantic (H-V1, H-V2, H-V3).** Correct delivery structure, wrong delivered
  value: linter **PASS** (3/3, by design) and frozen-oracle **FAIL** (3/3) on the
  pre-registered case set. The linter disclaims value semantics; these confirm it,
  with H-V3 (party *j* receives party *(j+1)*'s payload) a genuine cross-party value
  leak the delivery linter accepts.
- **Compile-invalid (H-X1, H-X2).** Both fail to compile → bucketed compile-invalid,
  **never** counted as detections. H-X1 is meaningful: the naive direct cross-tape
  reference (`accept[1].reveal(False)` inside a `new_tape`) does not compile —
  `CompilerError: … "s749" … Register from other tape` — which is *why* B3/B5 needed
  a memory hop, and a layer **below** the linter.

### B. Synthetic manifest-level rule probes (NOT a security-detection rate)

Each transform appends one assembly pattern to the honest compiled manifest and asks
whether a linter rule fires. A REJECT shows the rule matches that pattern; a PASS
shows **no rule** would reject it — it does **not** demonstrate a source-realizable
attack. We therefore report per-rule outcomes and compute **no** aggregate security
percentage over these.

| probe | injected pattern | rule targeted | linter | note |
|-------|------------------|---------------|--------|------|
| H-O1 | `asm_open …,True in a subtape` | (c) public open | REJECT | raw public open caught |
| H-O2 | `vasm_open …,True in a subtape` | (c) public open | REJECT | vectorized open caught |
| H-O3 | `asm_open …,False (register) in a subtape` | — (no rule) | PASS | rule-gap: (c) needs True, (h) needs memory, (f) intact |
| H-T1 | `reversed tape order` | — (sorted) | PASS | benign; order-insensitive |
| H-T2 | `extra pure masked tape` | (f) multiset | REJECT | non-leaking topology; conservative REJECT |
| H-T3 | `off-pin name EQZ(7)_63` | (f) multiset | REJECT | off-pin name caught |
| H-C1 | `ldmsi (indirect load) in a subtape` | (h) memory | REJECT | indirect memory form caught |
| H-C2 | `gldms (gf2n load) in a subtape` | (h) memory | REJECT | gf2n memory form caught |
| H-C3 | `movs (register move) in a subtape` | — (benign) | PASS | legit register use not flagged |
| H-P1 | `writesharestofile in a subtape` | (d) sink | REJECT | file sink opcode caught |
| H-P2 | `writesocketshare in a subtape` | (d) sink | REJECT | socket sink opcode caught |
| H-P3 | `print_int in a subtape` | (d) sink | REJECT | numeric print sink caught |

The two PASS rows are the informative ones: **H-O3** is the acknowledged `call_arg`
rule-gap (the checker's own docstring says the register channel cannot be
blocklisted); **H-C3**/**H-T1** are benign patterns the linter correctly does not
flag. The nine REJECT rows confirm rules (c)/(d)/(f)/(h) match assembly forms the
B-series never exercised (indirect/gf2n memory, socket/file/numeric-print sinks,
vectorized public open, off-pin/extra masked tapes) — a **rule-coverage** result,
not a count of executable attacks caught.

### C. Provenance — non-isolated supporting checks (different frozen checker)

These target `validate_evidence.py`, not `delivery_inspect`, and each rejection
fired on **more than one** condition, so **neither isolates a single validator
mechanism**:

- **H-E1** (forged `delivery_sig`) — rejected for **both** `delivery_sig not 64-hex`
  (malformed length) **and** `delivery_sig != recomputed manifest signature`.
- **H-E2** (wrong `--repo`) — rejected for **both** `repo_sha … != deadbeef…` **and**
  a `bad/duplicate case_id '(1, 2, 0)-sum_even'` condition in the generated evidence.

They support "the provenance layer rejects tampered/replayed evidence" but do not
attribute the rejection to one specific check.

## Accounting for the raw `prediction_matches: 18`

The raw `results.json` `summary.prediction_matches` field is **18**, not 22, **by
construction**: that field counts only mutants whose *linter* prediction was PASS or
REJECT (18 of them, all matched). The remaining four are predicted with a different
outcome type — **2 provenance** (predicted `validate-REJECT`, both rejected) and **2
compile-invalid** (predicted compile-FAIL, both failed to compile) — and are tracked
in separate summary fields, not in `prediction_matches`. So all 22 mutants behaved
as pre-registered; the "18" is a field-scope artifact, and the raw file is left
unchanged.

## Limitations / threats to validity

- **Not blind.** Same author built the checker and the mutants; predictions are
  static reasoning about the rules. Pre-registration + the no-tuning rule bound this
  (predictions committed at `d3d11e4` before the run; checker unchanged; run
  reproduced the predictions), but this is out-of-sample, **not**
  independent-adversary; matching one's own predictions is not evidence the rules are
  complete.
- **Synthetic ≠ executable.** 12 mutants are manifest-level probes. A REJECT proves a
  rule fires on that assembly pattern; a PASS (esp. **H-O3**) proves only that no rule
  *would* reject it — **not** that a source program can produce that manifest without
  tripping another rule (the paper's B6 shows the naive source realization is caught).
  Only the source-realizable mutants (recipient, value-semantic) speak to executable
  behavior.
- **Small N, single backend/ring/query for linting** (22 mutants, pin only, `-R 64`,
  `p1_is_max`). Not a saturation study, and no universal detection claim is made.
- **Outcome-deterministic, not byte-deterministic.** The PASS/REJECT/oracle/compile/
  validate **outcomes** reproduce on re-run. The raw `results.json` is **not**
  byte-identical across environments: it captures absolute paths, compiler register
  indices (e.g. `s749`), and stdout snippets, which are environment/path dependent
  and are **not** normalized here.

## Assessment: strengthen, weaken, or clarify?

**Primarily CLARIFIES; mildly STRENGTHENS the coverage/layered story; does NOT weaken
the thesis.**

- **Clarifies.** It pins down what the delivery linter does and does not establish:
  on executable, source-realizable mutants it rejects wrong-recipient *sets*
  (H-R1/H-R3) but accepts a recipient *permutation* (H-R2); and it is blind, by
  construction, to *value* semantics (H-V1/2/3). On assembly patterns it has rules
  for (opens, sinks, illicit memory/tapes), those rules match new forms (the
  manifest-level probes) — but that is rule coverage, not executable-attack coverage.
  None of this contradicts a manuscript claim; the paper already states the linter is
  not a non-leakage proof.
- **Strengthens (mildly).** The rules generalize to assembly forms they had never
  seen (manifest-level probes), and the `call_arg` rule-gap the checker documents is
  now exhibited concretely at the manifest level (H-O3).
- **Does not weaken.** No result falsifies any frozen claim.
- **One item worth the manuscript's attention (decision deferred; not acted on):**
  the manuscript's current false-accept examples are *semantic* (S1). **H-R2 is a
  demonstrated *source-realizable structural* false accept** — a recipient
  permutation the structural linter passes; the frozen `private_run` strict parser
  rejected *this concrete build* because a foreign `PRIV j` record appears on the
  receiving party's stream (this is a property of this mutant, **not** a general claim
  that the artifact catches recipient permutations). Per the sprint rules we do
  **not** edit the manuscript or patch the linter.

## Reproduce

`bash paper/heldout/reproduce.sh` — checks out & verifies the 305a3a8 checker (fail
closed), verifies the MP-SPDZ pin, self-tests the harness on the public B-series,
then runs the single held-out evaluation. `run_heldout.py` additionally asserts the
`delivery_inspect.py` git-blob hash. **Outcome-deterministic** (the PASS/REJECT/
oracle/compile/validate outcomes reproduce; the raw `results.json` is not byte-
identical across environments — see limitations). `results.json` is the full
machine-readable record and is left exactly as produced by the single run.
