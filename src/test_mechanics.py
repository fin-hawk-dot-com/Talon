import sys
import os
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.game_engine import GameEngine
from src.models import Essence, AwakeningStone, Ability, RANK_INDICES, RANKS

def test_attribute_training():
    engine = GameEngine()
    char = engine.create_character("Trainee", "Human")

    # Give XP
    char.current_xp = 1000

    # Train Power (Normal Rank 10.0 -> Cost 100)
    # 10.0 is Normal Rank (0-99). Rank Index 0.
    # Cost: 100 * (0 + 1) = 100.

    initial_val = char.attributes["Power"].value
    initial_xp = char.current_xp

    msg = engine.train_attribute("Power")

    assert char.current_xp == initial_xp - 100
    assert char.attributes["Power"].value > initial_val
    # Narrative might be flavor text, just check for successful execution via stats or generic success indicator
    # The message '[XP -100] ...' indicates success
    assert "[XP -100]" in msg

def test_ability_practice():
    engine = GameEngine()
    char = engine.create_character("Student", "Human")

    # Setup Ability manually
    essence = Essence("TestEssence", "Base", "Common", [], "Desc")
    stone = AwakeningStone("TestStone", "Attack", "Desc")

    # Add Essence to char so we can add ability
    char.add_essence(essence, "Power")

    # Create Ability
    ability = Ability("TestMove", "Desc", "Iron", 0, essence, stone)
    char.abilities[essence.name][0] = ability

    # Practice
    # Max XP for Iron 0 is 100 * (0+1) * (1+1) = 200.
    # Gain is 10.

    res = engine.practice_ability(essence.name, 0)

    assert ability.xp == 10.0
    assert "Practiced" in res
    assert "Level Up" not in res

    # Force Level Up
    ability.xp = 195.0
    res = engine.practice_ability(essence.name, 0)

    assert ability.level == 1
    assert ability.xp == 5.0 # 205 - 200 = 5
    assert "Level Up" in res

def test_ability_rank_up():
    engine = GameEngine()
    char = engine.create_character("Master", "Human")

    # Setup Ability
    essence = Essence("TestEssence", "Base", "Common", [], "Desc")
    stone = AwakeningStone("TestStone", "Attack", "Desc")
    char.add_essence(essence, "Power")

    ability = Ability("TestMove", "Desc", "Iron", 9, essence, stone)
    ability.xp = 0 # XP doesn't matter for rank up check in current impl, just level 9

    char.abilities[essence.name][0] = ability

    # Case 1: Character is Normal (default attributes 10.0)
    # Character Rank Index = 0. Ability Rank Index (Iron) = 1.
    # Condition in training_mgr: if current_rank_idx >= char_rank_idx: return "not high enough"
    # 1 >= 0 -> True.

    res = engine.rank_up_ability(essence.name, 0)
    assert "not high enough" in res

    # Boost Character to Bronze (200)
    for attr in char.attributes.values():
        attr.value = 200.0

    assert char.rank == "Bronze" # Index 2

    # Ability is Iron (Index 1).
    # 1 >= 2 False.
    # So it should succeed.

    res = engine.rank_up_ability(essence.name, 0)

    assert "Success" in res
    assert ability.rank == "Bronze"
    assert ability.level == 0
    assert ability.xp == 0
