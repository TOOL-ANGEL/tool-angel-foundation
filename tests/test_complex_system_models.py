from uuid import uuid4

from tool_angel.complex_systems import (
    ComplexSystem,
    Component,
    Indicator,
    Relationship,
    SystemState,
)


def test_relationship_create():
    source_id = uuid4()
    target_id = uuid4()

    relationship = Relationship.create(
        source_id=source_id,
        target_id=target_id,
        relationship_type="depends_on",
        weight=0.8,
    )

    assert relationship.source_id == source_id
    assert relationship.target_id == target_id
    assert relationship.relationship_type == "depends_on"
    assert relationship.weight == 0.8


def test_state_create():
    state = SystemState.create(
        name="Operativo",
        value=1.0,
        metadata={"source": "test"},
    )

    assert state.name == "Operativo"
    assert state.value == 1.0
    assert state.metadata["source"] == "test"
    assert state.id is not None
    assert state.timestamp is not None


def test_indicator_create():
    indicator = Indicator.create(
        name="Índice de resiliencia",
        value=0.75,
        unit="index",
        description="Indicador de prueba",
        metadata={"source": "test"},
    )

    assert indicator.name == "Índice de resiliencia"
    assert indicator.value == 0.75
    assert indicator.unit == "index"
    assert indicator.description == "Indicador de prueba"
    assert indicator.metadata["source"] == "test"
    assert indicator.id is not None


def test_component_create():
    component = Component.create(
        name="Acueducto",
        type="infraestructura",
        description="Infraestructura histórica y territorial",
        metadata={
            "location": "Segovia",
            "role": "patrimonio",
        },
    )

    assert component.name == "Acueducto"
    assert component.type == "infraestructura"
    assert component.description == "Infraestructura histórica y territorial"
    assert component.metadata["location"] == "Segovia"
    assert component.metadata["role"] == "patrimonio"
    assert component.id is not None


def test_complex_system_with_models():
    system = ComplexSystem(
        name="Sistema Territorial de Segovia",
        description="Modelo inicial de sistema complejo territorial",
    )

    system.add_state(
        SystemState.create(
            name="Operativo",
            value=1.0,
        )
    )

    system.add_indicator(
        Indicator.create(
            name="Índice territorial",
            value=0.85,
            unit="index",
        )
    )

    summary = system.summary()

    assert summary["name"] == "Sistema Territorial de Segovia"
    assert summary["states"] == 1
    assert summary["indicators"] == 1
    assert summary["components"] == 0
    assert summary["relationships"] == 0


def test_complex_system_add_component():
    system = ComplexSystem(
        name="Sistema Territorial de Segovia",
        description="Modelo inicial de sistema complejo territorial",
    )

    component = Component.create(
        name="Acueducto",
        type="infraestructura",
    )

    system.add_component(component)

    assert len(system.components) == 1
    assert system.components[0] == component


def test_complex_system_add_relationship():
    system = ComplexSystem(
        name="Sistema Territorial de Segovia",
        description="Modelo inicial de sistema complejo territorial",
    )

    source_id = uuid4()
    target_id = uuid4()

    relationship = Relationship.create(
        source_id=source_id,
        target_id=target_id,
        relationship_type="depends_on",
        weight=0.8,
    )

    system.add_relationship(relationship)

    assert len(system.relationships) == 1
    assert system.relationships[0] == relationship


def test_complex_system_full_model():
    system = ComplexSystem(
        name="Sistema Territorial de Segovia",
        description="Modelo integrado de sistema complejo territorial",
    )

    component_a = Component.create(name="Acueducto", type="infraestructura")

    component_b = Component.create(name="Población", type="social")

    system.add_component(component_a)
    system.add_component(component_b)

    state = SystemState.create(
        name="Operativo",
        value=1.0,
    )

    indicator = Indicator.create(
        name="Índice de resiliencia territorial",
        value=0.85,
        unit="index",
    )

    system.add_state(state)
    system.add_indicator(indicator)

    relationship = Relationship.create(
        source_id=state.id,
        target_id=indicator.id,
        relationship_type="influences",
        weight=0.8,
    )

    system.add_relationship(relationship)

    summary = system.summary()

    assert summary["name"] == "Sistema Territorial de Segovia"
    assert summary["components"] == 2
    assert summary["states"] == 1
    assert summary["indicators"] == 1
    assert summary["relationships"] == 1


def test_complex_system_name_cannot_be_empty():
    import pytest

    with pytest.raises(ValueError):
        ComplexSystem(name="")
