
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models import Essence, AwakeningStone, Character, Ability
from src.mechanics import GameEngine, CombatManager

def test_combat_abilities():
    print("Testing Combat Ability Integration...")
    engine = GameEngine()

    # Create Character
    char = engine.create_character("TestChar", "Human")

    # Init stats
    char.attributes["Spirit"].value = 50.0 # 500 Mana
    char.attributes["Power"].value = 20.0
    char.attributes["Recovery"].value = 20.0 # 200 Stamina
    # Force reset stats since __post_init__ only fixes negative values
    char.current_health = char.max_health
    char.current_mana = char.max_mana
    char.current_stamina = char.max_stamina

    print(f"Stats: HP {char.current_health}/{char.max_health}, Mana {char.current_mana}/{char.max_mana}")

    # Create Mock Essence & Stone
    essence = Essence(name="Fire", type="Base", rarity="Common", tags=["Fire"], description="Fire stuff")
    stone = AwakeningStone(name="Stone of Blast", function="Ranged Attack", description="Blast", rarity="Common", cost_type="Mana", cooldown="Low")

    # Generate Ability
    ability = engine.ability_gen.generate(essence, stone, "Iron", "Mage")
    ability.cost = 20

    print(f"Generated Ability: {ability.name} (Cost: {ability.cost} {stone.cost_type})")

    # Create Enemy
    enemy = Character("Dummy", "Monster")
    enemy.attributes["Recovery"].value = 10.0 # 100 HP
    enemy.__post_init__()

    print(f"Enemy HP: {enemy.current_health}")

    # Execute Ability
    print("Executing Ability...")
    log = engine.combat_mgr.execute_ability(char, enemy, ability)
    for l in log:
        print(l)

    print(f"Enemy HP after: {enemy.current_health}")
    print(f"Char Mana after: {char.current_mana}")

    if enemy.current_health < 100:
        print("PASS: Damage dealt")
    else:
        print("FAIL: No damage dealt")

    if char.current_mana == 480: # 500 - 20
        print("PASS: Mana consumed")
    else:
        print(f"FAIL: Mana not consumed correctly (Expected 480, got {char.current_mana})")

    # Test Insufficient Mana
    char.current_mana = 10
    # Reset cooldown manually for this test because execute_ability sets it
    ability.current_cooldown = 0
    print("Testing Insufficient Mana...")
    log = engine.combat_mgr.execute_ability(char, enemy, ability)
    print(log[0])
    if "Not enough" in log[0]:
        print("PASS: Insufficient resource check")
    else:
        print("FAIL: Allowed usage without mana")

if __name__ == "__main__":
    test_combat_abilities()
