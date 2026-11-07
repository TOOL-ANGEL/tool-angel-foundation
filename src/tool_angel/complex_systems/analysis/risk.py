"""
CS-02 Ecosystem Analysis — expected ecosystem risk (Definition 3).

E[R] = Σ_e λ_e · Δ_e · (1 − γ_e) · (1 + 𝓘_e)

Risk grows with the provider's yearly rate of failures or incompatible changes
(λ), its structural impact (Δ), the lack of contractual control (1 − γ) and the
reach of its changes (Katz impact 𝓘). The absolute value depends on α; the
ranking of providers is the decision-relevant output (limitation L4).
"""

from dataclasses import dataclass
from uuid import UUID

from tool_angel.complex_systems.analysis import propagation, reliability
from tool_angel.complex_systems.system import ComplexSystem


@dataclass(frozen=True, slots=True)
class ProviderRisk:
    """Risk contribution of one external component."""

    component_id: UUID
    name: str
    failure_rate: float
    structural_impact: float
    control: float
    katz_impact: float
    risk: float


def provider_risks(
    system: ComplexSystem,
    alpha: float = propagation.DEFAULT_ALPHA,
) -> list[ProviderRisk]:
    """
    Risk of every external component, highest first.
    """

    impact = reliability.structural_impact(system)
    katz = propagation.katz_impact(system, alpha)
    rows = [
        ProviderRisk(
            component_id=component.id,
            name=component.name,
            failure_rate=component.failure_rate,
            structural_impact=impact[component.id],
            control=component.control,
            katz_impact=katz[component.id],
            risk=component.failure_rate
            * impact[component.id]
            * (1.0 - component.control)
            * (1.0 + katz[component.id]),
        )
        for component in system.external_components()
    ]
    return sorted(rows, key=lambda row: row.risk, reverse=True)


def expected_risk(
    system: ComplexSystem,
    alpha: float = propagation.DEFAULT_ALPHA,
) -> float:
    """E[R]: total expected ecosystem risk per year."""

    return sum(row.risk for row in provider_risks(system, alpha))
