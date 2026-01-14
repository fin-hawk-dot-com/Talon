import sys
import os

# Add the project root to sys.path so we can import src modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models import Character, Attribute
from src.mechanics import DataLoader, ConfluenceManager, AbilityGenerator
# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models import Essence, AwakeningStone, Character
from src.mechanics import GameEngine

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
def choose_option(options, prompt):
    print(prompt)
    for i, opt in enumerate(options):
        print(f"{i+1}. {opt}")
    while True:
        try:
            choice = int(input("> "))
            if 1 <= choice <= len(options):
                return options[choice-1]
        except ValueError:
            pass
        print("Invalid choice.")

def main():
    engine = GameEngine()
    print_separator()
    print("Welcome to the HWFWM Progression Simulator")

    # Load Data
    # Optimized: Use engine's loader and ability_gen
    loader = engine.data_loader
    confluence_mgr = engine.confluence_mgr
    ability_gen = engine.ability_gen

    # Create Character
    name = input("Enter character name: ")
    race = "Human" # Simplified for now
    character = Character(name=name, race=race)
    print(f"Character {name} created.")
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

    print("Select Affinity (Focus):")
    affinities = ["Warrior", "Mage", "Rogue", "Guardian", "Support", "General"]
    affinity = choose_option(affinities, "Choose affinity: ")

    character = Character(name=name, race=race, affinity=affinity)
    print(f"Character {name} created with affinity {affinity}.")
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
        print("6. Simulate Training")
        print("7. Quest Log / Adventure")
        print("8. Exit")

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

            # Note: This block contains undefined variables (empty_indices) and is preserved
            # for existing behavior despite being broken.

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
        elif choice == "6":
            print("Simulating training montage...")
            # Simulate training all attributes
            for attr_name in character.attributes:
                engine.training_mgr.train_attribute(character, attr_name)

            # Simulate practicing all abilities and attempting rank up
            for essence_name, abilities in character.abilities.items():
                for i, ability in enumerate(abilities):
                    if ability:
                        leveled_up = engine.training_mgr.practice_ability(character, essence_name, i)
                        if leveled_up:
                            print(f"{ability.name} leveled up to {ability.level}!")

                        if ability.level == 9:
                            rank_up_msg = engine.training_mgr.attempt_rank_up_ability(character, essence_name, i)
                            if "Success" in rank_up_msg:
                                print(f"{ability.name} {rank_up_msg}")

        elif choice == "7":
            # Quest Menu
            print("\n--- Quest Log ---")

            # Show Active Quests
            active_quests = [q_id for q_id, prog in char.quests.items() if prog.status == "Active"]
            if active_quests:
                print("Active Quests:")
                for q_id in active_quests:
                    q = engine.quest_mgr.data_loader.get_quest(q_id)
                    stage = q.stages.get(char.quests[q_id].current_stage_id)
                    print(f"- {q.title}: {stage.description}")
            else:
                print("No active quests.")

            print("\nOptions:")
            print("1. Find New Quest")
            print("2. Continue Quest")
            print("3. Back")

            q_choice = input("> ").strip()

            if q_choice == "1":
                available = engine.quest_mgr.get_available_quests(char)
                if not available:
                    print("No new quests available.")
                else:
                    print("Available Quests:")
                    for i, q in enumerate(available):
                        print(f"{i+1}. {q.title} ({q.type}) - {q.description}")

                    try:
                        idx = int(input("Select quest to start (0 to cancel): ")) - 1
                        if 0 <= idx < len(available):
                            res = engine.quest_mgr.start_quest(char, available[idx].id)
                            print(res)
                    except ValueError:
                        pass

            elif q_choice == "2":
                if not active_quests:
                    print("No active quests.")
                else:
                    print("Select Quest to continue:")
                    active_list = []
                    for q_id in active_quests:
                         active_list.append(engine.quest_mgr.data_loader.get_quest(q_id))

                    for i, q in enumerate(active_list):
                        print(f"{i+1}. {q.title}")

                    try:
                        idx = int(input("> ")) - 1
                        if 0 <= idx < len(active_list):
                            q = active_list[idx]
                            stage_id = char.quests[q.id].current_stage_id
                            stage = q.stages.get(stage_id)

                            print(f"\n--- {q.title} ---")
                            print(stage.description)

                            if not stage.choices:
                                print("(No choices available - Stage might be end or broken)")
                            else:
                                for k, c in enumerate(stage.choices):
                                    print(f"{k+1}. {c.text}")

                                c_idx = int(input("Make a choice: ")) - 1
                                res = engine.quest_mgr.make_choice(char, q.id, c_idx)
                                print(f"\n> {res}")
                    except ValueError:
                        print("Invalid input.")

        elif choice == "8":
            sys.exit()

if __name__ == "__main__":
    main()
