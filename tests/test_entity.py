import unittest

from tool_angel.model.entity import Entity


class TestEntity(unittest.TestCase):

    def test_create_entity(self):

        entity = Entity(
            id="123e4567-e89b-12d3-a456-426614174000",
            name="Golden Component"
        )

        self.assertEqual(
            entity.name,
            "Golden Component"
        )

    def test_change_name(self):

        entity = Entity(
            id="123e4567-e89b-12d3-a456-426614174000",
            name="Old"
        )

        entity.update_name("New")

        self.assertEqual(
            entity.name,
            "New"
        )


if __name__ == "__main__":
    unittest.main()
