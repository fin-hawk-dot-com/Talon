import tkinter as tk
from tkinter import ttk, messagebox, font
import sys
import os
import math

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.mechanics import GameEngine
from src.models import Character
from src.map_widget import MapWidget

class GameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Essence Bound - RPG")
        self.root.geometry("1200x800")

        # Game State
        self.engine = GameEngine()
        self.state = "MAIN_MENU" # MAIN_MENU, HUB, COMBAT, DIALOGUE
        self.current_monster = None

        # Styles
        self.setup_styles()

        # Layout
        self.create_layout()

        # Bindings
        self.root.bind("<w>", lambda e: self.handle_movement("North"))
        self.root.bind("<a>", lambda e: self.handle_movement("West"))
        self.root.bind("<s>", lambda e: self.handle_movement("South"))
        self.root.bind("<d>", lambda e: self.handle_movement("East"))
        self.root.bind("<W>", lambda e: self.handle_movement("North"))
        self.root.bind("<A>", lambda e: self.handle_movement("West"))
        self.root.bind("<S>", lambda e: self.handle_movement("South"))
        self.root.bind("<D>", lambda e: self.handle_movement("East"))

        # Initial Screen
        self.show_main_menu()

    def handle_movement(self, direction):
        if self.state != "HUB" or not self.engine.character:
            return

        char = self.engine.character
        curr_loc_name = char.current_location
        # Need to fetch object from loader
        curr_loc = self.engine.data_loader.get_location(curr_loc_name)

        if not curr_loc: return

        # Target vectors
        vectors = {
            "North": (0, -1),
            "South": (0, 1),
            "West": (-1, 0),
            "East": (1, 0)
        }
        target_dx, target_dy = vectors[direction]

        best_neighbor = None
        best_score = -1.0 # Cosine similarity

        for neighbor_name in curr_loc.connected_locations:
            n_loc = self.engine.data_loader.get_location(neighbor_name)
            if not n_loc: continue

            # Vector to neighbor
            # Use getattr with defaults just in case
            nx = getattr(n_loc, 'x', 500)
            ny = getattr(n_loc, 'y', 500)
            cx = getattr(curr_loc, 'x', 500)
            cy = getattr(curr_loc, 'y', 500)

            dx = nx - cx
            dy = ny - cy

            # Normalize
            dist = math.sqrt(dx*dx + dy*dy)
            if dist == 0: continue

            ndx = dx / dist
            ndy = dy / dist

            # Dot product
            score = ndx * target_dx + ndy * target_dy

            # Threshold: Must be roughly in that direction (> 0.5 is 60 deg cone)
            if score > 0.5 and score > best_score:
                best_score = score
                best_neighbor = neighbor_name

        if best_neighbor:
            # Travel
            res = self.engine.travel(best_neighbor)
            self.log(res, "event")
            self.update_status_display() # Updates map too
        else:
            self.log(f"No path {direction}.", "info")

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')

        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=10)

        self.style.configure("TButton", padding=6, font=('Helvetica', 10))
        self.style.configure("Title.TLabel", font=('Helvetica', 18, 'bold'))
        self.style.configure("Status.TLabel", font=('Consolas', 10))

    def create_layout(self):
        # Main Container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # 1. Top Menubar (Native)
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Game", command=self.confirm_new_game)
        file_menu.add_command(label="Save Game", command=self.save_game_dialog)
        file_menu.add_command(label="Load Game", command=self.load_game_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # 2. Left Panel: Character Status
        self.left_panel = ttk.Frame(self.main_container, width=250, relief=tk.RIDGE, borderwidth=2)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.left_panel.pack_propagate(False) # Don't shrink

        ttk.Label(self.left_panel, text="Character Status", style="Title.TLabel").pack(pady=10)
        self.status_text = tk.Text(self.left_panel, wrap=tk.WORD, height=30, bg="#2b2b2b", fg="#e0e0e0", relief=tk.FLAT, state=tk.DISABLED, font=('Consolas', 9))
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 3. Center Panel: Map + Game Log
        self.center_container = ttk.Frame(self.main_container)
        self.center_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Map (Top)
        self.map_widget = MapWidget(self.center_container, self.engine, height=350)
        self.map_widget.pack(fill=tk.BOTH, expand=False, pady=(0, 5))

        # Log (Bottom)
        self.center_panel = ttk.Frame(self.center_container, relief=tk.SUNKEN, borderwidth=2)
        self.center_panel.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(self.center_panel, wrap=tk.WORD, state=tk.DISABLED, font=('Georgia', 11), bg="#1e1e1e", fg="#cccccc")
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        log_scroll = ttk.Scrollbar(self.center_panel, orient=tk.VERTICAL, command=self.log_text.yview)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.configure(yscrollcommand=log_scroll.set)

        # Tag configs for coloring text
        self.log_text.tag_config("info", foreground="#cccccc")
        self.log_text.tag_config("combat", foreground="#ff5555")
        self.log_text.tag_config("gain", foreground="#55ff55")
        self.log_text.tag_config("event", foreground="#55aaff")
        self.log_text.tag_config("error", foreground="#ffaaff")

        # 4. Right Panel: Actions
        self.right_panel = ttk.Frame(self.main_container, width=200, relief=tk.RIDGE, borderwidth=2)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        self.right_panel.pack_propagate(False)

        ttk.Label(self.right_panel, text="Actions", style="Title.TLabel").pack(pady=10)

        self.action_frame = ttk.Frame(self.right_panel)
        self.action_frame.pack(fill=tk.BOTH, expand=True, padx=5)

    def log(self, message, tag="info"):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n", tag)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def clear_actions(self):
        for widget in self.action_frame.winfo_children():
            widget.destroy()

    def add_action_button(self, text, command):
        btn = ttk.Button(self.action_frame, text=text, command=command)
        btn.pack(fill=tk.X, pady=2)
        return btn

    def update_status_display(self):
        if not self.engine.character:
            self.status_text.config(state=tk.NORMAL)
            self.status_text.delete("1.0", tk.END)
            self.status_text.insert(tk.END, "No Character Loaded")
            self.status_text.config(state=tk.DISABLED)
            return

        char = self.engine.character
        text = f"Name: {char.name}\n"
        text += f"Race: {char.race}\n"
        text += f"Rank: {char.rank}\n"
        text += f"XP: {char.current_xp}\n"
        text += f"Dram: {char.currency}\n"
        text += "-"*20 + "\n"
        text += f"HP: {char.current_health:.0f}/{char.max_health:.0f}\n"
        text += f"MP: {char.current_mana:.0f}/{char.max_mana:.0f}\n"
        text += f"SP: {char.current_stamina:.0f}/{char.max_stamina:.0f}\n"

        if char.status_effects:
            text += "-"*10 + "\n"
            text += "Status Effects:\n"
            for e in char.status_effects:
                text += f"[{e.name} {e.duration}]\n"

        active_q_count = len([q for q in char.quests.values() if q.status == "Active"])
        if active_q_count > 0:
            text += f"Active Quests: {active_q_count}\n"

        text += "-"*20 + "\n"
        text += "Attributes:\n"
        for attr in char.attributes.values():
            text += f" {attr.name[:3]}: {attr.value:.1f} ({attr.rank})\n"

        text += "-"*20 + "\n"
        text += "Equipment/Essences:\n"
        for e in char.get_all_essences():
            text += f"- {e.name}\n"

        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete("1.0", tk.END)
        self.status_text.insert(tk.END, text)
        self.status_text.config(state=tk.DISABLED)

        # Also update map
        self.map_widget.refresh()

    # --- MENUS & STATES ---

    def show_main_menu(self):
        self.state = "MAIN_MENU"
        self.clear_actions()
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)

        self.log("Welcome to Essence Bound.", "event")

        self.add_action_button("New Game", self.new_game_setup)
        self.add_action_button("Load Game", self.load_game_dialog)
        self.add_action_button("Exit", self.root.quit)

    def confirm_new_game(self):
        if messagebox.askyesno("New Game", "Are you sure? Unsaved progress will be lost."):
            self.new_game_setup()

    def new_game_setup(self):
        # Simple popup for name
        popup = tk.Toplevel(self.root)
        popup.title("Create Character")
        popup.geometry("300x200")

        ttk.Label(popup, text="Character Name:").pack(pady=5)
        name_entry = ttk.Entry(popup)
        name_entry.pack(pady=5)

        ttk.Label(popup, text="Affinity:").pack(pady=5)
        affinity_var = tk.StringVar(value="General")
        affinities = ["Warrior", "Mage", "Rogue", "Guardian", "Support", "General"]
        affinity_combo = ttk.Combobox(popup, textvariable=affinity_var, values=affinities)
        affinity_combo.pack(pady=5)

        def confirm():
            name = name_entry.get()
            if not name: return

            self.engine.create_character(name, "Human")
            self.engine.character.affinity = affinity_var.get()

            # Starter Items
            starter_essence = self.engine.data_loader.get_essence("Dark")
            if starter_essence:
                self.engine.character.inventory.append(starter_essence)
            starter_stone = self.engine.data_loader.get_stone("Stone of the Strike")
            if starter_stone:
                self.engine.character.inventory.append(starter_stone)

            popup.destroy()
            self.log(f"Character {name} created!", "event")
            self.enter_hub()

        ttk.Button(popup, text="Start Adventure", command=confirm).pack(pady=20)

    def load_game_dialog(self):
        saves = self.engine.get_save_files()
        if not saves:
            messagebox.showinfo("Load Game", "No save files found.")
            return

        popup = tk.Toplevel(self.root)
        popup.title("Load Game")
        popup.geometry("300x300")

        lb = tk.Listbox(popup)
        lb.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        for s in saves:
            lb.insert(tk.END, s)

        def load():
            sel = lb.curselection()
            if not sel: return
            fname = lb.get(sel[0])
            res = self.engine.load_game(fname)
            self.log(res, "event")
            popup.destroy()
            if self.engine.character:
                self.enter_hub()

        ttk.Button(popup, text="Load", command=load).pack(pady=10)

    def save_game_dialog(self):
        if not self.engine.character: return

        popup = tk.Toplevel(self.root)
        popup.title("Save Game")
        popup.geometry("300x150")

        ttk.Label(popup, text="Filename:").pack(pady=5)
        name_entry = ttk.Entry(popup)
        name_entry.insert(0, f"{self.engine.character.name}_save.json")
        name_entry.pack(pady=5)

        def save():
            fname = name_entry.get()
            if not fname.endswith(".json"): fname += ".json"
            res = self.engine.save_game(fname)
            self.log(res, "event")
            popup.destroy()

        ttk.Button(popup, text="Save", command=save).pack(pady=10)

    # --- GAMEPLAY: HUB ---

    def enter_hub(self):
        self.state = "HUB"
        self.update_status_display()
        self.clear_actions()

        self.log("\n--- You are in a safe location ---", "info")

        self.add_action_button("Train Attribute", self.show_train_options)
        self.add_action_button("Adventure (Combat)", self.start_combat_encounter)
        self.add_action_button("Inventory / Absorb", self.show_inventory_options)
        self.add_action_button("Awaken Ability", self.show_awaken_options)
        self.add_action_button("Quests", self.show_quest_log)
        self.add_action_button("Rest (Save)", self.save_game_dialog)
        self.add_action_button("Main Menu", self.show_main_menu)

    def show_train_options(self):
        self.clear_actions()
        self.add_action_button("<< Back", self.enter_hub)

        def train(attr):
            self.engine.training_mgr.train_attribute(self.engine.character, attr)
            self.log(f"Trained {attr}!", "gain")
            self.update_status_display()

        self.add_action_button("Train Power", lambda: train("Power"))
        self.add_action_button("Train Speed", lambda: train("Speed"))
        self.add_action_button("Train Spirit", lambda: train("Spirit"))
        self.add_action_button("Train Recovery", lambda: train("Recovery"))

    def show_inventory_options(self):
        self.clear_actions()
        self.add_action_button("<< Back", self.enter_hub)

        char = self.engine.character
        if not char.inventory:
            self.log("Inventory is empty.", "info")
            return

        def use_item(idx):
            item = char.inventory[idx]
            # Simple Absorb logic for Essences
            if hasattr(item, 'type'): # Essence
                # Ask for attribute (simplified: just popup)
                self.absorb_essence_dialog(idx)
            else:
                self.log(f"Cannot 'use' {item.name} directly. Use Awaken menu.", "error")

        for i, item in enumerate(char.inventory):
            self.add_action_button(f"{item.name}", lambda idx=i: use_item(idx))

    def absorb_essence_dialog(self, idx):
        # Simplified dialog to pick attribute
        popup = tk.Toplevel(self.root)
        popup.title("Absorb Essence")
        ttk.Label(popup, text="Bond with which attribute?").pack(pady=10)

        def confirm(attr):
            res = self.engine.absorb_essence(idx, attr)
            self.log(res, "event")
            self.update_status_display()
            popup.destroy()
            self.show_inventory_options() # Refresh

        ttk.Button(popup, text="Power", command=lambda: confirm("Power")).pack()
        ttk.Button(popup, text="Speed", command=lambda: confirm("Speed")).pack()
        ttk.Button(popup, text="Spirit", command=lambda: confirm("Spirit")).pack()
        ttk.Button(popup, text="Recovery", command=lambda: confirm("Recovery")).pack()

    def show_awaken_options(self):
        # Simplified flow: Select Stone -> Select Essence -> Select Slot
        # This is complex to GUI-ify in one go, so I'll just check if possible
        char = self.engine.character
        stones = [x for x in char.inventory if hasattr(x, 'function')]

        if not stones:
            self.log("No Awakening Stones in inventory.", "error")
            return

        self.log("Logic for Awakening via GUI is complex (needs wizard). Use CLI for full features or wait for updates.", "error")
        # For now, just placeholder or basic hint

    def show_quest_log(self):
        self.clear_actions()
        self.add_action_button("<< Back", self.enter_hub)

        char = self.engine.character

        self.log("\n--- Quest Log ---", "info")
        active = [q for q in char.quests.values() if q.status == "Active"]
        if not active:
            self.log("No active quests.", "info")
        else:
            for qp in active:
                quest = self.engine.data_loader.get_quest(qp.quest_id)
                self.log(f"Active: {quest.title}", "event")

        # Available quests
        available = self.engine.quest_mgr.get_available_quests(char)
        if available:
            self.add_action_button("Find New Quests", self.show_available_quests)

    def show_available_quests(self):
        self.clear_actions()
        self.add_action_button("<< Back", self.show_quest_log)

        char = self.engine.character
        available = self.engine.quest_mgr.get_available_quests(char)

        def start(q_id):
            res = self.engine.quest_mgr.start_quest(char, q_id)
            self.log(res, "event")
            self.show_quest_log()

        for q in available:
            self.add_action_button(f"Start: {q.title}", lambda qid=q.id: start(qid))

    # --- COMBAT ---

    def start_combat_encounter(self):
        import random
        monsters = self.engine.data_loader.get_all_monsters()
        if not monsters:
            self.log("No monsters found in data!", "error")
            return

        m_name = random.choice(monsters)
        self.current_monster = self.engine.data_loader.get_monster(m_name)

        self.log(f"\n!!! ENCOUNTER !!!", "combat")
        self.log(f"You faced a {self.current_monster.name} ({self.current_monster.rank})!", "combat")

        self.enter_combat_mode()

    def enter_combat_mode(self):
        self.state = "COMBAT"
        self.clear_actions()

        self.add_action_button("Attack", lambda: self.combat_round("Attack"))
        self.add_action_button("Abilities", self.show_combat_abilities)
        self.add_action_button("Flee", lambda: self.combat_round("Flee"))

        self.update_combat_status()

    def update_combat_status(self):
        self.update_status_display()
        m = self.current_monster
        self.log(f"Enemy HP: {m.current_health:.0f}/{m.max_health:.0f}", "combat")

    def show_combat_abilities(self):
        self.clear_actions()
        self.add_action_button("<< Back", self.enter_combat_mode)

        char = self.engine.character
        # Collect all abilities
        abilities_flat = []
        for ess_name, slots in char.abilities.items():
            for ab in slots:
                if ab: abilities_flat.append(ab)

        if not abilities_flat:
            self.log("No abilities available.", "error")
            return

        def use_ab(ab):
            self.combat_round(ab)

        for ab in abilities_flat:
            txt = f"{ab.name} (CD:{ab.current_cooldown})"
            if ab.current_cooldown > 0:
                self.add_action_button(txt, lambda: None) # Disabled-ish
            else:
                self.add_action_button(txt, lambda a=ab: use_ab(a))

    def combat_round(self, action):
        if not self.current_monster or self.state != "COMBAT": return

        char = self.engine.character
        monster = self.current_monster

        logs, combat_over = self.engine.combat_mgr.combat_round(char, monster, action)

        for line in logs:
            tag = "combat" if "damage" in line else "info"
            self.log(line, tag)

        if combat_over:
            if char.current_health <= 0:
                self.log("You have died...", "combat")
                # Respawn logic
                char.current_health = char.max_health
                self.log("Revived at temple.", "event")
                self.enter_hub()
            elif monster.current_health <= 0:
                self.log(f"Victory! Gained {monster.xp_reward} XP.", "gain")
                # Loot logic simplified
                loot = self.engine.loot_mgr.get_loot_for_monster(monster)
                for item in loot:
                    char.inventory.append(item)
                    self.log(f"Loot: {item.name}", "gain")

                self.enter_hub()
            else:
                # Fled
                self.enter_hub()
        else:
            self.update_combat_status()
            if self.state == "COMBAT":
                self.enter_combat_mode() # Refresh buttons if we were in ability menu

if __name__ == "__main__":
    root = tk.Tk()
    app = GameApp(root)
    root.mainloop()
