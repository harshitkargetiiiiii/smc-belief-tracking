#!/usr/bin/env bash
# Minimal-command clean-room reproduction of the frozen artifact + paper mutations.
# Orchestrates the EXISTING, UNMODIFIED artifact scripts. Adds no artifact logic.
# Usage:  bash paper/reproduce.sh   (run from a fresh clone at tag paper-external-review-v1)
set -euo pipefail
PIN=9d809599ea6ce627216a389ca7d984fbb75d0cb9
ROOT=$(pwd); WORK=${WORK:-$ROOT/_repro}; mkdir -p "$WORK"; cd "$WORK"
if [ ! -x MP-SPDZ/replicated-ring-party.x ]; then
  [ -d MP-SPDZ ] || git clone --depth 1 https://github.com/data61/MP-SPDZ.git MP-SPDZ
  ( cd MP-SPDZ && git fetch --depth 1 origin "$PIN" && git checkout "$PIN" \
      && make -j"$(nproc)" replicated-ring-party.x && Scripts/setup-ssl.sh 3 )
fi
export MPSPDZ="$WORK/MP-SPDZ"; cd "$ROOT"
echo "== unit tests =="; python3 -m pytest reference/ conformance/ -q
echo "== harness ==";  EVIDENCE=$PWD/conformance/_evidence/repro-harness.jsonl  MPSPDZ=$MPSPDZ python3 conformance/harness.py
echo "== private ==";  EVIDENCE=$PWD/conformance/_evidence/repro-private.jsonl  MPSPDZ=$MPSPDZ python3 conformance/private_run.py
echo "== coverage =="; EVIDENCE=$PWD/conformance/_evidence/repro-coverage.jsonl MPSPDZ=$MPSPDZ python3 conformance/coverage.py
echo "== validate =="
MPSPDZ=$MPSPDZ python3 conformance/validate_evidence.py conformance/_evidence/repro-private.jsonl  --count 4   --private --repo "$(git rev-parse HEAD)" --mpspdz "$PIN" --recompute
MPSPDZ=$MPSPDZ python3 conformance/validate_evidence.py conformance/_evidence/repro-coverage.jsonl --count 228           --repo "$(git rev-parse HEAD)" --mpspdz "$PIN"
echo "ALL REPRODUCED (mutation reproductions B4/B6/S1: see paper/mutations/README.md and REPRODUCIBILITY.md)"
