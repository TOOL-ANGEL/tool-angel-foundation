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
