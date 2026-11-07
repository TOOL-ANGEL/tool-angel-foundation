"""
CS-02 Ecosystem Analysis — sensitivity and uncertainty (Part IV, L3, L4).

- Monte Carlo over ICE weights β ~ Dirichlet(1, …, 1) (OECD-JRC, 2008).
- Leave-one-signal-out and θ sensitivity of the ICE.
- α sensitivity of the expected risk.
- β-factor common-cause correction for redundant groups (IEC 61508).
"""

import math
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

import numpy as np

from tool_angel.complex_systems.analysis import index, risk
from tool_angel.complex_systems.analysis.index import Signals
from tool_angel.complex_systems.system import ComplexSystem


@dataclass(frozen=True, slots=True)
class WeightUncertainty:
    """Distribution of the ICE under random weights."""

    mean: float
    p5: float
    p95: float
    probabilities: dict[str, float]


def weight_samples(samples: int = 10_000, seed: int = 42) -> np.ndarray:
    """Weight vectors drawn uniformly from the 5-simplex."""

    return np.random.default_rng(seed).dirichlet(np.ones(5), samples)


def weight_uncertainty(
    values: Signals,
    weights: np.ndarray | None = None,
    thresholds: tuple[float, float] = index.DEFAULT_THRESHOLDS,
) -> WeightUncertainty:
    """ICE mean, 5th–95th percentile and class probabilities under random β."""

    weights = weight_samples() if weights is None else weights
    scores = weights @ np.asarray(values.as_tuple())
    low, high = thresholds
    return WeightUncertainty(
        mean=float(scores.mean()),
        p5=float(np.percentile(scores, 5)),
        p95=float(np.percentile(scores, 95)),
        probabilities={
            index.CLOSED: float((scores < low).mean()),
            index.TRANSITION: float(((scores >= low) & (scores < high)).mean()),
            index.ECOSYSTEM: float((scores >= high).mean()),
        },
    )


def rank_stability(
    first: Signals,
    second: Signals,
    weights: np.ndarray | None = None,
) -> float:
    """Share of random weightings in which the first system scores higher."""

    weights = weight_samples() if weights is None else weights
    diff = np.asarray(first.as_tuple()) - np.asarray(second.as_tuple())
    return float(((weights @ diff) > 0).mean())


def leave_one_out(values: Signals) -> list[float]:
    """ICE with equal weights after removing each signal in turn."""

    s = values.as_tuple()
    return [sum(s[:k] + s[k + 1 :]) / (len(s) - 1) for k in range(len(s))]


def theta_sensitivity(
    system: ComplexSystem,
    thetas: Iterable[float] = (0.01, 0.03, 0.05, 0.10, 0.20),
) -> dict[float, float]:
    """ICE (equal weights) for each structural-impact threshold θ."""

    return {theta: index.ice(index.signals(system, theta)) for theta in thetas}


def alpha_sensitivity(
    system: ComplexSystem,
    alphas: Iterable[float] = (0.25, 0.50, 0.75),
) -> dict[float, float]:
    """Expected risk E[R] for each Katz factor α."""

    return {alpha: risk.expected_risk(system, alpha) for alpha in alphas}


def common_cause_unavailability(
    unavailabilities: Sequence[float],
    beta: float,
) -> float:
    """
    Q_g = Π (1 − β) Q_j + β · min Q_j  (β-factor model).

    With β = 0 it reduces to the independent product.
    """

    if not 0.0 <= beta <= 1.0:
        raise ValueError("beta must lie in [0, 1]")
    if len(unavailabilities) < 2:
        raise ValueError("a redundant group needs at least two components")
    independent = math.prod((1.0 - beta) * q for q in unavailabilities)
    return independent + beta * min(unavailabilities)


def redundancy_penalty(system: ComplexSystem, beta: float) -> dict[str, float]:
    """
    Unavailability of every redundant group, independent vs common cause.

    Keys are the group's component names joined by " ∥ ".
    """

    components = system.component_map()
    result: dict[str, float] = {}
    for function in system.value_functions:
        for element in function.path:
            if isinstance(element, tuple):
                q = [1.0 - components[c].availability for c in element]
                label = " ∥ ".join(components[c].name for c in element)
                result[label] = common_cause_unavailability(q, beta) / math.prod(q)
    return result


__all__ = [
    "WeightUncertainty",
    "alpha_sensitivity",
    "common_cause_unavailability",
    "leave_one_out",
    "rank_stability",
    "redundancy_penalty",
    "theta_sensitivity",
    "weight_samples",
    "weight_uncertainty",
]
