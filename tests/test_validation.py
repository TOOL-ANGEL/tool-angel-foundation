"""
CS-03 Empirical validation (REQ-VAL-001..060).

The statistics are checked against their definitions and hand-computed
values; the protocol is checked on the pilot sample (insufficient by design)
and on a seeded synthetic sample whose ground truth is known.
"""

import copy
import random
from pathlib import Path

import numpy as np
import pytest
from test_ecosystem_properties import random_system

from tool_angel.builtin_commands.ecosystem import USAGE, EcosystemCommand
from tool_angel.complex_systems.analysis import analyze, classify, index, risk
from tool_angel.complex_systems.analysis import validation as v
from tool_angel.complex_systems.io import load_system, system_from_dict
from tool_angel.complex_systems.measurement import (
    CONTROL_CHECKLIST,
    Measurement,
    availability_from_mtbf,
    control_score,
)

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
MEASURED = EXAMPLES / "piit_segovia_measured.yaml"
PILOT = EXAMPLES / "validation" / "pilot_sample.yaml"

FULL = dict.fromkeys(CONTROL_CHECKLIST, 1.0)


# ---------------------------------------------------------------- measurement


def test_availability_from_mtbf():
    assert availability_from_mtbf(995, 5) == pytest.approx(0.995)
    with pytest.raises(ValueError):
        availability_from_mtbf(0, 1)


def test_control_score_is_checklist_mean():
    answers = dict.fromkeys(CONTROL_CHECKLIST, 0.0)
    answers["sla_penalty"] = 1.0
    answers["change_notice"] = 0.5
    assert control_score(answers) == pytest.approx(1.5 / 6)
    assert control_score(FULL) == 1.0


@pytest.mark.parametrize(
    "answers",
    [
        {"sla_penalty": 1},  # missing items
        {**FULL, "bribery": 1},  # unknown item
        {**FULL, "sla_penalty": 0.7},  # not in {0, ½, 1}
    ],
)
def test_control_score_rejects_incomplete_or_free_answers(answers):
    with pytest.raises(ValueError):
        control_score(answers)


def test_measurement_point_estimates():
    m = Measurement.from_dict(
        {
            "monitoring": {"up_hours": 990, "down_hours": 10, "outages": 4},
            "incidents": {"count": 3, "years": 2},
            "checklist": FULL,
        }
    )
    assert m.availability == pytest.approx(0.99)
    assert m.failure_rate == pytest.approx(1.5)
    assert m.control == 1.0
    mtbf = Measurement.from_dict({"mtbf": {"mtbf": 99, "mttr": 1, "outages": 5}})
    assert mtbf.availability == pytest.approx(0.99)
    assert (mtbf.up_hours, mtbf.down_hours) == (495, 5)


@pytest.mark.parametrize(
    "block",
    [
        {"monitoring": {"up_hours": 1, "down_hours": 1, "outages": 1}, "mtbf": {}},
        {"monitoring": {"up_hours": 10, "down_hours": 1, "outages": 0}},
        {"monitoring": {"up_hours": 10, "down_hours": 0, "outages": 2}},
        {"incidents": {"count": -1}},
        {"guesses": {}},
    ],
)
def test_measurement_rejects_inconsistent_evidence(block):
    with pytest.raises((ValueError, KeyError)):
        Measurement.from_dict(block)


def test_measured_distributions_are_centered_and_seeded():
    m = Measurement(
        up_hours=8660, down_hours=100, outages=25, incidents=4, years=1
    )
    draws = m.sample_availability(np.random.default_rng(1), 20_000)
    assert draws.mean() == pytest.approx(m.availability, abs=2e-4)
    assert ((draws >= 0) & (draws <= 1)).all()
    # relative error of the unavailability ≈ 1/√n
    assert (1 - draws).std() / (1 - m.availability) == pytest.approx(0.2, abs=0.02)
    rates = m.sample_failure_rate(np.random.default_rng(1), 20_000)
    assert rates.mean() == pytest.approx(4.5, abs=0.05)
    again = m.sample_availability(np.random.default_rng(1), 20_000)
    assert np.array_equal(draws, again)
    zero = Measurement(up_hours=100, down_hours=0, outages=0)
    assert (zero.sample_availability(np.random.default_rng(), 5) == 1.0).all()


