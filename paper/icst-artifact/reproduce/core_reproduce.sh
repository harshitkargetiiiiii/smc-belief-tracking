#!/usr/bin/env bash
# Complete clean-room reproduction of the FROZEN artifact AND the B4/B6/S1 mutation
# evidence, driven from the paper/strengthening branch.
#
# It orchestrates ONLY the frozen artifact's own scripts and functions
# (delivery_inspect, mpc_run, coverage, private_run) plus the compiler/runtime; it
# adds NO detection or oracle logic. The artifact UNDER TEST is not the branch you
# invoke this from: the script checks out the frozen tag (paper-external-review-v1)
# into a scratch worktree and runs the artifact from THERE, so the strengthening
# branch's paper/ files cannot influence the result.
#
# FAIL CLOSED: aborts if the frozen checkout is not the expected frozen commit, or
# if MP-SPDZ is not the pinned commit.
#
# Usage (from any checkout of paper/strengthening that has the frozen tag):
#     [MPSPDZ=/path/to/pinned/MP-SPDZ] bash paper/reproduce.sh
# If MPSPDZ is unset (or not the pin) a fresh pinned MP-SPDZ is cloned and built.
set -euo pipefail

FROZEN_TAG=paper-external-review-v1
EXPECTED_COMMIT=67da5eb1bd4796945b3b6a0cfb80066c3ea65751
PIN=9d809599ea6ce627216a389ca7d984fbb75d0cb9

ROOT=$(git rev-parse --show-toplevel)
HELPER="$ROOT/paper/mutations/reproduce_mutations.py"   # orchestration glue (this branch)
WORK=${WORK:-$(mktemp -d)}
FROZEN="$WORK/frozen"
cleanup() { git -C "$ROOT" worktree remove --force "$FROZEN" >/dev/null 2>&1 || true; }
trap cleanup EXIT
echo "== work dir: $WORK =="

# 1. Frozen artifact under test: check out the frozen tag, VERIFY the commit --------
if ! git -C "$ROOT" rev-parse -q --verify "refs/tags/$FROZEN_TAG" >/dev/null 2>&1; then
  git -C "$ROOT" fetch --tags --quiet || true
fi
git -C "$ROOT" rev-parse -q --verify "refs/tags/$FROZEN_TAG" >/dev/null 2>&1 || {
  echo "FAIL CLOSED: frozen tag $FROZEN_TAG not available in $ROOT"; exit 1; }
git -C "$ROOT" worktree add --detach "$FROZEN" "$FROZEN_TAG" >/dev/null
GOT=$(git -C "$FROZEN" rev-parse HEAD)
if [ "$GOT" != "$EXPECTED_COMMIT" ]; then
  echo "FAIL CLOSED: frozen checkout $GOT != expected $EXPECTED_COMMIT"; exit 1
fi
echo "== frozen artifact under test: $FROZEN_TAG @ $GOT (verified) =="

# 2. MP-SPDZ at the pin (reuse $MPSPDZ only if it IS the pin; else build) -----------
if [ -n "${MPSPDZ:-}" ] && [ -x "${MPSPDZ}/replicated-ring-party.x" ] \
   && [ "$(git -C "$MPSPDZ" rev-parse HEAD 2>/dev/null || true)" = "$PIN" ]; then
  echo "== reusing MP-SPDZ at $MPSPDZ =="
else
  MPSPDZ="$WORK/MP-SPDZ"
  git clone --depth 1 https://github.com/data61/MP-SPDZ.git "$MPSPDZ"
  ( cd "$MPSPDZ" && git fetch --depth 1 origin "$PIN" && git checkout "$PIN" \
      && make -j"$(nproc)" replicated-ring-party.x )
fi
MPGOT=$(git -C "$MPSPDZ" rev-parse HEAD 2>/dev/null || echo none)
if [ "$MPGOT" != "$PIN" ]; then
  echo "FAIL CLOSED: MP-SPDZ $MPGOT != pinned $PIN"; exit 1
fi
export MPSPDZ
# TLS certs (runtime; needed for the S1 execution)
if [ "$(ls "$MPSPDZ"/Player-Data/*.pem 2>/dev/null | wc -l | tr -d ' ')" -lt 3 ]; then
  ( cd "$MPSPDZ" && Scripts/setup-ssl.sh 3 )
fi
echo "== MP-SPDZ under test: $MPGOT (verified) =="

# 3. Core artifact -- run FROM the verified frozen checkout -------------------------
cd "$FROZEN"
mkdir -p conformance/_evidence
echo "== unit tests =="
python3 -m pytest reference/ conformance/ -q
echo "== named-case harness =="
EVIDENCE=$FROZEN/conformance/_evidence/repro-harness.jsonl  python3 conformance/harness.py
echo "== delivery gate + 5 negative controls + private cases =="
EVIDENCE=$FROZEN/conformance/_evidence/repro-private.jsonl  python3 conformance/private_run.py
echo "== 228-case coverage matrix =="
EVIDENCE=$FROZEN/conformance/_evidence/repro-coverage.jsonl python3 conformance/coverage.py
echo "== validate evidence (SHA-bound + --recompute) =="
python3 conformance/validate_evidence.py conformance/_evidence/repro-private.jsonl \
    --count 4 --private --repo "$GOT" --mpspdz "$PIN" --recompute
python3 conformance/validate_evidence.py conformance/_evidence/repro-coverage.jsonl \
    --count 228 --repo "$GOT" --mpspdz "$PIN"

# 4. Mutation reproductions B4 / B6 / S1 (frozen linter + frozen mutation sources) --
echo "== mutation reproductions B4 / B6 / S1 =="
PYTHONPATH="$FROZEN/conformance" MUT_SRC="$FROZEN/paper/mutations" MPSPDZ="$MPSPDZ" \
    python3 "$HELPER"

echo
echo "ALL REPRODUCED: core artifact (117 tests, harness, gate+5 controls, 228-case"
echo "matrix, evidence validation) + B4 synthetic + B6 caught + S1 lint-PASS/runtime"
echo "oracle mismatch. Frozen tag $FROZEN_TAG @ $GOT ; MP-SPDZ $PIN."
