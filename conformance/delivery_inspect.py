"""
Compiled-delivery inspection (gate 2 re-review, issue #5, blocker 2).

A stdout oracle CANNOT distinguish private output from public open + hidden
printing. This does. It compiles a build to assembly (compile.py -a) and inspects
the MAIN tape's delivery of the six final verdict wires:

  - PRIVATE build: delivered via `privateoutput` to players [0,0,1,1,2,2], and
    the main tape contains NO public open (`asm_open`/`open`) — the masked
    comparison opens live in separate EQZ/LTZ subroutine tapes, not the main tape.
  - LEAKY build (reveal()+print_ln_to): the six verdicts are `asm_open`ed
    publicly in the main tape; no `privateoutput`. is_private_delivery() returns
    False -> the gate REJECTS it.

This is the executable negative control the stdout checker could not provide.
"""
import hashlib
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mpc_run import MPSPDZ, HERE

_PRIVOUT = re.compile(r"^privateoutput\s+(\d+),\s*(.+?)(?:#.*)?$")
_OPEN = re.compile(r"\b(v?asm_open|open)\b")


def compile_asm(build_stem, query, prefix):
    """Compile <build_stem> for <query> emitting assembly with the given prefix.
    Returns the MAIN tape (`-0`) assembly text."""
    src = f"{HERE}/mpc/{build_stem}.mpc"
    subprocess.run(["cp", src, f"{MPSPDZ}/Programs/Source/"], check=True)
    c = subprocess.run(["./compile.py", "-R", "64", "-a", prefix, build_stem, query],
                       cwd=MPSPDZ, capture_output=True, text=True)
    if c.returncode != 0:
        raise RuntimeError(f"compile -a failed:\n{c.stderr}\n{c.stdout}")
    main = f"{MPSPDZ}/{prefix}-{build_stem}-{query}-0"
    with open(main) as f:
        return f.read()


def classify(main_text):
    """Classify the MAIN tape's final-verdict delivery."""
    priv_players = []
    priv_lines = []
    for line in main_text.splitlines():
        m = _PRIVOUT.match(line.strip())
        if m:
            priv_lines.append(line.strip())
            # groups look like: 1, <player>, cX, sY  (repeated)
            toks = [t.strip() for t in m.group(2).split(",")]
            # every 4th token starting at index 1 is the player
            for k in range(1, len(toks), 4):
                try:
                    priv_players.append(int(toks[k]))
                except (ValueError, IndexError):
                    pass
    public_opens = [l.strip() for l in main_text.splitlines()
                    if _OPEN.search(l) and "privateoutput" not in l]
    return {
        "private_players": sorted(priv_players),
        "n_private": len(priv_players),
        "public_opens": public_opens,
        "priv_lines": priv_lines,
    }


def is_private_delivery(main_text):
    """(ok, reasons). Private iff privateoutput delivers 6 outputs to
    [0,0,1,1,2,2] AND the main tape has no public open."""
    c = classify(main_text)
    reasons = []
    if c["private_players"] != [0, 0, 1, 1, 2, 2]:
        reasons.append(f"privateoutput players {c['private_players']} != [0,0,1,1,2,2]")
    if c["public_opens"]:
        reasons.append(f"main tape has {len(c['public_opens'])} public open(s): "
                       f"{c['public_opens'][:2]}")
    return (not reasons), reasons


def delivery_signature(main_text):
    """Stable hash of the delivery instructions (for evidence)."""
    c = classify(main_text)
    blob = "\n".join(c["priv_lines"] + c["public_opens"])
    return hashlib.sha256(blob.encode()).hexdigest()


def gate(query):
    """Run the executable negative control: the real private build must pass
    delivery inspection AND the leaky sibling must be rejected. Returns
    (ok, detail)."""
    detail = {}
    priv_main = compile_asm("threshold_smc_private", query, "asm_priv")
    ok_priv, r_priv = is_private_delivery(priv_main)
    detail["private_ok"] = ok_priv
    detail["private_reasons"] = r_priv
    detail["private_delivery_sig"] = delivery_signature(priv_main)

    leaky_main = compile_asm("threshold_smc_leaky", query, "asm_leaky")
    ok_leaky, _ = is_private_delivery(leaky_main)
    detail["leaky_rejected"] = (not ok_leaky)      # must be True
    detail["leaky_delivery_sig"] = delivery_signature(leaky_main)

    ok = ok_priv and (not ok_leaky)
    return ok, detail


if __name__ == "__main__":
    all_ok = True
    for q in ("sum_even", "p1_is_max"):
        ok, d = gate(q)
        print(f"[delivery] {q}: private_ok={d['private_ok']} "
              f"leaky_rejected={d['leaky_rejected']} -> {'PASS' if ok else 'FAIL'}")
        if d["private_reasons"]:
            print("   private reasons:", d["private_reasons"])
        all_ok = all_ok and ok
    print("DELIVERY INSPECTION OK" if all_ok else "DELIVERY INSPECTION FAILED")
    sys.exit(0 if all_ok else 1)
