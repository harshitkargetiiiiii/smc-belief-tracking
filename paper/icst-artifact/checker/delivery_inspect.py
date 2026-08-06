"""
LINTER, NOT A SOUNDNESS PROOF (re-review-7 decision). This inspects compiled
assembly for GROSS leak patterns and rejects five committed negative controls, but
it does NOT and CANNOT certify non-leakage. A masked comparison-open and a raw
verdict-reveal are the SAME opcode (`asm_open`, either flag; masked vs raw is not
determined by opcode identity alone), and a verdict can be routed into a subtape's
open via the `call_tape`/`call_arg` register-argument channel the honest comparison
subtapes THEMSELVES use (Codex's call_arg finding, issue #5; verified: the clean
subtapes receive operands via `call_arg`, no memory), so it cannot be forbidden.
The memory channel this linter DOES forbid (rules g+h) was attacker-only. A `PASS`
means "no known gross leak pattern found", NOT "provably private". Sound
non-leakage needs the protocol-level human/formal review ADVERSARY.md mandates and
is OUT OF SCOPE for this linter. See docs/limits.md.

Compiled-delivery inspection by CONTENT + pinned multiset + memory channel (rr-5).

Re-review-2 keyed the masked-subtape allowlist on the tape KIND string
(`(EQZ|LTZ)\\(`). But an .mpc author controls tape names: `program.new_tape(fn,
name='EQZ(spoof)')` writes the name verbatim, so a subtape that `privateoutput`s
another party's secret to the wrong player and `intoutput`s it to a file passed
the old gate (verified). `_main_players` also only parsed the MAIN tape, so a
wrong-player `privateoutput` in a subtape was never checked.

This version binds on CONTENT. Verified facts about the pinned backend
(replicated-ring-party.x @ 9d80959):
  * an open instruction (`asm_open`/`vasm_open`, EITHER the `True` or the `False`
    flag) is a PUBLIC reveal -- reconstructing the value to all parties. The flag
    only controls the post-open correctness check, NOT privacy (re-review-4:
    `final_verdict.reveal(False)` compiles to `asm_open ..., False` and still
    leaks). A masked comparison open is safe because it opens a BLINDED
    intermediate, which cannot be distinguished from a raw reveal at the opcode
    level. So the gate does NOT treat `False` opens as safe; see (f).
  * the clean private build's MAIN tape has exactly: `privateoutput` to players
    [0,0,1,1,2,2], guarded `cond_print_*`, and NO open and NO other sink.
  * the full per-tape assembly is DETERMINISTIC across compiles, and the non-main
    tape multiset is exactly {EQZ(3)_63, EQZ(81)_63, LTZ(36)_64} for both queries.

A build is private-delivering iff ALL hold:
  (a) exactly one MAIN tape ("-0"); its `privateoutput` player multiset is
      exactly [0,0,1,1,2,2]; it performs NO open; its only sinks are
      `privateoutput` + guarded `cond_print_*`.
  (b) NO `privateoutput` appears in ANY non-main tape (player set is bound across
      the WHOLE manifest, not just main).
  (c) NO public open-to-all (`... , True`) appears in ANY tape.
  (d) NO cleartext/file/socket sink opcode (print_reg*/print_char*/print_int*/
      print_float*/print_str*/intoutput/floatoutput/rawoutput/writesocket*/
      writefile*/writesharestofile) appears in ANY tape; guarded `cond_print_*`
      is the only permitted print, and only in main.
  (e) every non-main tape is a compiler-generated masked comparison tape, matched
      by the STRICT pattern `^(EQZ|LTZ)\\(\\d+\\)_\\d+$` (an author-introduced
      tape, incl. a non-digit name spoof like `EQZ(spoof)`, is rejected).
  (f) the non-main tape base MULTISET equals the pinned comparison subtapes
      exactly ({EQZ(3)_63, EQZ(81)_63, LTZ(36)_64}); an author who ADDS an open in
      a new/duplicate subtape breaks it (removing a real comparison breaks
      functional conformance).
  (g) the MAIN tape performs NO memory STORE, and (h) every non-main tape performs
      NO memory access at all. Together (g)+(h) are the load-bearing defense
      against a `reveal(False)` injected into an EXISTING expected subtape while
      keeping the multiset (re-review-5): the verdict is a MAIN register, a
      cross-tape register reference is a compiler error, so the only way a verdict
      reaches a subtape's open is MAIN store -> subtape load. The clean build's
      MAIN never stores and its subtapes never touch memory, so both are forbidden.
      `threshold_smc_openfalse.mpc` (scalar `stms`/`ldms`) and
      `threshold_smc_openfalse_vec.mpc` (vectorized `vstms`/`vldms`, re-review-6)
      are the committed controls.

manifest_signature() now hashes the FULL normalized assembly of every tape, so an
injected sink/tape/open changes it (the old 4-pattern hash collided).
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
_OPEN = re.compile(r"\b(v?asm_open|open)\b")
_OPEN_TRUE = re.compile(r"\b(v?asm_open|open)\b[^#]*\bTrue\b")
_CONDPRINT = re.compile(r"\bcond_print\w*\b")
_MASKED_NAME = re.compile(r"^(EQZ|LTZ)\(\d+\)_\d+$")
# cleartext / file / socket output sinks (guarded cond_print_* is NOT here)
_SINK = re.compile(
    r"\b(print_reg\w*|print_char\w*|print_int\w*|print_float\w*|print_str\w*|"
    r"print_bit\w*|print_mem\w*|intoutput|floatoutput|rawoutput|"
    r"writesocket\w*|writesharestofile|writefileclear|writefileshare|"
    r"write_to_file)\b")

# Memory opcodes. The verdict is computed in MAIN; a cross-tape register reference
# is a COMPILER ERROR ("Register from other tape"), so the ONLY way a verdict can
# reach a subtape (to be opened there) is via memory: MAIN stores it, the subtape
# loads it. The clean private build's MAIN performs NO store and its subtapes touch
# memory NOT AT ALL (verified), so forbidding a MAIN store and ANY subtape memory
# access closes that channel -- catching a `reveal(False)` injected into an
# expected subtape even when the tape multiset is left untouched (re-review-5).
# The `v?` (VECTORIZED, e.g. vstms/vldms) and `g?` (GF2n) prefixes are BOTH
# covered -- re-review-6 showed a scalar-only regex missed the vectorized forms.
_MEMSTORE = re.compile(r"\bv?g?stm[a-z]*\b")     # stm*/gstm*/vstms/vgstm* (all store forms)
_MEMLOAD = re.compile(r"\bv?g?ldm[a-z]*\b")       # ldm*/gldm*/vldms/vgldm* (all load forms)

# The EXACT non-main tape multiset the computation must generate (both queries).
# re-review-4: `asm_open(..., False, ...)` is ALSO a public reveal (the flag only
# skips the post-open check), and a masked open cannot be told from a raw reveal
# at the opcode level. The load-bearing defense is therefore this pin: an author
# can only ADD an open (removing a comparison breaks functional conformance), and
# any added open lands in a NEW or DUPLICATE subtape, perturbing this multiset.
EXPECTED_SUBTAPES = ("EQZ(3)_63", "EQZ(81)_63", "LTZ(36)_64")


def compile_manifest(build_stem, query, prefix):
    """Compile with assembly output; return {tape_kind: asm_text} for ALL tapes.
    Removes stale assembly for this (prefix,stem,query) first (re-review-3 C4), so
    a cached MP-SPDZ dir cannot pollute the manifest with a prior run's tapes."""
    subprocess.run(["cp", f"{HERE}/mpc/{build_stem}.mpc",
                    f"{MPSPDZ}/Programs/Source/"], check=True)
    marker = f"{build_stem}-{query}-"
    for f in glob.glob(f"{MPSPDZ}/{prefix}-{marker}*"):
        os.remove(f)
    c = subprocess.run(["./compile.py", "-R", "64", "-a", prefix, build_stem, query],
                       cwd=MPSPDZ, capture_output=True, text=True)
    if c.returncode != 0:
        raise RuntimeError(f"compile -a failed:\n{c.stderr}\n{c.stdout}")
    man = {}
    for f in sorted(glob.glob(f"{MPSPDZ}/{prefix}-{marker}*")):
        kind = os.path.basename(f).split(marker, 1)[1]      # '0','EQZ(3)_63-5',...
        with open(f) as fh:
            man[kind] = fh.read()
    return man


