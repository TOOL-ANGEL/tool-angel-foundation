"""
Edge cases found in the CS-02 code review.

Each test pins down an input that used to produce a wrong number, a crash or a
silent misreading.
"""

import pytest

from tool_angel.builtin_commands.ecosystem import EcosystemCommand
from tool_angel.complex_systems import (
    ComplexSystem,
    Component,
    Relationship,
    ValueFunction,
)
from tool_angel.complex_systems.analysis import analyze, risk, sensitivity, signals
from tool_angel.complex_systems.analysis import reliability
from tool_angel.complex_systems.io import load_system, schema_errors


def _system_without_functions() -> ComplexSystem:
    system = ComplexSystem("S")
    a = Component.create("A")
    b = Component.create("B", scope="external", availability=0.99)
    system.add_component(a)
    system.add_component(b)
    system.add_relationship(Relationship.create(a.id, b.id, "depends_on"))
    return system


# --------------------------------------------------------------------------
# 1. No value functions: availability is undefined, not zero
# --------------------------------------------------------------------------


def test_analysis_without_value_functions_is_rejected():
    system = _system_without_functions()
    system.validate()  # structurally valid: self_analysis relies on this
    with pytest.raises(ValueError, match="value function"):
        reliability.system_availability(system)
    with pytest.raises(ValueError, match="value function"):
        analyze(system)


# --------------------------------------------------------------------------
# 2. Redundant group with a perfectly available member
# --------------------------------------------------------------------------


def test_redundancy_penalty_with_perfect_member_does_not_divide_by_zero():
    system = ComplexSystem("S")
    a = Component.create("A", scope="external", availability=1.0)
    b = Component.create("B", scope="external", availability=0.99)
    system.add_component(a)
    system.add_component(b)
    system.add_value_function(ValueFunction.create("F", 1.0, [(a.id, b.id)]))

    assert sensitivity.redundancy_penalty(system, 0.1) == {"A ∥ B": 1.0}


# --------------------------------------------------------------------------
# 4. parameters: null in a system file
# --------------------------------------------------------------------------


MINIMAL = """\
system: S
parameters: {parameters}
components:
  - {{code: A}}
  - {{code: B, scope: external, availability: 0.99, control: 0.2, failure_rate: 1}}
dependencies:
  - [A, B, 2]
functions:
  - {{name: F, weight: 1.0, path: [A, B]}}
"""


def test_null_parameters_are_treated_as_empty(tmp_path):
    path = tmp_path / "s.yaml"
    path.write_text(MINIMAL.format(parameters="null"), encoding="utf-8")
    _, codes, parameters = load_system(path)
    assert parameters == {}
    assert set(codes) == {"A", "B"}


# --------------------------------------------------------------------------
# 5. Repeated component in a critical path
# --------------------------------------------------------------------------


def test_value_function_rejects_repeated_components():
    a, b = Component.create("A"), Component.create("B")
    with pytest.raises(ValueError, match="only once"):
        ValueFunction.create("F", 1.0, [a.id, a.id])
    with pytest.raises(ValueError, match="only once"):
        ValueFunction.create("F", 1.0, [a.id, (a.id, b.id)])


# --------------------------------------------------------------------------
# 6. JSON schema is enforced on files
# --------------------------------------------------------------------------


def test_schema_rejects_unknown_fields(tmp_path):
    pytest.importorskip("jsonschema")
    path = tmp_path / "s.yaml"
    text = MINIMAL.format(parameters="{theta: 0.05}").replace(
        "{code: A}", "{code: A, availabilty: 0.9}"
    )
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError, match="schema"):
        load_system(path)


def test_schema_rejects_non_string_codes():
    """YAML reads NO as False; the schema catches it before it becomes 'False'."""

    pytest.importorskip("jsonschema")
    errors = schema_errors({"system": "S", "components": [{"code": False}]})
    assert errors and "code" in errors[0]


# --------------------------------------------------------------------------
# 7. Duplicate and self dependencies
# --------------------------------------------------------------------------


def test_validate_rejects_duplicate_and_self_dependencies():
    system = ComplexSystem("S")
    a, b = Component.create("A"), Component.create("B")
    system.add_component(a)
    system.add_component(b)
    system.add_relationship(Relationship.create(a.id, b.id, "depends_on", 2))
    system.add_relationship(Relationship.create(a.id, b.id, "depends_on", 3))
    system.add_relationship(Relationship.create(b.id, b.id, "depends_on"))

    errors = system.validation_errors()
    assert any("duplicate dependency" in e for e in errors)
    assert any("depend on itself" in e for e in errors)


# --------------------------------------------------------------------------
# 9. Public operators validate their input
# --------------------------------------------------------------------------


def test_public_operators_report_invalid_systems_clearly():
    system = ComplexSystem("S")
    a = Component.create("A")
    system.add_component(a)
    system.add_relationship(
        Relationship.create(a.id, Component.create("ghost").id, "depends_on")
    )
    system.add_value_function(ValueFunction.create("F", 1.0, [a.id]))

    for operator in (signals, risk.provider_risks, risk.expected_risk):
        with pytest.raises(ValueError, match="unknown component"):
            operator(system)


# --------------------------------------------------------------------------
# 11. CLI errors are messages, not tracebacks
# --------------------------------------------------------------------------


def test_cli_reports_missing_file_and_unknown_options(tmp_path):
    command = EcosystemCommand()

    missing = command.execute("analyze", str(tmp_path / "nope.yaml"))
    assert missing.startswith("Error: file not found")

    path = tmp_path / "s.yaml"
    path.write_text(MINIMAL.format(parameters="{}"), encoding="utf-8")
    typo = command.execute("analyze", str(path), teta="0.1")
    assert typo.startswith("Error: unknown option(s) teta")

    bad_value = command.execute("analyze", str(path), theta="abc")
    assert bad_value.startswith("Error:")

    broken = tmp_path / "broken.yaml"
    broken.write_text("system: [unclosed", encoding="utf-8")
    assert command.execute("analyze", str(broken)).startswith("Error: invalid YAML")
