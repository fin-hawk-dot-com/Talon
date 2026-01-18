import sys
import os
import random
import argparse
from typing import Dict, Any, Callable

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models import Essence, AwakeningStone, Character, StatusEffect
from src.mechanics import GameEngine
from src.world_map import MapVisualizer

def print_separator():
    print("-" * 60)

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

class GameInterface:
    def __init__(self):
        self.engine = GameEngine()
        self.map_viz = MapVisualizer(self.engine.data_loader)
        self.running = True
        self.menu_actions: Dict[str, Callable] = {
            "1": self.action_train_attribute,
            "2": self.action_adventure,
            "3": self.action_absorb_essence,
            "4": self.action_awaken_ability,
            "5": self.action_practice_ability,
            "6": self.action_simulate_training,
            "7": self.action_quest_log,
            "8": self.action_grimoire,
            "9": self.action_system,
            "10": self.action_travel,
            "11": self.action_view_map,
            "0": self.action_exit
        }

    def start(self, args):
        print_separator()
        print("Welcome to the HWFWM Progression Simulator")

        if args.load:
            print(self.engine.load_game(args.load))
            if not self.engine.character:
                 print("Failed to load specified save file. Starting fresh.")

        if not self.engine.character:
            self.main_menu(args)

        if not self.engine.character: # Should have been created or loaded
             return

        self.game_loop()

    def main_menu(self, args):
        # If passed --new, skip menu and create new game
        if args.new:
             self.create_character(args.new)
             return

        print("1. New Game")
        print("2. Load Game")
        start_choice = input("> ").strip()

        if start_choice == "2":
            self.load_game_menu()
            if not self.engine.character:
                print("Starting New Game.")
                self.create_character()
        else:
            self.create_character()

    def load_game_menu(self):
        saves = self.engine.get_save_files()
        if not saves:
            print("No save files found.")
            return

        print("Select Save File:")
        for i, s in enumerate(saves):
            print(f"{i+1}. {s}")
        try:
            s_idx = int(input("> ")) - 1
            if 0 <= s_idx < len(saves):
                res = self.engine.load_game(saves[s_idx])
                print(res)
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")

    def create_character(self, name=None):
        if not name:
            name = input("Enter character name: ")

        race = "Human" # Simplified for now

        print("Select Affinity (Focus):")
        affinities = ["Warrior", "Mage", "Rogue", "Guardian", "Support", "General"]
        affinity = choose_option(affinities, "Choose affinity: ")

        # Use engine to create character
        self.engine.create_character(name, race)
        self.engine.character.affinity = affinity

        # Give some starter items for testing
        starter_essence = self.engine.data_loader.get_essence("Dark")
        if starter_essence:
            self.engine.character.inventory.append(starter_essence)

        starter_stone = self.engine.data_loader.get_stone("Stone of the Strike")
        if starter_stone:
            self.engine.character.inventory.append(starter_stone)

        print(f"Character {name} created with affinity {affinity}.")

    def game_loop(self):
        while self.running:
            self.print_status()
            self.print_menu()
            choice = input("\nSelect Action: ").strip()

            action = self.menu_actions.get(choice)
            if action:
                action()
            else:
                print("Invalid selection.")

    def print_status(self):
        char = self.engine.character
        print_separator()
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
        print_separator()

    def print_menu(self):
        print("Actions:")
        print("1. Train Attribute")
        print("2. Adventure (Combat)")
        print("3. Absorb Essence (from Inventory)")
        print("4. Awaken Ability (using Stone)")
        print("5. Practice Ability")
        print("6. Simulate Training")
        print("7. Quest Log / Adventure")
        print("8. Grimoire (Lore)")
        print("9. System (Save/Load)")
        print("10. Travel / Interact")
        print("11. View World Map")
        print("0. Exit")

    def action_train_attribute(self):
        print("\nSelect Attribute to train:")
        print("P. Power, S. Speed, M. Spirit, R. Recovery")
        attr_choice = input("> ").strip().lower()
        mapping = {'p': 'Power', 's': 'Speed', 'm': 'Spirit', 'r': 'Recovery'}
        if attr_choice in mapping:
            result = self.engine.training_mgr.train_attribute(self.engine.character, mapping[attr_choice])
            print(f"\n{result}")
        else:
            print("Invalid attribute.")

    def action_adventure(self):
        print("\nSearching for trouble...")
        monsters = self.engine.data_loader.get_all_monsters()
        if not monsters:
            print("No monsters found.")
            return

        # Pick a random monster
        m_name = random.choice(monsters)
        monster = self.engine.data_loader.get_monster(m_name)

        print(f"You encountered a {monster.name} ({monster.rank})!")
        print(f"Health: {monster.current_health:.1f}/{monster.max_health:.1f}")

        char = self.engine.character
        while True:
            # Refresh status display
            char_status_str = f"Your Status: HP {char.current_health:.0f}/{char.max_health:.0f} | MP {char.current_mana:.0f}/{char.max_mana:.0f} | SP {char.current_stamina:.0f}/{char.max_stamina:.0f}"
            if char.status_effects:
                effects_str = " ".join([f"[{e.name} {e.duration}]" for e in char.status_effects])
                char_status_str += f" | Effects: {effects_str}"

            enemy_status_str = f"Enemy Status: HP {monster.current_health:.0f}/{monster.max_health:.0f}"
            if monster.status_effects:
                 effects_str = " ".join([f"[{e.name} {e.duration}]" for e in monster.status_effects])
                 enemy_status_str += f" | Effects: {effects_str}"

            print("\n" + "="*60)
            print(char_status_str)
            print(enemy_status_str)
            print("="*60)

            print("\nCombat Options:")
            print("1. Attack")
            print("2. Flee")
            print("3. Use Ability")

            c_choice = input("> ").strip()
            action = None
            combat_over = False

            if c_choice == "1":
                action = "Attack"
            elif c_choice == "2":
                action = "Flee"
            elif c_choice == "3":
                # List abilities
                abilities_flat = []
                for ess_name, slots in char.abilities.items():
                    for ab in slots:
                        if ab:
                            abilities_flat.append(ab)

                if not abilities_flat:
                    print("No abilities available.")
                    continue

                print("Select Ability:")
                for i, ab in enumerate(abilities_flat):
                    cost_str = f"{ab.cost} {ab.parent_stone.cost_type}"
                    cd_str = f" [CD: {ab.current_cooldown}]" if ab.current_cooldown > 0 else ""
                    print(f"{i+1}. {ab.name} ({cost_str}){cd_str} - {ab.description}")

                try:
                    ab_idx_input = int(input("> ")) - 1
                    if 0 <= ab_idx_input < len(abilities_flat):
                        action = abilities_flat[ab_idx_input]
                    else:
                        print("Invalid selection.")
                        continue
                except ValueError:
                    print("Invalid input.")
                    continue
            else:
                print("Invalid choice.")
                continue

            logs, combat_over = self.engine.combat_mgr.combat_round(char, monster, action)
            for line in logs:
                print(line)

            if combat_over:
                if monster.current_health <= 0:
                    self.handle_combat_victory(monster)
                elif char.current_health <= 0:
                    print("You have been defeated. (Game Over - Reviving at temple...)")
                    char.current_health = char.max_health # Reset for now
                break

    def handle_combat_victory(self, monster):
        char = self.engine.character
        print(f"You gained {monster.xp_reward} XP!")

        # Update Quests
        notifications = self.engine.quest_mgr.check_objectives(char, "kill", monster.name)
        for note in notifications:
            print(f"\n! {note} !")

        # Loot
        loot_items = self.engine.loot_mgr.get_loot_for_monster(monster)
        if loot_items:
            print("Loot:")
            for loot_item_name in monster.loot_table:
                # Try to find as Essence or Stone
                item = self.engine.data_loader.get_essence(loot_item_name)
                if not item:
                    item = self.engine.data_loader.get_stone(loot_item_name)

                if item:
                    char.inventory.append(item)
                    print(f"- Found {item.name}!")

                    # Quest Check for Collection
                    col_notes = self.engine.quest_mgr.check_objectives(char, "collect", item.name)
                    for note in col_notes:
                        print(f"\n! {note} !")
                else:
                    print(f"- Found unknown item: {loot_item_name}")

        # Random Loot Chance
        random_loot = self.engine.loot_mgr.generate_random_loot()
        if random_loot:
             char.inventory.append(random_loot)
             print(f"Random Drop: Found {random_loot.name}!")

    def action_absorb_essence(self):
        char = self.engine.character
        if not char.inventory:
            print("Inventory empty.")
            return

        print("Inventory:")
        for i, item in enumerate(char.inventory):
            type_name = "Essence" if isinstance(item, Essence) else "Stone"
            print(f"  {i}. {item.name} ({type_name})")

        try:
            idx = int(input("Enter inventory item index to absorb: "))
            if idx < 0 or idx >= len(char.inventory):
                print("Invalid index.")
                return

            item = char.inventory[idx]
            if isinstance(item, Essence):
                print("Select attribute to bond with (Power, Speed, Spirit, Recovery):")
                attr = input("> ").strip().title()
                if attr in char.attributes:
                    res = self.engine.absorb_essence(idx, attr)
                    print(res)
                else:
                    print("Invalid attribute.")
            else:
                print("That is not an Essence.")
        except (ValueError, IndexError):
            print("Invalid input.")

    def action_awaken_ability(self):
        char = self.engine.character
        if not char.inventory:
            print("Inventory empty.")
            return

        print("Inventory:")
        for i, item in enumerate(char.inventory):
            type_name = "Essence" if isinstance(item, Essence) else "Stone"
            print(f"  {i}. {item.name} ({type_name})")

        try:
            stone_idx = int(input("Enter inventory index of Stone: "))
            if stone_idx < 0 or stone_idx >= len(char.inventory):
                print("Invalid index.")
                return

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

            res = self.engine.awaken_ability(essence_name, stone_idx, slot_idx)
            print(res)

        except (ValueError, IndexError):
            print("Invalid input.")

    def action_practice_ability(self):
        char = self.engine.character
        print("Select Essence:")
        essences = char.get_all_essences()
        for i, e in enumerate(essences):
            print(f"{i}. {e.name}")
        try:
            e_idx = int(input("> "))
            if e_idx < 0 or e_idx >= len(essences): return
            essence_name = essences[e_idx].name

            print("Select Ability Slot to Practice:")
            abilities = char.abilities.get(essence_name, [])
            for i, ab in enumerate(abilities):
                if ab:
                     print(f"{i}. {ab.name} [Lvl {ab.level}]")
                else:
                     print(f"{i}. [Empty]")

            slot = int(input("Slot (0-4): "))
            res = self.engine.training_mgr.practice_ability(char, essence_name, slot)
            if res:
                print("Ability Leveled Up!")
            else:
                print("Practiced ability.")
        except ValueError:
            print("Invalid input.")

    def action_simulate_training(self):
        print("Simulating training montage...")
        char = self.engine.character
        # Simulate training all attributes
        for attr_name in char.attributes:
            res = self.engine.training_mgr.train_attribute(char, attr_name)
            if "*** BREAKTHROUGH ***" in res:
                print(res)

        # Simulate practicing all abilities and attempting rank up
        for essence_name, abilities in char.abilities.items():
            for i, ability in enumerate(abilities):
                if ability:
                    leveled_up = self.engine.training_mgr.practice_ability(char, essence_name, i)
                    if leveled_up:
                        print(f"{ability.name} leveled up to {ability.level}!")

                    if ability.level == 9:
                        rank_up_msg = self.engine.training_mgr.attempt_rank_up_ability(char, essence_name, i)
                        if "Success" in rank_up_msg:
                            print(f"{ability.name} {rank_up_msg}")

    def action_quest_log(self):
        char = self.engine.character
        print("\n--- Quest Log ---")

        # Show Active Quests
        active_quests = [q_id for q_id, prog in char.quests.items() if prog.status == "Active"]
        if active_quests:
            print("Active Quests:")
            for q_id in active_quests:
                q = self.engine.quest_mgr.data_loader.get_quest(q_id)
                prog = char.quests[q_id]
                stage = q.stages.get(prog.current_stage_id)

                # Format Objectives
                objectives_text = ""
                if stage.objectives:
                    objectives_text = "\n    Objectives:"
                    for obj in stage.objectives:
                        key = f"{obj.type}:{obj.target}"
                        current = prog.objectives_progress.get(key, 0)
                        objectives_text += f"\n    - {obj.type} {obj.target}: {current}/{obj.count}"

                print(f"- {q.title}: {stage.description}{objectives_text}")
        else:
            print("No active quests.")

        print("\nOptions:")
        print("1. Find New Quest")
        print("2. Continue Quest")
        print("3. Back")

        q_choice = input("> ").strip()

        if q_choice == "1":
            available = self.engine.quest_mgr.get_available_quests(char)
            if not available:
                print("No new quests available.")
            else:
                print("Available Quests:")
                for i, q in enumerate(available):
                    print(f"{i+1}. {q.title} ({q.type}) - {q.description}")

                try:
                    idx = int(input("Select quest to start (0 to cancel): ")) - 1
                    if 0 <= idx < len(available):
                        res = self.engine.quest_mgr.start_quest(char, available[idx].id)
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
                     active_list.append(self.engine.quest_mgr.data_loader.get_quest(q_id))

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
                            res = self.engine.quest_mgr.make_choice(char, q.id, c_idx)
                            print(f"\n> {res}")
                except ValueError:
                    print("Invalid input.")

    def action_grimoire(self):
        char = self.engine.character
        print("\n--- Grimoire ---")
        if not char.lore:
            print("You have not discovered any lore yet.")
        else:
            # Group by category
            categories = {}
            for lore_id in char.lore:
                entry = self.engine.data_loader.get_lore(lore_id)
                if entry:
                    if entry.category not in categories:
                        categories[entry.category] = []
                    categories[entry.category].append(entry)

            for cat, entries in categories.items():
                print(f"\n[{cat}]")
                for entry in entries:
                    print(f"  - {entry.title}: {entry.text}")
        input("\nPress Enter to continue...")

    def action_system(self):
        print("\nSystem Menu:")
        print("1. Save Game")
        print("2. Load Game")
        print("3. Back")
        sys_choice = input("> ").strip()

        if sys_choice == "1":
            filename = input("Enter save filename (e.g., save1.json): ")
            print(self.engine.save_game(filename))
        elif sys_choice == "2":
            self.load_game_menu()

    def handle_conversation(self, npc_name):
        node_id = "root"
        print(f"\n--- Talking to {npc_name} ---")

        while True:
            node = self.engine.interaction_mgr.get_dialogue_node(npc_name, node_id)
            if not node:
                print(f"{npc_name} has nothing more to say.")
                break

            print(f"\n{npc_name}: \"{node.text}\"")

            if not node.choices:
                input("[Press Enter to end conversation]")
                break

            print("\nOptions:")
            for i, choice in enumerate(node.choices):
                print(f"{i+1}. {choice.text}")

            try:
                c_idx = int(input("> ")) - 1
                if 0 <= c_idx < len(node.choices):
                    choice = node.choices[c_idx]
                    if choice.next_id == "exit":
                        print(f"You end the conversation with {npc_name}.")
                        break
                    node_id = choice.next_id
                else:
                    print("Invalid choice.")
            except ValueError:
                print("Invalid input.")

    def action_travel(self):
        char = self.engine.character
        print("\n--- Travel ---")
        locations = self.engine.data_loader.get_all_locations()
        for i, loc in enumerate(locations):
            print(f"{i+1}. {loc.name} ({loc.type}) [Rank: {loc.danger_rank}]")

        try:
            l_idx = int(input("Select location: ")) - 1
            if 0 <= l_idx < len(locations):
                loc = locations[l_idx]
                print(f"\nArrived at {loc.name} [{loc.region}].")
                print(loc.description)

                if loc.connected_locations:
                    print(f"Connected to: {', '.join(loc.connected_locations)}")
                if loc.resources:
                    print(f"Resources: {', '.join(loc.resources)}")

                while True:
                    print("\nPoints of Interest:")
                    if loc.points_of_interest:
                        for k, poi in enumerate(loc.points_of_interest):
                            print(f"{k+1}. {poi.name} ({poi.type})")
                    else:
                        print("No specific points of interest.")

                    if loc.npcs:
                        print("\nPeople here:")
                        for k, npc_name in enumerate(loc.npcs):
                            print(f"{k+1}. {npc_name}")

                    print("\nOptions:")
                    print("1. Talk to someone")
                    print("2. Explore Point of Interest")
                    print("3. Leave")

                    sub_choice = input("> ").strip()
                    if sub_choice == "1":
                        if loc.npcs:
                            try:
                                npc_idx = int(input("Select person number: ")) - 1
                                if 0 <= npc_idx < len(loc.npcs):
                                    npc_name = loc.npcs[npc_idx]
                                    self.handle_conversation(npc_name)
                                else:
                                    print("Invalid selection.")
                            except ValueError:
                                print("Invalid input.")
                        else:
                            print("No one to talk to.")

                    elif sub_choice == "2":
                         if loc.points_of_interest:
                             try:
                                 poi_idx = int(input("Select POI number: ")) - 1
                                 if 0 <= poi_idx < len(loc.points_of_interest):
                                     poi = loc.points_of_interest[poi_idx]
                                     print(f"\n[{poi.name}]")
                                     print(poi.description)
                                 else:
                                     print("Invalid selection.")
                             except ValueError:
                                 print("Invalid input.")
                         else:
                             print("No points of interest to explore.")

                    elif sub_choice == "3":
                        print("Leaving location...")
                        break

                    else:
                        print("Invalid choice.")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")

    def action_view_map(self):
        self.map_viz.display_map()
        input("\nPress Enter to continue...")

    def action_exit(self):
        sys.exit()

def main():
    parser = argparse.ArgumentParser(description="Essence Bound: Progression Simulator")
    parser.add_argument("--load", help="Load a specific save file on startup")
    parser.add_argument("--new", help="Start a new game with the given character name")
    args = parser.parse_args()

    game = GameInterface()
    game.start(args)

if __name__ == "__main__":
    main()
