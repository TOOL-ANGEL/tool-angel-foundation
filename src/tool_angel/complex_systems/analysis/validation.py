"""
CS-03 Empirical validation of the ecosystem model (limitations L1–L5).

Implements the four-phase validation roadmap of the model, each with the
acceptance criterion written in "Modelo Matemático de Sistemas Ecosistémicos":

| Phase          | Sample          | Test                                    | Accept when                |
|----------------|-----------------|-----------------------------------------|----------------------------|
| 1. Measurement | 3–5 real systems| Measured Θ, Monte Carlo of the ICE      | p95 − p5 ≤ 0.15            |
| 2. Validity    | N ≥ 30          | Cronbach α, Spearman vs experts, ρ_ij   | α_C ≥ 0.70, ρ_S ≥ 0.6,     |
|                |                 |                                         | no pair with |ρ| > 0.9     |
| 3. Calibration | same sample     | ROC thresholds (Youden), β_cc, α        | J ≥ 0.5 for both cuts      |
| 4. Prediction  | 12-month follow | E[R] vs observed outage hours           | ρ > 0 and p < 0.05         |

Statistics are implemented on numpy only. p-values come from a seeded
permutation test, so results are reproducible and need no scipy.

Until a sample passes these phases, Ω, τ, ρ_V, K, E[R], the ICE and its
thresholds remain experimental operators (ADR-0002, ADR-0003).
"""

import copy
import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from tool_angel.complex_systems.analysis import index, propagation, reliability, risk
from tool_angel.complex_systems.io import load_system
from tool_angel.complex_systems.measurement import Measurement
from tool_angel.complex_systems.system import ComplexSystem

Values = Sequence[float] | np.ndarray

SIGNAL_NAMES: tuple[str, ...] = ("s1", "s2", "s3", "s4", "s5")

CLASS_ORDER: dict[str, int] = {index.CLOSED: 0, index.TRANSITION: 1, index.ECOSYSTEM: 2}

# Acceptance criteria of the roadmap.
MAX_INTERVAL_WIDTH = 0.15
MIN_MEASURED_SYSTEMS = 3
MIN_SAMPLE = 30
MIN_CRONBACH = 0.70
MIN_SPEARMAN = 0.6
MAX_SIGNAL_CORRELATION = 0.9
MIN_KMO = 0.6
MIN_YOUDEN = 0.5
MAX_P_VALUE = 0.05

PASS = "pass"
FAIL = "fail"
INSUFFICIENT = "insufficient"


# ---------------------------------------------------------------------------
# Phase 1 — measurement and parameter uncertainty (L1)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Interval:
    """Mean and 5th–95th percentile of a Monte Carlo sample."""

    mean: float
    p5: float
    p95: float

    @property
    def width(self) -> float:
        return self.p95 - self.p5

    @classmethod
    def of(cls, values: np.ndarray) -> "Interval":
        return cls(
            mean=float(values.mean()),
            p5=float(np.percentile(values, 5)),
            p95=float(np.percentile(values, 95)),
        )


@dataclass(frozen=True, slots=True)
class ParameterUncertainty:
    """Propagation of measured-parameter uncertainty to the model outputs."""

    system_name: str
    samples: int
    measured_components: int
    ice: Interval
    system_availability: Interval
    expected_risk: Interval
    probabilities: dict[str, float]
    max_width: float = MAX_INTERVAL_WIDTH

    @property
    def accepted(self) -> bool:
        return self.ice.width <= self.max_width


def measured_components(system: ComplexSystem) -> dict[Any, Measurement]:
    """Components carrying a Measurement in their metadata, by id."""

    return {
        c.id: c.metadata["measurement"]
        for c in system.components
        if isinstance(c.metadata.get("measurement"), Measurement)
    }


