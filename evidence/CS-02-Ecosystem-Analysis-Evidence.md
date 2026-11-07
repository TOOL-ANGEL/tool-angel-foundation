# CS-02 Evidence Report

## Component

CS-02 Ecosystem Analysis — version 0.2.0

---

## Verification

- Requirements reviewed ✔ (34 requirements, REQ-ECO-001 … REQ-ECO-084)
- Specification reviewed ✔ (`specs/ecosystem_analysis.spec.yaml` 0.2.0)
- JSON Schema created ✔ (`schemas/ecosystem.schema.json`)
- Python implementation completed ✔
- Unit, golden and property tests created ✔
- Examples created ✔
- CLI command and self-analysis script created ✔

---

## Test results

| Suite | Tests | Result |
| --- | --- | --- |
| Golden results of both case studies | 9 | PASSED |
| Formal properties and data-model rules (Propositions 1, 2, 4, 6; α-independence of reach) | 508 | PASSED |
| Risk, sensitivity and common-cause correction | 8 | PASSED |
| System files, CLI and self-analysis | 7 | PASSED |
| Whole repository | 585 | PASSED |

Static checks on the CS-02 code: ruff and mypy clean.

---

## Reference results reproduced

| Indicator | Online store | PIIT Segovia |
| --- | --- | --- |
| ICE (equal weights) | 0.679 — ecosystem | 0.543 — transition |
| A_sys | 0.99564 (38.2 h/year) | 0.94547 (477.7 h/year) |
| E[R] (α = 0.5) | 9.42 | 6.19 |
| Riskiest provider | Authentication (2.96) | Hosting (2.19) |
| P(ecosystem) under random β | ≈ 0.77 | ≈ 0.29 |

Rank order of the two systems is preserved in 100 % of 10,000 random weightings.

---

## Traceability

Requirements:
- requirements/ecosystem.requirements.yaml

Specification:
- specs/ecosystem_analysis.spec.yaml
- specs/complex_system.spec.yaml (CS-01 1.1.0)

Schema:
- schemas/ecosystem.schema.json

Implementation:
- src/tool_angel/complex_systems/{actor,component,system,value_function,io}.py
- src/tool_angel/complex_systems/analysis/{structure,reliability,propagation,risk,sensitivity,index}.py
- src/tool_angel/builtin_commands/ecosystem.py
- scripts/self_analysis.py

Tests:
- tests/test_ecosystem_golden.py
- tests/test_ecosystem_properties.py
- tests/test_ecosystem_risk.py
- tests/test_ecosystem_io_cli.py

Examples:
- examples/tienda_online.yaml
- examples/piit_segovia.yaml

---

## Findings

- The self-analysis detects a package-level dependency cycle
  `builtin_commands ↔ commands` (`commands/discovery.py` imports the built-in
  commands, which import `commands/command.py`). It predates CS-02 and does not
  break imports, but it should be resolved before `--fail-on-cycles` is enabled
  in CI.

---

## Self-analysis gate

- The self-analysis found one dependency cycle (`commands` <-> `builtin_commands`):
  `commands/discovery.py` imported concrete commands. Discovery moved to
  `builtin_commands/discovery.py`; the internal graph is now acyclic.
- CI runs `scripts/self_analysis.py --fail-on-cycles --strict-instability 0.8`
  as a blocking step, backed by `tests/test_self_analysis.py`.

---

## Limitations

- Case-study inputs are illustrative assumptions, not measurements.
- Ω, τ, ρ_V, K, E[R], the ICE and its thresholds are experimental operators
  pending the empirical validation protocol (phases 1–4 of the model).

---

## Status

Verification: PASSED — empirical validation: PENDING
