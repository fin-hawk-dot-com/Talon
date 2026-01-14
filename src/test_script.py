import sys
import os

# Add the project root to sys.path so we can import src modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models import Character, Attribute
from src.mechanics import DataLoader, ConfluenceManager, AbilityGenerator

def test_simulation():
    print("Running Simulation Test...")

    # 1. Load Data
    loader = DataLoader()
    confluence_mgr = ConfluenceManager(loader)
    ability_gen = AbilityGenerator()

    # 2. Create Character
    char = Character(name="Tester", race="Human")

    # 3. Add Essences (Testing Confluence Logic)
    # Fire + Earth + Potent -> Volcano (from confluences.json)
    essences_to_add = [
        ("Fire", "Power"),
        ("Earth", "Recovery"),
        ("Potent", "Power")
    ]

    for e_name, bond in essences_to_add:
        essence = loader.get_essence(e_name)
        if not essence:
            print(f"ERROR: Essence {e_name} not found.")
            return
        char.add_essence(essence, bond)

    print(f"Base Essences: {[e.name for e in char.base_essences]}")

    # 4. Check Confluence
    confluence = confluence_mgr.determine_confluence(char.base_essences)
    print(f"Determined Confluence: {confluence.name}")

    if confluence.name != "Volcano":
        print(f"FAIL: Expected Volcano, got {confluence.name}")
    else:
        print("PASS: Confluence Logic (Exact Match)")

    char.add_essence(confluence, "Power")

    # 5. Check Attribute Growth Multipliers
    # Power has 3 essences bonded (Fire, Potent, Volcano) -> Should be 2.0x
    # Recovery has 1 essence bonded (Earth) -> Should be 1.2x
    # Speed has 0 -> 1.0x

    power_mult = char.attributes["Power"].growth_multiplier
    rec_mult = char.attributes["Recovery"].growth_multiplier
    speed_mult = char.attributes["Speed"].growth_multiplier

    print(f"Power Multiplier: {power_mult}x (Expected 2.0)")
    print(f"Recovery Multiplier: {rec_mult}x (Expected 1.2)")

    if power_mult == 2.0 and rec_mult == 1.2 and speed_mult == 1.0:
         print("PASS: Attribute Bonding Logic")
    else:
         print("FAIL: Attribute Bonding Logic")

    # 6. Test Ability Generation
    # Awakening Stone of the Strike on Fire Essence
    fire_essence = char.base_essences[0] # Fire
    stone = loader.get_stone("Stone of the Strike")

    # Set affinity to Warrior to bias towards "Strike" or "Smash"
    char.affinity = "Warrior"
    ability = ability_gen.generate(fire_essence, stone, char.rank, char.affinity)
    print(f"Generated Ability (Warrior Affinity): {ability.name}")
    print(f"Description: {ability.description}")

    # The templates for Strike include "{essence} Strike", "{essence} Slash", "{essence} Smash", "{essence} Blade"
    # "Fire Strike" is likely for Warrior/General.
    # Just check if it's one of the valid templates or contains the Essence Name
    if fire_essence.name in ability.name:
        print("PASS: Ability Generation")
    else:
        print(f"FAIL: Ability name {ability.name} does not contain essence name {fire_essence.name}")

    # 7. Test Confluence Fallback
    print("\nTesting Confluence Fallback...")
    char2 = Character(name="Tester2", race="Human")
    # Might, Water, Air -> No recipe.
    # Might (Physical), Water (Elemental), Air (Elemental)
    # Tags: Strength, Force, Body | Liquid, Flow, Life | Gas, Movement, Wind
    # No obvious 3x tag overlap in my simple dataset?
    # Let's see tags:
    # Might: Physical, Strength, Force, Body
    # Water: Elemental, Liquid, Flow, Life
    # Air: Elemental, Gas, Movement, Wind

    # 'Elemental' tag appears 2 times.
    # So it should hit fallback "Might Hybrid"

    e1 = loader.get_essence("Might")
    e2 = loader.get_essence("Water")
    e3 = loader.get_essence("Air")

    char2.add_essence(e1, "Power")
    char2.add_essence(e2, "Spirit")
    char2.add_essence(e3, "Speed")

    conf2 = confluence_mgr.determine_confluence(char2.base_essences)
    print(f"Fallback Confluence: {conf2.name}")

    # Updated logic produces "Force Confluence" etc. based on bonded stats
    # or "Hybrid" if no stats bonded (unlikely in this flow)
    if "Confluence" in conf2.name or "Hybrid" in conf2.name:
         print("PASS: Confluence Fallback")
    else:
         print(f"FAIL: Expected Confluence/Hybrid, got {conf2.name}")


if __name__ == "__main__":
    test_simulation()