def parameter_uncertainty(
    system: ComplexSystem,
    *,
    samples: int = 1000,
    seed: int = 42,
    theta: float = reliability.DEFAULT_THETA,
    alpha: float = propagation.DEFAULT_ALPHA,
    weights: Sequence[float] | None = None,
    thresholds: tuple[float, float] = index.DEFAULT_THRESHOLDS,
    max_width: float = MAX_INTERVAL_WIDTH,
) -> ParameterUncertainty:
    """
    Monte Carlo of the ICE, A_sys and E[R] under the measured distributions
    A ~ 1 − Û·Gamma(n, 1/n) and λ ~ Gamma(k + ½, 1/T).

    The checklist control γ is deterministic. The input system is never
    mutated: draws are applied to a private copy.
    """

    system.validate()
    measured = measured_components(system)
    if not measured:
        raise ValueError("the system has no measured components")
    if samples < 2:
        raise ValueError("samples must be >= 2")

    rng = np.random.default_rng(seed)
    work = copy.deepcopy(system)
    by_id = work.component_map()
    draws_a: dict[Any, np.ndarray] = {}
    draws_l: dict[Any, np.ndarray] = {}
    for cid, measurement in measured.items():
        availability = measurement.sample_availability(rng, samples)
        if availability is not None:
            draws_a[cid] = availability
        failure_rate = measurement.sample_failure_rate(rng, samples)
        if failure_rate is not None:
            draws_l[cid] = failure_rate

    ice = np.empty(samples)
    a_sys = np.empty(samples)
    e_risk = np.empty(samples)
    for t in range(samples):
        for cid, values in draws_a.items():
            by_id[cid].availability = float(values[t])
        for cid, values in draws_l.items():
            by_id[cid].failure_rate = float(values[t])
        ice[t] = index.ice(index.signals(work, theta), weights)
        a_sys[t] = reliability.system_availability(work)
        e_risk[t] = risk.expected_risk(work, alpha)

    low, high = thresholds
    return ParameterUncertainty(
        system_name=system.name,
        samples=samples,
        measured_components=len(measured),
        ice=Interval.of(ice),
        system_availability=Interval.of(a_sys),
        expected_risk=Interval.of(e_risk),
        probabilities={
            index.CLOSED: float((ice < low).mean()),
            index.TRANSITION: float(((ice >= low) & (ice < high)).mean()),
            index.ECOSYSTEM: float((ice >= high).mean()),
        },
        max_width=max_width,
    )


# ---------------------------------------------------------------------------
# Statistics (numpy only)
# ---------------------------------------------------------------------------


def _vector(values: Values, label: str) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    if array.ndim != 1:
        raise ValueError(f"{label} must be one-dimensional")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{label} contains non-finite values")
    return array


def ranks(values: Values) -> np.ndarray:
    """Ranks 1..n with ties given their average rank."""

    x = _vector(values, "values")
    order = np.argsort(x, kind="mergesort")
    result = np.empty(len(x))
    sorted_x = x[order]
    start = 0
    while start < len(x):
        end = start
        while end + 1 < len(x) and sorted_x[end + 1] == sorted_x[start]:
            end += 1
        result[order[start : end + 1]] = (start + end) / 2.0 + 1.0
        start = end + 1
    return result


def spearman(x: Values, y: Values) -> float:
    """Spearman rank correlation ρ_S (Pearson correlation of the ranks)."""

    a, b = _vector(x, "x"), _vector(y, "y")
    if len(a) != len(b):
        raise ValueError("x and y must have the same length")
    if len(a) < 3:
        raise ValueError("Spearman needs at least 3 observations")
    ra, rb = ranks(a), ranks(b)
    if ra.std() == 0 or rb.std() == 0:
        raise ValueError("Spearman is undefined for a constant variable")
    return float(np.corrcoef(ra, rb)[0, 1])


def permutation_p_value(
    x: Values,
    y: Values,
    *,
    permutations: int = 10_000,
    seed: int = 42,
) -> float:
    """
    One-sided p-value of H1: ρ_S > 0, by permutation of y.

    p = (1 + #{ρ_perm ≥ ρ_obs}) / (1 + permutations).
    """

    observed = spearman(x, y)
    ra, rb = ranks(x), ranks(y)
    rng = np.random.default_rng(seed)
    ra = (ra - ra.mean()) / ra.std()
    hits = 0
    for _ in range(permutations):
        perm = rng.permutation(rb)
        perm = (perm - perm.mean()) / perm.std()
        if float((ra * perm).mean()) >= observed - 1e-12:
            hits += 1
    return (1 + hits) / (1 + permutations)


