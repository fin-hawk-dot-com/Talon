import sys
import os
import random

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models import Character
from src.data_loader import DataLoader
from src.combat_system import CombatManager

def test_monster_loading():
    print("Testing Monster Loading...")
    loader = DataLoader()

    # Test Iron Wolf
    wolf = loader.get_monster("Iron Wolf")
    assert wolf is not None, "Iron Wolf should exist"

    if "Natural" not in wolf.abilities:
        print("FAIL: 'Natural' essence not found in abilities.")
        print(f"Abilities keys: {wolf.abilities.keys()}")
        return None

    assert len(wolf.abilities["Natural"]) == 2

    abilities = {ab.name: ab for ab in wolf.abilities["Natural"]}
    assert "Steel Bite" in abilities
    assert "Howl of Iron" in abilities

    steel_bite = abilities["Steel Bite"]
    # Check if custom attributes were attached
    if not hasattr(steel_bite, 'custom_damage_multiplier'):
        print("FAIL: custom_damage_multiplier not found on Ability object.")
    else:
        assert steel_bite.custom_damage_multiplier == 1.2

    assert steel_bite.parent_stone.function == "Attack"

    print("PASS: Monster abilities loaded correctly.")
    return wolf

def test_monster_combat():
    print("Testing Monster Combat AI...")
    loader = DataLoader()
    cm = CombatManager(loader)

    wolf = loader.get_monster("Iron Wolf")
    if not wolf: return

    player = Character(name="Hero", race="Human")

    # Give player lots of health
    player.attributes["Recovery"].value = 100.0 # 1000 HP
    player.current_health = player.max_health

    # Give wolf mana/stamina
    wolf.current_mana = wolf.max_mana
    wolf.current_stamina = wolf.max_stamina

    # Force use of Steel Bite
    steel_bite = [ab for ab in wolf.abilities["Natural"] if ab.name == "Steel Bite"][0]

    print(f"Executing {steel_bite.name}...")
    log = cm.execute_ability(wolf, player, steel_bite)
    for l in log:
        print(l)

    damage_done = False
    for l in log:
        if "Used Steel Bite" in l and "damage" in l:
            damage_done = True
            break

    if not damage_done:
        print("FAIL: Steel Bite did not deal damage or log correctly.")
    else:
        print("PASS: Steel Bite executed.")

    # Check damage roughly
    # Wolf Power 120. Multiplier 1.2.
    # Player Recovery 100.
    assert player.current_health < player.max_health
    print(f"Player HP: {player.current_health}/{player.max_health}")

    # Test AI decision making (statistical)
    print("Testing AI decision making...")
    abilities_used = 0
    attacks_used = 0

    # Loop to verify randomness works
    for _ in range(30):
        # Reset HP and Cooldowns to ensure combat continues
        player.current_health = player.max_health
        wolf.current_health = wolf.max_health
        wolf.current_mana = wolf.max_mana
        wolf.current_stamina = wolf.max_stamina

        for ab in wolf.abilities["Natural"]:
            ab.current_cooldown = 0

        # Capture log
        # Note: combat_round logic: 1. Player acts 2. Summons act 3. Enemy acts
        # We pass "Attack" for player.
        log, _ = cm.combat_round(player, wolf, "Attack")

        # Look for wolf's action in log
        # Usually appears after "You attacked..."

        wolf_action_found = False
        for l in log:
            # Check for ability usage (format: "Used Ability on Target..." or "Name used Ability...")
            if "Used" in l and ("Steel Bite" in l or "Howl" in l):
                abilities_used += 1
                wolf_action_found = True
            elif l.startswith(wolf.name) and ("attacked you" in l or "missed" in l):
                attacks_used += 1
                wolf_action_found = True

    print(f"Abilities used: {abilities_used}, Basic Attacks: {attacks_used}")

    if abilities_used > 0:
        print("PASS: Monster AI uses abilities.")
    else:
        print("FAIL: Monster AI never used abilities (bad luck or bug).")

if __name__ == "__main__":
    wolf = test_monster_loading()
    if wolf:
        test_monster_combat()
