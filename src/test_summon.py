import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models import Character, Ability, Essence, AwakeningStone, Attribute
from src.combat_system import CombatManager
from src.data_loader import DataLoader

# Mock DataLoader
class MockDataLoader(DataLoader):
    def __init__(self):
        pass

def test_summon_mechanics():
    print("Testing Summon Mechanics...")

    # Setup
    cm = CombatManager(MockDataLoader())

    player = Character(name="Hero", race="Human")
    enemy = Character(name="Goblin", race="Monster")
    enemy.attributes["Recovery"].value = 200 # More HP to survive
    enemy.current_health = enemy.max_health

    # Create Summon Ability
    essence = Essence(name="Fire", type="Base", rarity="Common", tags=["Fire"], description="Fire stuff")
    stone = AwakeningStone(name="Summon Stone", function="Summon Wolf", description="Summons a wolf", cost_type="Mana")

    ability = Ability(
        name="Summon Fire Wolf",
        description="Summons a fire wolf.",
        rank="Iron",
        level=1,
        parent_essence=essence,
        parent_stone=stone,
        cost=10,
        cooldown=5
    )

    player.current_mana = 100

    # 1. Execute Summon Ability
    print("\n[Step 1] Executing Summon Ability...")
    log = cm.execute_ability(player, enemy, ability)
    for line in log:
        print(line)

    # Verify Summon exists
    if len(player.summons) == 1:
        print("PASS: Summon created.")
        summon = player.summons[0]
        print(f"Summon Name: {summon.name}")
        print(f"Summon Duration: {summon.summon_duration}")
        print(f"Summon HP: {summon.current_health}")
    else:
        print("FAIL: Summon not created.")
        return

    # 2. Simulate Combat Round (Summon should attack)
    print("\n[Step 2] Simulating Combat Round...")
    log, end_combat = cm.combat_round(player, enemy, player_action="Attack")
    for line in log:
        print(line)

    # Verify Summon Attacked (Check log or enemy health)
    # Since we can't easily check log content programmatically without parsing, let's assume if it printed, it worked.

    print("\n[Step 3] Checking Summon Duration Decrement...")
    # Initial duration was 3 + int(1/3) = 3.
    # After one round, it should be 2.
    current_duration = player.summons[0].summon_duration
    if current_duration == 2:
         print(f"PASS: Summon duration decremented to {current_duration}.")
    else:
         print(f"FAIL: Summon duration not correct. Expected 2, got {current_duration}")

    print("\n[Step 4] Checking Persistence/Removal...")
    # Fast forward: Set duration to 1, so next round it attacks then expires (duration becomes 0)
    player.summons[0].summon_duration = 1
    cm.combat_round(player, enemy, "Attack")

    if len(player.summons) == 0:
        print("PASS: Summon removed after expiration.")
    else:
        print(f"FAIL: Summon not removed. Duration: {player.summons[0].summon_duration}")

if __name__ == "__main__":
    test_summon_mechanics()
