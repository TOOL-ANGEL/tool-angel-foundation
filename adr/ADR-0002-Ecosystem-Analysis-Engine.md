# ADR-0002

## Title

Add the Ecosystem Analysis Engine to Complex Systems

---

## Status

Accepted (merged in PR #1; extended by CS-02 0.2.0)

---

## Context

CS-01 ComplexSystem represents components, relationships, states and indicators,
but it cannot measure them. Its specification lists *dependency graphs*,
*resilience analysis* and *temporal evolution* as future extensions.

The mathematical model of ecosystemic systems (document "Modelo Matemático de
Sistemas Ecosistémicos", 2026) defines a system as

    S = (V, E, w, A, ω, F, Θ)

and derives from it a set of measurable operators (openness Ω, coordination
cost τ, ownership entropy H_B, relational value ρ_V, effective control K,
availability A_sys, structural impact Δ_e, change propagation) aggregated into
the Ecosystem Behavior Index (ICE).

The engine needs data that CS-01 does not model today: component scope
(internal or external), owner actor, availability, contractual control,
failure rate, and value functions with their critical paths.

ADR-0001 froze the repository structure. This decision must therefore fit
inside the existing architecture.

---

## Decision

1. The engine lives in `src/tool_angel/complex_systems/analysis/` as pure
   functions that read a `ComplexSystem` and never mutate it.
2. `Component` gains typed, validated fields with backward-compatible defaults:
   `scope`, `owner_id`, `availability`, `control`, `failure_rate`.
3. Two models are added to `complex_systems`: `Actor` (the set A) and
   `ValueFunction` (the set F, with weights φ and critical paths).
4. `ComplexSystem` enforces the type constraints already written in
   `specs/complex_system.spec.yaml`, and gains `validate()` to check the
   dependency graph before analysis.
5. Operators taken from the literature (reliability block diagrams, Katz
   centrality, Shannon entropy) are marked `established`. Operators of own
   elaboration (Ω, ρ_V, K, ICE and its thresholds) are marked `experimental`
   until the empirical validation protocol of the model is completed.
6. Reference results of the model's two case studies are frozen as golden
   tests. Any change that alters them must be justified in a new ADR.

No new top-level directory is created.

---

## Consequences

### Benefits

- CS-01 moves from a structural container to a measurable model.
- Every operator is traceable from requirement to test.
- Golden tests protect the published results.

### Risks

- `ComplexSystem.add_component` now rejects objects that are not `Component`
  instances. Two existing tests that passed dictionaries or `Entity` objects
  were updated accordingly.
- Experimental operators must not be presented as a standard before validation.
