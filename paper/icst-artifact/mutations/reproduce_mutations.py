#!/usr/bin/env python3
"""
Mutation reproduction (B4 synthetic / B6 reconstructed / S1 reconstructed) driven
ENTIRELY by the FROZEN artifact's own functions.

This file is ORCHESTRATION GLUE ONLY. Every detection and oracle decision is made
by the frozen modules imported below (delivery_inspect, mpc_run, private_run); this
script adds no linter or oracle logic of its own. It re-runs, from a clean state:

  * B4 -- rebuild the SYNTHETIC manifest counterexample (real private manifest with
          a reveal(False) injected into an EXISTING EQZ(3)_63 body) and re-run the
          FROZEN is_private_manifest. Expect: REJECTED by the memory rule (h) with
          the tape multiset intact (not a multiset rejection).
  * B6 -- compile the reconstructed call_arg mutation and re-run the FROZEN
          is_private_manifest. Expect: REJECTED (the naive realization is caught --
          it is NOT a bypass). manifest_signature must equal the committed value.
  * S1 -- (a) compile the reconstructed wrong-semantics mutation and re-run the
          FROZEN is_private_manifest. Expect: PASS (delivery structure intact);
          manifest_signature must equal the committed value. Then
          (b) EXECUTE it at the pin for the discriminating (0,0,0)/uniform-weights/
          p1_is_max case and compare delivered (accept,payload) to the FROZEN
          oracle. Expect: a real oracle mismatch at parties [0,1,2].

Signatures compared are manifest_signature() = sha256 over the FULL NORMALIZED
per-tape assembly (comments and blank lines stripped); raw object files are not
byte-compared.

Environment:
  PYTHONPATH -> the FROZEN conformance/   (imports the frozen modules)
  MUT_SRC    -> the FROZEN paper/mutations/ (mutation sources + committed evidence)
  MPSPDZ     -> the pinned MP-SPDZ checkout
Exits non-zero on ANY deviation (fail closed).
"""
import copy
import glob
import hashlib
import json
import os
import subprocess
import sys

MUT = os.environ["MUT_SRC"]
QUERY = "p1_is_max"

import delivery_inspect as di  # noqa: E402  (frozen linter -- all detection lives here)
from mpc_run import MPSPDZ, N, S, state, oracle_expect, write_inputs  # noqa: E402
from private_run import strict_parse_party  # noqa: E402

DM = json.load(open(f"{MUT}/detection_matrix.json"))
SIG = {m["id"]: m.get("assembly_sha256_manifest") for m in DM["mutations"]}
S1EV = json.load(open(f"{MUT}/s1_runtime_evidence.json"))

_fails = []


