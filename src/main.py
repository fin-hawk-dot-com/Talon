import sys
import os
import random
import time
import argparse
from typing import Dict, Any, Callable

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models import Essence, AwakeningStone, Character, StatusEffect
from src.mechanics import GameEngine
from src.world_map import MapVisualizer
from src.console_ui import ui, Colors

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
        ui.clear()
        ui.print_header("Essence Bound: Progression Simulator")

        if args.load:
            ui.loading_effect("Loading Save")
            res = self.engine.load_game(args.load)
            ui.print_info(res)
            if not self.engine.character:
                 ui.print_error("Failed to load specified save file. Starting fresh.")

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

        choice = ui.menu_choice(["New Game", "Load Game"], "Welcome")

        if choice == 1: # Load Game (index 1)
            self.load_game_menu()
            if not self.engine.character:
                ui.print_info("Starting New Game.")
                self.create_character()
        else:
            self.create_character()

    def load_game_menu(self):
        saves = self.engine.get_save_files()
        if not saves:
            ui.print_warning("No save files found.")
            return

        choice = ui.menu_choice(saves, "Select Save File")
        if choice is not None:
             res = self.engine.load_game(saves[choice])
             ui.print_info(res)

    def create_character(self, name=None):
        if not name:
            name = input("Enter character name: ")

        race = "Human" # Simplified for now

        affinities = ["Warrior", "Mage", "Rogue", "Guardian", "Support", "General"]
        affinity_idx = ui.menu_choice(affinities, "Select Affinity (Focus)")
        affinity = affinities[affinity_idx]

        ui.loading_effect("Creating Character")
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

        ui.print_success(f"Character {name} created with affinity {affinity}.")
        time.sleep(1)

    def game_loop(self):
        while self.running:
            ui.clear()
            self.print_status()
            self.print_menu()

            try:
                choice = input(ui.colored("\nSelect Action > ", Colors.YELLOW)).strip()
            except KeyboardInterrupt:
                self.action_exit()

            action = self.menu_actions.get(choice)
            if action:
                action()
                if choice not in ["2", "10", "11"]: # Combat and Travel have their own loops/inputs, others are instant
                     input(ui.colored("\nPress Enter to continue...", Colors.GREY))
            else:
                ui.print_error("Invalid selection.")
                time.sleep(0.5)

    def print_status(self):
        char = self.engine.character
        ui.print_header(f"{char.name} the {char.race} | Rank: {char.rank}")

        print(ui.colored("Attributes:", Colors.BOLD))
        for attr in char.attributes.values():
            val_str = f"{attr.value:.1f}"
            print(f"  {ui.colored(attr.name, Colors.CYAN)}: {val_str} ({attr.rank}) [Mult: {attr.growth_multiplier}x]")

        print(ui.colored("\nEssences:", Colors.BOLD))
        for e in char.get_all_essences():
            print(f"  {ui.colored(e.name, Colors.MAGENTA if hasattr(Colors, 'MAGENTA') else Colors.HEADER)} ({e.bonded_attribute})")
            abilities = char.abilities.get(e.name, [])
            for i, ab in enumerate(abilities):
                if ab:
                    print(f"    Slot {i}: {ab.name} [{ab.rank} {ab.level}] - {ab.description}")
                else:
                    print(f"    Slot {i}: " + ui.colored("[Empty]", Colors.GREY))
        ui.print_separator()

    def print_menu(self):
        print(ui.colored("Actions:", Colors.BOLD))
        options = [
            "Train Attribute", "Adventure (Combat)", "Absorb Essence",
            "Awaken Ability", "Practice Ability", "Simulate Training",
            "Quest Log", "Grimoire", "System", "Travel / Interact", "View Map"
        ]

        # Split into two columns
        half = (len(options) + 1) // 2
        for i in range(half):
            left = f"{i+1}. {options[i]}"
            right_idx = i + half
            right = f"{right_idx+1}. {options[right_idx]}" if right_idx < len(options) else ""
            if right_idx == 9: right = "10. Travel / Interact" # Fix alignment manually if needed or just simple
            if right_idx == 10: right = "11. View Map"

            print(f"{left:<30} {right}")

        print("0. Exit")

    def action_train_attribute(self):
        print("\nSelect Attribute to train:")
        mapping = {'P': 'Power', 'S': 'Speed', 'M': 'Spirit', 'R': 'Recovery'}
        for k, v in mapping.items():
            print(f"{k}. {v}")

        attr_choice = input("> ").strip().upper()

        if attr_choice in mapping:
            ui.loading_effect("Training", 0.5)
            result = self.engine.training_mgr.train_attribute(self.engine.character, mapping[attr_choice])
            ui.print_success(f"\n{result}")
        else:
            ui.print_error("Invalid attribute.")

    def action_adventure(self):
        ui.clear()
        ui.print_header("Adventure")
        ui.slow_print("Searching for trouble...", speed=0.03)

        monsters = self.engine.data_loader.get_all_monsters()
        if not monsters:
            ui.print_error("No monsters found.")
            return

        m_name = random.choice(monsters)
        monster = self.engine.data_loader.get_monster(m_name)

        ui.print_warning(f"\nYou encountered a {monster.name} ({monster.rank})!")
        print(f"Health: {monster.current_health:.1f}/{monster.max_health:.1f}")
        time.sleep(1)

        char = self.engine.character
        while True:
            ui.clear()
            ui.print_header("Combat Encounter")

            # Status Bars
            def draw_bar(val, max_val, color, label, width=20):
                pct = val / max_val
                fill = int(pct * width)
                bar = "=" * fill + "-" * (width - fill)
                return f"{label}: [{ui.colored(bar, color)}] {val:.0f}/{max_val:.0f}"

            print(draw_bar(char.current_health, char.max_health, Colors.RED, "HP"))
            print(draw_bar(char.current_mana, char.max_mana, Colors.BLUE, "MP"))
            print(draw_bar(char.current_stamina, char.max_stamina, Colors.GREEN, "SP"))

            if char.status_effects:
                effects_str = " ".join([f"[{e.name} {e.duration}]" for e in char.status_effects])
                print(f"Effects: {effects_str}")

            ui.print_separator()
            print(f"Enemy: {monster.name}")
            print(draw_bar(monster.current_health, monster.max_health, Colors.RED, "HP"))
            if monster.status_effects:
                 effects_str = " ".join([f"[{e.name} {e.duration}]" for e in monster.status_effects])
                 print(f"Effects: {effects_str}")
            ui.print_separator()

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
                    ui.print_warning("No abilities available.")
                    time.sleep(1)
                    continue

                print("\nSelect Ability:")
                for i, ab in enumerate(abilities_flat):
                    cost_str = f"{ab.cost} {ab.parent_stone.cost_type}"
                    cd_str = ui.colored(f" [CD: {ab.current_cooldown}]", Colors.RED) if ab.current_cooldown > 0 else ""
                    print(f"{i+1}. {ab.name} ({cost_str}){cd_str}")

                try:
                    ab_idx_input = int(input("> ")) - 1
                    if 0 <= ab_idx_input < len(abilities_flat):
                        action = abilities_flat[ab_idx_input]
                    else:
                        continue
                except ValueError:
                    continue
            else:
                continue

            logs, combat_over = self.engine.combat_mgr.combat_round(char, monster, action)
            print("")
            for line in logs:
                ui.print_combat_log(line)
                time.sleep(0.3)

            input(ui.colored("\nPress Enter...", Colors.GREY))

            if combat_over:
                if monster.current_health <= 0:
                    self.handle_combat_victory(monster)
                elif char.current_health <= 0:
                    ui.print_error("You have been defeated. (Game Over - Reviving at temple...)")
                    char.current_health = char.max_health
                break

    def handle_combat_victory(self, monster):
        char = self.engine.character
        ui.print_success(f"You gained {monster.xp_reward} XP!")

        # Update Quests
        notifications = self.engine.quest_mgr.check_objectives(char, "kill", monster.name)
        for note in notifications:
            ui.print_info(f"! {note} !")

        # Loot
        loot_items = self.engine.loot_mgr.get_loot_for_monster(monster)
        if loot_items:
            print(ui.colored("Loot:", Colors.YELLOW))
            for loot_item_name in monster.loot_table:
                # Try to find as Essence or Stone
                item = self.engine.data_loader.get_essence(loot_item_name)
                if not item:
                    item = self.engine.data_loader.get_stone(loot_item_name)

                if item:
                    char.inventory.append(item)
                    print(f"- Found {ui.colored(item.name, Colors.GREEN)}!")

                    # Quest Check for Collection
                    col_notes = self.engine.quest_mgr.check_objectives(char, "collect", item.name)
                    for note in col_notes:
                        ui.print_info(f"! {note} !")
                else:
                    print(f"- Found unknown item: {loot_item_name}")

        # Random Loot Chance
        random_loot = self.engine.loot_mgr.generate_random_loot()
        if random_loot:
             char.inventory.append(random_loot)
             print(f"Random Drop: Found {ui.colored(random_loot.name, Colors.GREEN)}!")

        input("\nVictory! Press Enter...")

    def action_absorb_essence(self):
        char = self.engine.character
        if not char.inventory:
            ui.print_warning("Inventory empty.")
            return

        options = [f"{item.name} ({'Essence' if isinstance(item, Essence) else 'Stone'})" for item in char.inventory]
        idx = ui.menu_choice(options, "Select item to absorb")
        if idx is None: return

        item = char.inventory[idx]
        if isinstance(item, Essence):
            attr_options = ["Power", "Speed", "Spirit", "Recovery"]
            attr_idx = ui.menu_choice(attr_options, "Select Attribute to Bond")
            if attr_idx is not None:
                attr = attr_options[attr_idx]
                if attr in char.attributes:
                    ui.loading_effect("Absorbing")
                    res = self.engine.absorb_essence(idx, attr)
                    ui.print_success(res)
        else:
            ui.print_error("That is not an Essence.")

    def action_awaken_ability(self):
        char = self.engine.character
        if not char.inventory:
            ui.print_warning("Inventory empty.")
            return

        # Filter stones
        stones = [(i, item) for i, item in enumerate(char.inventory) if isinstance(item, AwakeningStone)]
        if not stones:
            ui.print_warning("No Awakening Stones in inventory.")
            return

        stone_opts = [s[1].name for s in stones]
        s_choice_idx = ui.menu_choice(stone_opts, "Select Awakening Stone")
        if s_choice_idx is None: return

        stone_inv_idx = stones[s_choice_idx][0]

        essences = char.get_all_essences()
        if not essences:
             ui.print_error("You have no bonded Essences.")
             return

        e_opts = [e.name for e in essences]
        e_choice_idx = ui.menu_choice(e_opts, "Select Essence to awaken on")
        if e_choice_idx is None: return

        essence_name = essences[e_choice_idx].name

        try:
            slot_idx = int(input("Enter Slot Index (0-4): "))
            ui.loading_effect("Awakening")
            res = self.engine.awaken_ability(essence_name, stone_inv_idx, slot_idx)
            ui.print_success(res)
        except ValueError:
            ui.print_error("Invalid input")

    def action_practice_ability(self):
        char = self.engine.character
        essences = char.get_all_essences()
        e_opts = [e.name for e in essences]
        e_idx = ui.menu_choice(e_opts, "Select Essence")
        if e_idx is None: return

        essence_name = essences[e_idx].name

        abilities = char.abilities.get(essence_name, [])
        ab_opts = []
        for i, ab in enumerate(abilities):
            if ab:
                 ab_opts.append(f"{ab.name} [Lvl {ab.level}]")
            else:
                 ab_opts.append("[Empty]")

        slot = ui.menu_choice(ab_opts, "Select Ability Slot")
        if slot is not None:
            res = self.engine.training_mgr.practice_ability(char, essence_name, slot)
            if res:
                ui.print_success("Ability Leveled Up!")
            else:
                ui.print_info("Practiced ability.")

    def action_simulate_training(self):
        ui.print_info("Simulating training montage...")
        char = self.engine.character
        ui.loading_effect("Training", 2.0)

        for attr_name in char.attributes:
            res = self.engine.training_mgr.train_attribute(char, attr_name)
            if "*** BREAKTHROUGH ***" in res:
                ui.print_success(res)

        for essence_name, abilities in char.abilities.items():
            for i, ability in enumerate(abilities):
                if ability:
                    leveled_up = self.engine.training_mgr.practice_ability(char, essence_name, i)
                    if leveled_up:
                        ui.print_success(f"{ability.name} leveled up to {ability.level}!")

                    if ability.level == 9:
                        rank_up_msg = self.engine.training_mgr.attempt_rank_up_ability(char, essence_name, i)
                        if "Success" in rank_up_msg:
                            ui.print_header(f"RANK UP: {ability.name}")
                            print(rank_up_msg)

    def action_quest_log(self):
        char = self.engine.character
        ui.print_header("Quest Log")

        active_quests = [q_id for q_id, prog in char.quests.items() if prog.status == "Active"]
        if active_quests:
            print(ui.colored("Active Quests:", Colors.YELLOW))
            for q_id in active_quests:
                q = self.engine.quest_mgr.data_loader.get_quest(q_id)
                prog = char.quests[q_id]
                stage = q.stages.get(prog.current_stage_id)

                objectives_text = ""
                if stage.objectives:
                    objectives_text = "\n    Objectives:"
                    for obj in stage.objectives:
                        key = f"{obj.type}:{obj.target}"
                        current = prog.objectives_progress.get(key, 0)
                        objectives_text += f"\n    - {obj.type} {obj.target}: {current}/{obj.count}"

                print(f"- {ui.colored(q.title, Colors.BOLD)}: {stage.description}{objectives_text}")
        else:
            print("No active quests.")

        choice = ui.menu_choice(["Find New Quest", "Continue Quest", "Back"], "Options")

        if choice == 0:
            available = self.engine.quest_mgr.get_available_quests(char)
            if not available:
                ui.print_warning("No new quests available.")
            else:
                q_opts = [f"{q.title} ({q.type})" for q in available]
                q_idx = ui.menu_choice(q_opts, "Select quest to start")
                if q_idx is not None:
                    res = self.engine.quest_mgr.start_quest(char, available[q_idx].id)
                    ui.print_success(res)

        elif choice == 1:
            if not active_quests:
                ui.print_warning("No active quests.")
            else:
                active_list = [self.engine.quest_mgr.data_loader.get_quest(q_id) for q_id in active_quests]
                q_opts = [q.title for q in active_list]

                q_idx = ui.menu_choice(q_opts, "Select Quest to continue")
                if q_idx is not None:
                    q = active_list[q_idx]
                    stage_id = char.quests[q.id].current_stage_id
                    stage = q.stages.get(stage_id)

                    ui.print_header(q.title)
                    ui.slow_print(stage.description)

                    if not stage.choices:
                        ui.print_error("(No choices available)")
                    else:
                        c_opts = [c.text for c in stage.choices]
                        c_idx = ui.menu_choice(c_opts, "Make a choice")
                        if c_idx is not None:
                            res = self.engine.quest_mgr.make_choice(char, q.id, c_idx)
                            ui.print_info(f"\n> {res}")

    def action_grimoire(self):
        char = self.engine.character
        ui.print_header("Grimoire")
        if not char.lore:
            ui.print_info("You have not discovered any lore yet.")
        else:
            categories = {}
            for lore_id in char.lore:
                entry = self.engine.data_loader.get_lore(lore_id)
                if entry:
                    if entry.category not in categories:
                        categories[entry.category] = []
                    categories[entry.category].append(entry)

            for cat, entries in categories.items():
                print(f"\n[{ui.colored(cat, Colors.CYAN)}]")
                for entry in entries:
                    print(f"  - {ui.colored(entry.title, Colors.BOLD)}: {entry.text}")

    def action_system(self):
        choice = ui.menu_choice(["Save Game", "Load Game", "Back"], "System Menu")
        if choice == 0:
            filename = input("Enter save filename: ")
            print(self.engine.save_game(filename))
        elif choice == 1:
            self.load_game_menu()

    def handle_conversation(self, npc_name):
        node_id = "root"
        ui.clear()
        ui.print_header(f"Talking to {npc_name}")

        while True:
            node = self.engine.interaction_mgr.get_dialogue_node(npc_name, node_id)
            if not node:
                ui.print_info(f"{npc_name} has nothing more to say.")
                break

            ui.print_dialogue(npc_name, node.text)

            if not node.choices:
                input("[Press Enter to end conversation]")
                break

            print("\n")
            opts = [c.text for c in node.choices]
            c_idx = ui.menu_choice(opts, "Your response")

            if c_idx is not None:
                choice = node.choices[c_idx]
                if choice.next_id == "exit":
                    ui.print_info(f"You end the conversation with {npc_name}.")
                    break
                node_id = choice.next_id

    def action_travel(self):
        char = self.engine.character
        ui.clear()
        ui.print_header("Travel")
        locations = self.engine.data_loader.get_all_locations()

        loc_opts = [f"{loc.name} ({loc.type}) [Rank: {loc.danger_rank}]" for loc in locations]
        l_idx = ui.menu_choice(loc_opts, "Select location")

        if l_idx is not None:
            loc = locations[l_idx]
            ui.loading_effect("Traveling")
            ui.clear()
            ui.print_header(f"{loc.name} [{loc.region}]")
            ui.slow_print(loc.description)

            if loc.connected_locations:
                print(f"\nConnected to: {', '.join(loc.connected_locations)}")
            if loc.resources:
                print(f"Resources: {', '.join(loc.resources)}")

            while True:
                print(ui.colored("\n--- Location Menu ---", Colors.BLUE))

                # Dynamic menu building
                options = ["Talk to someone", "Explore Point of Interest", "Leave"]
                choice_idx = ui.menu_choice(options, "What do you want to do?")

                if choice_idx == 0: # Talk
                    if loc.npcs:
                        npc_idx = ui.menu_choice(loc.npcs, "Select person")
                        if npc_idx is not None:
                            self.handle_conversation(loc.npcs[npc_idx])
                            ui.clear() # Re-clear after talking
                            ui.print_header(f"{loc.name}") # Reprint header
                    else:
                        ui.print_info("No one here.")

                elif choice_idx == 1: # POI
                     if loc.points_of_interest:
                         poi_opts = [f"{p.name} ({p.type})" for p in loc.points_of_interest]
                         poi_idx = ui.menu_choice(poi_opts, "Select POI")
                         if poi_idx is not None:
                             poi = loc.points_of_interest[poi_idx]
                             print(f"\n[{ui.colored(poi.name, Colors.BOLD)}]")
                             ui.slow_print(poi.description)
                     else:
                         ui.print_info("No points of interest.")

                elif choice_idx == 2: # Leave
                    print("Leaving location...")
                    break

    def action_view_map(self):
        ui.clear()
        self.map_viz.display_map()
        input("\nPress Enter to continue...")

    def action_exit(self):
        ui.print_info("Goodbye!")
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
