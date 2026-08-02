# Raw conformance evidence (machine-readable)

Each record is one circuit execution, with the full compiler/runtime transcript
AND the finalized verdict.

## Authoritative, SHA-BOUND evidence: the CI artifact

The exact-SHA raw evidence is the CI `conformance-evidence` artifact, produced by
the `conformance-mpc` job. Only CI evidence is **bound**: records carry
`bound: true`, `repo_sha = $GITHUB_SHA`, `repo_sha_source: github_actions`, and
`mpspdz_sha` = the pinned commit. A CI validation step (`validate_evidence.py`)
fails the job unless both files have the exact record counts (4 and 228), all
required fields, `bound: true`, the exact repo SHA, and the pinned MP-SPDZ SHA.

## Committed files here are UNBOUND local snapshots

`local-unbound-*.jsonl.gz` were generated outside CI. A committed file cannot
contain the hash of the commit that hashes it, so these carry `repo_sha: null`,
`repo_sha_source: "unbound"`, `bound: false`. They are convenience snapshots for
offline inspection, NOT SHA-bound provenance. Do not cite them as exact-SHA
evidence — cite the CI artifact.

## Record fields

Transcript: `mpspdz_sha, query, case_id, input_hash, compile_rc, compile_stdout,
compile_stderr, ring_rc, ring_stdout, ring_stderr`.
Provenance: `repo_sha, repo_sha_source, bound`.
Finalized verdict (added after strict parse + oracle compare): `parse_ok,
comparison_ok, mismatches, error, final` (PASS/FAIL). Failure records are retained.

Regenerate (unbound):
  `EVIDENCE=$PWD/_evidence/coverage.jsonl MPSPDZ=/path python3 coverage.py`
