"""
CS-02 Ecosystem Analysis Engine.

Pure functions that measure a ComplexSystem according to the mathematical
model of ecosystemic systems. See ADR-0002 and specs/ecosystem_analysis.spec.yaml.
"""

from tool_angel.complex_systems.analysis import risk, sensitivity
from tool_angel.complex_systems.analysis.index import (
    CLOSED,
    ECOSYSTEM,
    TRANSITION,
    EcosystemReport,
    Signals,
    analyze,
    classify,
    ice,
    signals,
)

__all__ = [
    "CLOSED",
    "ECOSYSTEM",
    "TRANSITION",
    "EcosystemReport",
    "Signals",
    "analyze",
    "classify",
    "ice",
    "risk",
    "sensitivity",
    "signals",
]
