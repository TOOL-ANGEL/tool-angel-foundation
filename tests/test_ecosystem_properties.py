"""
Formal properties of the model (REQ-ECO-050..053) and data-model rules.
"""

import random

import pytest

from tool_angel.complex_systems import (
    Actor,
    ComplexSystem,
    Component,
    Relationship,
    ValueFunction,
)
from tool_angel.complex_systems.analysis import (
    Signals,
    analyze,
    ice,
    propagation,
    structure,
)

# --------------------------------------------------------------------------
# Data model
# --------------------------------------------------------------------------


def test_component_rejects_out_of_range_parameters():
    with pytest.raises(ValueError):
        Component.create("X", availability=1.2)
    with pytest.raises(ValueError):
        Component.create("X", scope="external", control=-0.1)
    with pytest.raises(ValueError):
        Component.create("X", failure_rate=-1)
    with pytest.raises(ValueError):
        Component.create("X", scope="partner")


def test_internal_component_has_full_control():
    with pytest.raises(ValueError):
        Component.create("X", control=0.5)
    assert Component.create("X").control == 1.0
    assert Component.create("Y", scope="external").control == 0.0


def test_add_component_enforces_type():
    system = ComplexSystem("S")
    with pytest.raises(TypeError):
        system.add_component({"name": "Acueducto"})


def test_validate_detects_unknown_endpoint_and_bad_weights():
    system = ComplexSystem("S")
    a = Component.create("A")
    system.add_component(a)
    system.add_relationship(
        Relationship.create(a.id, Component.create("B").id, "depends_on")
    )
    system.add_value_function(ValueFunction.create("F", 0.5, [a.id]))

    errors = system.validation_errors()
    assert any("unknown component" in e for e in errors)
    assert any("sum to 1" in e for e in errors)
    with pytest.raises(ValueError):
        analyze(system)


def test_analysis_does_not_mutate(online_store):
    system, _ = online_store
    before = (system.summary(), [c.availability for c in system.components])
    analyze(system)
    assert (system.summary(), [c.availability for c in system.components]) == before


# --------------------------------------------------------------------------
# Random systems for property checks
# --------------------------------------------------------------------------


def random_system(seed: int, single_internal_owner: bool = True) -> ComplexSystem:
    rng = random.Random(seed)
    system = ComplexSystem(f"random-{seed}")
    internal_owner = Actor.create("Operador")
    system.add_actor(internal_owner)
    components = []
    for k in range(rng.randint(3, 10)):
        external = rng.random() < 0.5
        if external:
            owner = Actor.create(f"P{k}")
            system.add_actor(owner)
            component = Component.create(
                f"E{k}",
                scope="external",
                owner_id=owner.id,
                availability=rng.uniform(0.9, 1.0),
                control=rng.random(),
            )
        else:
            owner_id = internal_owner.id
            if not single_internal_owner and rng.random() < 0.5:
                team = Actor.create(f"T{k}")
                system.add_actor(team)
                owner_id = team.id
            component = Component.create(
                f"I{k}", owner_id=owner_id, availability=rng.uniform(0.9, 1.0)
            )
        system.add_component(component)
        components.append(component)
    for i, source in enumerate(components):
        for target in components[i + 1 :]:
            if rng.random() < 0.4:
                system.add_relationship(
                    Relationship.create(
                        source.id, target.id, "depends_on", rng.uniform(1, 10)
                    )
                )
    raw = [rng.random() + 0.01 for _ in range(rng.randint(1, 4))]
    total = sum(raw)
    for k, weight in enumerate(raw):
        path = rng.sample([c.id for c in components], rng.randint(1, len(components)))
        system.add_value_function(ValueFunction.create(f"F{k}", weight / total, path))
    return system


SEEDS = range(200)


@pytest.mark.parametrize("seed", SEEDS)
def test_proposition_1_bounded(seed):
    report = analyze(random_system(seed, single_internal_owner=seed % 2 == 0))
    values = (
        report.openness,
        report.coordination_cost,
        report.ownership_entropy,
        report.relational_value,
        report.effective_control,
        report.ice,
        *report.signals.as_tuple(),
    )
    assert all(-1e-12 <= v <= 1 + 1e-12 for v in values)


@pytest.mark.parametrize("seed", SEEDS)
def test_proposition_2_tau_le_omega(seed):
    system = random_system(seed, single_internal_owner=True)
    assert structure.coordination_cost(system) <= structure.openness(system) + 1e-12


def test_proposition_4_control_threshold(online_store):
    system, _ = online_store
    k_before = structure.effective_control(system)
    owner = Actor.create("Nuevo")
    system.add_actor(owner)
    newcomer = Component.create(
        "NEW", scope="external", owner_id=owner.id, control=k_before - 0.1
    )
    system.add_component(newcomer)
    system.value_functions[0].path.append(newcomer.id)
    assert structure.effective_control(system) < k_before


@pytest.mark.parametrize("seed", range(50))
def test_proposition_6_dominance(seed):
    rng = random.Random(seed)
    low = Signals(*[rng.random() for _ in range(5)])
    high = Signals(*[min(1.0, x + rng.random() * 0.3) for x in low.as_tuple()])
    raw = [rng.random() for _ in range(5)]
    weights = [w / sum(raw) for w in raw]
    assert ice(high, weights) >= ice(low, weights)


@pytest.mark.parametrize("seed", range(50))
def test_reach_is_independent_of_alpha(seed):
    """Correction L4 of the model: s3 does not depend on α."""

    system = random_system(seed)
    reach = propagation.reach(system)
    impact_low = propagation.katz_impact(system, 0.25)
    impact_high = propagation.katz_impact(system, 0.75)
    for cid, count in reach.items():
        assert (impact_low[cid] > 0) == (count > 0)
        assert (impact_high[cid] > 0) == (count > 0)


def test_katz_rejects_divergent_alpha_on_cycles():
    system = ComplexSystem("ciclo")
    a, b = Component.create("A"), Component.create("B")
    system.add_component(a)
    system.add_component(b)
    system.add_relationship(Relationship.create(a.id, b.id, "depends_on"))
    system.add_relationship(Relationship.create(b.id, a.id, "depends_on"))

    assert propagation.has_cycles(system)
    with pytest.raises(ValueError):
        propagation.katz_impact(system, alpha=1.0)
    assert propagation.katz_impact(system, alpha=0.5)[a.id] > 0


def test_single_actor_has_sharp_boundary():
    system = ComplexSystem("cerrado")
    for name in ("A", "B", "C"):
        system.add_component(Component.create(name))
    assert structure.ownership_entropy(system) == 0.0
    assert structure.openness(system) == 0.0
