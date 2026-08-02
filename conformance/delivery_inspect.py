"""
Compiled-delivery inspection over the COMPLETE tape manifest (gate 2 re-review 2,
issue #5). The previous version inspected only the `-0` main tape, so a leak in a
separate `@function_tape` (public `reveal()` + `print_ln`) slipped through. This
inspects EVERY generated tape and binds them.

A build is private-delivering iff ALL hold:
  (a) the MAIN tape delivers the six verdicts via `privateoutput` to players
      [0,0,1,1,2,2] and has NO public open;
  (b) every NON-main tape is an allowlisted masked-comparison subtape (EQZ/LTZ);
  (c) NO public open (`asm_open ... True` / `open`) appears outside those masked
      subtapes;
  (d) NO UNCONDITIONAL cleartext print (`print_reg_plain` / `print_char*` /
      `print_float_plain` / `print_int`) appears in ANY tape. The legitimate
      per-player delivery uses `cond_print_*` (guarded by player id); a public
      leak uses the unconditional variants.

Codex's separate-tape `reveal()+print_ln('LEAK')` sibling violates (b), (c), and
(d); it is committed as `threshold_smc_subleak.mpc` and the gate REJECTS it.
"""
import glob
import hashlib
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mpc_run import MPSPDZ, HERE

_PRIVOUT = re.compile(r"^privateoutput\s+\d+,\s*(.+?)(?:#.*)?$")
_PUBOPEN = re.compile(r"\b(v?asm_open)\b")
_MASKED = re.compile(r"(EQZ|LTZ)\(")
_CLEARPRINT = re.compile(r"\b(print_reg_plain|print_float_plain|print_char4|"
                         r"print_char|print_int)\b")


def compile_manifest(build_stem, query, prefix):
    """Compile with assembly output; return {tape_kind: asm_text} for ALL tapes."""
    subprocess.run(["cp", f"{HERE}/mpc/{build_stem}.mpc",
                    f"{MPSPDZ}/Programs/Source/"], check=True)
    c = subprocess.run(["./compile.py", "-R", "64", "-a", prefix, build_stem, query],
                       cwd=MPSPDZ, capture_output=True, text=True)
    if c.returncode != 0:
        raise RuntimeError(f"compile -a failed:\n{c.stderr}\n{c.stdout}")
    marker = f"{build_stem}-{query}-"
    man = {}
    for f in sorted(glob.glob(f"{MPSPDZ}/{prefix}-{marker}*")):
        kind = os.path.basename(f).split(marker, 1)[1]      # '0','EQZ(3)_63-5',...
        with open(f) as fh:
            man[kind] = fh.read()
    return man


def _base(kind):
    return re.sub(r"-\d+$", "", kind)                       # drop trailing -index


def _main_players(text):
    players = []
    for line in text.splitlines():
        m = _PRIVOUT.match(line.strip())
        if m:
            toks = [t.strip() for t in m.group(1).split(",")]
            for k in range(1, len(toks), 4):                # groups: 1,<player>,c,s
                try:
                    players.append(int(toks[k]))
                except (ValueError, IndexError):
                    pass
    return sorted(players)


def _public_opens(text):
    return [l.strip() for l in text.splitlines()
            if _PUBOPEN.search(l) and "privateoutput" not in l]


def _cleartext_prints(text):
    return [l.strip() for l in text.splitlines() if _CLEARPRINT.search(l)]


def is_private_manifest(man):
    """(ok, reasons) over the complete manifest."""
    reasons = []
    main = None
    for kind, text in man.items():
        if _base(kind) == "0":
            main = text
    if main is None:
        return False, ["no main tape (-0) found"]

    if _main_players(main) != [0, 0, 1, 1, 2, 2]:
        reasons.append(f"main privateoutput players {_main_players(main)} != [0,0,1,1,2,2]")
    if _public_opens(main):
        reasons.append("main tape has a public open")

    for kind, text in man.items():
        base = _base(kind)
        if base == "0":
            pass
        elif not _MASKED.search(base):
            reasons.append(f"unexpected non-masked tape: {base}")
        # public opens only allowed inside masked subtapes
        if base != "0" and not _MASKED.search(base) and _public_opens(text):
            reasons.append(f"public open outside masked allowlist in {base}")
        # unconditional cleartext print anywhere is a leak
        cp = _cleartext_prints(text)
        if cp:
            reasons.append(f"unconditional cleartext print in {base}: {cp[:1]}")
    return (not reasons), reasons


def manifest_signature(man):
    """Stable hash binding the whole delivery manifest (tape kinds + their
    privateoutput / open / print structure). Any added leak tape changes it."""
    parts = []
    for kind in sorted(man):
        base = _base(kind)
        struct = sorted(
            l.strip() for l in man[kind].splitlines()
            if l.strip().startswith("privateoutput") or _PUBOPEN.search(l)
            or _CLEARPRINT.search(l) or "cond_print" in l)
        parts.append(base + "\n" + "\n".join(struct))
    return hashlib.sha256("\n==\n".join(parts).encode()).hexdigest()


# --- backward-compatible single-tape helpers (used by synthetic unit tests) ---

def is_private_delivery(main_text):
    reasons = []
    if _main_players(main_text) != [0, 0, 1, 1, 2, 2]:
        reasons.append(f"privateoutput players {_main_players(main_text)} != [0,0,1,1,2,2]")
    if _public_opens(main_text):
        reasons.append(f"main tape has public open(s)")
    return (not reasons), reasons


def delivery_signature(main_text):
    return hashlib.sha256(main_text.encode()).hexdigest()


def gate(query):
    """Executable negative controls: private build accepted; the public-open
    sibling AND the separate-tape leak sibling both rejected."""
    detail = {}
    priv = compile_manifest("threshold_smc_private", query, "asm_priv")
    ok_priv, r_priv = is_private_manifest(priv)
    detail["private_ok"] = ok_priv
    detail["private_reasons"] = r_priv
    detail["private_delivery_sig"] = manifest_signature(priv)

    leaky = compile_manifest("threshold_smc_leaky", query, "asm_leaky")
    detail["leaky_rejected"] = not is_private_manifest(leaky)[0]

    sub = compile_manifest("threshold_smc_subleak", query, "asm_sub")
    detail["subleak_rejected"] = not is_private_manifest(sub)[0]

    ok = ok_priv and detail["leaky_rejected"] and detail["subleak_rejected"]
    return ok, detail


if __name__ == "__main__":
    all_ok = True
    for q in ("sum_even", "p1_is_max"):
        ok, d = gate(q)
        print(f"[delivery] {q}: private_ok={d['private_ok']} "
              f"leaky_rejected={d['leaky_rejected']} "
              f"subleak_rejected={d['subleak_rejected']} -> {'PASS' if ok else 'FAIL'}")
        if d["private_reasons"]:
            print("   ", d["private_reasons"])
        all_ok = all_ok and ok
    print("DELIVERY INSPECTION OK" if all_ok else "DELIVERY INSPECTION FAILED")
    sys.exit(0 if all_ok else 1)
