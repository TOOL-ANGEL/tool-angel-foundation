"""
AngelOS Ecosystem Command (CS-02, CS-03).

Usage:
    python -m tool_angel.cli ecosystem analyze  <system.yaml> [theta=0.05] [alpha=0.5]
    python -m tool_angel.cli ecosystem measure  <system.yaml> [samples=1000] [seed=42]
    python -m tool_angel.cli ecosystem validate <sample.yaml> [permutations=10000] [seed=42]
"""

from tool_angel.commands.command import Command
from tool_angel.complex_systems.analysis import analyze, validation
from tool_angel.complex_systems.io import load_system

USAGE = (
    "Usage: ecosystem analyze <system.yaml> [theta=<float>] [alpha=<float>]\n"
    "       ecosystem measure <system.yaml> [samples=<int>] [seed=<int>]\n"
    "       ecosystem validate <sample.yaml> [permutations=<int>] [seed=<int>]"
)


def format_report(report, codes: dict) -> str:
    """Render an EcosystemReport as plain text."""

    names = {cid: code for code, cid in codes.items()}
    lines = [
        f"Ecosystem analysis — {report.system_name}",
        "",
        f"  ICE                 {report.ice:.3f}  ({report.classification})",
        f"  Openness Ω          {report.openness:.3f}",
        f"  Coordination τ      {report.coordination_cost:.3f}",
        f"  Ownership H_B       {report.ownership_entropy:.3f}",
        f"  Relational ρ_V      {report.relational_value:.3f}",
        f"  Control K           {report.effective_control:.3f}",
        (
            f"  Availability A_sys  {report.system_availability:.5f}"
            f"  ({report.downtime_hours_per_year:.1f} h/year)"
        ),
        f"  Composite           {'yes' if report.composite else 'no'}",
        f"  Expected risk E[R]  {report.expected_risk:.2f}",
        "",
        "  Provider ranking (risk, Δ_e, γ):",
    ]
    for row in report.provider_risks:
        lines.append(
            f"    {names.get(row.component_id, row.name):<8} {row.risk:6.2f}"
            f"   Δ={row.structural_impact:.4f}   γ={row.control:.2f}"
        )
    lines += [
        "",
        "  Ω, τ, ρ_V, K, E[R] and ICE are experimental operators (ADR-0002).",
    ]
    return "\n".join(lines)


def format_uncertainty(result: validation.ParameterUncertainty) -> str:
    """Render a phase-1 parameter uncertainty as plain text."""

    def row(label: str, interval: validation.Interval, digits: int) -> str:
        return (
            f"  {label:<20}{interval.mean:.{digits}f}"
            f"  [p5 {interval.p5:.{digits}f} – p95 {interval.p95:.{digits}f}]"
        )

    verdict = "PASS" if result.accepted else "FAIL"
    probabilities = "  ".join(f"{k} {v:.0%}" for k, v in result.probabilities.items())
    return "\n".join(
        [
            f"Measurement uncertainty (CS-03 phase 1) — {result.system_name}",
            "",
            f"  measured components {result.measured_components}",
            f"  Monte Carlo draws   {result.samples}",
            row("ICE", result.ice, 3),
            row("Availability A_sys", result.system_availability, 5),
            row("Expected risk E[R]", result.expected_risk, 2),
            f"  class probability   {probabilities}",
            "",
            (
                f"  ICE interval width  {result.ice.width:.3f}"
                f" (≤ {result.max_width}) → {verdict}"
            ),
        ]
    )


def _fmt(value) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    if isinstance(value, tuple):
        return "(" + ", ".join(_fmt(v) for v in value) + ")"
    if isinstance(value, dict):
        return "{" + ", ".join(f"{k}: {_fmt(v)}" for k, v in value.items()) + "}"
    if isinstance(value, list):
        return "[" + ", ".join(_fmt(v) for v in value) + "]"
    return str(value)


def format_validation(report: validation.ValidationReport) -> str:
    """Render the four-phase validation report as plain text."""

    lines = [
        f"Empirical validation (CS-03) — {report.sample}",
        f"  systems in sample   {report.n}",
        "",
    ]
    for phase in report.phases:
        lines.append(
            f"  {phase.phase}. {phase.name:<12} {phase.status.upper():<13} n={phase.n}"
        )
        for key, value in phase.criteria.items():
            lines.append(f"       {key:<22}{_fmt(value)}")
        for note in phase.notes:
            lines.append(f"       · {note}")
    lines += [
        "",
        "  Model status: "
        + (
            "VALIDATED on this sample"
            if report.validated
            else "experimental — the protocol is not complete (ADR-0003)"
        ),
    ]
    return "\n".join(lines)


class EcosystemCommand(Command):
    """
    Analyze a declarative system file with the ecosystem model.
    """

    name = "ecosystem"

    description = (
        "Analyze, measure or validate systems with the ecosystem model (CS-02/03)."
    )

    def execute(self, *args, **kwargs):
        if len(args) < 2 or args[0] not in {"analyze", "measure", "validate"}:
            return USAGE
        action, path = args[0], args[1]
        seed = int(kwargs.get("seed", 42))
        if action == "validate":
            name, entries = validation.load_sample(path)
            report = validation.validate_sample(
                entries,
                sample=name,
                permutations=int(kwargs.get("permutations", 10_000)),
                seed=seed,
            )
            return format_validation(report)
        system, codes, parameters = load_system(path)
        theta = float(kwargs.get("theta", parameters.get("theta", 0.05)))
        alpha = float(kwargs.get("alpha", parameters.get("alpha", 0.5)))
        if action == "measure":
            result = validation.parameter_uncertainty(
                system,
                samples=int(kwargs.get("samples", 1000)),
                seed=seed,
                theta=theta,
                alpha=alpha,
            )
            return format_uncertainty(result)
        return format_report(analyze(system, theta=theta, alpha=alpha), codes)