def cronbach_alpha(matrix: np.ndarray) -> float:
    """
    α_C = k/(k−1) · (1 − Σ σ²_j / σ²_total), for an N × k matrix of items.
    """

    m = np.asarray(matrix, dtype=float)
    if m.ndim != 2 or m.shape[1] < 2 or m.shape[0] < 2:
        raise ValueError("Cronbach's alpha needs an N × k matrix with N, k ≥ 2")
    k = m.shape[1]
    total = m.sum(axis=1).var(ddof=1)
    if total == 0:
        raise ValueError("Cronbach's alpha is undefined when the total is constant")
    return float(k / (k - 1) * (1 - m.var(axis=0, ddof=1).sum() / total))


def signal_correlations(matrix: np.ndarray) -> np.ndarray:
    """k × k Spearman correlation matrix of the columns."""

    m = np.asarray(matrix, dtype=float)
    k = m.shape[1]
    result = np.eye(k)
    for i in range(k):
        for j in range(i + 1, k):
            result[i, j] = result[j, i] = spearman(m[:, i], m[:, j])
    return result


def redundant_pairs(
    matrix: np.ndarray,
    limit: float = MAX_SIGNAL_CORRELATION,
    names: Sequence[str] = SIGNAL_NAMES,
) -> list[tuple[str, str, float]]:
    """Signal pairs whose |ρ_S| exceeds the redundancy limit."""

    corr = signal_correlations(matrix)
    k = corr.shape[0]
    return [
        (names[i], names[j], float(corr[i, j]))
        for i in range(k)
        for j in range(i + 1, k)
        if abs(corr[i, j]) > limit
    ]


def kmo(matrix: np.ndarray) -> float:
    """
    Kaiser–Meyer–Olkin sampling adequacy of the columns.

    KMO = Σ r²_ij / (Σ r²_ij + Σ p²_ij) over i ≠ j, where p are the partial
    correlations from the inverse correlation matrix. KMO ≥ 0.6 allows the
    weights β to be derived from principal components.
    """

    m = np.asarray(matrix, dtype=float)
    r = np.corrcoef(m, rowvar=False)
    inverse = np.linalg.pinv(r)
    d = np.sqrt(np.outer(np.diag(inverse), np.diag(inverse)))
    partial = -inverse / d
    off = ~np.eye(r.shape[0], dtype=bool)
    r2 = float((r[off] ** 2).sum())
    p2 = float((partial[off] ** 2).sum())
    return r2 / (r2 + p2)


# ---------------------------------------------------------------------------
# Phase 3 — calibration (L2, L3, L4)
# ---------------------------------------------------------------------------


def youden_threshold(scores: Values, positives: Sequence[bool]) -> tuple[float, float]:
    """
    Cut maximizing J = sensitivity + specificity − 1 for "score ≥ cut".

    Candidate cuts are midpoints between consecutive distinct scores.
    Returns (cut, J).
    """

    s = _vector(scores, "scores")
    y = np.asarray(positives, dtype=bool)
    if len(s) != len(y):
        raise ValueError("scores and labels must have the same length")
    if y.all() or not y.any():
        raise ValueError("the labels need both positive and negative cases")
    values = np.unique(s)
    cuts = (values[:-1] + values[1:]) / 2.0 if len(values) > 1 else values
    best_cut, best_j = float(cuts[0]), -math.inf
    for cut in cuts:
        predicted = s >= cut
        sensitivity = float((predicted & y).sum() / y.sum())
        specificity = float((~predicted & ~y).sum() / (~y).sum())
        j = sensitivity + specificity - 1.0
        if j > best_j + 1e-12:
            best_cut, best_j = float(cut), j
    return best_cut, best_j


@dataclass(frozen=True, slots=True)
class ThresholdCalibration:
    """ICE thresholds fitted against an expert classification."""

    low: float
    youden_low: float
    high: float
    youden_high: float

    @property
    def thresholds(self) -> tuple[float, float]:
        return (self.low, self.high)

    @property
    def accepted(self) -> bool:
        return (
            self.low < self.high
            and self.youden_low >= MIN_YOUDEN
            and self.youden_high >= MIN_YOUDEN
        )


