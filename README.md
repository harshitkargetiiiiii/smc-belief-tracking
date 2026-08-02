# smc-belief-tracking

**A refuted prototype and a benchmark harness. Not an implementation of SMC
belief tracking.** Paper work is stopped. See "Status" below before reading
anything else.

Context: Mardziel, Hicks, Katz & Srivatsa, *Knowledge-Oriented Secure Multiparty
Computation*, PLAS 2012 (https://www.cs.umd.edu/~mwh/papers/belief-smc.pdf)
proposed two mechanisms for enforcing knowledge-threshold policies in MPC,
implemented one (belief sets), and simulated the other (SMC belief tracking)
without implementing it. This repository was an attempt at the second. It does
not realize it.

## Status: stopped

Two rounds of external adversarial review ([issue #1](https://github.com/harshitkargetiiiiii/smc-belief-tracking/issues/1)):

**Round 1 refuted all three claims the project rested on.**

- *Conditioning is free* — false. The secret belief weight must be multiplied by
  the secret indicator. This circuit does it 41,098 times. The true part —
  public-constant x share is local — is textbook (Cramer, Damgard & Maurer,
  EUROCRYPT 2000).
- *Indicator conditioning is exact in integers* — an unbounded-arithmetic lemma.
  Not implemented in MPC, assumes a uniform prior, no ring-overflow bound, and
  the p=1/2 bit-growth estimate was wrong.
- *The recursion objection does not apply* — misreads PLAS, which states Q is
  public (SS4.3, SS4.6) before raising the interpreter objection (SS5).

**Round 2 stopped the paper.** "Nobody appears to have implemented it" is an
engineering gap, not a research contribution. Implementing and timing a 2012
construction is not a paper absent a new protocol, theorem, compiler, security
result, or empirically supported systems insight. This project has none.

This is **not** a finding that the true cost is prohibitive. There is no
faithful implementation from which to draw that conclusion. It is a finding that
measuring the cost no longer answers a novel research question.

**Reopening gate:** an independent literature review producing a specific, new,
falsifiable contribution, stated *before* further implementation work.
"First implementation" does not satisfy the gate.

## What is here

```
mpc/         MP-SPDZ circuits. NON-CONFORMING - see docs/gap.md. Do not extend.
reference/   Exact-rational plaintext model. Implements our model, not PLAS.
results/     Raw CI outputs. Timings for a computation that is not the mechanism.
docs/
  claims.md       what we claimed and why each was wrong
  gap.md          what the circuits are missing
  conformance.md  the target any future attempt must hit first
  review-log.md   every critique, logged, append-only
  workflow.md     how the three-way review loop runs
scripts/     Build helpers.
```

## Do not cite the timings

`results/` contains real, reproducible measurements of `belief3` across
localhost/LAN/WAN. They are retained because the harness works. They measure a
circuit that publicly reveals the accept/reject verdict — which PLAS SS4.4
explicitly forbids — tracks one observer/target pair, and carries no state
between invocations. They are timings for the wrong computation.

## If work resumes

Not with CI, and not with benchmarks. `docs/conformance.md` defines the gate:
an executable conformance target checked against an independently written
plaintext oracle on a tiny fixture including a rejection. Performance work only
after that passes.

## License

MIT. The mechanisms are due to Mardziel, Hicks, Katz & Srivatsa (PLAS 2012);
this repository claims no credit for them and does not implement them.
