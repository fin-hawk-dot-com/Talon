import sys
import os

# Add the project root to sys.path so we can import src modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models import Character, Attribute
from src.mechanics import DataLoader, ConfluenceManager, AbilityGenerator

def print_separator():
    print("-" * 60)

def choose_option(options, prompt="Choose an option: "):
    for i, option in enumerate(options):
        print(f"{i + 1}. {option}")
    while True:
        try:
            choice = int(input(prompt))
            if 1 <= choice <= len(options):
                return options[choice - 1]
            else:
                print("Invalid choice. Try again.")
        except ValueError:
            print("Invalid input. Enter a number.")

def main():
    print("Welcome to the HWFWM Progression Simulator")
    print_separator()

    # Load Data
    loader = DataLoader()
    confluence_mgr = ConfluenceManager(loader)
    ability_gen = AbilityGenerator()

    # Create Character
    name = input("Enter character name: ")
    race = "Human" # Simplified for now

    print("Select Affinity (Focus):")
    affinities = ["Warrior", "Mage", "Rogue", "Guardian", "Support", "General"]
    affinity = choose_option(affinities, "Choose affinity: ")

    character = Character(name=name, race=race, affinity=affinity)
    print(f"Character {name} created with affinity {affinity}.")
    print_separator()

    # Select Base Essences
    available_essences = loader.get_all_base_essences()
    attributes = ["Power", "Speed", "Spirit", "Recovery"]

    for i in range(3):
        print(f"Select Base Essence #{i+1}")
        # Show a subset or allow typing? Let's allow typing for speed in this demo, with validation
        # But for better UX in this script, let's list them in chunks or filter?
        # Let's just print them all
        print("Available Essences:", ", ".join(available_essences))

        while True:
            choice = input(f"Enter name of Essence #{i+1}: ").strip()
            # Case insensitive search
            match = next((e for e in available_essences if e.lower() == choice.lower()), None)
            if match:
                essence = loader.get_essence(match)
                # Choose Bond
                bond = choose_option(attributes, f"Bond {match} to which attribute? ")
                character.add_essence(essence, bond)
                print(f"Added {match} bonded to {bond}.")
                break
            else:
                print("Essence not found. Try again.")
        print_separator()

    # Determine Confluence
    print("Determining Confluence Essence...")
    confluence = confluence_mgr.determine_confluence(character.base_essences)
    print(f"Confluence Essence: {confluence.name}")
    print(f"Description: {confluence.description}")

    bond = choose_option(attributes, f"Bond {confluence.name} to which attribute? ")
    character.add_essence(confluence, bond)
    print_separator()

    # Main Loop
    while True:
        print(f"\nCharacter: {character.name} [{character.rank}]")
        print("Attributes:")
        for attr in character.attributes.values():
            print(f"  {attr.name}: {attr.value:.1f} (Growth: {attr.growth_multiplier}x)")

        print("\nAbilities:")
        for ess_name, slots in character.abilities.items():
            abilities_str = []
            for j, ability in enumerate(slots):
                if ability:
                    abilities_str.append(f"[{j+1}: {ability.name}]")
                else:
                    abilities_str.append(f"[{j+1}: Empty]")
            print(f"  {ess_name}: " + " ".join(abilities_str))

        print_separator()
        action = choose_option(["Awaken Ability", "Train (Simulate Growth)", "Exit"], "Choose action: ")

        if action == "Exit":
            break

        elif action == "Awaken Ability":
            # Choose Essence
            essences = character.get_all_essences()
            ess_names = [e.name for e in essences]
            target_ess_name = choose_option(ess_names, "Select Essence to awaken ability for: ")

            # Choose Slot
            # Find empty slots
            slots = character.abilities[target_ess_name]
            empty_indices = [i for i, x in enumerate(slots) if x is None]

            if not empty_indices:
                print("All slots for this Essence are full!")
                continue

            slot_idx = choose_option([str(i+1) for i in empty_indices], "Select Slot to fill: ")
            slot_idx = int(slot_idx) - 1

            # Choose Awakening Stone
            # For brevity, let's just list 5 random ones or search
            all_stones = loader.get_all_stones()
            print("Available Stones (Top 10):")
            for k, s in enumerate(all_stones[:10]):
                print(f"{k+1}. {s}")
            print("...")

            stone_name = input("Enter Awakening Stone name (exact or partial): ")
            # Simple fuzzy match
            match_stone = next((s for s in all_stones if stone_name.lower() in s.lower()), None)

            if match_stone:
                stone = loader.get_stone(match_stone)
                essence_obj = next(e for e in essences if e.name == target_ess_name)

                new_ability = ability_gen.generate(essence_obj, stone, character.rank, character.affinity)
                character.abilities[target_ess_name][slot_idx] = new_ability
                print(f"Awakened: {new_ability.name}!")
                print(f"Effect: {new_ability.description}")
            else:
                print("Stone not found.")

        elif action == "Train (Simulate Growth)":
            # Simulate usage
            print("Simulating training montage...")
            # For simplicity, just add 1 to all bonded stats based on multiplier
            for attr_name, attr in character.attributes.items():
                gain = 1.0 * attr.growth_multiplier
                attr.value += gain
                print(f"{attr_name} gained {gain:.1f} points.")

            # TODO: Logic for ranking up abilities

if __name__ == "__main__":
    main()