def calibrate_thresholds(
    ices: Sequence[float], expert_classes: Sequence[str]
) -> ThresholdCalibration:
    """
    Replace the 0.3 / 0.6 cuts by the Youden-optimal ones:
    low separates closed from the rest, high separates ecosystem from the rest.
    """

    unknown = set(expert_classes) - set(CLASS_ORDER)
    if unknown:
        raise ValueError(f"unknown classes: {sorted(unknown)}")
    low, j_low = youden_threshold(ices, [c != index.CLOSED for c in expert_classes])
    high, j_high = youden_threshold(
        ices, [c == index.ECOSYSTEM for c in expert_classes]
    )
    return ThresholdCalibration(low, j_low, high, j_high)


def estimate_beta_cc(common_cause_failures: int, total_failures: int) -> float:
    """
    β-factor of a redundant group: share of its failures with a common cause.
    """

    if total_failures <= 0 or not 0 <= common_cause_failures <= total_failures:
        raise ValueError("need 0 ≤ common-cause failures ≤ total failures, total > 0")
    return common_cause_failures / total_failures


def select_alpha(
    systems: Sequence[ComplexSystem],
    outage_hours: Sequence[float],
    alphas: Sequence[float] = (0.25, 0.50, 0.75),
) -> tuple[float, dict[float, float]]:
    """
    Katz factor α whose E[R] best ranks the observed outage hours.

    Returns the best α and ρ_S for every candidate. Candidates must satisfy
    α < 1/ρ(D) for every cyclic system (checked by risk.expected_risk).
    """

    if len(systems) != len(outage_hours):
        raise ValueError("one observation per system is required")
    scores = {
        alpha: spearman([risk.expected_risk(s, alpha) for s in systems], outage_hours)
        for alpha in alphas
    }
    best = max(scores, key=lambda a: (scores[a], -abs(a - propagation.DEFAULT_ALPHA)))
    return best, scores


# ---------------------------------------------------------------------------
# Phase 4 — prediction (L2)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class PredictiveValidity:
    """Rank agreement between expected risk and observed outage hours."""

    n: int
    rho: float
    p_value: float

    @property
    def accepted(self) -> bool:
        return self.rho > 0 and self.p_value < MAX_P_VALUE


def predictive_validity(
    expected_risks: Values,
    outage_hours: Values,
    *,
    permutations: int = 10_000,
    seed: int = 42,
) -> PredictiveValidity:
    """ρ_S between E[R] and outage hours, with a one-sided permutation p-value."""

    return PredictiveValidity(
        n=len(expected_risks),
        rho=spearman(expected_risks, outage_hours),
        p_value=permutation_p_value(
            expected_risks, outage_hours, permutations=permutations, seed=seed
        ),
    )


# ---------------------------------------------------------------------------
# Validation sample and protocol
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class SampleEntry:
    """One system of a validation sample and its external evidence."""

    system: ComplexSystem
    parameters: dict[str, Any] = field(default_factory=dict)
    expert_class: str | None = None
    expert_score: float | None = None
    outage_hours: float | None = None

    def __post_init__(self) -> None:
        if self.expert_class is not None and self.expert_class not in CLASS_ORDER:
            raise ValueError(f"unknown expert class {self.expert_class!r}")
        if self.outage_hours is not None and self.outage_hours < 0:
            raise ValueError("outage_hours must be >= 0")

    @property
    def expert_rank(self) -> float | None:
        """Expert judgement as an ordinal: the score, else the class order."""

        if self.expert_score is not None:
            return float(self.expert_score)
        if self.expert_class is not None:
            return float(CLASS_ORDER[self.expert_class])
        return None


def load_sample(path: str | Path) -> tuple[str, list[SampleEntry]]:
    """
    Load a validation sample file. System paths are relative to it:

        sample: Piloto Nordeste Antioqueño
        systems:
          - file: ../piit_segovia.yaml
            expert_class: transition      # closed | transition | ecosystem
            expert_score: 3.5             # optional ordinal (e.g. panel mean)
            outage_hours: 41.0            # optional, observed over 12 months
    """

    path = Path(path)
    with open(path, encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, Mapping) or "systems" not in data:
        raise ValueError(f"{path} needs a 'systems' list")
    entries = []
    for item in data["systems"]:
        system, _codes, parameters = load_system(path.parent / item["file"])
        entries.append(
            SampleEntry(
                system=system,
                parameters=parameters,
                expert_class=item.get("expert_class"),
                expert_score=item.get("expert_score"),
                outage_hours=item.get("outage_hours"),
            )
        )
    return str(data.get("sample", path.stem)), entries


