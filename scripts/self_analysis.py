"""
TOOL-ANGEL self-analysis with its own ecosystem model (CS-02).

Each sub-package or top-level module of ``src/tool_angel`` is a component;
every third-party import is an external component; every import between them
is a dependency. The script prints the structural indicators. With
``--fail-on-cycles`` it exits with code 1 when the internal dependency graph has
cycles; with ``--strict-instability X`` it also fails when the core packages
(model, complex_systems) exceed instability X.

Usage:
    python scripts/self_analysis.py [--fail-on-cycles] [--strict-instability 0.8]
"""

import argparse
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
PACKAGE = SRC / "tool_angel"
sys.path.insert(0, str(SRC))

from tool_angel.complex_systems import (
    Actor,
    ComplexSystem,
    Component,
    Relationship,
)
from tool_angel.complex_systems.analysis import propagation, structure

STDLIB = set(sys.stdlib_module_names)


def unit_of(path: Path) -> str:
    """Component name: first level under tool_angel (package or module)."""

    relative = path.relative_to(PACKAGE)
    return relative.parts[0].removesuffix(".py")


def imports_of(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            found.add(node.module)
    return found


def build_system() -> ComplexSystem:
    edges: dict[tuple[str, str], int] = {}
    units: set[str] = set()
    externals: set[str] = set()
    for path in PACKAGE.rglob("*.py"):
        source = unit_of(path)
        if source == "__init__":
            continue
        units.add(source)
        for name in imports_of(path):
            top = name.split(".")[0]
            if top == "tool_angel":
                parts = name.split(".")
                if len(parts) < 2:
                    continue
                target = parts[1]
            elif top in STDLIB or top == "__future__":
                continue
            else:
                target = f"ext:{top}"
                externals.add(target)
            if target != source:
                edges[(source, target)] = edges.get((source, target), 0) + 1

    system = ComplexSystem("TOOL-ANGEL foundation")
    foundation = Actor.create("TOOL-ANGEL Foundation")
    system.add_actor(foundation)
    ids = {}
    for unit in sorted(units):
        component = Component.create(unit, owner_id=foundation.id)
        system.add_component(component)
        ids[unit] = component.id
    for unit in sorted(externals):
        owner = Actor.create(unit.removeprefix("ext:"))
        system.add_actor(owner)
        component = Component.create(unit, scope="external", owner_id=owner.id)
        system.add_component(component)
        ids[unit] = component.id
    for (source, target), count in sorted(edges.items()):
        if target in ids:
            system.add_relationship(
                Relationship.create(
                    ids[source], ids[target], "depends_on", float(count)
                )
            )
    return system


def cycle_edges(system: ComplexSystem) -> list[tuple[str, str]]:
    """Pairs of components that depend on each other directly."""

    names = {c.id: c.name for c in system.components}
    pairs = {(r.source_id, r.target_id) for r in system.dependencies()}
    return sorted(
        {tuple(sorted((names[a], names[b]))) for a, b in pairs if (b, a) in pairs}
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--fail-on-cycles", action="store_true")
    parser.add_argument("--strict-instability", type=float, default=None)
    options = parser.parse_args()

    system = build_system()
    system.validate()
    names = {c.id: c.name for c in system.components}
    reach = propagation.reach(system)
    instability = propagation.instability(system)
    cyclic = propagation.has_cycles(system)

    print("TOOL-ANGEL self-analysis (CS-02)")
    print(
        f"  components        {len(system.components)}"
        f" ({len(system.external_components())} external)"
    )
    print(f"  dependencies      {len(system.dependencies())}")
    print(f"  openness Ω        {structure.openness(system):.3f}")
    print(f"  ownership H_B     {structure.ownership_entropy(system):.3f}")
    print(f"  cycles            {'YES' if cyclic else 'no'}")
    if cyclic:
        for source, target in cycle_edges(system):
            print(f"  cycle edge        {source} <-> {target}")
    print("  component           reach  instability")
    for cid in sorted(reach, key=lambda c: (-reach[c], names[c])):
        print(f"    {names[cid]:<18} {reach[cid]:>5}  {instability[cid]:>11.2f}")

    failures = []
    if cyclic and options.fail_on_cycles:
        failures.append("the internal dependency graph has cycles")
    if options.strict_instability is not None:
        core = [c for c in system.components if c.name in {"model", "complex_systems"}]
        for component in core:
            if instability[component.id] > options.strict_instability:
                failures.append(
                    f"{component.name} instability {instability[component.id]:.2f}"
                    f" exceeds {options.strict_instability}"
                )
    for failure in failures:
        print(f"FAIL: {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
