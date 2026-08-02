# Review log

Every external critique gets an entry, whether it survived or not. Entries are
append-only — do not delete a refuted objection, mark it resolved and say why.

Two reasons this file exists. First, so we do not relitigate the same objection
three times. Second, because a paper that can show what was challenged and how
it was answered is a stronger paper, and reviewers notice.

Status values: `open` · `resolved` · `fatal` · `deferred`

---

## Template

```
### R-NN — <one-line summary>

- **Date:**
- **Source:** (name / model / venue — be specific, "an LLM" is not a source)
- **Targets:** claim 1 / claim 2 / claim 3 / measurement / other
- **Objection:** what they actually said, in their words where possible
- **Assessment:** our evaluation — does it land?
- **Resolution:** what changed as a result. "Nothing" is a valid answer if justified.
- **Status:**
```

---

## Open questions nobody has answered yet

These are seeded from our own uncertainty, not from external review. They stay
open until someone with actual MPC expertise addresses them.

### R-01 — Is claim 1 already folklore?

- **Date:** seeded at repo creation
- **Source:** self (Claude, during initial scoping)
- **Targets:** claim 1
- **Objection:** The observation that public-constant × secret-share is local,
  and therefore that indicator conditioning on an enumerated public hypothesis
  space is free, may be common knowledge among MPC practitioners. If so the
  claim is true but contributes nothing.
- **Assessment:** Unresolved and important. An initial literature search did not
  find it stated, but that search could not reach Google Scholar or Semantic
  Scholar, so absence of evidence is weak here.
- **Resolution:** pending. Ask on the MP-SPDZ issue tracker or at TPMPC before
  writing anything up.
- **Status:** `open`

### R-02 — Loopback timings are not network timings

- **Date:** seeded at repo creation
- **Source:** self
- **Targets:** measurement
- **Objection:** All reported timings ran with three parties on one 2-core host
  over loopback. Round count × RTT is entirely hidden. At 50 ms WAN RTT, 88
  rounds adds ~4.4 s — two orders of magnitude above the reported 22.6 ms.
- **Assessment:** Lands completely. The numbers are honest about what they
  measure and useless as performance claims.
- **Resolution:** CI matrix with `tc netem` added (localhost / LAN / WAN). Still
  emulation on one host; a paper must say so explicitly.
- **Status:** `open` until real multi-machine numbers exist

### R-03 — The security argument has never been checked

- **Date:** seeded at repo creation
- **Source:** self
- **Targets:** other
- **Objection:** The claim "the rejection decision leaks nothing" is a security
  claim written by people with no MPC background. Its failure modes are silent:
  a leaky truncation, a loop bound that depends on a revealed value, a circuit
  whose shape depends on a secret.
- **Assessment:** Lands. No part of this has been reviewed.
- **Resolution:** pending. Needs an ideal-functionality statement, an explicit
  list of what is revealed, and a data-independence checklist — then a human
  who knows MPC.
- **Status:** `open`

### R-04 — Probabilistic truncation leaks and gives no worst-case bound

- **Date:** seeded at repo creation
- **Source:** MP-SPDZ compiler warning, citing eprint 2024/1127
- **Targets:** measurement
- **Objection:** MP-SPDZ's default probabilistic truncation is unbiased but not
  bounded, so no certified error bound `eps` can be derived — and the compiler
  itself warns that it leaks.
- **Assessment:** Lands. Any soundness argument needs deterministic
  round-to-nearest, measured at 17.7× more multiplications.
- **Resolution:** Claim 2 (exact integer conditioning) sidesteps this entirely
  for deterministic queries. Not yet implemented in the circuits.
- **Status:** `open`
