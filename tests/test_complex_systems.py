from uuid import UUID

from tool_angel.complex_systems import ComplexSystem, Component, Relationship
from tool_angel.model.entity import Entity


def test_entity_creation():
    entity = Entity.create(
        name="Municipio de Segovia",
        description="Sistema territorial",
    )

    assert isinstance(entity.id, UUID)
    assert entity.name == "Municipio de Segovia"


def test_relationship_creation():
    source = Entity.create("Segovia")
    target = Entity.create("Infraestructura")

    relationship = Relationship.create(
        source_id=source.id,
        target_id=target.id,
        relationship_type="depends_on",
        weight=0.8,
    )

    assert isinstance(relationship.id, UUID)
    assert relationship.source_id == source.id
    assert relationship.target_id == target.id
    assert relationship.relationship_type == "depends_on"
    assert relationship.weight == 0.8


def test_complex_system():
    system = ComplexSystem(
        name="Sistema Territorial de Segovia",
        description="Modelo inicial de sistema complejo territorial",
    )

    municipality = Component.create("Segovia")
    infrastructure = Component.create("Infraestructura")

    relationship = Relationship.create(
        source_id=municipality.id,
        target_id=infrastructure.id,
        relationship_type="depends_on",
        weight=0.9,
    )

    system.add_component(municipality)
    system.add_component(infrastructure)
    system.add_relationship(relationship)

    summary = system.summary()

    assert summary["name"] == "Sistema Territorial de Segovia"
    assert summary["components"] == 2
    assert summary["relationships"] == 1
    assert summary["states"] == 0
    assert summary["indicators"] == 0
