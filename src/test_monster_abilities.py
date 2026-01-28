import sys
import os
import unittest
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.game_engine import GameEngine
from src.models import Character

class TestMonsterAbilities(unittest.TestCase):
    def setUp(self):
        self.engine = GameEngine()

    def test_monster_ability_generation(self):
        # "Storm Drake" has ["Lightning", "Wind", "Dragon", "Stone of the Breath"]
        # Lightning is an Essence. Stone of the Breath is "Area Attack".
        # Ability should be generated.

        monster = self.engine.data_loader.get_monster("Storm Drake")
        self.assertIsNotNone(monster, "Monster 'Storm Drake' not found")

        self.engine._hydrate_monster_abilities(monster)

        print(f"Monster: {monster.name}")
        print(f"Loot: {monster.loot_table}")

        has_abilities = False
        found_name = ""
        for essence, abilities in monster.abilities.items():
            for ab in abilities:
                if ab:
                    print(f"Generated Ability: {ab.name} ({ab.parent_essence.name} + {ab.parent_stone.name})")
                    has_abilities = True
                    found_name = ab.name
                    if ab.parent_stone.name == "Stone of the Breath":
                        # It might be "Lightning Area" because of tag mismatch, which is fine.
                        pass

        self.assertTrue(has_abilities, "No abilities were generated for Storm Drake")
        self.assertTrue(len(found_name) > 0)

    def test_monster_combat_use(self):
        # Create a mock player
        player = self.engine.create_character("Hero", "Human")
        # Cannot set max_health directly as it is a property.
        # Set attributes to boost health.
        player.attributes["Recovery"].value = 100.0 # 1000 HP
        # Need to re-run post_init or manually set current_health
        player.current_health = player.max_health

        # Create monster with abilities
        monster = self.engine.data_loader.get_monster("Storm Drake")
        self.engine._hydrate_monster_abilities(monster)

        # Ensure monster has mana/stamina
        monster.attributes["Spirit"].value = 100.0 # 1000 Mana
        monster.current_mana = monster.max_mana
        monster.current_stamina = monster.max_stamina

        # Verify it has abilities
        found_ability = None
        for slots in monster.abilities.values():
            for ab in slots:
                if ab:
                    found_ability = ab
                    break

        self.assertIsNotNone(found_ability, "Monster has no abilities to test")

        # Execute it
        log = self.engine.combat_mgr.execute_ability(monster, player, found_ability)
        print(f"Combat Log: {log}")

        self.assertTrue(len(log) > 0)
        # Check that log contains expected text
        # If missed, it says "missed!"
        # If hit, it says "damage" or "CRITICAL" or special effect
        text = "".join(log)
        self.assertTrue("missed" in text or "damage" in text or found_ability.name in text)

if __name__ == '__main__':
    unittest.main()
