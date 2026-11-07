"""
CS-02 Ecosystem Analysis — change propagation (Definition 3, Proposition 5).

D_ij = 1 when component i depends on component j. A change in j reaches every
i that has a dependency path towards j.
"""

from uuid import UUID

import numpy as np

from tool_angel.complex_systems.system import ComplexSystem

DEFAULT_ALPHA = 0.5


def dependency_matrix(system: ComplexSystem) -> tuple[np.ndarray, list[UUID]]:
    """Return the binary dependency matrix D and the component order."""

    order = system.component_ids()
    index = {cid: k for k, cid in enumerate(order)}
    matrix = np.zeros((len(order), len(order)))
    for relationship in system.dependencies():
        matrix[index[relationship.source_id], index[relationship.target_id]] = 1.0
    return matrix, order


def _dependents(system: ComplexSystem) -> dict[UUID, set[UUID]]:
    result: dict[UUID, set[UUID]] = {cid: set() for cid in system.component_ids()}
    for relationship in system.dependencies():
        result[relationship.target_id].add(relationship.source_id)
    return result


def reach(system: ComplexSystem) -> dict[UUID, int]:
    """
    Number of components i ≠ j that a change in j can reach.

    Equivalent to counting R_ij > 0 for R = (I − αD)^−1 − I, and therefore
    independent of α (requirement REQ-ECO-030).
    """

    dependents = _dependents(system)
    result: dict[UUID, int] = {}
    for start in dependents:
        seen: set[UUID] = set()
        stack = list(dependents[start])
        while stack:
            node = stack.pop()
            if node in seen:
                continue
            seen.add(node)
            stack.extend(dependents[node])
        seen.discard(start)
        result[start] = len(seen)
    return result


def spectral_radius(system: ComplexSystem) -> float:
    """ρ(D). Zero for acyclic dependency graphs."""

    matrix, _ = dependency_matrix(system)
    if matrix.size == 0:
        return 0.0
    return float(max(abs(np.linalg.eigvals(matrix))))


def has_cycles(system: ComplexSystem) -> bool:
    """True when some component depends, directly or not, on itself."""

    dependents = _dependents(system)
    state: dict[UUID, int] = {}

    def visit(node: UUID) -> bool:
        state[node] = 1
        for nxt in dependents[node]:
            if state.get(nxt) == 1:
                return True
            if nxt not in state and visit(nxt):
                return True
        state[node] = 2
        return False

    return any(node not in state and visit(node) for node in dependents)


def katz_impact(
    system: ComplexSystem, alpha: float = DEFAULT_ALPHA
) -> dict[UUID, float]:
    """
    𝓘_j = Σ_{i≠j} R_ij with R = (I − αD)^−1 − I.
    """

    if alpha <= 0:
        raise ValueError("alpha must be > 0")
    matrix, order = dependency_matrix(system)
    if has_cycles(system):
        radius = spectral_radius(system)
        if alpha >= 1.0 / radius:
            raise ValueError(
                f"alpha must be < 1/ρ(D) = {1.0 / radius:.4f} on a cyclic graph"
            )
    identity = np.eye(len(order))
    propagation = np.linalg.inv(identity - alpha * matrix) - identity
    np.fill_diagonal(propagation, 0.0)
    return {cid: float(propagation[:, k].sum()) for k, cid in enumerate(order)}


def instability(system: ComplexSystem) -> dict[UUID, float]:
    """
    Martin instability I_v = C_e / (C_a + C_e) (Martin, 2002).

    C_e (efferent): components v depends on. C_a (afferent): components that
    depend on v. 0 = maximally stable, 1 = maximally unstable; isolated
    components get 0.
    """

    efferent = {cid: 0 for cid in system.component_ids()}
    afferent = {cid: 0 for cid in system.component_ids()}
    for relationship in system.dependencies():
        efferent[relationship.source_id] += 1
        afferent[relationship.target_id] += 1
    return {
        cid: (
            (efferent[cid] / (efferent[cid] + afferent[cid]))
            if efferent[cid] + afferent[cid]
            else 0.0
        )
        for cid in efferent
    }
