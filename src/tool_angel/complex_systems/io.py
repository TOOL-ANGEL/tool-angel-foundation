"""
AngelOS Complex Systems — declarative system files (CS-02).

A system is described in YAML (or an equivalent dict) and validated against
``schemas/ecosystem.schema.json``:

    system: Tienda online
    parameters: {theta: 0.05, alpha: 0.5}        # optional
    components:
      - {code: WEB, owner: Empresa, availability: 0.999}
      - {code: PAG, scope: external, owner: Pasarela,
         availability: 0.9995, control: 0.4, failure_rate: 2}
    dependencies:
      - [WEB, PAG, 8]                            # WEB depends on PAG, weight 8
    functions:
      - {name: Compra, weight: 0.55, path: [WEB, PAG, [IGA, OSM]]}

A nested list in a path is a redundant group. Actors are created from the
distinct ``owner`` names.
"""

from collections.abc import Mapping
from pathlib import Path
from typing import Any
from uuid import UUID

import yaml

from tool_angel.complex_systems.actor import Actor
from tool_angel.complex_systems.component import Component
from tool_angel.complex_systems.relationship import Relationship
from tool_angel.complex_systems.system import ComplexSystem
from tool_angel.complex_systems.value_function import PathElement, ValueFunction

DEFAULT_INTERNAL_OWNER = "Operador"


def system_from_dict(data: Mapping[str, Any]) -> tuple[ComplexSystem, dict[str, UUID]]:
    """
    Build a ComplexSystem from a declarative mapping.

    Returns the system and a map from component code to component id.
    """

    if "system" not in data or "components" not in data:
        raise ValueError("a system file needs 'system' and 'components'")

    system = ComplexSystem(
        name=str(data["system"]), description=str(data.get("description", ""))
    )
    actors: dict[str, Actor] = {}
    ids: dict[str, UUID] = {}

    def actor(name: str) -> Actor:
        if name not in actors:
            actors[name] = Actor.create(name)
            system.add_actor(actors[name])
        return actors[name]

    for item in data["components"]:
        code = str(item["code"])
        if code in ids:
            raise ValueError(f"duplicate component code {code!r}")
        scope = item.get("scope", "internal")
        owner = actor(
            str(
                item.get(
                    "owner", DEFAULT_INTERNAL_OWNER if scope == "internal" else code
                )
            )
        )
        component = Component.create(
            name=str(item.get("name", code)),
            type=str(item.get("type", "")),
            description=str(item.get("description", "")),
            metadata={"code": code},
            scope=scope,
            owner_id=owner.id,
            availability=float(item.get("availability", 1.0)),
            control=None if item.get("control") is None else float(item["control"]),
            failure_rate=float(item.get("failure_rate", 0.0)),
        )
        system.add_component(component)
        ids[code] = component.id

    def resolve(code: Any) -> UUID:
        if str(code) not in ids:
            raise ValueError(f"unknown component code {code!r}")
        return ids[str(code)]

    for edge in data.get("dependencies", []):
        if isinstance(edge, Mapping):
            source, target, weight = edge["from"], edge["to"], edge.get("weight", 1.0)
        else:
            source, target, *rest = edge
            weight = rest[0] if rest else 1.0
        system.add_relationship(
            Relationship.create(
                resolve(source), resolve(target), "depends_on", float(weight)
            )
        )

    for function in data.get("functions", []):
        path: list[PathElement] = [
            (
                tuple(resolve(c) for c in element)
                if isinstance(element, list)
                else resolve(element)
            )
            for element in function["path"]
        ]
        system.add_value_function(
            ValueFunction.create(str(function["name"]), float(function["weight"]), path)
        )

    system.validate()
    return system, ids


def load_system(
    path: str | Path,
) -> tuple[ComplexSystem, dict[str, UUID], dict[str, Any]]:
    """
    Load a system file. Returns the system, the code map and its parameters.
    """

    with open(path, encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, Mapping):
        raise TypeError(f"{path} does not contain a mapping")
    system, ids = system_from_dict(data)
    return system, ids, dict(data.get("parameters", {}))
