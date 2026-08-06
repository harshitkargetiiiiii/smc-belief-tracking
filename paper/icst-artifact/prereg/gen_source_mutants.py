#!/usr/bin/env python3
"""Generate the SOURCE held-out mutants as minimal exact diffs off the frozen
honest build (conformance/mpc/threshold_smc_private.mpc @ 305a3a8). Each mutant
is byte-identical to the honest build except the single marked change, so any
linter/oracle difference is attributable only to that change. The generated
.mpc files are the committed pre-registered artifacts."""
import os, sys

HONEST = sys.argv[1]           # path to frozen threshold_smc_private.mpc
OUT = sys.argv[2]              # mutants output dir
src = open(HONEST).read()

DELIV = (
    "for j in range(N):\n"
    "    print_ln_to(j, 'PRIV %s ACCEPT %s', j, accept[j].reveal_to(j))\n"
    "    print_ln_to(j, 'PRIV %s PAYLOAD %s', j, payload[j].reveal_to(j))\n"
)
assert src.count(DELIV) == 1, "honest delivery block not found uniquely"
ACC = "    accept[j] = (viol == 0)\n"
assert src.count(ACC) == 1, "accept line not found uniquely"

def write(name, text):
    p = os.path.join(OUT, name)
    open(p, "w").write(text)
    print("wrote", name, len(text), "bytes")

# H-R1 recip_extra: append an extra foreign delivery (party0 payload -> player1)
write("H-R1_recip_extra.mpc", src +
      "\n# [H-R1] held-out: extra foreign recipient -- party 0's payload also to player 1\n"
      "print_ln_to(1, 'PRIV 0 PAYLOAD %s', payload[0].reveal_to(1))\n")

# H-R2 recip_perm: rotate destinations, keep original 'PRIV j' label
write("H-R2_recip_perm.mpc", src.replace(DELIV,
      "# [H-R2] held-out: recipient permutation -- party j delivered to player (j+1)%N\n"
      "for j in range(N):\n"
      "    r = (j + 1) % N\n"
      "    print_ln_to(r, 'PRIV %s ACCEPT %s', j, accept[j].reveal_to(r))\n"
      "    print_ln_to(r, 'PRIV %s PAYLOAD %s', j, payload[j].reveal_to(r))\n"))

# H-R3 recip_collapse: all verdicts to player 0
write("H-R3_recip_collapse.mpc", src.replace(DELIV,
      "# [H-R3] held-out: recipient collapse -- all verdicts delivered to player 0\n"
      "for j in range(N):\n"
      "    print_ln_to(0, 'PRIV %s ACCEPT %s', j, accept[j].reveal_to(0))\n"
      "    print_ln_to(0, 'PRIV %s PAYLOAD %s', j, payload[j].reveal_to(0))\n"))

# H-V1 sem_negate_accept: flip the accept predicate
write("H-V1_sem_negate_accept.mpc", src.replace(ACC,
      "    accept[j] = (viol != 0)    # [H-V1] held-out: negated accept (semantic)\n"))

# H-V2 sem_swap_acc_pay: swap the two delivered VALUES (structure intact)
write("H-V2_sem_swap_acc_pay.mpc", src.replace(DELIV,
      "# [H-V2] held-out: swapped accept/payload values (semantic)\n"
      "for j in range(N):\n"
      "    print_ln_to(j, 'PRIV %s ACCEPT %s', j, payload[j].reveal_to(j))\n"
      "    print_ln_to(j, 'PRIV %s PAYLOAD %s', j, accept[j].reveal_to(j))\n"))

# H-V3 sem_neighbor_payload: party j gets party (j+1)%N's payload VALUE (correct dest)
write("H-V3_sem_neighbor_payload.mpc", src.replace(DELIV,
      "# [H-V3] held-out: neighbor payload leak -- party j gets party (j+1)%N payload\n"
      "for j in range(N):\n"
      "    print_ln_to(j, 'PRIV %s ACCEPT %s', j, accept[j].reveal_to(j))\n"
      "    print_ln_to(j, 'PRIV %s PAYLOAD %s', j, payload[(j + 1) % N].reveal_to(j))\n"))

# H-X1 invalid_crosstape_ref: direct cross-tape register ref (expected COMPILE-FAIL)
write("H-X1_invalid_crosstape_ref.mpc", src +
      "\n# [H-X1] held-out: direct cross-tape register reference (expected COMPILE-FAIL)\n"
      "def _direct():\n"
      "    accept[1].reveal(False)      # closes over a MAIN register across a tape boundary\n"
      "program.run_tapes([program.new_tape(_direct, name='EQZ(3)_63')])\n")

# H-X2 invalid_syntax: undefined symbol (expected COMPILE-FAIL)
write("H-X2_invalid_undefined.mpc", src +
      "\n# [H-X2] held-out: undefined symbol (expected COMPILE-FAIL)\n"
      "_bogus = undefined_symbol_xyz + 1\n")