def _file(component):
    return {"system": "S", "components": [{"code": "A"}, component]}


def test_loader_uses_measured_values():
    system, codes = system_from_dict(
        _file(
            {
                "code": "E",
                "scope": "external",
                "measurement": {
                    "monitoring": {"up_hours": 99, "down_hours": 1, "outages": 1},
                    "incidents": {"count": 2},
                    "checklist": FULL,
                },
            }
        )
    )
    e = system.component_map()[codes["E"]]
    assert (e.availability, e.failure_rate, e.control) == (0.99, 2.0, 1.0)
    assert isinstance(e.metadata["measurement"], Measurement)


@pytest.mark.parametrize(
    "component",
    [
        {
            "code": "E",
            "scope": "external",
            "availability": 0.9,
            "measurement": {
                "monitoring": {"up_hours": 9, "down_hours": 1, "outages": 1}
            },
        },
        {"code": "I", "measurement": {"checklist": FULL}},
    ],
)
def test_loader_rejects_given_and_measured_or_internal_checklist(component):
    with pytest.raises(ValueError):
        system_from_dict(_file(component))


# ---------------------------------------------------------------- phase 1


def test_measured_example_keeps_the_piit_point_result():
    system, _codes, parameters = load_system(MEASURED)
    report = analyze(system, **parameters)
    assert report.ice == pytest.approx(0.5432, abs=1e-3)
    assert report.classification == index.TRANSITION
    assert len(v.measured_components(system)) == 10


def test_parameter_uncertainty_is_reproducible_and_pure():
    system, _codes, parameters = load_system(MEASURED)
    before = copy.deepcopy([(c.availability, c.failure_rate) for c in system.components])
    first = v.parameter_uncertainty(system, samples=300, **parameters)
    second = v.parameter_uncertainty(system, samples=300, **parameters)
    assert first == second
    assert [(c.availability, c.failure_rate) for c in system.components] == before
    point = analyze(system, **parameters)
    assert first.system_availability.p5 <= point.system_availability
    assert point.system_availability <= first.system_availability.p95
    assert first.expected_risk.width > 0
    assert sum(first.probabilities.values()) == pytest.approx(1.0)
    assert first.accepted == (first.ice.width <= v.MAX_INTERVAL_WIDTH)


def test_parameter_uncertainty_requires_measurements():
    system, _codes, _parameters = load_system(EXAMPLES / "piit_segovia.yaml")
    with pytest.raises(ValueError, match="no measured components"):
        v.parameter_uncertainty(system)


def test_parameter_uncertainty_widens_with_fewer_outages():
    """Less evidence (fewer outages) must never give a narrower A_sys interval."""

    def build(outages):
        component = {
            "code": "E",
            "scope": "external",
            "measurement": {
                "monitoring": {
                    "up_hours": 8700,
                    "down_hours": 60,
                    "outages": outages,
                }
            },
        }
        data = _file(component)
        data["dependencies"] = [["A", "E", 1]]
        data["functions"] = [{"name": "F", "weight": 1, "path": ["A", "E"]}]
        return system_from_dict(data)[0]

    few = v.parameter_uncertainty(build(2), samples=2000)
    many = v.parameter_uncertainty(build(50), samples=2000)
    assert few.system_availability.width > many.system_availability.width


# ---------------------------------------------------------------- statistics


def test_ranks_average_ties():
    assert v.ranks([10, 20, 20, 5]).tolist() == [2.0, 3.5, 3.5, 1.0]


