"""
Expected risk, sensitivity and uncertainty (REQ-ECO-070..075).

Reference values: Parts II–IV and limitations L3–L4 of the model.
"""

import pytest

from tool_angel.complex_systems.analysis import analyze, propagation, risk, sensitivity

TOL = 1e-3


def test_expected_risk_matches_published_values(online_store, piit_segovia):
    store, _ = online_store
    piit, _ = piit_segovia
    assert risk.expected_risk(store) == pytest.approx(9.419, abs=TOL)
    assert risk.expected_risk(piit) == pytest.approx(6.193, abs=TOL)


def test_provider_ranking(online_store, piit_segovia):
    store, ids = online_store
    ranking = risk.provider_risks(store)
    assert [row.component_id for row in ranking[:3]] == [
        ids["AUT"],
        ids["CLD"],
        ids["PAG"],
    ]
    assert ranking[0].risk == pytest.approx(2.959, abs=TOL)

    piit, pids = piit_segovia
    assert [row.component_id for row in risk.provider_risks(piit)[:2]] == [
        pids["HOS"],
        pids["SEC"],
    ]


def test_report_carries_risk(online_store):
    system, _ = online_store
    report = analyze(system)
    assert report.expected_risk == pytest.approx(9.419, abs=TOL)
    assert any(i.name.startswith("E[R]") for i in report.indicators())


def test_alpha_changes_magnitude_not_priority(online_store, piit_segovia):
    """Limitation L4: E[R] scales with α; the top-3 set is stable."""

    store, _ = online_store
    values = sensitivity.alpha_sensitivity(store)
    assert values[0.25] == pytest.approx(5.908, abs=TOL)
    assert values[0.75] == pytest.approx(14.962, abs=TOL)

    piit, _ = piit_segovia
    tops = {
        alpha: {row.component_id for row in risk.provider_risks(piit, alpha)[:3]}
        for alpha in (0.25, 0.5, 0.75)
    }
    assert tops[0.25] == tops[0.5] == tops[0.75]


def test_weight_uncertainty_and_rank_stability(online_store, piit_segovia):
    store, _ = online_store
    piit, _ = piit_segovia
    s_store, s_piit = analyze(store).signals, analyze(piit).signals

    u_store = sensitivity.weight_uncertainty(s_store)
    u_piit = sensitivity.weight_uncertainty(s_piit)
    assert u_store.mean == pytest.approx(0.6786, abs=0.005)
    assert u_piit.mean == pytest.approx(0.5432, abs=0.005)
    assert 0.72 < u_store.probabilities["ecosystem"] < 0.82
    assert 0.65 < u_piit.probabilities["transition"] < 0.75
    assert sum(u_store.probabilities.values()) == pytest.approx(1.0)
    assert sensitivity.rank_stability(s_store, s_piit) == 1.0


def test_leave_one_out_and_theta(online_store):
    system, _ = online_store
    values = sensitivity.leave_one_out(analyze(system).signals)
    assert values[2] == pytest.approx(0.7938, abs=TOL)  # without s3

    by_theta = sensitivity.theta_sensitivity(system)
    assert by_theta[0.01] == by_theta[0.05]
    assert by_theta[0.10] == pytest.approx(0.5786, abs=TOL)


def test_common_cause_penalty(piit_segovia):
    """Limitation L3: β = 0.10 multiplies IGAC ∥ OSM unavailability by 5.8."""

    assert sensitivity.common_cause_unavailability([0.02, 0.005], 0.0) == pytest.approx(
        1e-4
    )
    assert sensitivity.common_cause_unavailability([0.02, 0.005], 0.1) == pytest.approx(
        5.81e-4
    )

    system, _ = piit_segovia
    (factor,) = sensitivity.redundancy_penalty(system, 0.1).values()
    assert factor == pytest.approx(5.81, abs=0.01)

    with pytest.raises(ValueError):
        sensitivity.common_cause_unavailability([0.02], 0.1)


def test_martin_instability(online_store):
    system, ids = online_store
    values = propagation.instability(system)
    assert values[ids["WEB"]] == pytest.approx(0.9)
    assert values[ids["BD"]] == pytest.approx(1 / 6)
    assert values[ids["CLD"]] == 0.0
