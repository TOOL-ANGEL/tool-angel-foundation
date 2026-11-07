"""
Self-analysis gate (CS-02 applied to TOOL-ANGEL itself).

The internal dependency graph must stay acyclic and the core packages must
stay stable. These checks back the CI step `scripts/self_analysis.py
--fail-on-cycles --strict-instability 0.8`.
"""

import importlib.util
from pathlib import Path

import pytest

from tool_angel.complex_systems.analysis import propagation

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "self_analysis.py"


@pytest.fixture(scope="module")
def self_analysis():
    spec = importlib.util.spec_from_file_location("self_analysis", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def system(self_analysis):
    built = self_analysis.build_system()
    built.validate()
    return built


def test_dependency_graph_is_acyclic(system, self_analysis):
    assert self_analysis.cycle_edges(system) == []
    assert not propagation.has_cycles(system)


def test_commands_package_does_not_import_concrete_commands(system):
    names = {c.id: c.name for c in system.components}
    edges = {(names[r.source_id], names[r.target_id]) for r in system.dependencies()}
    assert ("commands", "builtin_commands") not in edges


@pytest.mark.parametrize("core", ["model", "complex_systems"])
def test_core_instability_below_threshold(system, core):
    instability = propagation.instability(system)
    component = next(c for c in system.components if c.name == core)
    assert instability[component.id] <= 0.8


def test_gate_exits_zero(self_analysis, monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        ["self_analysis.py", "--fail-on-cycles", "--strict-instability", "0.8"],
    )
    assert self_analysis.main() == 0
