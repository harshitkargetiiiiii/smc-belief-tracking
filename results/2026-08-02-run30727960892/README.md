# CI run 30727960892 — 2026-08-02

First cross-network measurement. GitHub Actions, `tc netem` on loopback,
3-party semi-honest replicated, `belief3` at domain 91, f=16, secrets (63,40,55).

| condition | RTT | MP-SPDZ time | data/party | rounds |
|---|---|---|---|---|
| localhost | 0 | 0.0148 s | 0.402 MB | ~80 |
| LAN | 0.2 ms | 0.0386 s | 0.402 MB | ~80 |
| WAN | 50 ms | **4.1997 s** | 0.402 MB | ~80 |

80 rounds x 50 ms = 4.0 s. The WAN figure is 4.20 s, and MP-SPDZ reports
communication as >95% of total time. Round count dominates on WAN, exactly as
predicted, and the prediction is now measured rather than arithmetic.

## What this does and does not establish

**Does:** the measurement harness works end to end — build, cache, netem,
3-party run, artifact capture. Round-minimisation is confirmed as the
highest-leverage optimisation for any WAN deployment.

**Does not:** validate anything scientific. `belief3` is not the PLAS ideal
functionality — it reveals the accept/reject verdict publicly, tracks one
observer/target pair, and carries no state between invocations. See
`../../docs/gap.md`. These are timings for a computation that is not the
mechanism.

Also: GitHub runners are shared and noisy. Treat absolute wall-clock as
indicative; round counts and data volumes are reliable.

---

**Superseded by the round-2 review.** These numbers establish only that adding
~50 ms of delay to an ~80-round program adds ~4 s. They validate the harness.
They do not validate the mechanism and are not a publishable result. No further
performance runs until `docs/conformance.md` passes.
