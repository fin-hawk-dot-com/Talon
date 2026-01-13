import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models import Essence, AwakeningStone
from src.mechanics import GameEngine

def print_separator():
    print("-" * 60)

def main():
    engine = GameEngine()
    print_separator()
    print("Welcome to the HWFWM Progression Simulator")
    print_separator()

    # Character Creation
    name = input("Enter Character Name: ").strip()
    race = input("Enter Race: ").strip()
    engine.create_character(name, race)
    print(f"Character {name} created!")
    print_separator()

    while True:
        char = engine.character
        print(f"\nName: {char.name} | Race: {char.race} | Rank: {char.rank}")
        print("Attributes:")
        for attr in char.attributes.values():
            print(f"  {attr.name}: {attr.value:.1f} ({attr.rank}) [Mult: {attr.growth_multiplier}x]")

        print("\nEssences:")
        for e in char.get_all_essences():
            print(f"  {e.name} ({e.bonded_attribute})")
            abilities = char.abilities.get(e.name, [])
            for i, ab in enumerate(abilities):
                if ab:
                    print(f"    Slot {i}: {ab.name} [{ab.rank} {ab.level}] - {ab.description}")
                else:
                    print(f"    Slot {i}: [Empty]")

        print("\nInventory:")
        if not char.inventory:
            print("  (Empty)")
        else:
            for i, item in enumerate(char.inventory):
                type_name = "Essence" if isinstance(item, Essence) else "Stone"
                print(f"  {i}. {item.name} ({type_name})")

        print_separator()
        print("Actions:")
        print("1. Train Attribute")
        print("2. Hunt for Loot")
        print("3. Absorb Essence (from Inventory)")
        print("4. Awaken Ability (using Stone)")
        print("5. Practice Ability")
        print("6. Exit")

        choice = input("\nSelect Action: ").strip()

        if choice == "1":
            print("\nSelect Attribute to train:")
            print("P. Power, S. Speed, M. Spirit, R. Recovery")
            attr_choice = input("> ").strip().lower()
            mapping = {'p': 'Power', 's': 'Speed', 'm': 'Spirit', 'r': 'Recovery'}
            if attr_choice in mapping:
                engine.training_mgr.train_attribute(char, mapping[attr_choice])
                print(f"Trained {mapping[attr_choice]}!")
            else:
                print("Invalid attribute.")

        elif choice == "2":
            print("\nHunting...")
            item = engine.loot_mgr.generate_random_loot()
            if item:
                char.inventory.append(item)
                print(f"You found a {item.name}!")
            else:
                print("You found nothing.")

        elif choice == "3":
            if not char.inventory:
                print("Inventory empty.")
                continue
            try:
                idx = int(input("Enter inventory item index to absorb: "))
                item = char.inventory[idx]
                if isinstance(item, Essence):
                    print("Select attribute to bond with (Power, Speed, Spirit, Recovery):")
                    attr = input("> ").strip().title()
                    if attr in char.attributes:
                        res = engine.absorb_essence(idx, attr)
                        print(res)
                    else:
                        print("Invalid attribute.")
                else:
                    print("That is not an Essence.")
            except (ValueError, IndexError):
                print("Invalid input.")

        elif choice == "4":
            if not char.inventory:
                print("Inventory empty.")
                continue
            try:
                stone_idx = int(input("Enter inventory index of Stone: "))
                if not isinstance(char.inventory[stone_idx], AwakeningStone):
                    print("Not a stone.")
                    continue

                print("Select Essence to awaken on:")
                essences = char.get_all_essences()
                for i, e in enumerate(essences):
                    print(f"{i}. {e.name}")

                e_idx = int(input("> "))
                if e_idx < 0 or e_idx >= len(essences):
                    print("Invalid essence.")
                    continue

                essence_name = essences[e_idx].name

                slot_idx = int(input("Enter Slot Index (0-4): "))

                res = engine.awaken_ability(essence_name, stone_idx, slot_idx)
                print(res)

            except (ValueError, IndexError):
                print("Invalid input.")

        elif choice == "5":
            print("Select Essence:")
            essences = char.get_all_essences()
            for i, e in enumerate(essences):
                print(f"{i}. {e.name}")
            try:
                e_idx = int(input("> "))
                if e_idx < 0 or e_idx >= len(essences): continue
                essence_name = essences[e_idx].name

                slot = int(input("Slot (0-4): "))
                res = engine.training_mgr.practice_ability(char, essence_name, slot)
                if res:
                    print("Ability Leveled Up!")
                else:
                    print("Practiced ability.")
            except ValueError:
                print("Invalid input.")

        elif choice == "6":
            print("Goodbye!")
            break

        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
