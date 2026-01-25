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
        self.pressed_keys = {'w': False, 'a': False, 's': False, 'd': False}
        for key in ['w', 'a', 's', 'd', 'W', 'A', 'S', 'D']:
            self.root.bind(f"<KeyPress-{key}>", self.on_key_press)
            self.root.bind(f"<KeyRelease-{key}>", self.on_key_release)

        self.root.bind("<e>", lambda e: self.handle_interaction())
        self.root.bind("<E>", lambda e: self.handle_interaction())
        self.root.bind("<m>", lambda e: self.toggle_map_mode())
        self.root.bind("<M>", lambda e: self.toggle_map_mode())

        # Dialogue State
        self.dialogue_npc_name = None
        self.dialogue_visited_roots = set()

        # Start Game Loop
        self.movement_loop()

        # Initial Screen
        self.show_main_menu()

    def on_key_press(self, event):
        key = event.char.lower()
        if key in self.pressed_keys:
            self.pressed_keys[key] = True

    def on_key_release(self, event):
        key = event.char.lower()
        if key in self.pressed_keys:
            self.pressed_keys[key] = False

    def handle_interaction(self):
        if self.state != "HUB" or not self.engine.character:
            return

        char = self.engine.character
        curr_loc_name = char.current_location
        loc = self.engine.data_loader.get_location(curr_loc_name)
        if not loc: return

        # Check for NPCs
        if loc.npcs:
            # For simplicity, if multiple, just pick first or show list.
            # Showing a list in Actions panel is best.
            if len(loc.npcs) == 1:
                self.start_dialogue(loc.npcs[0])
            else:
                self.show_interaction_menu(loc.npcs, loc.points_of_interest)
            return

        # Check POIs if no NPCs
        if loc.points_of_interest:
             self.show_interaction_menu([], loc.points_of_interest)
             return

        self.log("Nothing to interact with here.", "info")

    def show_interaction_menu(self, npcs, pois):
        self.clear_actions()
        self.add_action_button("<< Cancel", self.enter_hub)
        self.log("\n--- Interact ---", "info")

        for npc in npcs:
            self.add_action_button(f"Talk to {npc}", lambda n=npc: self.start_dialogue(n))

        for poi in pois:
             # Placeholder for POI interaction
            self.add_action_button(f"Inspect {poi.name}", lambda p=poi: self.log(f"{p.name}: {p.description}", "event"))

    def start_dialogue(self, npc_name):
        self.state = "DIALOGUE"
        self.dialogue_npc_name = npc_name
        self.dialogue_visited_roots = set()
        self.log(f"\n--- Dialogue: {npc_name} ---", "event")
        self.show_dialogue_node("root")

    def show_dialogue_node(self, node_id):
        node = self.engine.interaction_mgr.get_dialogue_node(self.dialogue_npc_name, node_id)
        if not node:
            self.log("Dialogue Error: Node not found.", "error")
            self.enter_hub()
            return

        self.clear_actions()

        # Determine Text (Handle Hub Logic)
        text_to_show = node.text
        if node_id == "root":
            if self.dialogue_npc_name in self.dialogue_visited_roots and node.hub_text:
                text_to_show = node.hub_text
            self.dialogue_visited_roots.add(self.dialogue_npc_name)

        # Show Text in Log
        # Use a distinct color for dialogue
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{self.dialogue_npc_name}: \"{text_to_show}\"\n", "info")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

        # Show Choices
        for choice in node.choices:
            if choice.next_id == "exit":
                self.add_action_button(choice.text, self.enter_hub)
            else:
                self.add_action_button(choice.text, lambda nid=choice.next_id: self.show_dialogue_node(nid))

    def movement_loop(self):
        if self.state == "HUB" and self.engine.character:
            dx, dy = 0.0, 0.0
            speed = 4.0

            if self.pressed_keys['w']: dy -= speed
            if self.pressed_keys['s']: dy += speed
            if self.pressed_keys['a']: dx -= speed
            if self.pressed_keys['d']: dx += speed

            if dx != 0 or dy != 0:
                if dx != 0 and dy != 0:
                    dx *= 0.7071
                    dy *= 0.7071

                msg = self.engine.update_position(int(dx), int(dy))
                if msg:
                    self.log(msg, "event")
                    self.update_status_display()

                self.map_widget.refresh()

        elif self.state == "MEDITATION" and self.engine.character:
             if not hasattr(self, 'meditation_counter'): self.meditation_counter = 0
             self.meditation_counter += 1
             if self.meditation_counter >= 50: # Approx 1 second
                 self.meditation_counter = 0
                 self.engine.meditate_tick()
                 self.update_status_display()

        self.root.after(20, self.movement_loop)

    def toggle_map_mode(self):
        new_mode = 'mini' if self.map_widget.mode == 'world' else 'world'
        self.map_widget.set_mode(new_mode)
        self.log(f"Map switched to {new_mode} view.", "info")

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

        # Details Text (Name, Race, Rank, XP, Dram)
        self.status_details_text = tk.Text(self.left_panel, wrap=tk.WORD, height=8, bg="#2b2b2b", fg="#e0e0e0", relief=tk.FLAT, state=tk.DISABLED, font=('Consolas', 9))
        self.status_details_text.pack(fill=tk.X, padx=5, pady=5)

        # Bars
        self.bars_frame = ttk.Frame(self.left_panel)
        self.bars_frame.pack(fill=tk.X, padx=5, pady=5)

        self.hp_bar, self.hp_val = self.create_resource_bar("Health", "#ff5555")
        self.mp_bar, self.mp_val = self.create_resource_bar("Mana", "#5555ff")
        self.sp_bar, self.sp_val = self.create_resource_bar("Stamina", "#55ff55")
        self.wp_bar, self.wp_val = self.create_resource_bar("Willpower", "#aa55aa")

        # Attributes
        ttk.Label(self.left_panel, text="Attributes & Effects", font=('Helvetica', 12, 'bold')).pack(pady=(10, 5))
        self.attributes_text = tk.Text(self.left_panel, wrap=tk.WORD, height=15, bg="#2b2b2b", fg="#e0e0e0", relief=tk.FLAT, state=tk.DISABLED, font=('Consolas', 9))
        self.attributes_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 3. Center Panel: Map + Game Log
        self.center_container = ttk.Frame(self.main_container)
        self.center_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Map (Top)
        self.map_widget = MapWidget(self.center_container, self.engine, height=350)
        self.map_widget.pack(fill=tk.BOTH, expand=False, pady=(0, 5))

        # Map Controls
        self.map_controls = ttk.Frame(self.center_container)
        self.map_controls.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(self.map_controls, text="Toggle Map Mode (M)", command=self.toggle_map_mode).pack(side=tk.RIGHT)

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

    def create_resource_bar(self, name, color):
        frame = ttk.Frame(self.bars_frame)
        frame.pack(fill=tk.X, pady=2)

        lbl_frame = ttk.Frame(frame)
        lbl_frame.pack(fill=tk.X)
        ttk.Label(lbl_frame, text=name, font=('Consolas', 9)).pack(side=tk.LEFT)
        val_lbl = ttk.Label(lbl_frame, text="0/0", font=('Consolas', 9))
        val_lbl.pack(side=tk.RIGHT)

        # Style for colored bar
        style_name = f"{name}.Horizontal.TProgressbar"
        self.style.configure(style_name, troughcolor='#404040', background=color, thickness=15)

        bar = ttk.Progressbar(frame, style=style_name, orient=tk.HORIZONTAL, mode='determinate', length=200)
        bar.pack(fill=tk.X)

        return bar, val_lbl

    def update_bar(self, bar, label, current, maximum):
        bar['maximum'] = maximum
        bar['value'] = current
        label.config(text=f"{int(current)}/{int(maximum)}")

    def update_status_display(self):
        if not self.engine.character:
            self.status_details_text.config(state=tk.NORMAL)
            self.status_details_text.delete("1.0", tk.END)
            self.status_details_text.insert(tk.END, "No Character Loaded")
            self.status_details_text.config(state=tk.DISABLED)
            return

        char = self.engine.character

        # Details
        text = f"Name: {char.name}\n"
        text += f"Race: {char.race}\n"
        text += f"Rank: {char.rank}\n"
        text += f"XP: {char.current_xp}\n"
        text += f"Dram: {char.currency}\n"

        active_q_count = len([q for q in char.quests.values() if q.status == "Active"])
        if active_q_count > 0:
            text += f"Active Quests: {active_q_count}\n"

        self.status_details_text.config(state=tk.NORMAL)
        self.status_details_text.delete("1.0", tk.END)
        self.status_details_text.insert(tk.END, text)
        self.status_details_text.config(state=tk.DISABLED)

        # Bars
        self.update_bar(self.hp_bar, self.hp_val, char.current_health, char.max_health)
        self.update_bar(self.mp_bar, self.mp_val, char.current_mana, char.max_mana)
        self.update_bar(self.sp_bar, self.sp_val, char.current_stamina, char.max_stamina)
        self.update_bar(self.wp_bar, self.wp_val, char.current_willpower, char.max_willpower)

        # Attributes & Rest
        text = "Attributes:\n"
        for attr in char.attributes.values():
            text += f" {attr.name[:3]}: {attr.value:.1f} ({attr.rank})\n"

        text += "-"*10 + "\n"
        text += "Status Effects:\n"
        for e in char.status_effects:
             text += f"[{e.name} {e.duration}]\n"

        text += "-"*10 + "\n"
        text += "Equipment/Essences:\n"
        for e in char.get_all_essences():
            text += f"- {e.name}\n"

        self.attributes_text.config(state=tk.NORMAL)
        self.attributes_text.delete("1.0", tk.END)
        self.attributes_text.insert(tk.END, text)
        self.attributes_text.config(state=tk.DISABLED)

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
        self.add_action_button("Meditate", self.start_meditation)
        self.add_action_button("Adventure (Combat)", self.start_combat_encounter)
        self.add_action_button("Inventory / Absorb", self.show_inventory_options)
        self.add_action_button("Awaken Ability", self.show_awaken_options)
        self.add_action_button("Quests", self.show_quest_log)
        self.add_action_button("Rest (Save)", self.save_game_dialog)
        self.add_action_button("Main Menu", self.show_main_menu)

    def start_meditation(self):
        self.state = "MEDITATION"
        self.clear_actions()
        self.log("\n--- Entering Meditation ---", "event")
        self.log("You focus your mind to gather energy.", "info")
        self.add_action_button("Stop Meditating", self.enter_hub)

    def show_train_options(self):
        self.clear_actions()
        self.add_action_button("<< Back", self.enter_hub)

        def train(attr):
            msg = self.engine.train_attribute(attr)
            self.log(msg, "gain")
            self.update_status_display()

        self.add_action_button("Train Power", lambda: train("Power"))
        self.add_action_button("Train Speed", lambda: train("Speed"))
        self.add_action_button("Train Spirit", lambda: train("Spirit"))
        self.add_action_button("Train Recovery", lambda: train("Recovery"))

        self.add_action_button("Practice Ability", self.show_practice_ability_options)
        self.add_action_button("Rank Up Ability", self.show_rank_up_ability_options)

    def show_practice_ability_options(self):
        self.clear_actions()
        self.add_action_button("<< Back", self.show_train_options)

        char = self.engine.character
        found_any = False

        for ess_name, slots in char.abilities.items():
            for i, ab in enumerate(slots):
                if ab:
                    found_any = True
                    txt = f"{ab.name} (Lvl {ab.level})"
                    self.add_action_button(txt, lambda e=ess_name, s=i: self.perform_practice(e, s))

        if not found_any:
            self.log("No abilities to practice.", "info")

    def perform_practice(self, essence_name, slot_index):
        msg = self.engine.practice_ability(essence_name, slot_index)
        tag = "gain" if "XP" in msg else "info"
        if "Level Up" in msg: tag = "event"
        self.log(msg, tag)
        self.show_practice_ability_options() # Refresh to show new level

    def show_rank_up_ability_options(self):
        self.clear_actions()
        self.add_action_button("<< Back", self.show_train_options)

        char = self.engine.character
        found_any = False

        for ess_name, slots in char.abilities.items():
            for i, ab in enumerate(slots):
                if ab and self.engine.can_rank_up_ability(ess_name, i): # Only show eligible
                    found_any = True
                    txt = f"Rank Up {ab.name} ({ab.rank})"
                    self.add_action_button(txt, lambda e=ess_name, s=i: self.perform_rank_up(e, s))

        if not found_any:
            self.log("No abilities ready for Rank Up (Need Level 9).", "info")

    def perform_rank_up(self, essence_name, slot_index):
        msg = self.engine.rank_up_ability(essence_name, slot_index)
        tag = "event" if "Success" in msg else "error"
        self.log(msg, tag)
        self.show_rank_up_ability_options() # Refresh

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
