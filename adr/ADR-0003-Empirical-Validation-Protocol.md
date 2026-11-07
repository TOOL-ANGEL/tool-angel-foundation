# ADR-0003

## Title

Add the Empirical Validation Protocol (CS-03) to the ecosystem model

---

## Status

Accepted

---

## Context

ADR-0002 introduced the ecosystem analysis engine (CS-02) and marked Ω, τ,
ρ_V, K, E[R], the ICE and its thresholds 0.3 / 0.6 as experimental operators
"until the empirical validation protocol of the model is completed".

The model document ("Modelo Matemático de Sistemas Ecosistémicos", 2026)
lists five limitations (L1–L5) and a four-phase roadmap with explicit
acceptance criteria:

| Phase | Sample | Test | Accept when |
| --- | --- | --- | --- |
| 1. Measurement | 3–5 real systems | Measured parameters; γ by checklist (L1) | ICE p5–p95 width ≤ 0.15 |
| 2. Validity | N ≥ 30 | Cronbach α, Spearman vs experts, signal correlation (L2, L5) | α_C ≥ 0.70; ρ_S ≥ 0.6; no pair with abs(ρ) > 0.9 |
| 3. Calibration | same sample | ROC thresholds, β_cc and α estimated (L2, L3, L4) | Youden J ≥ 0.5 |
| 4. Prediction | 12-month follow-up | E[R] vs observed outage hours | positive and significant correlation (p < 0.05) |

Until now the repository could compute the operators but had no way to
ingest field evidence or to test them against it, so the "experimental"
label could never be lifted by evidence.

---

## Decision

1. Field evidence becomes part of the system file. A component may carry a
   `measurement` block (monitoring hours and outages, or MTBF/MTTR; incident
   history; contractual checklist). The loader derives A, λ and γ from it and
   rejects a parameter that is both given and measured.
   - γ is the mean of a fixed six-item checklist with answers in {0, ½, 1}.
   - The precision of A is limited by the number of outages n, not by the
     number of hours: U = 1 − A ~ Û · Gamma(n, 1/n).
   - λ ~ Gamma(k + ½, 1/T), the Jeffreys posterior of a Poisson rate.
2. The primitives live in `complex_systems/measurement.py` (no analysis
   dependency) and the protocol in `complex_systems/analysis/validation.py`.
   No new top-level directory is created (ADR-0001).
3. Statistics use numpy only. p-values come from a seeded permutation test,
   so every result is reproducible and scipy is not required.
4. A validation sample is a YAML file listing system files plus external
   evidence: expert class, optional expert score and observed outage hours.
5. Each phase reports `pass`, `fail` or `insufficient`. A phase whose sample
   is below the roadmap minimum is `insufficient` even when its statistics
   can be computed: small pilots are informative but cannot validate.
6. The model is reported as validated only when the four phases pass on the
   same sample. Until then CS-02 operators stay experimental.
7. No expert judgement or outage record is invented: the bundled pilot
   sample deliberately leaves them empty and the protocol reports it as
   insufficient.

---

## Consequences

### Benefits

- The experimental label of CS-02 can now be lifted by evidence, not by
  decision, and the evidence is reproducible.
- Measured systems report intervals instead of point values.
- Redundant signals (the H_B ~ τ candidate of L5) are detected automatically.

### Risks

- Phase 1 only propagates parameter uncertainty. With the current ICE the
  structural share s1 changes only when a provider crosses θ, so the ICE
  interval is often narrow while E[R] is wide. Weight uncertainty remains the
  separate CS-02 analysis (`sensitivity.weight_uncertainty`).
- Thresholds of the roadmap (0.15, 30, 0.70, 0.6, 0.9, 0.5, 0.05) are frozen
  as module constants; changing them requires a new ADR.
- Synthetic samples in the tests demonstrate the mechanics only; they are
  not evidence about real systems.
