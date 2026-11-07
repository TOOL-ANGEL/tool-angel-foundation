# tool-angel-foundation
Foundation repository for TOOL-ANGEL (AngelOS): architecture, kernel, SDK and specifications.

## Ecosystem analysis (CS-02)

Measures how far a system has moved from a closed solution to an ecosystem,
following the mathematical model of ecosystemic systems (ADR-0002).

```bash
pip install numpy pyyaml pytest
PYTHONPATH=src python -m tool_angel.cli ecosystem analyze examples/piit_segovia.yaml
python scripts/self_analysis.py        # the model applied to this repository
python -m pytest -q
```

System files follow `schemas/ecosystem.schema.json`; see `examples/`.
Ω, τ, ρ_V, K, E[R] and the ICE are experimental operators until empirically validated.

## Empirical validation (CS-03)

Turns field evidence into model parameters and tests the CS-02 operators
against it, following the four-phase roadmap of the model (ADR-0003).

```bash
# Phase 1: measured parameters → ICE, A_sys and E[R] as p5–p95 intervals
PYTHONPATH=src python -m tool_angel.cli ecosystem measure examples/piit_segovia_measured.yaml

# Phases 1–4 on a sample of systems with expert judgements and outage records
PYTHONPATH=src python -m tool_angel.cli ecosystem validate examples/validation/pilot_sample.yaml
```

A component's `measurement` block (monitoring hours and outages, incident
history, contractual checklist) replaces hand-set A, λ and γ. The bundled
pilot carries no expert or outage data yet, so every phase is reported as
INSUFFICIENT and the model stays experimental until a real sample of N ≥ 30
systems passes all four phases.
