"""
AngelOS Ecosystem Command (CS-02).

Usage:
    python -m tool_angel.cli ecosystem analyze <system.yaml> [theta=0.05] [alpha=0.5]
"""

from tool_angel.commands.command import Command
from tool_angel.complex_systems.analysis import analyze
from tool_angel.complex_systems.io import load_system

USAGE = "Usage: ecosystem analyze <system.yaml> [theta=<float>] [alpha=<float>]"


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


class EcosystemCommand(Command):
    """
    Analyze a declarative system file with the ecosystem model.
    """

    name = "ecosystem"

    description = "Analyze a system file with the ecosystem model (CS-02)."

    def execute(self, *args, **kwargs):
        if len(args) < 2 or args[0] != "analyze":
            return USAGE
        system, codes, parameters = load_system(args[1])
        theta = float(kwargs.get("theta", parameters.get("theta", 0.05)))
        alpha = float(kwargs.get("alpha", parameters.get("alpha", 0.5)))
        return format_report(analyze(system, theta=theta, alpha=alpha), codes)
