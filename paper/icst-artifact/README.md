# Supplementary Artifact — Testing Delivery-Conformance Checks in MP-SPDZ

Anonymous supplementary artifact for the double-blind submission
*"Testing Delivery-Conformance Checks in MP-SPDZ: A Pre-Registered Mutation
Case Study."* This package contains the frozen conformance checkers, the honest
subject builds and negative controls, the plaintext reference/pseudo-oracle, the
pre-registered held-out mutation evaluation, and reproduction wrappers.

This artifact supports a **software-testing case study**. It makes **no** MPC
protocol, simulation-security, or privacy-proof claim. Its central empirical
result is a *boundary* finding: an opcode-identity / channel-blocklist delivery
linter accepts a source-realizable, destination-multiset-preserving recipient
permutation (**H-R2**) that mis-delivers a party's verdict to the wrong recipient,
and that structural false accept is caught only by the downstream transcript
oracle for that one concrete build. See the manuscript for the exact scope.

## Package layout

```
icst-artifact/
├── README.md                 ← this file
├── REPRODUCE.md              ← prerequisites + how to run (read before reproducing)
├── ERRATA.md                 ← superseded in-code comments + frozen-file annotations
├── SHA256SUMS.txt            ← integrity checksums over every shipped file
├── checker/                  ← the frozen checkers under test (byte-identical to the reviewed artifact)
│   ├── delivery_inspect.py       delivery linter, rules (a)–(h) — the primary subject of the mutation study
│   ├── oracle.py                 plaintext pseudo-oracle (all-possible-outputs tcheck transcription)
│   ├── mpc_run.py                pinned-backend runtime driver
│   ├── private_run.py            three-layer private-delivery gate + strict transcript parser
│   ├── coverage.py, harness.py   case drivers (228-case matrix; named-case harness)
│   ├── validate_evidence.py      hash-bound evidence validator (--recompute)
│   ├── circuit_spec.py           interface / no-wraparound bound checks
│   └── test_*.py                 unit + regression tests for the above
├── subject-and-controls/     ← the .mpc builds
│   ├── threshold_smc.mpc          honest public-query subject
│   ├── threshold_smc_private.mpc  honest private-delivery subject (the build the linter guards)
│   └── threshold_smc_{leaky,subleak,namespoof,openfalse,openfalse_vec}.mpc
│                                  five committed negative-control leak mutants
├── reference/                ← independent plaintext reference used by the pseudo-oracle
│   ├── belief_exact.py, fp_sim_legacy.py, test_reference.py
├── prereg/                   ← the PRE-REGISTERED held-out evaluation (predictions locked before results)
│   ├── PLAN.md                    locked predictions + hard rules (committed before any result)
│   ├── corpus.py, corpus.json     the 22-mutant held-out corpus (taxonomy + per-mutant predictions)
│   ├── synthetic_transforms.py    manifest-level transforms (synthetic rule-coverage probes)
│   ├── gen_source_mutants.py      generator for the source-realizable mutants
│   ├── run_heldout.py             single-run evaluation harness (orchestration glue only)
│   ├── selftest_bseries.py        self-test on the public B-series (sanity check)
│   └── mutants/                   the 8 source-realizable mutant .mpc files (H-R{1,2,3}, H-V{1,2,3}, H-X{1,2})
├── mutations/                ← the earlier adaptive detection matrix
│   ├── detection_matrix.json      per-mutation channel / checker-version-defeated / outcome
│   ├── reproduce_mutations.py     B4/B6/S1 reproduction glue
│   ├── s1_runtime_evidence.json   raw per-party output for the executed S1 mutant
│   └── threshold_smc_{callarg,wrongsem}.mpc
├── results/
│   └── results.json               machine-readable held-out outcomes (per-mutant + summary)
└── reproduce/
    ├── core_reproduce.sh          clean-room core reproduction + B4/B6/S1
    └── heldout_reproduce.sh       held-out evaluation reproduction
```

## Pre-registration

`prereg/PLAN.md` states the corpus, the mutant sources, the transforms, and the
per-mutant predictions, and was committed **before** the evaluation was run; the
outcomes in `results/results.json` were produced in a **separate, later** step.
This ordering (predictions before results) is the pre-registration guarantee. In
the project's version-control history it is enforced by committing the plan file
before the results file; a reviewer can independently re-run `prereg/run_heldout.py`
(see `REPRODUCE.md`) and confirm that the regenerated outcomes match the locked
predictions in `PLAN.md`. The held-out study remains **white-box and same-project**:
it reduces post-hoc adaptation but is not an independent red-team evaluation.

## Integrity

Every file's SHA-256 is recorded in `SHA256SUMS.txt`. The files under `checker/`,
`subject-and-controls/`, `reference/`, `prereg/`, `mutations/`, `results/`, and
`reproduce/` are **byte-identical** to the reviewed research artifact; only the
top-level Markdown prose (`README.md`, `REPRODUCE.md`, `ERRATA.md`) is
artifact-specific author text. Verify with:

```
sha256sum -c SHA256SUMS.txt
```

## Scope and claims (read `ERRATA.md` and the manuscript for the exact wording)

- **Functional conformance only.** A green result establishes that the checked
  build is consistent with the transcribed pseudo-oracle and the delivery rules on
  the enumerated cases. It is **not** a non-leakage guarantee, a simulation-security
  argument, or a privacy proof.
- **Restricted mutation model.** The mutation study permits only the
  application-level computational and delivery transformations enumerated by the
  corpus. Arbitrary compile-time Python imports, filesystem or network side effects,
  modification of the compiler environment, and mutation of the oracle, checker,
  policy, CI workflow, validator, or compiler are excluded. This is the *operator
  space of the mutation study*, not an adversarial-security boundary.
- **Cross-tape channels, non-exhaustive.** In the compiled paths exercised here,
  cross-tape transfer was observed through memory and through register arguments
  passed by `call_tape` / received by `call_arg`; we do not claim these are the only
  possible cross-tape channels.
- **Reproduction requires the project git history.** The `reproduce/*.sh` wrappers
  drive the checkers from a verified frozen checkout via `git worktree`; this flat
  snapshot does not carry that history. `REPRODUCE.md` gives the direct commands that
  run the evaluation on the shipped files without the wrappers.
