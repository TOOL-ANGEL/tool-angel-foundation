"""
Shared fixtures: the two case studies of the ecosystem model.

Values are the illustrative assumptions of Parts II and III of
"Modelo Matemático de Sistemas Ecosistémicos" (2026), not measurements.
"""

import pytest

from tool_angel.complex_systems import (
    Actor,
    ComplexSystem,
    Component,
    Relationship,
    ValueFunction,
)


def build_system(name, internal, external, edges, functions):
    """
    internal: {code: availability}
    external: {code: (owner_name, availability, control, failure_rate)}
    edges:    [(source_code, target_code, weight)]
    functions:[(name, weight, [code | (code, code, ...)])]
    """

    system = ComplexSystem(name=name)
    operator = Actor.create("Operador")
    system.add_actor(operator)
    ids = {}

    for code, availability in internal.items():
        component = Component.create(
            code, owner_id=operator.id, availability=availability
        )
        system.add_component(component)
        ids[code] = component.id

    for code, (owner_name, availability, control, failure_rate) in external.items():
        owner = Actor.create(owner_name)
        system.add_actor(owner)
        component = Component.create(
            code,
            scope="external",
            owner_id=owner.id,
            availability=availability,
            control=control,
            failure_rate=failure_rate,
        )
        system.add_component(component)
        ids[code] = component.id

    for source, target, weight in edges:
        system.add_relationship(
            Relationship.create(ids[source], ids[target], "depends_on", weight)
        )

    for fname, weight, path in functions:
        resolved = [
            (
                tuple(ids[c] for c in element)
                if isinstance(element, tuple)
                else ids[element]
            )
            for element in path
        ]
        system.add_value_function(ValueFunction.create(fname, weight, resolved))

    return system, ids


@pytest.fixture
def online_store():
    return build_system(
        "Tienda online",
        internal={"WEB": 0.999, "BD": 0.999, "ADM": 0.99, "APP": 0.999, "REC": 0.998},
        external={
            "PAG": ("Pasarela", 0.9995, 0.4, 2),
            "AUT": ("Identidad", 0.999, 0.2, 3),
            "LOG": ("Logística", 0.998, 0.5, 4),
            "MKT": ("Marketing", 0.997, 0.3, 2),
            "ANA": ("Analítica", 0.997, 0.2, 3),
            "CLD": ("Nube", 0.9999, 0.3, 1),
            "BOT": ("Chatbot", 0.995, 0.3, 4),
            "CRM": ("Atención", 0.998, 0.4, 2),
        },
        edges=[
            ("WEB", "BD", 10),
            ("WEB", "AUT", 6),
            ("WEB", "PAG", 8),
            ("WEB", "REC", 4),
            ("WEB", "ANA", 3),
            ("WEB", "CLD", 10),
            ("WEB", "LOG", 5),
            ("WEB", "MKT", 2),
            ("WEB", "BOT", 2),
            ("APP", "WEB", 8),
            ("APP", "AUT", 5),
            ("APP", "PAG", 6),
            ("BD", "CLD", 10),
            ("REC", "BD", 5),
            ("REC", "ANA", 3),
            ("ADM", "BD", 4),
            ("MKT", "BD", 3),
            ("BOT", "CRM", 4),
            ("CRM", "BD", 4),
        ],
        functions=[
            ("Compra", 0.55, ["WEB", "BD", "CLD", "AUT", "PAG"]),
            ("Envío", 0.20, ["WEB", "BD", "CLD", "LOG"]),
            ("Atención", 0.10, ["BOT", "CRM", "BD", "CLD"]),
            ("Marketing", 0.08, ["MKT", "BD", "CLD"]),
            ("Recomendación", 0.07, ["REC", "ANA", "BD", "CLD"]),
        ],
    )


@pytest.fixture
def piit_segovia():
    return build_system(
        "Plataforma municipal PIIT",
        internal={
            "POR": 0.995,
            "GEO": 0.99,
            "PGS": 0.995,
            "CON": 0.995,
            "TAB": 0.995,
            "ETL": 0.99,
        },
        external={
            "HOS": ("Hosting", 0.999, 0.5, 1),
            "SEC": ("Colombia Compra Eficiente", 0.98, 0.05, 4),
            "DAT": ("MinTIC", 0.98, 0.05, 3),
            "IGA": ("IGAC", 0.98, 0.05, 3),
            "OSM": ("OSM", 0.995, 0.0, 1),
            "EDU": ("EDURSEG", 0.95, 0.6, 6),
            "AAS": ("AASSA", 0.95, 0.5, 6),
        },
        edges=[
            ("POR", "GEO", 8),
            ("POR", "CON", 6),
            ("POR", "TAB", 5),
            ("POR", "HOS", 10),
            ("GEO", "PGS", 10),
            ("GEO", "IGA", 5),
            ("GEO", "OSM", 4),
            ("GEO", "HOS", 10),
            ("PGS", "HOS", 10),
            ("CON", "PGS", 6),
            ("TAB", "PGS", 6),
            ("ETL", "PGS", 8),
            ("ETL", "SEC", 6),
            ("ETL", "EDU", 5),
            ("ETL", "AAS", 5),
            ("ETL", "DAT", 3),
            ("ETL", "HOS", 6),
        ],
        functions=[
            ("Visor geográfico", 0.35, ["POR", "GEO", "PGS", "HOS", ("IGA", "OSM")]),
            (
                "Seguimiento contractual",
                0.30,
                ["POR", "CON", "PGS", "HOS", "ETL", "SEC", "EDU"],
            ),
            (
                "Indicadores de servicios públicos",
                0.20,
                ["TAB", "PGS", "HOS", "ETL", "AAS"],
            ),
            ("Publicación de datos abiertos", 0.15, ["ETL", "PGS", "HOS", "DAT"]),
        ],
    )
