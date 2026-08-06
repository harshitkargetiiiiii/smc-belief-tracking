"""
Executable spec of the three Step-4 interface rules that a circuit must obey,
so they can be regression-tested BEFORE any MPC circuit exists. Pure Python; no
MP-SPDZ. These are deliberately a SEPARATE formulation from oracle.py — the
tests assert they AGREE with the oracle, which is the point.

Rules pinned here (round-4b re-review, issue #3):

1. Public output alphabet + secret-support-safe zero branches.
   The circuit cannot look at the secret support, so it iterates the PUBLIC
   compile-time alphabet O_Q = {Q(s) : s in D^N}. A branch that is impossible
   under the actual belief has Z = 0, and with non-negative weights every M = 0,
   so `b*M <= a*Z` is `0 <= 0` = pass. Iterating the public alphabet therefore
   gives the SAME accept/reject as iterating the secret support, with no
   secret-dependent branching.

2. Signed no-wraparound bound.
   MP-SPDZ integer comparison is SIGNED: in a 2^k ring, values >= 2^(k-1) read as
   negative. So the requirement is `B < 2^(k-1)`, NOT `2^k > B`, where
   B = max(a,b) * S * W bounds every compared operand (and every intermediate in
   the secret evaluation of Q).

3. Fixed masking on reject.
   A rejected recipient must receive a payload independent of the actual output:
   `payload_j = o_actual if accept_j else MASK` (a fixed constant). Only
   `(accept_j, payload_j)` is revealed to P_j.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import product
from typing import Callable, Sequence

Assignment = tuple[int, ...]
Belief = dict[Assignment, Fraction]
Query = Callable[[Assignment], int]

MASK = 0                      # fixed reject payload


def public_output_alphabet(domain: Sequence[int], n: int, query: Query) -> list[int]:
    """O_Q over the whole public domain, independent of any secret/belief."""
    return sorted({query(s) for s in product(domain, repeat=n)})


def branch_check_int(dj: Belief, query: Query, i: int, o: int,
                     a: int, b: int) -> bool:
    """Integer, division-free check for one output branch and protected party i,
    using unnormalized weights: pass iff for all n, b*M_{i,n} <= a*Z.
    Z = 0 (impossible branch) => all M = 0 => 0 <= 0 => pass. No branching on Z."""
    z = Fraction(0)
    m: dict[int, Fraction] = {}
    for s, p in dj.items():
        if p < 0:
            raise ValueError("negative mass")
        if p > 0 and query(s) == o:
            z += p
            m[s[i]] = m.get(s[i], Fraction(0)) + p
    # scale-invariant: works for normalized Fractions or raw integer weights
    return all(b * mv <= a * z for mv in m.values()) if m else True


def tcheck_public(dj: Belief, query: Query, i: int, t_i: Fraction,
                  alphabet: Sequence[int]) -> bool:
    """The circuit's check: iterate the PUBLIC alphabet, integer comparison."""
    a, b = t_i.numerator, t_i.denominator
    return all(branch_check_int(dj, query, i, o, a, b) for o in alphabet)


def signed_ring_ok(B: int, k: int) -> bool:
    """A 2^k signed ring holds B iff B < 2^(k-1)."""
    return B < (1 << (k - 1))


def weight_bound(a: int, b: int, S: int, W: int) -> int:
    """B = max(a,b) * S * W — bounds every compared operand."""
    return max(a, b) * S * W


def signed_read(x: int, k: int) -> int:
    """How a 2^k signed ring interprets x (for demonstrating the bug)."""
    x %= (1 << k)
    return x - (1 << k) if x >= (1 << (k - 1)) else x


def masked_payload(accept: bool, o_actual: int, mask: int = MASK) -> int:
    return o_actual if accept else mask
