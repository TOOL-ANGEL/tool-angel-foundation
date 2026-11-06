"""
Golden tests (REQ-ECO-060): the published results of the model's two case
studies. A change that breaks these tests changes the model and requires an ADR.
"""

import pytest

from tool_angel.complex_systems.analysis import ECOSYSTEM, TRANSITION, analyze

TOL = 1e-4


def test_online_store_structure(online_store):
    system, _ = online_store
    report = analyze(system)

    assert report.openness == pytest.approx(0.696078, abs=TOL)
    assert report.coordination_cost == pytest.approx(0.696078, abs=TOL)
    assert report.ownership_entropy == pytest.approx(0.885633, abs=TOL)
    assert report.relational_value == pytest.approx(0.593333, abs=TOL)
    assert report.effective_control == pytest.approx(0.594631, abs=TOL)


def test_online_store_reliability(online_store):
    system, ids = online_store
    report = analyze(system)

    assert report.system_availability == pytest.approx(0.9956416, abs=1e-6)
    assert report.downtime_hours_per_year == pytest.approx(38.18, abs=0.01)
    assert report.structural_impact[ids["CLD"]] == pytest.approx(0.9956, abs=TOL)
    assert report.structural_impact[ids["PAG"]] == pytest.approx(0.5480, abs=TOL)
    assert report.structural_impact[ids["ANA"]] == pytest.approx(0.0696, abs=TOL)
    assert len(report.structural_dependencies) == 8
    assert report.composite is True


def test_online_store_propagation(online_store):
    system, ids = online_store
    report = analyze(system)

    assert report.acyclic is True
    assert report.reach[ids["CLD"]] == 8
    assert report.reach[ids["BD"]] == 7
    assert report.katz_impact[ids["BD"]] == pytest.approx(3.938, abs=1e-3)
    assert report.katz_impact[ids["CLD"]] == pytest.approx(3.219, abs=1e-3)


def test_online_store_index(online_store):
    system, _ = online_store
    report = analyze(system)

    assert report.signals.structural_share == pytest.approx(1.0)
    assert report.signals.mean_reach == pytest.approx(0.2179, abs=TOL)
    assert report.ice == pytest.approx(0.678599, abs=TOL)
    assert report.classification == ECOSYSTEM


def test_online_store_ahp_weights(online_store):
    system, _ = online_store
    weights = (0.3689, 0.1093, 0.2063, 0.2063, 0.1092)
    assert analyze(system, weights=weights).ice == pytest.approx(0.7091, abs=1e-3)


def test_piit_segovia(piit_segovia):
    system, _ = piit_segovia
    report = analyze(system)

    assert report.openness == pytest.approx(0.566372, abs=TOL)
    assert report.ownership_entropy == pytest.approx(0.835793, abs=TOL)
    assert report.relational_value == pytest.approx(0.458571, abs=TOL)
    assert report.effective_control == pytest.approx(0.684483, abs=TOL)
    assert report.system_availability == pytest.approx(0.945469, abs=1e-6)
    assert report.downtime_hours_per_year == pytest.approx(477.69, abs=0.01)
    assert report.ice == pytest.approx(0.543210, abs=TOL)
    assert report.classification == TRANSITION


def test_piit_redundancy_turns_structural_into_punctual(piit_segovia):
    """Corollary of Proposition 3: IGAC ∥ OSM are punctual integrations."""

    system, ids = piit_segovia
    report = analyze(system)
    names = {cid: code for code, cid in ids.items()}

    assert sorted(names[c] for c in report.structural_dependencies) == [
        "AAS",
        "DAT",
        "EDU",
        "HOS",
        "SEC",
    ]
    assert report.structural_impact[ids["IGA"]] == pytest.approx(0.0017, abs=TOL)
    assert report.structural_impact[ids["OSM"]] == pytest.approx(0.0068, abs=TOL)


def test_theta_sensitivity(online_store):
    system, _ = online_store
    assert analyze(system, theta=0.10).ice == pytest.approx(0.5786, abs=TOL)


def test_indicators_are_cs01_objects(online_store):
    system, _ = online_store
    indicators = analyze(system).indicators()
    ice = next(i for i in indicators if i.name == "ICE")

    assert ice.value == pytest.approx(0.678599, abs=TOL)
    assert ice.metadata["status"] == "experimental"
    assert ice.metadata["component"] == "CS-02"
