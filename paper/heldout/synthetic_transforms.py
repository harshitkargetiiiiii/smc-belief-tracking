#!/usr/bin/env python3
"""
Synthetic manifest transforms for the held-out evaluation.

Each function takes the honest compiled manifest (dict {tape_kind: asm_text} from
the FROZEN delivery_inspect.compile_manifest of threshold_smc_private) and returns
a NEW mutated manifest. These are MANIFEST-LEVEL counterexamples (like the paper's
B4): they test whether the frozen linter's RULES have a clause that rejects a given
assembly pattern. Source-realizability is NOT claimed by construction and is
recorded per-mutant in corpus.py (the paper's B6 showed a naive SOURCE realization
of the call_arg channel is itself caught; these probe the rule set, not a
demonstrated source attack).

Injected opcodes reference registers (e.g. `s99`) WITHOUT a preceding memory
load/store, modelling a value that arrived via the call_tape/call_arg register
channel the honest comparison subtapes themselves use. No transform renames a tape
unless that is the point of the probe (topo_valid_name_offpin).
"""
import copy


def _base(kind):
    import re
    return re.sub(r"-\d+$", "", kind)


def _find(man, base):
    for k in man:
        if _base(k) == base:
            return k
    raise KeyError(base)


def _append(man, base, line):
    m = copy.deepcopy(man)
    k = _find(m, base)
    m[k] = m[k].rstrip("\n") + "\n" + line + "\n"
    return m


# ---- category 2: public/private open (register channel, no memory) ------------
def open_true_subtape(man):
    # raw PUBLIC open (True) of a register-passed value inside an existing subtape
    return _append(man, "EQZ(3)_63", "asm_open 3, True, c99, s99")


def open_true_vec_subtape(man):
    # vectorized PUBLIC open (True) inside an existing subtape
    return _append(man, "EQZ(81)_63", "vasm_open 3, True, c99, s99")


def open_false_callarg(man):
    # open with the False flag of a register-passed value inside an existing masked
    # subtape: NO memory, NO added tape, NOT open-to-all(True). The acknowledged gap.
    return _append(man, "EQZ(3)_63", "asm_open 3, False, c99, s99")


# ---- category 3: subtape / topology -------------------------------------------
def topo_reorder(man):
    # same tapes, reversed insertion order (is_private_manifest sorts internally)
    return {k: man[k] for k in reversed(list(man))}


def topo_extra_masked(man):
    # add an EXTRA well-formed masked tape (pure copy of an existing EQZ(3)_63 body)
    m = copy.deepcopy(man)
    k = _find(m, "EQZ(3)_63")
    m["EQZ(3)_63-99"] = m[k]
    return m


def topo_valid_name_offpin(man):
    # rename a subtape to a name that MATCHES the masked pattern but is off-pin
    m = copy.deepcopy(man)
    k = _find(m, "EQZ(81)_63")
    body = m.pop(k)
    m["EQZ(7)_63-1"] = body
    return m


# ---- category 4: secret-transfer / channel ------------------------------------
def chan_indirect_mem(man):
    # INDIRECT memory load inside a subtape (ldmsi/stmsi -- not exercised by B-series)
    return _append(man, "LTZ(36)_64", "ldmsi si9, ci9")


def chan_gf2n_mem(man):
    # GF2n memory load inside a subtape (gldms -- not exercised by B-series)
    return _append(man, "LTZ(36)_64", "gldms sg9, 4000")


def chan_callarg_noop(man):
    # a register move using a passed operand, NO open/sink/memory: benign legit use
    return _append(man, "EQZ(3)_63", "movs s99, s98")


# ---- category 6: transcript / output-channel ----------------------------------
def sink_writefile(man):
    return _append(man, "EQZ(3)_63", "writesharestofile s9, 0")


def sink_writesocket(man):
    return _append(man, "LTZ(36)_64", "writesocketshare 0, 0, 1, s9")


def sink_print_int(man):
    return _append(man, "EQZ(81)_63", "print_int ci9")


TRANSFORMS = {
    "open_true_subtape": open_true_subtape,
    "open_true_vec_subtape": open_true_vec_subtape,
    "open_false_callarg": open_false_callarg,
    "topo_reorder": topo_reorder,
    "topo_extra_masked": topo_extra_masked,
    "topo_valid_name_offpin": topo_valid_name_offpin,
    "chan_indirect_mem": chan_indirect_mem,
    "chan_gf2n_mem": chan_gf2n_mem,
    "chan_callarg_noop": chan_callarg_noop,
    "sink_writefile": sink_writefile,
    "sink_writesocket": sink_writesocket,
    "sink_print_int": sink_print_int,
}
