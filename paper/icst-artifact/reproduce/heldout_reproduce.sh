#!/usr/bin/env bash
# Reproduce the held-out evaluation against the FROZEN delivery linter @ 305a3a8.
#
# Orchestration only: the checker (conformance/delivery_inspect.py), the oracle
# (mpc_run/private_run), and the evidence validator are all taken UNMODIFIED from a
# verified 305a3a8 checkout. This script and the held-out corpus live on the
# evaluation branch; the checker under test does not.
#
# FAIL CLOSED: aborts unless the checker checkout is commit 305a3a8 and MP-SPDZ is
# the pin. run_heldout.py additionally asserts the delivery_inspect.py git-blob hash.
#
# Usage (from a checkout of the held-out branch):
#     [MPSPDZ=/path/to/pinned/MP-SPDZ] bash paper/heldout/reproduce.sh
set -euo pipefail

BASELINE=305a3a8d1810c427edcc32520352e74610c7866c
PIN=9d809599ea6ce627216a389ca7d984fbb75d0cb9

ROOT=$(git rev-parse --show-toplevel)
HELDOUT="$ROOT/paper/heldout"
WORK=${WORK:-$(mktemp -d)}
FROZEN="$WORK/frozen305"
cleanup() { git -C "$ROOT" worktree remove --force "$FROZEN" >/dev/null 2>&1 || true; }
trap cleanup EXIT

# 1. Frozen checker under test: 305a3a8, verified (fail closed) --------------------
git -C "$ROOT" rev-parse -q --verify "$BASELINE^{commit}" >/dev/null 2>&1 || git -C "$ROOT" fetch --quiet origin "$BASELINE" || true
git -C "$ROOT" worktree add --detach "$FROZEN" "$BASELINE" >/dev/null
GOT=$(git -C "$FROZEN" rev-parse HEAD)
[ "$GOT" = "$BASELINE" ] || { echo "FAIL CLOSED: checker checkout $GOT != $BASELINE"; exit 1; }
echo "== frozen checker under test: 305a3a8 @ $GOT (verified) =="

# 2. MP-SPDZ at the pin ------------------------------------------------------------
if [ -n "${MPSPDZ:-}" ] && [ -x "${MPSPDZ}/replicated-ring-party.x" ] \
   && [ "$(git -C "$MPSPDZ" rev-parse HEAD 2>/dev/null || true)" = "$PIN" ]; then
  echo "== reusing MP-SPDZ at $MPSPDZ =="
else
  MPSPDZ="$WORK/MP-SPDZ"
  git clone --depth 1 https://github.com/data61/MP-SPDZ.git "$MPSPDZ"
  ( cd "$MPSPDZ" && git fetch --depth 1 origin "$PIN" && git checkout "$PIN" \
      && make -j"$(nproc)" replicated-ring-party.x )
fi
[ "$(git -C "$MPSPDZ" rev-parse HEAD)" = "$PIN" ] || { echo "FAIL CLOSED: MP-SPDZ != pin"; exit 1; }
export MPSPDZ
if [ "$(ls "$MPSPDZ"/Player-Data/*.pem 2>/dev/null | wc -l | tr -d ' ')" -lt 3 ]; then
  ( cd "$MPSPDZ" && Scripts/setup-ssl.sh 3 )
fi
echo "== MP-SPDZ under test: $PIN (verified) =="

# 3. (optional) harness self-test on the PUBLIC B-series ---------------------------
if [ "${SELFTEST:-1}" = "1" ]; then
  echo "== harness self-test on the committed B-series (public outcomes) =="
  PYTHONPATH="$FROZEN/conformance" HELDOUT="$HELDOUT" MPSPDZ="$MPSPDZ" \
      python3 "$HELDOUT/selftest_bseries.py"
fi

# 4. Held-out evaluation (single run) ----------------------------------------------
echo "== held-out evaluation (single run) =="
PYTHONPATH="$FROZEN/conformance" HELDOUT="$HELDOUT" MPSPDZ="$MPSPDZ" \
    python3 "$HELDOUT/run_heldout.py"
echo "== wrote $HELDOUT/results.json =="