def test_spearman_known_values():
    assert v.spearman([1, 2, 3, 4], [10, 20, 30, 1000]) == pytest.approx(1.0)
    assert v.spearman([1, 2, 3, 4], [4, 3, 2, 1]) == pytest.approx(-1.0)
    # textbook: d = (0, 0, 1, -1, 0) → ρ = 1 − 6·2/(5·24) = 0.9
    assert v.spearman([1, 2, 3, 4, 5], [1, 2, 4, 3, 5]) == pytest.approx(0.9)
    with pytest.raises(ValueError):
        v.spearman([1, 2, 3], [5, 5, 5])
    with pytest.raises(ValueError):
        v.spearman([1, 2], [1, 2])


def test_permutation_p_value():
    x = list(range(12))
    assert v.permutation_p_value(x, x, permutations=2000) < 0.01
    assert v.permutation_p_value(x, x[::-1], permutations=2000) > 0.99
    assert v.permutation_p_value(x, x, permutations=999) >= 1 / 1000


def test_cronbach_alpha_matches_definition():
    m = np.array([[1, 2, 2], [2, 3, 3], [3, 3, 4], [4, 5, 5], [2, 2, 3]], float)
    k = 3
    expected = k / (k - 1) * (
        1 - m.var(axis=0, ddof=1).sum() / m.sum(axis=1).var(ddof=1)
    )
    assert v.cronbach_alpha(m) == pytest.approx(expected)
    identical = np.tile(np.arange(6.0)[:, None], (1, 4))
    assert v.cronbach_alpha(identical) == pytest.approx(1.0)
    with pytest.raises(ValueError):
        v.cronbach_alpha(np.ones((4, 3)))


def test_redundancy_and_kmo():
    rng = np.random.default_rng(3)
    base = rng.normal(size=60)
    m = np.column_stack(
        [
            base,
            base + rng.normal(scale=0.01, size=60),  # near-duplicate of s1
            rng.normal(size=60),
            rng.normal(size=60),
            rng.normal(size=60),
        ]
    )
    pairs = v.redundant_pairs(m)
    assert [(a, b) for a, b, _ in pairs] == [("s1", "s2")]
    corr = v.signal_correlations(m)
    assert np.allclose(corr, corr.T) and np.allclose(np.diag(corr), 1.0)
    assert 0.0 <= v.kmo(m) <= 1.0


def test_youden_threshold():
    cut, j = v.youden_threshold([0.1, 0.2, 0.7, 0.9], [False, False, True, True])
    assert j == pytest.approx(1.0)
    assert 0.2 < cut < 0.7
    _cut, j = v.youden_threshold([0.1, 0.9, 0.2, 0.8], [True, False, True, False])
    assert j <= 0.0 + 1e-12
    with pytest.raises(ValueError):
        v.youden_threshold([0.1, 0.2], [True, True])


def test_calibrate_thresholds():
    ices = [0.1, 0.2, 0.25, 0.4, 0.5, 0.55, 0.7, 0.8, 0.9]
    classes = ["closed"] * 3 + ["transition"] * 3 + ["ecosystem"] * 3
    result = v.calibrate_thresholds(ices, classes)
    assert 0.25 < result.low < 0.4 and 0.55 < result.high < 0.7
    assert result.accepted
    with pytest.raises(ValueError):
        v.calibrate_thresholds(ices, ["open"] * 9)


def test_estimate_beta_cc():
    assert v.estimate_beta_cc(1, 10) == pytest.approx(0.1)
    for bad in ((3, 2), (0, 0), (-1, 4)):
        with pytest.raises(ValueError):
            v.estimate_beta_cc(*bad)


def test_predictive_validity():
    risks = [1, 2, 3, 4, 5, 6, 7, 8]
    good = v.predictive_validity(risks, [3, 4, 9, 10, 15, 14, 20, 30], permutations=2000)
    assert good.accepted and good.rho > 0.9
    bad = v.predictive_validity(risks, risks[::-1], permutations=2000)
    assert not bad.accepted


# ---------------------------------------------------------------- protocol


