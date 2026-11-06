"""
CS-02 Ecosystem Analysis — reliability operators (Definition 3).

Function availability A_f, system availability A_sys, structural impact Δ_e
and the composite-architecture criterion. Failures are assumed independent
(see limitation L3 of the model).
"""

import math
from collections.abc import Mapping
from uuid import UUID

from tool_angel.complex_systems.analysis.structure import actor_count
from tool_angel.complex_systems.system import ComplexSystem
from tool_angel.complex_systems.value_function import ValueFunction

DEFAULT_THETA = 0.05


def function_availability(
    function: ValueFunction, availability: Mapping[UUID, float]
) -> float:
    """
    A_f: product over serial components and, for each redundant group g,
    the factor 1 − Π_{j∈g}(1 − A_j).
    """

    result = 1.0
    for element in function.path:
        if isinstance(element, tuple):
            result *= 1.0 - math.prod(1.0 - availability[item] for item in element)
        else:
            result *= availability[element]
    return result


def system_availability(
    system: ComplexSystem,
    overrides: Mapping[UUID, float] | None = None,
) -> float:
    """
    A_sys = Σ φ_f A_f. ``overrides`` replaces the availability of some components.
    """

    availability = {
        component.id: component.availability for component in system.components
    }
    if overrides:
        availability.update(overrides)
    return sum(
        function.weight * function_availability(function, availability)
        for function in system.value_functions
    )


def structural_impact(system: ComplexSystem) -> dict[UUID, float]:
    """
    Δ_e = A_sys − A_sys|_{A_e = 0} for every external component e.
    """

    baseline = system_availability(system)
    return {
        component.id: baseline - system_availability(system, {component.id: 0.0})
        for component in system.external_components()
    }


def structural_dependencies(
    system: ComplexSystem, theta: float = DEFAULT_THETA
) -> list[UUID]:
    """External components whose structural impact exceeds θ."""

    return [cid for cid, impact in structural_impact(system).items() if impact > theta]


def is_composite(system: ComplexSystem, theta: float = DEFAULT_THETA) -> bool:
    """
    Composite architecture: at least two structural dependencies and two actors.
    """

    return len(structural_dependencies(system, theta)) >= 2 and actor_count(system) >= 2
