#!/usr/bin/env python3
"""
Harness self-test: drive the FROZEN linter over the already-PUBLIC committed
B-series controls (whose outcomes are in paper/mutations/detection_matrix.json) to
validate the compile+lint pipeline BEFORE the held-out run. This touches NONE of the
held-out mutants, so it does not peek at any pre-registered prediction.

Expected (public): the private build PASSES; leaky/subleak/namespoof/openfalse/
openfalse_vec all REJECT.
"""
import os
import sys

sys.path.insert(0, os.environ["HELDOUT"])
import delivery_inspect as DI

EXPECT = {
    "threshold_smc_private": True,        # PASS
    "threshold_smc_leaky": False,         # REJECT
    "threshold_smc_subleak": False,
    "threshold_smc_namespoof": False,
    "threshold_smc_openfalse": False,
    "threshold_smc_openfalse_vec": False,
}
fails = []
for stem, expect_pass in EXPECT.items():
    man = DI.compile_manifest(stem, "p1_is_max", "asm_self")
    ok, reasons = DI.is_private_manifest(man, DI.EXPECTED_SUBTAPES)
    good = (ok == expect_pass)
    print(f"  [{'ok' if good else 'BAD'}] {stem:32} linter={'PASS' if ok else 'REJECT':6} "
          f"expected={'PASS' if expect_pass else 'REJECT'}")
    if not good:
        fails.append(stem)
if fails:
    sys.exit(f"SELFTEST FAILED: {fails}")
print("SELFTEST OK: harness reproduces the public B-series outcomes")
