# REPRODUCE — prerequisites and how to run

## What is reproducible here

- **Held-out mutation evaluation** against the frozen delivery linter
  (`checker/delivery_inspect.py`), regenerating `results/results.json`.
- **Clean-room core** (unit tests, named-case harness, delivery gate + five negative
  controls, the 228-case coverage matrix, hash-bound evidence validation) plus the
  **B4 / B6 / S1** mutation reproductions.

Every PASS/REJECT verdict is produced by the **frozen** checkers; the harnesses are
orchestration glue only and make no detection decision of their own. The runner
**fails closed** unless the imported `delivery_inspect.py` has the frozen git-blob
hash and MP-SPDZ is the pin.

## Prerequisites

- Linux/macOS, Python 3.9+, `pytest`, a C++ toolchain (`g++`/`clang`, `make`), and
  `git`.
- The MP-SPDZ backend at the **pinned** commit, built and SSL-provisioned:

```bash
git clone https://github.com/data61/MP-SPDZ.git
cd MP-SPDZ
git checkout 9d809599ea6ce627216a389ca7d984fbb75d0cb9   # the pin
make -j"$(nproc)" replicated-ring-party.x
Scripts/setup-ssl.sh 3                                    # 3-party TLS certs (runtime)
export MPSPDZ="$PWD"                                      # absolute path to this build
```

The paper-critical backend observations also replicate on one additional MP-SPDZ
version (v0.4.3); the pin above is the primary, fully-supported backend.

## Path A — direct held-out run on the shipped files (no project git history)

From the `icst-artifact/` directory, with `MPSPDZ` exported as above:

```bash
PYTHONPATH="$PWD/checker" HELDOUT="$PWD/prereg" MPSPDZ="$MPSPDZ" \
    python3 prereg/run_heldout.py
```

This drives the frozen linter over the 22-mutant corpus and writes
`prereg/results.json`. Compare it against the shipped `results/results.json`; the
summary block (`n_mutants`, `prediction_matches`, the strict/inclusive denominators,
the `H-R2` false accept, the semantic-out-of-scope set, the provenance verdicts)
should match. The linter-verdict portion runs directly on this flat snapshot. The
runtime-oracle and provenance sub-steps invoke `private_run.py` /
`validate_evidence.py`, which expect the repository's `conformance/` layout; if a
sub-step cannot locate a subject build under this flat layout, use Path B.

## Path B — reproduction wrappers (fully supported; requires the project repository)

`reproduce/core_reproduce.sh` and `reproduce/heldout_reproduce.sh` are the
fully-supported reproduction path. They check out the **frozen** checker from a
verified commit via `git worktree` and run the artifact from there, so the branch you
invoke them from cannot influence the result. **They therefore require the project's
version-control history.**

This anonymized flat snapshot deliberately omits that history (shipping it would
carry author-identifying metadata and is unnecessary for reading the code). The
wrappers as shipped will **fail closed** at the frozen-checkout step. To use them,
obtain the project repository through the submission's artifact channel (provided at
de-anonymization / camera-ready), place this artifact's directories at the layout the
scripts expect — `conformance/` = `checker/` + `subject-and-controls/*.mpc` under
`conformance/mpc/`, `reference/` = `reference/`, `paper/heldout/` = `prereg/`,
`paper/mutations/` = `mutations/` — and run:

```bash
MPSPDZ="$MPSPDZ" bash paper/heldout/reproduce.sh   # held-out evaluation
MPSPDZ="$MPSPDZ" bash paper/reproduce.sh           # clean-room core + B4/B6/S1
```

This git-history dependency is a **packaging limitation** of the anonymized snapshot,
not of the evaluation: the science is fully contained in the shipped files, and
Path A regenerates the held-out outcomes directly.

## Restricted mutation model

The mutation study permits only the **application-level computational and delivery
transformations enumerated by the corpus** (`prereg/corpus.py` / `corpus.json`).
Arbitrary compile-time Python imports, filesystem or network side effects,
modification of the compiler environment, and mutation of the oracle, checker,
policy, CI workflow, validator, or compiler are **excluded**. This defines the
*operator space of the mutation study*; it is **not** an adversarial-security
boundary. A determined build-time adversary outside this operator space is out of
scope for the study and is not claimed to be caught.

## Integrity

```bash
sha256sum -c SHA256SUMS.txt
```

All files under `checker/`, `subject-and-controls/`, `reference/`, `prereg/`,
`mutations/`, `results/`, and `reproduce/` are byte-identical to the reviewed
research artifact. See `ERRATA.md` for two supersession notes (the non-exhaustive
cross-tape wording, and retained non-identifying development annotations).
