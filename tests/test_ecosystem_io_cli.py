"""
System files, CLI command and self-analysis (REQ-ECO-080..084).
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from tool_angel.builtin_commands.ecosystem import USAGE, EcosystemCommand
from tool_angel.complex_systems.analysis import ECOSYSTEM, TRANSITION, analyze
from tool_angel.complex_systems.io import load_system, system_from_dict
from tool_angel.runtime.engine import RuntimeEngine

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


@pytest.mark.parametrize(
    ("file", "ice", "classification"),
    [
        ("tienda_online.yaml", 0.678599, ECOSYSTEM),
        ("piit_segovia.yaml", 0.543210, TRANSITION),
    ],
)
def test_example_files_reproduce_golden_results(file, ice, classification):
    system, codes, parameters = load_system(EXAMPLES / file)
    report = analyze(system, **parameters)
    assert report.ice == pytest.approx(ice, abs=1e-4)
    assert report.classification == classification
    assert set(parameters) == {"theta", "alpha"}
    assert len(codes) == len(system.components)


def test_example_files_follow_the_schema():
    schema = json.loads((ROOT / "schemas" / "ecosystem.schema.json").read_text())
    allowed = set(schema["properties"])
    component_keys = set(schema["properties"]["components"]["items"]["properties"])
    for path in EXAMPLES.glob("*.yaml"):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert set(data) <= allowed
        assert all(set(c) <= component_keys for c in data["components"])


def test_dict_loader_accepts_mapping_edges_and_rejects_unknown_codes():
    base = {
        "system": "S",
        "components": [
            {"code": "A"},
            {"code": "B", "scope": "external", "control": 0.5},
        ],
        "functions": [{"name": "F", "weight": 1.0, "path": ["A", "B"]}],
    }
    system, codes = system_from_dict(
        {**base, "dependencies": [{"from": "A", "to": "B"}]}
    )
    assert system.dependencies()[0].target_id == codes["B"]

    with pytest.raises(ValueError):
        system_from_dict({**base, "dependencies": [["A", "Z", 1]]})
    with pytest.raises(ValueError):
        system_from_dict({"system": "S", "components": [{"code": "A"}, {"code": "A"}]})


def test_ecosystem_command_is_registered_and_reports():
    engine = RuntimeEngine()
    engine.load_commands()
    assert "ecosystem" in engine.command_registry.list()

    output = engine.execute_command(
        "ecosystem", "analyze", str(EXAMPLES / "piit_segovia.yaml")
    )
    assert "ICE                 0.543  (transition)" in output
    assert "Expected risk E[R]  6.19" in output
    assert output.index("HOS") < output.index("SEC")


def test_ecosystem_command_options_and_usage():
    command = EcosystemCommand()
    assert command.execute() == USAGE
    output = command.execute(
        "analyze", str(EXAMPLES / "tienda_online.yaml"), theta="0.10"
    )
    assert "ICE                 0.579  (transition)" in output


def test_self_analysis_runs_and_detects_cycles():
    script = ROOT / "scripts" / "self_analysis.py"
    report = subprocess.run(
        [sys.executable, str(script)], capture_output=True, text=True, check=False
    )
    assert report.returncode == 0
    assert "TOOL-ANGEL self-analysis" in report.stdout

    strict = subprocess.run(
        [sys.executable, str(script), "--fail-on-cycles"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert strict.returncode == (1 if "cycles            YES" in report.stdout else 0)
