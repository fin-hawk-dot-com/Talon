import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models import Essence, AwakeningStone, Character
from src.mechanics import GameEngine

def print_separator():
    """Prints a separator line."""
    print("-" * 60)

def _display_character_summary(char: Character):
    """Displays a summary of the character's status."""
    if not char:
        return
    print(f"\nName: {char.name} | Race: {char.race} | Rank: {char.rank}")
    print("Attributes:")
    for attr in char.attributes.values():
        print(f"  {attr.name}: {attr.value:.1f} ({attr.rank}) [Mult: {attr.growth_multiplier}x]")

def _handle_view_character_details(engine: GameEngine):
    """Handles the View Character Details action."""
    char = engine.character
    if not char:
        print("No character created yet.")
        return

    print_separator()
    print("Character Details")
    print_separator()
    print(f"Name:     {char.name}")
    print(f"Race:     {char.race}")
    print(f"Rank:     {char.rank}")
    print(f"Affinity: {char.affinity}")
    print(f"Faction:  {char.faction or 'None'}")
    print_separator()

    print("Attributes:")
    for attr in char.attributes.values():
        print(f"  - {attr.name:<10} | Value: {attr.value:<8.1f} | Rank: {attr.rank:<8} | Growth: {attr.growth_multiplier:.1f}x")
    print_separator()

    print("Essences & Abilities:")
    essences = char.get_all_essences()
    if not essences:
        print("  (None)")
    else:
        for e in essences:
            print(f"\n  Essence: {e.name} (Bonded to: {e.bonded_attribute})")
            print(f"  Description: {e.description}")
            abilities = char.abilities.get(e.name, [])
            if not any(abilities):
                print("    - No abilities awakened.")
            else:
                for i, ab in enumerate(abilities):
                    if ab:
                        print(f"    - Slot {i}: {ab.name} [{ab.rank} Lvl {ab.level}]")
                        print(f"      Desc: {ab.description}")
                    else:
                        print(f"    - Slot {i}: [Empty]")
    print_separator()

    print("Inventory:")
    if not char.inventory:
        print("  (Empty)")
    else:
        for i, item in enumerate(char.inventory):
            type_name = "Essence" if isinstance(item, Essence) else "Stone"
            print(f"  - [{i}] {item.name} ({type_name})")
            print(f"    Desc: {item.description}")

    input("\nPress Enter to return to the main menu...")

def _handle_train_attribute(engine: GameEngine):
    """Handles the Train Attribute action."""
    char = engine.character
    print("\nSelect Attribute to train:")
    print("P. Power, S. Speed, M. Spirit, R. Recovery")
    attr_choice = input("> ").strip().lower()
    mapping = {'p': 'Power', 's': 'Speed', 'm': 'Spirit', 'r': 'Recovery'}
    if attr_choice in mapping:
        engine.training_mgr.train_attribute(char, mapping[attr_choice])
        print(f"Trained {mapping[attr_choice]}!")
    else:
        print("Invalid attribute.")

def _handle_hunt_for_loot(engine: GameEngine):
    """Handles the Hunt for Loot action."""
    print("\nHunting...")
    item = engine.loot_mgr.generate_random_loot()
    if item:
        engine.character.inventory.append(item)
        print(f"You found a {item.name}!")
    else:
        print("You found nothing.")

def _handle_absorb_essence(engine: GameEngine):
    """Handles the Absorb Essence action."""
    char = engine.character
    if not char.inventory:
        print("Inventory empty.")
        return
    try:
        idx = int(input("Enter inventory item index to absorb: "))
        item = char.inventory[idx]
        if not isinstance(item, Essence):
            print("That is not an Essence.")
            return

        print(f"You selected: {item.name}")
        print("Select attribute to bond with (Power, Speed, Spirit, Recovery):")
        attr = input("> ").strip().title()

        if attr not in char.attributes:
            print("Invalid attribute.")
            return

        confirm = input(f"Are you sure you want to absorb {item.name} and bond it to {attr}? (y/n): ").strip().lower()
        if confirm == 'y':
            res = engine.absorb_essence(idx, attr)
            print(res)
        else:
            print("Absorption cancelled.")

    except (ValueError, IndexError):
        print("Invalid input.")