def _base(kind):
    return re.sub(r"-\d+$", "", kind)                       # drop trailing -index


def _privout_players(text):
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


def _lines_matching(rx, text):
    return [l.strip() for l in text.splitlines() if rx.search(l)]


def is_private_manifest(man, expected_subtapes=None):
    """(ok, reasons) over the complete manifest, by content (see module docstring).
    When expected_subtapes is given, the non-main tape base multiset must equal it
    EXACTLY -- the load-bearing defense, since any injected open (True OR False)
    adds/duplicates a subtape and cannot be told from a masked open by opcode."""
    reasons = []
    mains = [k for k in man if _base(k) == "0"]
    if len(mains) != 1:
        return False, [f"expected exactly one main tape, got {sorted(mains)}"]
    main = man[mains[0]]

    # (f) pinned comparison-subtape multiset: an added open perturbs it
    if expected_subtapes is not None:
        got = sorted(_base(k) for k in man if _base(k) != "0")
        if got != sorted(expected_subtapes):
            reasons.append(f"non-main tape multiset {got} != pinned {sorted(expected_subtapes)}")

    # (a) main: correct private delivery, no open, no non-cond print
    if _privout_players(main) != [0, 0, 1, 1, 2, 2]:
        reasons.append(f"main privateoutput players {_privout_players(main)} != [0,0,1,1,2,2]")
    if _lines_matching(_OPEN, main):
        reasons.append("main tape performs a protocol open (reveal)")
    main_sinks = _lines_matching(_SINK, main)
    if main_sinks:
        reasons.append(f"main tape has non-delivery output opcode: {main_sinks[:1]}")
    # (g) main must not STORE to memory: that is the only channel by which a
    # verdict register can reach a subtape (cross-tape refs are a compiler error).
    main_stores = _lines_matching(_MEMSTORE, main)
    if main_stores:
        reasons.append(f"main tape stores to memory (verdict exfil channel): {main_stores[:1]}")

    for kind, text in man.items():
        base = _base(kind)
        if base == "0":
            continue
        # (e) only compiler-generated masked comparison tapes may exist
        if not _MASKED_NAME.match(base):
            reasons.append(f"unexpected non-masked tape (author-introduced): {base}")
        # (b) no delivery out of a subtape
        if _privout_players(text):
            reasons.append(f"privateoutput in non-main tape {base}")
        # (d) no print/file/socket sink in a subtape; guarded print only in main
        sinks = _lines_matching(_SINK, text)
        if sinks:
            reasons.append(f"output/exfil opcode in non-main tape {base}: {sinks[:1]}")
        if _CONDPRINT.search(text):
            reasons.append(f"per-player print in non-main tape {base}")
        # (h) subtapes are pure (no memory): a verdict can only enter a subtape via
        # a load, so ANY subtape memory access is a possible verdict-exfil path.
        mem = _lines_matching(_MEMLOAD, text) + _lines_matching(_MEMSTORE, text)
        if mem:
            reasons.append(f"non-main tape {base} accesses memory (verdict exfil path): {mem[:1]}")

    # (c) public open-to-all forbidden anywhere
    for kind, text in man.items():
        pub = _lines_matching(_OPEN_TRUE, text)
        if pub:
            reasons.append(f"public open-to-all (reveal) in tape {_base(kind)}: {pub[:1]}")
    return (not reasons), reasons


