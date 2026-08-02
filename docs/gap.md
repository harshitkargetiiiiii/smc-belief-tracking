# What the circuits are missing

From the 2026-08-02 review (issue #1, §4). Independent of the three refuted
claims, the programs in `mpc/` do not realise the ideal functionality in PLAS
2012 Figures 8-9.

## Security-breaking

- **The verdict is revealed publicly.** `belief3.mpc:57` calls `reveal()` on the
  accept/reject bit. PLAS explicitly requires that whether `P_j` receives output
  or a rejection must NOT be observable by other participants, and gives a
  concrete threshold-violation example for when it is. This is not a missing
  feature — it breaks the property the mechanism exists to provide.
- **No selective output.** `o` and `reject` are never privately released to the
  intended recipient.

## Functionally absent

- Tracks one observer's belief against one target marginal. PLAS requires every
  `j` and every `i != j`.
- Returns no new secret shares of `Sigma_T`; no protocol state persists between
  invocations.
- Does not leave the prior unchanged on rejection.
- No per-round accept/reject decision — `belief4.mpc` updates unconditionally.

## Outright bug

`belief4.mpc` builds `q` once, before the loop, from the `Q_0` comparison
vector, then changes the query inside the loop via `x2 + r` / `x3 + r`. Rounds
`r > 0` condition on the output of `Q_r` using the hypothesis table for `Q_0`.
The reported "20 rounds = 1.61 s" measures an incoherent computation.

## Reproducibility

- No raw outputs committed; the README tables are unsupported by anything in the
  repo.
- MP-SPDZ is cloned from unpinned `main` in both `scripts/setup.sh` and CI. The
  cache key claims `v0.4.3` but no tag is checked out.
- The workflow's `rounds` input is unused; only `belief3` is compiled.
- Compiler statistics are not preserved in the uploaded artifact.
- **No MPC result is ever compared against the reference oracle.** This is the
  single highest-value fix: it is the only thing that would make CI meaningful.

## Consequence

22.6 ms is a timing for a partial, security-incompatible subcomputation. A
correct implementation must carry secret belief state across rounds, which
forces the secret × secret multiplication of Claim 1 on every update, for every
observer/target pair — so the real cost is strictly higher, and the interesting
question is by how much.

That question is still open and we have not answered it.
