"""
CS-02 Ecosystem Analysis — Ecosystem Behavior Index (Definition 4).

The five signals of the base text are normalized to [0, 1] and aggregated as
ICE = β·s. The index and its thresholds are experimental operators: they must
not be presented as a standard before empirical validation (ADR-0002).
"""

from collections.abc import Sequence
from dataclasses import astuple, dataclass, field
from uuid import UUID

from tool_angel.complex_systems.analysis import (
    propagation,
    reliability,
    risk,
    structure,
)
from tool_angel.complex_systems.indicator import Indicator
from tool_angel.complex_systems.system import ComplexSystem

DEFAULT_THRESHOLDS = (0.3, 0.6)

CLOSED = "closed"
TRANSITION = "transition"
ECOSYSTEM = "ecosystem"


@dataclass(frozen=True, slots=True)
class Signals:
    """The five normalized signals s1..s5 of the ICE."""

    structural_share: float
    ownership_entropy: float
    mean_reach: float
    relational_value: float
    coordination_cost: float

    def as_tuple(self) -> tuple[float, ...]:
        return astuple(self)


def signals(
    system: ComplexSystem,
    theta: float = reliability.DEFAULT_THETA,
) -> Signals:
    """Compute s1..s5. Validates the system first."""

    system.validate()
    external = system.external_components()
    structural = reliability.structural_dependencies(system, theta)
    n = len(system.components)
    reach = propagation.reach(system)
    return Signals(
        structural_share=len(structural) / len(external) if external else 0.0,
        ownership_entropy=structure.ownership_entropy(system),
        mean_reach=(sum(reach.values()) / (n * (n - 1))) if n > 1 else 0.0,
        relational_value=structure.relational_value(system),
        coordination_cost=structure.coordination_cost(system),
    )


def ice(values: Signals, weights: Sequence[float] | None = None) -> float:
    """
    ICE = β·s with β ≥ 0 and Σβ = 1. Uniform weights by default.
    """

    s = values.as_tuple()
    if weights is None:
        return sum(s) / len(s)
    if len(weights) != len(s):
        raise ValueError(f"expected {len(s)} weights, got {len(weights)}")
    if any(w < 0 for w in weights) or abs(sum(weights) - 1.0) > 1e-9:
        raise ValueError("weights must be non-negative and sum to 1")
    return sum(w * x for w, x in zip(weights, s))


def classify(value: float, thresholds: tuple[float, float] = DEFAULT_THRESHOLDS) -> str:
    """Classify an ICE value as closed, transition or ecosystem."""

    low, high = thresholds
    if value < low:
        return CLOSED
    if value < high:
        return TRANSITION
    return ECOSYSTEM


@dataclass(frozen=True, slots=True)
class EcosystemReport:
    """Every operator of the model for one system."""

    system_name: str
    openness: float
    coordination_cost: float
    ownership_entropy: float
    relational_value: float
    effective_control: float
    system_availability: float
    structural_impact: dict[UUID, float]
    structural_dependencies: list[UUID]
    composite: bool
    katz_impact: dict[UUID, float]
    reach: dict[UUID, int]
    acyclic: bool
    signals: Signals
    ice: float
    classification: str
    expected_risk: float
    provider_risks: list[risk.ProviderRisk]
    parameters: dict[str, object] = field(default_factory=dict)

    @property
    def downtime_hours_per_year(self) -> float:
        """Weighted unavailability expressed in hours per year."""

        return (1.0 - self.system_availability) * 8760.0

    def indicators(self) -> list[Indicator]:
        """Express the report as CS-01 Indicator objects."""

        rows = [
            ("Ω openness", self.openness, "ratio", "experimental"),
            ("τ coordination cost", self.coordination_cost, "ratio", "experimental"),
            ("H_B ownership entropy", self.ownership_entropy, "ratio", "established"),
            ("ρ_V relational value", self.relational_value, "ratio", "experimental"),
            ("K effective control", self.effective_control, "ratio", "experimental"),
            (
                "A_sys system availability",
                self.system_availability,
                "ratio",
                "established",
            ),
            ("Downtime", self.downtime_hours_per_year, "h/year", "established"),
            ("E[R] expected risk", self.expected_risk, "events/year", "experimental"),
            ("ICE", self.ice, "index", "experimental"),
        ]
        return [
            Indicator.create(
                name=name,
                value=value,
                unit=unit,
                metadata={
                    "component": "CS-02",
                    "status": status,
                    "system": self.system_name,
                },
            )
            for name, value, unit, status in rows
        ]


def analyze(
    system: ComplexSystem,
    *,
    theta: float = reliability.DEFAULT_THETA,
    alpha: float = propagation.DEFAULT_ALPHA,
    weights: Sequence[float] | None = None,
    thresholds: tuple[float, float] = DEFAULT_THRESHOLDS,
) -> EcosystemReport:
    """
    Validate the system and compute every operator of the model.

    The system is never mutated. It needs at least one value function.
    """

    system.validate()
    if not system.value_functions:
        raise ValueError("ecosystem analysis needs at least one value function")
    values = signals(system, theta)
    score = ice(values, weights)
    return EcosystemReport(
        system_name=system.name,
        openness=structure.openness(system),
        coordination_cost=structure.coordination_cost(system),
        ownership_entropy=structure.ownership_entropy(system),
        relational_value=structure.relational_value(system),
        effective_control=structure.effective_control(system),
        system_availability=reliability.system_availability(system),
        structural_impact=reliability.structural_impact(system),
        structural_dependencies=reliability.structural_dependencies(system, theta),
        composite=reliability.is_composite(system, theta),
        katz_impact=propagation.katz_impact(system, alpha),
        reach=propagation.reach(system),
        acyclic=not propagation.has_cycles(system),
        signals=values,
        ice=score,
        classification=classify(score, thresholds),
        expected_risk=risk.expected_risk(system, alpha),
        provider_risks=risk.provider_risks(system, alpha),
        parameters={
            "theta": theta,
            "alpha": alpha,
            "weights": weights,
            "thresholds": thresholds,
        },
    )
