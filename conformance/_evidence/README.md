# Raw conformance evidence (machine-readable)

`*.jsonl.gz` — one JSON record per circuit execution (round-5 re-review, issue #4).
These are the RAW compiler/runtime logs, not summaries. `../results-*.txt` are
human summaries only.

Each record:
- `repo_sha`, `mpspdz_sha` — provenance
- `query`, `case_id`, `input_hash` — which case, deterministic hash of the exact
  per-party input bytes
- `compile_rc`, `compile_stdout`, `compile_stderr` — compiler output (first
  compile per query; `null` rc when reusing cached bytecode)
- `ring_rc`, `ring_stdout`, `ring_stderr` — runtime output (every run)

Regenerate:  `EVIDENCE=$PWD/_evidence/coverage.jsonl MPSPDZ=/path python3 coverage.py`
CI produces and uploads these for every run.
