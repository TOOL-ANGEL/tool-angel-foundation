"""
CS-02 Ecosystem Analysis — structural operators (Definition 2).

Openness Ω, coordination cost τ, ownership entropy H_B, relational value ρ_V,
criticality π_v and effective control K.

Ownership convention: a component with ``owner_id`` set belongs to that actor.
An internal component without owner belongs to one implicit internal owner.
An external component without owner is treated as its own actor.
"""

import math
from collections import Counter
from collections.abc import Hashable
from uuid import UUID

from tool_angel.complex_systems.component import Component
from tool_angel.complex_systems.system import ComplexSystem

_INTERNAL_OWNER = "internal-owner"


def owner_key(component: Component) -> Hashable:
    """Return the actor that decides over the component (ω)."""

    if component.owner_id is not None:
        return component.owner_id
    if component.is_external:
        return component.id
    return _INTERNAL_OWNER


def actor_count(system: ComplexSystem) -> int:
    """Number m of distinct actors owning at least one component."""

    return len({owner_key(component) for component in system.components})


def _weight_share(system: ComplexSystem, *, cross_owner: bool) -> float:
    components = system.component_map()
    total = 0.0
    selected = 0.0
    for relationship in system.dependencies():
        source = components[relationship.source_id]
        target = components[relationship.target_id]
        total += relationship.weight
        if cross_owner:
            hit = owner_key(source) != owner_key(target)
        else:
            hit = source.is_external or target.is_external
        if hit:
            selected += relationship.weight
    return selected / total if total > 0 else 0.0


def openness(system: ComplexSystem) -> float:
    """
    Ω: weight share of dependencies touching at least one external component.
    """

    return _weight_share(system, cross_owner=False)


def coordination_cost(system: ComplexSystem) -> float:
    """
    τ: weight share of dependencies whose endpoints have different owners.
    """

    return _weight_share(system, cross_owner=True)


def ownership_entropy(system: ComplexSystem) -> float:
    """
    H_B: Shannon entropy of component ownership normalized by ln m.

    Returns 0 when there is a single actor (a sharp boundary).
    """

    counts = Counter(owner_key(component) for component in system.components)
    m = len(counts)
    if m <= 1:
        return 0.0
    n = sum(counts.values())
    entropy = -sum((c / n) * math.log(c / n) for c in counts.values())
    return entropy / math.log(m)


def criticality(system: ComplexSystem) -> dict[UUID, float]:
    """
    π_v: sum of φ over the value functions whose critical path contains v.

    Without value functions every component weighs 1.
    """

    if not system.value_functions:
        return {component.id: 1.0 for component in system.components}
    result = {component.id: 0.0 for component in system.components}
    for function in system.value_functions:
        for member in function.members():
            result[member] += function.weight
    return result


def effective_control(system: ComplexSystem) -> float:
    """
    K: criticality-weighted mean of the contractual control γ.
    """

    weights = criticality(system)
    total = sum(weights.values())
    if total == 0:
        return 1.0
    return (
        sum(
            component.control * weights[component.id] for component in system.components
        )
        / total
    )


def relational_value(system: ComplexSystem) -> float:
    """
    ρ_V: φ-weighted share of each critical path supplied by external components.
    """

    external = {component.id for component in system.external_components()}
    value = 0.0
    for function in system.value_functions:
        members = function.members()
        value += function.weight * len(members & external) / len(members)
    return value
