# CS-03 Evidence Report

## Component

CS-03 Empirical Validation — version 0.1.0

---

## Verification

- ADR reviewed ✔ (`adr/ADR-0003-Empirical-Validation-Protocol.md`)
- Requirements reviewed ✔ (23 requirements, REQ-VAL-001 … REQ-VAL-060)
- Specification reviewed ✔ (`specs/empirical_validation.spec.yaml` 0.1.0)
- JSON Schema extended ✔ (`measurement` block in `schemas/ecosystem.schema.json`)
- Python implementation completed ✔
- Unit and protocol tests created ✔
- Examples created ✔
- CLI subcommands created ✔ (`ecosystem measure`, `ecosystem validate`)

---

## Test results

| Suite | Tests | Result |
| --- | --- | --- |
| Measurement primitives and system-file rules | 15 | PASSED |
| Phase 1 propagation (reproducibility, purity, evidence monotonicity) | 4 | PASSED |
| Statistics against definitions and textbook values | 9 | PASSED |
| Protocol on pilot, synthetic and noise samples; CLI | 6 | PASSED |
| Whole repository | 619 | PASSED |

Static checks on the touched code: ruff clean.

---

## Results on the bundled data

Measured PIIT example (`examples/piit_segovia_measured.yaml`, illustrative
evidence, 1,000 draws, seed 42):

| Output | Mean | p5 – p95 |
| --- | --- | --- |
| ICE | 0.543 | 0.543 – 0.543 |
| A_sys | 0.94554 | 0.93093 – 0.95804 |
| E[R] | 7.67 | 4.17 – 13.12 |

Finding: with these parameters the ICE does not move, because every external
provider stays above θ = 0.05 in every draw; the uncertainty concentrates in
A_sys and, above all, in E[R] (p95/p5 ≈ 3). The E[R] mean exceeds the
point value 6.16 because λ uses the Jeffreys posterior mean (k + ½)/T. Phase 1 therefore says little about
the ICE and much about the risk ranking.

Pilot sample (`examples/validation/pilot_sample.yaml`): all four phases
INSUFFICIENT (1 measured system; 0 expert judgements; 0 outage records). The
model remains experimental.

Synthetic sample (40 random systems, labels generated from the model plus
noise; mechanics only, not evidence): calibration and prediction PASS; validity
FAILS on Cronbach α ≈ 0.43 although ρ_S(ICE, experts) ≈ 0.88. The five signals
are not internally consistent on random graphs, which is the kind of result
phase 2 exists to expose.

---

## Traceability

Requirements:
- requirements/validation.requirements.yaml

Specification:
- specs/empirical_validation.spec.yaml

Schema:
- schemas/ecosystem.schema.json

Implementation:
- src/tool_angel/complex_systems/measurement.py
- src/tool_angel/complex_systems/io.py
- src/tool_angel/complex_systems/analysis/validation.py
- src/tool_angel/builtin_commands/ecosystem.py

Tests:
- tests/test_validation.py

Examples:
- examples/piit_segovia_measured.yaml
- examples/validation/pilot_sample.yaml

---

## Limitations

- The measured example and the pilot carry no real field data.
- Synthetic samples in the tests verify the mechanics, not the model.
- Weight uncertainty is still analyzed separately (CS-02).

---

## Status

Verification: PASSED — validation of the CS-02 model: NOT STARTED (no real sample)
