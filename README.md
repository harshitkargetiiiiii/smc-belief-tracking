# SMC Belief Tracking

An implementation of the *SMC belief tracking* method proposed in:

> Piotr Mardziel, Michael Hicks, Jonathan Katz, Mudhakar Srivatsa.
> **Knowledge-Oriented Secure Multiparty Computation.**
> PLAS 2012. https://www.cs.umd.edu/~mwh/papers/belief-smc.pdf

That paper introduced two mechanisms for enforcing knowledge-threshold policies
in secure multiparty computation — the *belief set method* and *SMC belief
tracking* — proved them sound, and evaluated them by simulation. It implemented
the first. It did not implement the second, and said so:

> "belief tracking is a recursive procedure, since it is an interpreter, and
> recursive procedures are hard to implement with SMC. [...] So it remains to be
> seen whether SMC belief tracking can be implemented in a practical sense. We
> leave exploration of implementation strategies to future work."

An initial literature survey found no implementation in the fourteen years
since. That survey was not exhaustive — Google Scholar and Semantic Scholar were
both unreachable at the time — so **confirm this before claiming it anywhere.**

This repository is an attempt at that implementation.

## Status: claims refuted, do not build on this

An external adversarial review on 2026-08-02 refuted all three claims this
project rested on. See [issue #1](https://github.com/harshitkargetiiiiii/smc-belief-tracking/issues/1),
`docs/claims.md` (what we got wrong) and `docs/gap.md` (what is missing).

Summary of what is now known to be false:

- **Conditioning is not free.** The secret belief weight must be multiplied by
  the secret indicator. Our own circuit does this 41,098 times, a number the
  README previously printed beside the words "zero multiplications." The part
  of the claim that is true — public-constant x share is local — is textbook
  MPC (Cramer, Damgard & Maurer, EUROCRYPT 2000).
- **The integer-exactness claim** is an elementary unbounded-arithmetic lemma,
  is not implemented in MPC, assumes a uniform prior, has no ring-overflow
  bound, and its p=1/2 bit-growth estimate is wrong.
- **The specialisation argument misreads PLAS 2012**, which already states that
  Q is public before raising the interpreter objection.
- **The circuits are not the PLAS functionality.** They reveal the accept/reject
  verdict publicly, which PLAS explicitly forbids; they carry no state between
  invocations; and `belief4.mpc` conditions later rounds on the wrong hypothesis
  table.

The timings below are retained only as a record. They measure a partial,
security-incompatible subcomputation. **Do not cite them.**

## Layout

```
mpc/         MP-SPDZ circuits (.mpc). Start with belief3.mpc.
reference/   Exact-rational ground truth + tests. This is the oracle.
scripts/     Build and run helpers.
docs/        claims.md          - the two unverified observations. Read this second.
             for-external-review.md - self-contained brief for reviewers
             review-log.md      - every critique, logged with resolution
```

## Quick start

```bash
python3 -m pytest reference/ -v      # 25 tests, no dependencies beyond pytest
./scripts/setup.sh                   # builds MP-SPDZ, ~10 min
cd MP-SPDZ
./compile.py -R 64 belief3 91 16 31
Scripts/ring.sh belief3-91-16-31
```

CI runs the reference suite on every push and the MPC benchmark on demand
(Actions → benchmark → Run workflow) across emulated localhost/LAN/WAN.

## The setup

`N` parties, party *i* holds a secret `s_i` in a finite domain. A
knowledge-threshold policy for party *i* says no other party may assign
posterior probability greater than `t_i` to any value of `s_i`. Before releasing
a query output, the parties check — *inside* the secure computation, using the
real secret values — whether releasing it would push anyone's belief past their
threshold. Doing the check inside MPC is what keeps the rejection decision
itself from leaking.

Benchmark from the paper: 3 parties, domain 91 (values 10–100), query
"am I the richest?", 8281-state joint belief.

## Measured (loopback, 2 vCPU, one host — see status warning)

| Config | states | mults | rounds | time |
|---|---|---|---|---|
| 1 update, no renorm, f=16 | 8,281 | 41,098 | 88 | 22.6 ms |
| 1 update, no renorm, f=32, Z_2^128 | 8,281 | 58,642 | 97 | 45.5 ms |
| full unfactored 91³ joint | 753,571 | 758,997 | 86 | 760 ms |
| 1 update + secure renorm, f=16 | 8,281 | 49,650 | 131 | 109 ms |
| 20 rounds + renorm, f=16 | 8,281 | 531,376 | 834 | 1.61 s |

Correctness pin: with secrets (63, 40, 55) the posterior is uniform over the
54×54 states with `s2, s3 <= 63`, so the max marginal is exactly 1/54 =
0.0185185. Both the MPC and the reference agree.
(`reference/test_reference.py::test_known_case_63_40_55`)

## Why we thought it was cheap — and why that was wrong

Retained for the record. Both observations were refuted; see `docs/claims.md`.

1. ~~Conditioning is communication-free.~~ False: the secret weight must be
   multiplied by the secret indicator.
2. ~~Indicator conditioning is exact in integers.~~ Only as an unbounded-
   arithmetic lemma, unimplemented, with no ring bound.

~~The recursion objection does not apply.~~ False: PLAS already assumed a public
query before raising it.

## The real problem: fixed point

MP-SPDZ's default precision will silently give wrong answers. The uniform prior
over 8281 states is 1.2e-4, which at f=16 is ~8 ulp — 1.1% relative error before
the first update.

| revisions | exact max marginal | abs err f=16 | f=24 | f=32 |
|---|---|---|---|---|
| 0 | 0.0109890 | 1.19e-04 | 5.89e-08 | 4.61e-09 |
| 16 | 0.5054945 | 2.70e-03 | 6.86e-07 | 3.55e-08 |
| 32 | 0.5054945 | 3.68e-03 | 1.64e-05 | 4.18e-08 |

Against a threshold of 0.2 that is a ~2% band where accept/reject is arbitrary.
A policy mechanism that is wrong 2% of the time near the boundary is not a
security mechanism. Claim 2 is the way out.

Also note: probabilistic truncation leaks
([eprint 2024/1127](https://eprint.iacr.org/2024/1127)) and gives no worst-case
bound, so a soundness proof needs deterministic round-to-nearest — which cost
17.7× more multiplications here.

## What's missing

- [ ] Real timings on separate machines. Three runners, or netem, documented honestly.
- [ ] The other two benchmark queries: `similar_w` (w = 0..16) and `richest_p`.
- [ ] Migrate the circuits from `sfix` to integer weights (claim 2).
- [ ] Baselines: plaintext tracking; the belief-*set* method; reveal-then-update-locally.
- [ ] A security argument — ideal functionality, what is revealed, data-independence checklist.
- [ ] Scaling: parties ∈ {3,4,5}, domain ∈ {91, 1e3, 1e4}, revisions 1..50.
- [ ] Verify claims 1 and 2 with someone who knows MPC.

## License

MIT. The PLAS 2012 paper is the intellectual origin of both mechanisms
implemented here; this repository implements and benchmarks their proposal and
claims no credit for the mechanisms themselves.