def check(name, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  --  {detail}" if detail else ""))
    if not cond:
        _fails.append(name)


def _sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def compile_manifest_from(src, stem, query, prefix):
    """GLUE: compile an ARBITRARY .mpc (sources live in paper/mutations/, not under
    conformance/mpc/) into a {tape_kind: asm} manifest, mirroring the asm read in
    delivery_inspect.compile_manifest. Makes NO detection decision -- the returned
    manifest is handed to the frozen is_private_manifest/manifest_signature."""
    subprocess.run(["cp", src, f"{MPSPDZ}/Programs/Source/{stem}.mpc"], check=True)
    marker = f"{stem}-{query}-"
    for f in glob.glob(f"{MPSPDZ}/{prefix}-{marker}*"):
        os.remove(f)
    c = subprocess.run(["./compile.py", "-R", "64", "-a", prefix, stem, query],
                       cwd=MPSPDZ, capture_output=True, text=True)
    if c.returncode != 0:
        raise RuntimeError(f"compile -a failed:\n{c.stderr}\n{c.stdout}")
    man = {}
    for f in sorted(glob.glob(f"{MPSPDZ}/{prefix}-{marker}*")):
        kind = os.path.basename(f).split(marker, 1)[1]
        with open(f) as fh:
            man[kind] = fh.read()
    return man


# ---------------------------------------------------------------- B4 (synthetic)
print("== B4: synthetic manifest counterexample (frozen is_private_manifest) ==")
priv = di.compile_manifest("threshold_smc_private", QUERY, "asm_priv")   # frozen source
syn = copy.deepcopy(priv)
k = [x for x in syn if di._base(x) == "EQZ(3)_63"][0]
syn[k] += "\nldms s777, 4000\nasm_open 3, False, c0, s777\n"             # reveal(False) into existing body
ok4, r4 = di.is_private_manifest(syn, di.EXPECTED_SUBTAPES)
mem_reason = [r for r in r4 if "accesses memory" in r]
mset_reason = [r for r in r4 if "multiset" in r]
check("B4 rejected", not ok4)
check("B4 rejected by memory rule (h)", bool(mem_reason), str(mem_reason[:1]))
check("B4 tape multiset intact (NOT a multiset rejection)", not mset_reason)


# ------------------------------------------- honest-build call_tape/call_arg channel
# The channel B6 references: the honest private build passes SECRET comparison
# operands across the tape boundary via call_tape (main) / call_arg (subtapes),
# no memory -- so that channel cannot be blocklisted. `priv` is the honest manifest.
print("== honest build: call_tape/call_arg operand channel (frozen private manifest) ==")
_mk = [x for x in priv if di._base(x) == "0"][0]
main_call_tape = sum(1 for ln in priv[_mk].splitlines() if "call_tape" in ln)
sub_call_arg = sum(1 for kk, tt in priv.items() if di._base(kk) != "0"
                   for ln in tt.splitlines() if "call_arg" in ln)
sub_mem = any(("ldm" in ln or "stm" in ln)
              for kk, tt in priv.items() if di._base(kk) != "0"
              for ln in tt.splitlines())
check("honest MAIN uses call_tape x3", main_call_tape == 3, f"call_tape x{main_call_tape}")
check("honest subtapes use call_arg (no memory)",
      sub_call_arg == 3 and not sub_mem, f"call_arg x{sub_call_arg} subtape_mem={sub_mem}")


# ------------------------------------------------------------- B6 (reconstructed)
print("== B6: reconstructed call_arg mutation (frozen is_private_manifest) ==")
b6 = compile_manifest_from(f"{MUT}/threshold_smc_callarg.mpc",
                           "threshold_smc_callarg", QUERY, "asm_b6")
ok6, r6 = di.is_private_manifest(b6, di.EXPECTED_SUBTAPES)
sig6 = di.manifest_signature(b6)
check("B6 rejected (naive realization caught -- NOT a bypass)", not ok6, str(r6[:1]))
check("B6 manifest_signature == committed detection_matrix", sig6 == SIG["B6"], sig6[:16])


# ------------------------------------------------- S1 (reconstructed): lint + hash
print("== S1: reconstructed wrong-semantics mutation -- delivery linter ==")
check("S1 source sha256 == frozen s1_runtime_evidence",
      _sha(f"{MUT}/threshold_smc_wrongsem.mpc") == S1EV["source_sha256"])
s1 = compile_manifest_from(f"{MUT}/threshold_smc_wrongsem.mpc",
                           "threshold_smc_wrongsem", QUERY, "asm_s1")
ok1, r1 = di.is_private_manifest(s1, di.EXPECTED_SUBTAPES)
sig1 = di.manifest_signature(s1)
check("S1 PASSES the delivery linter structurally", ok1, str(r1[:1]))
check("S1 manifest_signature == committed detection_matrix", sig1 == SIG["S1"], sig1[:16])


# --------------------------------------------------- S1 runtime vs frozen oracle
print("== S1 runtime: execute at the pin, compare to the frozen oracle ==")
secrets = (0, 0, 0)


def _support(j, sj):
    return [i for i in range(S) if state(i)[j] == sj]


def _wv_uniform(j, sj):                        # == coverage.wvec(j,sj,'uniform')
    w = [0] * S
    for i in _support(j, sj):
        w[i] = 1
    return w


wv = [_wv_uniform(j, secrets[j]) for j in range(N)]
exp_acc, exp_pay, _, _ = oracle_expect(secrets, wv, QUERY)      # frozen oracle

subprocess.run(["cp", f"{MUT}/threshold_smc_wrongsem.mpc",
                f"{MPSPDZ}/Programs/Source/"], check=True)
c = subprocess.run(["./compile.py", "-R", "64", "threshold_smc_wrongsem", QUERY],
                   cwd=MPSPDZ, capture_output=True, text=True)
if c.returncode != 0:
    raise RuntimeError(f"runtime compile failed:\n{c.stderr}\n{c.stdout}")

write_inputs(secrets, wv)
prog = f"threshold_smc_wrongsem-{QUERY}"
port = os.environ.get("S1_PORT", "16723")
procs = []
for i in range(N):
    cmd = [f"{MPSPDZ}/replicated-ring-party.x", str(i), prog,
           "-pn", port, "-h", "localhost", "-OF", "."]
    procs.append(subprocess.Popen(cmd, cwd=MPSPDZ, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True))
delivered, rcs = {}, {}
for i, p in enumerate(procs):
    out, err = p.communicate(timeout=120)
    rcs[i] = p.returncode
    delivered[i] = strict_parse_party(out, i)     # frozen strict parser (2-line enforce)

mism = sorted(j for j in range(N)
              if delivered[j]["PAYLOAD"] != exp_pay[j] or delivered[j]["ACCEPT"] != exp_acc[j])
check("S1 all parties rc==0", all(v == 0 for v in rcs.values()), str(rcs))
check("S1 frozen oracle masks payload to [0,0,0] (all reject)",
      exp_pay == [0, 0, 0] and exp_acc == [0, 0, 0], f"acc={exp_acc} pay={exp_pay}")
check("S1 delivered PAYLOAD 1 to all parties (semantic error)",
      all(delivered[j]["PAYLOAD"] == 1 for j in range(N)),
      str({j: delivered[j] for j in range(N)}))
check("S1 oracle mismatch at parties [0,1,2]", mism == [0, 1, 2], str(mism))


print()
if _fails:
    print("MUTATION REPRODUCTION FAILED:", _fails)
    sys.exit(1)
print("MUTATION REPRODUCTION OK  (B4 synthetic / B6 caught / S1 lint-PASS + runtime oracle mismatch)")