@dataclass(frozen=True, slots=True)
class PhaseResult:
    """Outcome of one validation phase."""

    phase: int
    name: str
    status: str
    n: int
    criteria: dict[str, Any]
    notes: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class ValidationReport:
    """Outcome of the four-phase protocol on one sample."""

    sample: str
    n: int
    phases: list[PhaseResult]

    @property
    def validated(self) -> bool:
        """True only when every phase passes."""

        return all(p.status == PASS for p in self.phases)


def _status(enough: bool, ok: bool) -> str:
    if not enough:
        return INSUFFICIENT
    return PASS if ok else FAIL


def _ice(entry: SampleEntry) -> float:
    theta = float(entry.parameters.get("theta", reliability.DEFAULT_THETA))
    return index.ice(index.signals(entry.system, theta))


def _phase_measurement(
    entries: Sequence[SampleEntry], samples: int, seed: int
) -> PhaseResult:
    widths: dict[str, float] = {}
    for entry in entries:
        if measured_components(entry.system):
            result = parameter_uncertainty(
                entry.system,
                samples=samples,
                seed=seed,
                theta=float(entry.parameters.get("theta", reliability.DEFAULT_THETA)),
                alpha=float(entry.parameters.get("alpha", propagation.DEFAULT_ALPHA)),
            )
            widths[entry.system.name] = result.ice.width
    enough = len(widths) >= MIN_MEASURED_SYSTEMS
    ok = bool(widths) and max(widths.values()) <= MAX_INTERVAL_WIDTH
    notes = []
    if not enough:
        notes.append(
            f"{len(widths)} measured systems; at least {MIN_MEASURED_SYSTEMS} required"
        )
    return PhaseResult(
        1,
        "Measurement",
        _status(enough, ok),
        len(widths),
        {"ice_interval_width": widths, "max_width": MAX_INTERVAL_WIDTH},
        notes,
    )


def _phase_validity(
    entries: Sequence[SampleEntry], permutations: int, seed: int
) -> PhaseResult:
    rated = [e for e in entries if e.expert_rank is not None]
    n = len(rated)
    criteria: dict[str, Any] = {}
    notes: list[str] = []
    ok = False
    if n >= 3:
        matrix = np.array([index.signals(e.system).as_tuple() for e in rated])
        ice_values = [_ice(e) for e in rated]
        experts = [r for e in rated if (r := e.expert_rank) is not None]
        try:
            alpha_c = cronbach_alpha(matrix)
            rho = spearman(ice_values, experts)  # type: ignore[arg-type]
            pairs = redundant_pairs(matrix)
            criteria = {
                "cronbach_alpha": alpha_c,
                "spearman_vs_experts": rho,
                "p_value": permutation_p_value(
                    ice_values,
                    experts,
                    permutations=permutations,
                    seed=seed,  # type: ignore[arg-type]
                ),
                "redundant_pairs": pairs,
            }
            try:
                criteria["kmo"] = kmo(matrix)
            except (ValueError, np.linalg.LinAlgError):  # pragma: no cover
                notes.append("KMO undefined for this sample")
            ok = alpha_c >= MIN_CRONBACH and rho >= MIN_SPEARMAN and not pairs
            if alpha_c < MIN_CRONBACH:
                notes.append(
                    f"Cronbach α {alpha_c:.2f} < {MIN_CRONBACH}: the five signals are"
                    " not internally consistent"
                )
            if rho < MIN_SPEARMAN:
                notes.append(
                    f"ρ_S vs experts {rho:.2f} < {MIN_SPEARMAN}: weak convergent validity"
                )
            if pairs:
                notes.append(
                    "redundant signals: "
                    + ", ".join(f"{a}~{b} ({r:+.2f})" for a, b, r in pairs)
                    + "; consider replacing one by the observability O_E"
                )
            if criteria.get("kmo", 0.0) >= MIN_KMO:
                notes.append("KMO ≥ 0.6: β may be derived by principal components")
        except ValueError as error:
            notes.append(str(error))
    if n < MIN_SAMPLE:
        notes.append(f"{n} systems rated by experts; at least {MIN_SAMPLE} required")
    return PhaseResult(2, "Validity", _status(n >= MIN_SAMPLE, ok), n, criteria, notes)


