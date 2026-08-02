#!/usr/bin/env bash
# Build MP-SPDZ and stage the circuits. Linux only; tested on Ubuntu 24.04.
#
#   ./scripts/setup.sh          # build for 64-bit rings (f=16 precision)
#   ./scripts/setup.sh 128      # also build for 128-bit rings (f=32 precision)
#
# Takes roughly 8-15 minutes on 2-4 cores. Coffee.

set -euo pipefail

RING_SIZE="${1:-64}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Installing build dependencies (needs sudo)"
sudo apt-get update -qq
sudo apt-get install -y --no-install-recommends \
    git build-essential \
    libgmp-dev libsodium-dev libssl-dev \
    libboost-dev libboost-thread-dev libboost-filesystem-dev libboost-iostreams-dev

if [ ! -d "$ROOT/MP-SPDZ" ]; then
    echo "==> Cloning MP-SPDZ"
    git clone --depth 1 https://github.com/data61/MP-SPDZ "$ROOT/MP-SPDZ"
fi

cd "$ROOT/MP-SPDZ"

echo "==> Building replicated-ring-party.x (RING_SIZE=$RING_SIZE)"
if [ "$RING_SIZE" != "64" ]; then
    # MP-SPDZ requires 2k <= ring size, so f=32/k=63 needs a 128-bit build.
    echo "MOD = -DRING_SIZE=$RING_SIZE" >> CONFIG.mine
    make clean
fi
make -j"$(nproc)" replicated-ring-party.x

echo "==> Generating TLS certificates for 3 parties"
Scripts/setup-ssl.sh 3

echo "==> Staging circuits"
cp "$ROOT"/mpc/*.mpc Programs/Source/

cat <<'EOF'

Done. Try:

    cd MP-SPDZ
    ./compile.py -R 64 belief3 91 16 31
    Scripts/ring.sh belief3-91-16-31

Expected: prints a verdict bit, and a timing line. On a 2-core host the
8281-state update took ~22.6 ms including preprocessing.

Cross-check the semantics against the reference before believing anything:

    python3 -m pytest reference/ -v

EOF
