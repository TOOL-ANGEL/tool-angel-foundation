"""
AngelOS Complex Systems — measured parameters (CS-03, phase 1, limitation L1).

The case-study parameters of CS-02 are illustrative. This module turns field
evidence into the parameters Θ = (A, γ, λ) of each component, and keeps the
evidence as a probability distribution so that its uncertainty can be
propagated to the ICE:

- Availability from monitoring logs: A = MTBF / (MTBF + MTTR), or from
  observed up and down hours and the number n of outages. The precision of
  the unavailability U = 1 − A is limited by n (a Poisson count), not by the
  number of hours: U ~ Û · Gamma(n, 1/n), mean Û, relative error 1/√n.
  With n = 0 no downtime was observed and U = 0 is kept as a point value.
- Failure rate from the incident history: λ = incidents / years.
  Uncertainty: λ ~ Gamma(incidents + ½, scale = 1 / years), the Jeffreys
  posterior of a Poisson rate.
- Contractual control from a fixed checklist, γ = mean of c_q with
  c_q ∈ {0, ½, 1}, so that γ stops being a free judgement.

This module depends on nothing but the standard library and numpy.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import numpy as np

CONTROL_CHECKLIST: tuple[str, ...] = (
    "sla_penalty",  # SLA with penalty clauses
    "change_notice",  # advance notice of version or interface changes
    "audit_right",  # right to audit the provider
    "data_portability",  # data export and exit clause
    "support_times",  # support with agreed response times
    "substitution",  # contractual alternative or substitute provider
)

CHECKLIST_SCORES: frozenset[float] = frozenset({0.0, 0.5, 1.0})

HOURS_PER_YEAR = 8760.0


def availability_from_mtbf(mtbf: float, mttr: float) -> float:
    """A = MTBF / (MTBF + MTTR)."""

    if mtbf <= 0 or mttr < 0:
        raise ValueError("mtbf must be > 0 and mttr >= 0")
    return mtbf / (mtbf + mttr)


def control_score(answers: Mapping[str, float]) -> float:
    """
    γ = (1/|Q|) Σ c_q over the fixed checklist Q, with c_q ∈ {0, ½, 1}.

    Every item of CONTROL_CHECKLIST must be answered; unknown items are
    rejected so that two scorings are always comparable.
    """

    unknown = set(answers) - set(CONTROL_CHECKLIST)
    if unknown:
        raise ValueError(f"unknown checklist items: {sorted(unknown)}")
    missing = [q for q in CONTROL_CHECKLIST if q not in answers]
    if missing:
        raise ValueError(f"missing checklist items: {missing}")
    scores = [float(answers[q]) for q in CONTROL_CHECKLIST]
    if any(s not in CHECKLIST_SCORES for s in scores):
        raise ValueError("checklist answers must be 0, 0.5 or 1")
    return sum(scores) / len(scores)


@dataclass(frozen=True, slots=True)
class Measurement:
    """
    Field evidence for one component.

    up_hours, down_hours: observed operating and outage time.
    outages:              number of outage events in that window.
    incidents, years:     failures or incompatible changes in the window.
    checklist:            contractual control answers (external components).
    """

    up_hours: float | None = None
    down_hours: float | None = None
    outages: int | None = None
    incidents: int | None = None
    years: float | None = None
    checklist: Mapping[str, float] | None = None

    def __post_init__(self) -> None:
        if (self.up_hours is None) != (self.down_hours is None):
            raise ValueError("up_hours and down_hours go together")
        if self.up_hours is not None and (
            self.up_hours < 0 or self.down_hours < 0  # type: ignore[operator]
        ):
            raise ValueError("observed hours must be >= 0")
        if self.up_hours is not None and self.up_hours + self.down_hours <= 0:  # type: ignore[operator]
            raise ValueError("the observation window must be > 0 hours")
        if (self.up_hours is None) != (self.outages is None):
            raise ValueError("monitoring needs up_hours, down_hours and outages")
        if self.outages is not None:
            if self.outages < 0:
                raise ValueError("outages must be >= 0")
            if (self.outages == 0) != (self.down_hours == 0):
                raise ValueError("down_hours > 0 requires outages > 0 and vice versa")
        if (self.incidents is None) != (self.years is None):
            raise ValueError("incidents and years go together")
        if self.incidents is not None and (self.incidents < 0 or self.years <= 0):  # type: ignore[operator]
            raise ValueError("incidents must be >= 0 and years > 0")
        if self.checklist is not None:
            control_score(self.checklist)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Measurement":
        """Build from a system-file ``measurement`` block."""

        allowed = {"monitoring", "mtbf", "incidents", "checklist"}
        unknown = set(data) - allowed
        if unknown:
            raise ValueError(f"unknown measurement keys: {sorted(unknown)}")

        up = down = None
        outages = None
        if "monitoring" in data and "mtbf" in data:
            raise ValueError("give either monitoring or mtbf, not both")
        if "monitoring" in data:
            block = data["monitoring"]
            up = float(block["up_hours"])
            down = float(block["down_hours"])
            outages = int(block["outages"])
        elif "mtbf" in data:
            block = data["mtbf"]
            # n outages, each one MTBF of operation followed by MTTR of repair.
            outages = int(block["outages"])
            up = float(block["mtbf"]) * outages
            down = float(block["mttr"]) * outages

        incidents = years = None
        if "incidents" in data:
            incidents = int(data["incidents"]["count"])
            years = float(data["incidents"].get("years", 1.0))

        checklist = data.get("checklist")
        return cls(
            up_hours=up,
            down_hours=down,
            outages=outages,
            incidents=incidents,
            years=years,
            checklist=dict(checklist) if checklist is not None else None,
        )

    # Point estimates -------------------------------------------------------

    @property
    def availability(self) -> float | None:
        if self.up_hours is None:
            return None
        return self.up_hours / (self.up_hours + self.down_hours)  # type: ignore[operator]

    @property
    def failure_rate(self) -> float | None:
        if self.incidents is None:
            return None
        return self.incidents / self.years  # type: ignore[operator]

    @property
    def control(self) -> float | None:
        if self.checklist is None:
            return None
        return control_score(self.checklist)

    # Distributions ---------------------------------------------------------

    def sample_availability(
        self, rng: np.random.Generator, size: int
    ) -> np.ndarray | None:
        """A = 1 − U with U ~ Û · Gamma(n, 1/n), clipped to [0, 1]."""

        if self.up_hours is None:
            return None
        point = self.availability
        if self.outages == 0:
            return np.full(size, point)
        n = float(self.outages)  # type: ignore[arg-type]
        unavailability = (1.0 - point) * rng.gamma(n, 1.0 / n, size)  # type: ignore[operator]
        return np.clip(1.0 - unavailability, 0.0, 1.0)

    def sample_failure_rate(
        self, rng: np.random.Generator, size: int
    ) -> np.ndarray | None:
        """λ ~ Gamma(incidents + ½, scale = 1 / years)."""

        if self.incidents is None:
            return None
        return rng.gamma(self.incidents + 0.5, 1.0 / self.years, size)  # type: ignore[operator]


__all__ = [
    "CHECKLIST_SCORES",
    "CONTROL_CHECKLIST",
    "HOURS_PER_YEAR",
    "Measurement",
    "availability_from_mtbf",
    "control_score",
]