def _norm_body(text):
    """Full normalized tape body: strip comments + blank lines, keep every opcode."""
    out = []
    for l in text.splitlines():
        s = l.split("#", 1)[0].strip()
        if s:
            out.append(s)
    return out


def manifest_signature(man):
    """Hash the FULL normalized assembly of every tape (deterministic across
    compiles). Any injected opcode, tape, or open changes it -- unlike the old
    4-pattern hash, which collided on leaks injected as extra opcodes."""
    parts = []
    for kind in sorted(man, key=_base):
        parts.append(_base(kind) + "\n" + "\n".join(_norm_body(man[kind])))
    return hashlib.sha256("\n==\n".join(parts).encode()).hexdigest()


# --- backward-compatible single-tape helpers (used by synthetic unit tests) ---

def is_private_delivery(main_text):
    reasons = []
    if _privout_players(main_text) != [0, 0, 1, 1, 2, 2]:
        reasons.append(f"privateoutput players {_privout_players(main_text)} != [0,0,1,1,2,2]")
    if _lines_matching(_OPEN, main_text):
        reasons.append("main tape has public open(s)")
    return (not reasons), reasons


def delivery_signature(main_text):
    return hashlib.sha256(main_text.encode()).hexdigest()


def gate(query):
    """Executable negative controls: the private build is accepted; the public-open
    (leaky), separate-tape (subleak), name-spoof, and reveal(False) (openfalse)
    siblings are all rejected."""
    detail = {}
    priv = compile_manifest("threshold_smc_private", query, "asm_priv")
    ok_priv, r_priv = is_private_manifest(priv, EXPECTED_SUBTAPES)
    detail["private_ok"] = ok_priv
    detail["private_reasons"] = r_priv
    detail["private_delivery_sig"] = manifest_signature(priv)

    for stem, key, pfx in (
        ("threshold_smc_leaky", "leaky_rejected", "asm_leaky"),
        ("threshold_smc_subleak", "subleak_rejected", "asm_sub"),
        ("threshold_smc_namespoof", "namespoof_rejected", "asm_ns"),
        ("threshold_smc_openfalse", "openfalse_rejected", "asm_of"),
        ("threshold_smc_openfalse_vec", "openfalse_vec_rejected", "asm_ofv"),
    ):
        m = compile_manifest(stem, query, pfx)
        detail[key] = not is_private_manifest(m, EXPECTED_SUBTAPES)[0]

    ok = (ok_priv and detail["leaky_rejected"] and detail["subleak_rejected"]
          and detail["namespoof_rejected"] and detail["openfalse_rejected"]
          and detail["openfalse_vec_rejected"])
    return ok, detail


if __name__ == "__main__":
    all_ok = True
    for q in ("sum_even", "p1_is_max"):
        ok, d = gate(q)
        print(f"[delivery] {q}: private_ok={d['private_ok']} "
              f"leaky_rejected={d['leaky_rejected']} "
              f"subleak_rejected={d['subleak_rejected']} "
              f"namespoof_rejected={d['namespoof_rejected']} "
              f"openfalse_rejected={d['openfalse_rejected']} "
              f"openfalse_vec_rejected={d['openfalse_vec_rejected']} -> {'PASS' if ok else 'FAIL'}")
        if d["private_reasons"]:
            print("   ", d["private_reasons"])
        all_ok = all_ok and ok
    print("DELIVERY LINT OK (no gross leak pattern; NOT a non-leakage proof)"
          if all_ok else "DELIVERY LINT FAILED")
    sys.exit(0 if all_ok else 1)
