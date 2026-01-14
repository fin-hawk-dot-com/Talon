import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models import Character, Essence, AwakeningStone, Ability
from src.mechanics import TrainingManager, RANKS

class TestTrainingLoop(unittest.TestCase):

    def setUp(self):
        self.character = Character(name="Test", race="Human")
        self.essence = Essence(name="Fire", type="Base", rarity="Common", tags=["Elemental"], description="...")
        self.stone = AwakeningStone(name="Attack Stone", function="Attack", description="...")
        self.character.add_essence(self.essence, "Power")
        self.ability = Ability(
            name="Fireball",
            description="Throws a ball of fire.",
            rank="Iron",
            level=0,
            parent_essence=self.essence,
            parent_stone=self.stone
        )
        self.character.abilities[self.essence.name][0] = self.ability
        self.tm = TrainingManager()

    def test_ability_xp_and_level_up(self):
        # Initial state
        self.assertEqual(self.ability.level, 0)
        self.assertEqual(self.ability.xp, 0)

        # Practice once
        leveled_up = self.tm.practice_ability(self.character, self.essence.name, 0)
        self.assertFalse(leveled_up)
        self.assertEqual(self.ability.xp, 10.0)

        # Practice 8 more times (total 9) - should not level up yet
        for _ in range(8):
            leveled_up = self.tm.practice_ability(self.character, self.essence.name, 0)
            self.assertFalse(leveled_up)

        self.assertEqual(self.ability.xp, 90.0)
        self.assertEqual(self.ability.level, 0)

        # 10th practice should trigger level up
        leveled_up = self.tm.practice_ability(self.character, self.essence.name, 0)
        self.assertTrue(leveled_up)
        self.assertEqual(self.ability.level, 1)
        self.assertEqual(self.ability.xp, 0)

    def test_ability_rank_up(self):
        # Set ability to level 9
        self.ability.level = 9

        # Character rank needs to be higher than ability rank
        # Let's make the character Bronze
        for attr in self.character.attributes.values():
            attr.value = 100.0
        self.assertEqual(self.character.rank, "Bronze")
        self.assertEqual(self.ability.rank, "Iron")

        # Attempt rank up
        result = self.tm.attempt_rank_up_ability(self.character, self.essence.name, 0)

        self.assertIn("Success", result)
        self.assertEqual(self.ability.rank, "Bronze")
        self.assertEqual(self.ability.level, 0)
        self.assertEqual(self.ability.xp, 0)

    def test_ability_rank_up_fail_if_char_rank_too_low(self):
        self.ability.level = 9
        self.assertEqual(self.character.rank, "Iron") # Char rank is Iron
        self.assertEqual(self.ability.rank, "Iron")   # Ability rank is Iron

        result = self.tm.attempt_rank_up_ability(self.character, self.essence.name, 0)

        self.assertNotIn("Success", result)
        self.assertIn("not high enough", result)
        self.assertEqual(self.ability.rank, "Iron") # Should not have changed

if __name__ == '__main__':
    unittest.main()