def synthetic_sample(n=40, seed=7):
    """Systems whose expert labels and outages follow the model, plus noise."""

    rng = random.Random(seed)
    entries = []
    for k in range(n):
        system = random_system(k, single_internal_owner=k % 2 == 0)
        for component in system.components:
            if component.is_external:
                component.failure_rate = rng.uniform(0, 6)
        ice = index.ice(index.signals(system))
        entries.append(
            v.SampleEntry(
                system=system,
                expert_class=classify(ice + rng.gauss(0, 0.02)),
                expert_score=ice + rng.gauss(0, 0.05),
                outage_hours=max(
                    0.0, 10 * risk.expected_risk(system, 0.5) + rng.gauss(0, 1)
                ),
            )
        )
    return entries


def test_pilot_sample_is_insufficient_not_validated():
    name, entries = v.load_sample(PILOT)
    report = v.validate_sample(entries, sample=name, permutations=200)
    assert report.n == 3
    assert [p.status for p in report.phases] == [v.INSUFFICIENT] * 4
    assert report.phases[0].n == 1
    assert not report.validated


def test_synthetic_sample_runs_every_phase():
    entries = synthetic_sample()
    report = v.validate_sample(entries, sample="synthetic", permutations=2000)
    phases = {p.phase: p for p in report.phases}
    assert phases[1].status == v.INSUFFICIENT  # no measured systems
    validity = phases[2]
    expected = (
        validity.criteria["cronbach_alpha"] >= v.MIN_CRONBACH
        and validity.criteria["spearman_vs_experts"] >= v.MIN_SPEARMAN
        and not validity.criteria["redundant_pairs"]
    )
    assert validity.status == (v.PASS if expected else v.FAIL)
    assert validity.criteria["spearman_vs_experts"] > 0.8
    assert phases[3].status == v.PASS
    low, high = phases[3].criteria["thresholds"]
    assert low < high
    assert phases[3].criteria["alpha"] in (0.25, 0.5, 0.75)
    assert phases[4].status == v.PASS
    assert phases[4].criteria["p_value"] < v.MAX_P_VALUE
    assert not report.validated  # phase 1 is still missing


def test_noise_labels_fail_calibration_and_prediction():
    rng = random.Random(11)
    entries = synthetic_sample()
    for entry in entries:
        entry.expert_class = rng.choice(list(v.CLASS_ORDER))
        entry.outage_hours = rng.uniform(0, 50)
    report = v.validate_sample(entries, permutations=2000)
    phases = {p.phase: p for p in report.phases}
    assert phases[3].status == v.FAIL
    assert phases[4].status == v.FAIL
    assert phases[4].notes


def test_protocol_never_mutates_the_systems():
    entries = synthetic_sample(n=6)
    snapshot = [
        [(c.availability, c.failure_rate, c.control) for c in e.system.components]
        for e in entries
    ]
    v.validate_sample(entries, permutations=100)
    assert snapshot == [
        [(c.availability, c.failure_rate, c.control) for c in e.system.components]
        for e in entries
    ]


def test_sample_entry_validation():
    system, _codes, _parameters = load_system(EXAMPLES / "piit_segovia.yaml")
    with pytest.raises(ValueError):
        v.SampleEntry(system, expert_class="open")
    with pytest.raises(ValueError):
        v.SampleEntry(system, outage_hours=-1)
    assert v.SampleEntry(system, expert_class="ecosystem").expert_rank == 2.0
    assert v.SampleEntry(system, expert_score=4.5).expert_rank == 4.5


# ---------------------------------------------------------------- CLI


def test_cli_measure_and_validate():
    command = EcosystemCommand()
    assert "measure" in USAGE and "validate" in USAGE
    assert command.execute("calibrate", "x") == USAGE
    measured = command.execute("measure", str(MEASURED), samples="200")
    assert "Measurement uncertainty (CS-03 phase 1)" in measured
    assert "measured components 10" in measured
    assert "→ PASS" in measured or "→ FAIL" in measured
    report = command.execute("validate", str(PILOT), permutations="100")
    assert "1. Measurement  INSUFFICIENT" in report
    assert "4. Prediction   INSUFFICIENT" in report
    assert "experimental" in report