def _phase_calibration(entries: Sequence[SampleEntry]) -> PhaseResult:
    labelled = [e for e in entries if e.expert_class is not None]
    n = len(labelled)
    criteria: dict[str, Any] = {}
    notes: list[str] = []
    ok = False
    try:
        if n < 3:
            raise ValueError("calibration needs at least 3 classified systems")
        calibration = calibrate_thresholds(
            [_ice(e) for e in labelled],
            [e.expert_class for e in labelled],  # type: ignore[misc]
        )
        criteria = {
            "thresholds": calibration.thresholds,
            "youden_low": calibration.youden_low,
            "youden_high": calibration.youden_high,
        }
        ok = calibration.accepted
        for label, j in (
            ("low", calibration.youden_low),
            ("high", calibration.youden_high),
        ):
            if j < MIN_YOUDEN:
                notes.append(f"Youden J of the {label} cut {j:.2f} < {MIN_YOUDEN}")
        if calibration.low >= calibration.high:
            notes.append("calibrated low cut is not below the high cut")
    except ValueError as error:
        notes.append(str(error))
    observed = [e for e in labelled if e.outage_hours is not None]
    if len(observed) >= 3:
        try:
            best, scores = select_alpha(
                [e.system for e in observed],
                [e.outage_hours for e in observed],  # type: ignore[misc]
            )
            criteria["alpha"] = best
            criteria["alpha_spearman"] = scores
        except ValueError as error:
            notes.append(f"α not estimated: {error}")
    if n < MIN_SAMPLE:
        notes.append(
            f"{n} systems classified by experts; at least {MIN_SAMPLE} required"
        )
    return PhaseResult(
        3, "Calibration", _status(n >= MIN_SAMPLE, ok), n, criteria, notes
    )


def _phase_prediction(
    entries: Sequence[SampleEntry], permutations: int, seed: int
) -> PhaseResult:
    observed = [e for e in entries if e.outage_hours is not None]
    n = len(observed)
    criteria: dict[str, Any] = {}
    notes: list[str] = []
    ok = False
    if n >= 3:
        try:
            risks = [
                risk.expected_risk(
                    e.system,
                    float(e.parameters.get("alpha", propagation.DEFAULT_ALPHA)),
                )
                for e in observed
            ]
            result = predictive_validity(
                risks,
                [e.outage_hours for e in observed],  # type: ignore[misc]
                permutations=permutations,
                seed=seed,
            )
            criteria = {"spearman": result.rho, "p_value": result.p_value}
            ok = result.accepted
            if not ok:
                notes.append(
                    f"E[R] does not predict outages (ρ_S {result.rho:+.2f},"
                    f" p {result.p_value:.3f})"
                )
        except ValueError as error:
            notes.append(str(error))
    if n < MIN_SAMPLE:
        notes.append(
            f"{n} systems with 12-month outage records; at least {MIN_SAMPLE} required"
        )
    return PhaseResult(
        4, "Prediction", _status(n >= MIN_SAMPLE, ok), n, criteria, notes
    )


def validate_sample(
    entries: Sequence[SampleEntry],
    *,
    sample: str = "sample",
    samples: int = 500,
    permutations: int = 10_000,
    seed: int = 42,
) -> ValidationReport:
    """Run the four phases on a sample. Systems are never mutated."""

    for entry in entries:
        entry.system.validate()
    return ValidationReport(
        sample=sample,
        n=len(entries),
        phases=[
            _phase_measurement(entries, samples, seed),
            _phase_validity(entries, permutations, seed),
            _phase_calibration(entries),
            _phase_prediction(entries, permutations, seed),
        ],
    )


__all__ = [
    "CLASS_ORDER",
    "FAIL",
    "INSUFFICIENT",
    "PASS",
    "SIGNAL_NAMES",
    "Interval",
    "ParameterUncertainty",
    "PhaseResult",
    "PredictiveValidity",
    "SampleEntry",
    "ThresholdCalibration",
    "ValidationReport",
    "calibrate_thresholds",
    "cronbach_alpha",
    "estimate_beta_cc",
    "kmo",
    "load_sample",
    "measured_components",
    "parameter_uncertainty",
    "permutation_p_value",
    "predictive_validity",
    "ranks",
    "redundant_pairs",
    "select_alpha",
    "signal_correlations",
    "spearman",
    "validate_sample",
    "youden_threshold",
]