def _handle_awaken_ability(engine: GameEngine):
    """Handles the Awaken Ability action."""
    char = engine.character
    if not char.inventory:
        print("Inventory empty.")
        return
    try:
        stone_idx = int(input("Enter inventory index of Stone: "))
        if not isinstance(char.inventory[stone_idx], AwakeningStone):
            print("Not a stone.")
            return

        print("Select Essence to awaken on:")
        essences = char.get_all_essences()
        for i, e in enumerate(essences):
            print(f"{i}. {e.name}")

        e_idx = int(input("> "))
        if e_idx < 0 or e_idx >= len(essences):
            print("Invalid essence.")
            return

        essence_name = essences[e_idx].name
        slot_idx = int(input("Enter Slot Index (0-4): "))

        res = engine.awaken_ability(essence_name, stone_idx, slot_idx)
        print(res)

    except (ValueError, IndexError):
        print("Invalid input.")

def _handle_practice_ability(engine: GameEngine):
    """Handles the Practice Ability action."""
    char = engine.character
    print("Select Essence:")
    essences = char.get_all_essences()
    for i, e in enumerate(essences):
        print(f"{i}. {e.name}")
    try:
        e_idx = int(input("> "))
        if e_idx < 0 or e_idx >= len(essences):
            print("Invalid essence.")
            return

        essence_name = essences[e_idx].name
        slot = int(input("Slot (0-4): "))
        res = engine.training_mgr.practice_ability(char, essence_name, slot)
        if res:
            print("Ability Leveled Up!")
        else:
            print("Practiced ability.")
    except (ValueError, IndexError):
        print("Invalid input.")

def _handle_simulate_training(engine: GameEngine):
    """Handles the Simulate Training action."""
    char = engine.character
    print("Simulating training montage...")
    # Simulate training all attributes
    for attr_name in char.attributes:
        engine.training_mgr.train_attribute(char, attr_name)

    # Simulate practicing all abilities and attempting rank up
    for essence_name, abilities in char.abilities.items():
        for i, ability in enumerate(abilities):
            if ability:
                leveled_up = engine.training_mgr.practice_ability(char, essence_name, i)
                if leveled_up:
                    print(f"{ability.name} leveled up to {ability.level}!")

                if ability.level == 9:
                    rank_up_msg = engine.training_mgr.attempt_rank_up_ability(char, essence_name, i)
                    if "Success" in rank_up_msg:
                        print(f"{ability.name} {rank_up_msg}")
    print("Training complete.")

def main():
    """Main game loop."""
    engine = GameEngine()
    print_separator()
    print("Welcome to the HWFWM Progression Simulator")

    # Character Creation
    name = input("Enter Character Name: ").strip()
    race = input("Enter Race: ").strip()
    engine.create_character(name, race)
    print(f"Character {name} created!")
    print_separator()

    actions = {
        "1": ("Train Attribute", _handle_train_attribute),
        "2": ("Hunt for Loot", _handle_hunt_for_loot),
        "3": ("Absorb Essence (from Inventory)", _handle_absorb_essence),
        "4": ("Awaken Ability (using Stone)", _handle_awaken_ability),
        "5": ("Practice Ability", _handle_practice_ability),
        "6": ("Simulate Training", _handle_simulate_training),
        "7": ("View Character Details", _handle_view_character_details),
        "8": ("Exit", lambda e: sys.exit("Exiting.")),
    }

    while True:
        _display_character_summary(engine.character)
        print_separator()
        print("Actions:")
        for key, (desc, _) in actions.items():
            print(f"{key}. {desc}")

        choice = input("\nSelect Action: ").strip()

        action_handler = actions.get(choice)
        if action_handler:
            _, func = action_handler
            func(engine)
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
