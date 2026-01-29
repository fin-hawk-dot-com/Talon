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
from src.local_map_widget import LocalMapWidget

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
        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)

        # Specific actions
        self.root.bind("<e>", lambda e: self.handle_interaction())
        self.root.bind("<E>", lambda e: self.handle_interaction())
        self.root.bind("<m>", lambda e: self.toggle_map_mode())
        self.root.bind("<M>", lambda e: self.toggle_map_mode())

        # Movement State
        self.pressed_keys = {}

        # Dialogue State
        self.dialogue_npc_name = None
        self.dialogue_visited_roots = set()

        # Initial Screen
        self.show_main_menu()

    def safe_action(self, func):
        if self.state == "HUB":
            func()

    def handle_interaction(self):
        if self.state != "HUB" or not self.engine.character:
            return

        # Interaction is now handled by checking current tile or facing tile
        # But we also support the old menu-based style for flexibility
        char = self.engine.character
        curr_loc_name = char.current_location
        loc = self.engine.data_loader.get_location(curr_loc_name)

        # New: Check local tile entity
        if self.engine.current_section:
             tile = self.engine.current_section.get_tile(char.grid_x, char.grid_y)
             if tile and tile.entity:
                 self.log(f"Interacting with {tile.entity}...", "event")
                 # Check if NPC
                 if tile.entity in loc.npcs:
                     self.start_dialogue(tile.entity)
                     return
                 # Check if POI
                 for poi in loc.points_of_interest:
                     if poi.name == tile.entity:
                         self.log(f"{poi.name}: {poi.description}", "event")
                         return

        # Fallback to menu if nothing on tile (or legacy support)
        if loc.npcs or loc.points_of_interest:
            self.show_interaction_menu(loc.npcs, loc.points_of_interest)
        else:
            self.log("Nothing to interact with here.", "info")

    def show_interaction_menu(self, npcs, pois):
        self.clear_actions()
        self.add_action_button("<< Cancel", self.enter_hub)
        self.log("\n--- Interact ---", "info")

        for npc in npcs:
            self.add_action_button(f"Talk to {npc}", lambda n=npc: self.start_dialogue(n))

        for poi in pois:
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
        self.log(f"{self.dialogue_npc_name}: \"{text_to_show}\"", "info")

        # Show Choices
        for choice in node.choices:
            if choice.next_id == "exit":
                self.add_action_button(choice.text, self.enter_hub)
            else:
                self.add_action_button(choice.text, lambda nid=choice.next_id: self.show_dialogue_node(nid))

    def on_key_press(self, event):
        self.pressed_keys[event.keysym.lower()] = True

        # Handle Movement directly
        if self.state == "HUB" and self.engine.character:
            key = event.keysym.lower()
            dx, dy = 0, 0
            if key == 'w': dy = -1
            elif key == 's': dy = 1
            elif key == 'a': dx = -1
            elif key == 'd': dx = 1

            if dx != 0 or dy != 0:
                success, msg = self.engine.move_player_local(dx, dy)
                if msg:
                    self.log(msg, "event" if success else "error")

                # Refresh UI logic
                if success:
                    self.local_map.render(self.engine.current_section, self.engine.character)
                    # If we traveled, map changed, so full refresh
                    if "Traveled" in msg:
                        self.update_status_display() # full refresh

    def on_key_release(self, event):
        self.pressed_keys[event.keysym.lower()] = False

    def toggle_map_mode(self):
        new_mode = 'mini' if self.world_map.mode == 'world' else 'world'
        self.world_map.set_mode(new_mode)
        self.log(f"Global Map switched to {new_mode} view.", "info")

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')

        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=10)

        # Base Button Style (Tile-like)
        self.style.configure("TButton",
                             background="#333333",
                             foreground="#ffffff",
                             bordercolor="#555555",
                             lightcolor="#666666",
                             darkcolor="#111111",
                             relief="raised",
                             borderwidth=3,
                             padding=6,
                             font=('Helvetica', 10, 'bold'))
        self.style.map("TButton",
                       background=[('active', '#444444'), ('pressed', '#222222')],
                       relief=[('pressed', 'sunken')])

        # Combat Style (Red)
        self.style.configure("Combat.TButton",
                             background="#550000",
                             foreground="#ffcccc",
                             bordercolor="#ff3333",
                             lightcolor="#ff6666",
                             darkcolor="#330000")
        self.style.map("Combat.TButton",
                       background=[('active', '#770000'), ('pressed', '#330000')])

        # Interact Style (Blue)
        self.style.configure("Interact.TButton",
                             background="#002255",
                             foreground="#ccddff",
                             bordercolor="#3388ff",
                             lightcolor="#66aaff",
                             darkcolor="#001133")
        self.style.map("Interact.TButton",
                       background=[('active', '#003377'), ('pressed', '#001133')])

        # Growth Style (Green)
        self.style.configure("Growth.TButton",
                             background="#003300",
                             foreground="#ccffcc",
                             bordercolor="#33ff33",
                             lightcolor="#66ff66",
                             darkcolor="#002200")
        self.style.map("Growth.TButton",
                       background=[('active', '#005500'), ('pressed', '#002200')])

        # Value Style (Gold/Yellow)
        self.style.configure("Value.TButton",
                             background="#443300",
                             foreground="#ffffcc",
                             bordercolor="#ffcc00",
                             lightcolor="#ffee66",
                             darkcolor="#221100")
        self.style.map("Value.TButton",
                       background=[('active', '#664400'), ('pressed', '#221100')])

        # System Style (Grey/Neutral)
        self.style.configure("System.TButton",
                             background="#222222",
                             foreground="#aaaaaa",
                             bordercolor="#666666",
                             lightcolor="#888888",
                             darkcolor="#111111")
        self.style.map("System.TButton",
                       background=[('active', '#333333'), ('pressed', '#111111')])

        self.style.configure("Title.TLabel", font=('Helvetica', 18, 'bold'))
        self.style.configure("Status.TLabel", font=('Consolas', 10))

    def create_layout(self):
        # Main Container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # 1. Top Menubar
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Game", command=self.confirm_new_game)
        file_menu.add_command(label="Save Game", command=self.save_game_dialog)
        file_menu.add_command(label="Load Game", command=self.load_game_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # 2. Left Panel: Inventory (Width 250)
        self.left_panel = ttk.Frame(self.main_container, width=250, relief=tk.RIDGE, borderwidth=2)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=2, pady=2)
        self.left_panel.pack_propagate(False)

        ttk.Label(self.left_panel, text="Inventory", style="Title.TLabel").pack(pady=5)

        columns = ("Item", "Type")
        self.inventory_tree = ttk.Treeview(self.left_panel, columns=columns, show='headings', selectmode='browse')
        self.inventory_tree.heading("Item", text="Item")
        self.inventory_tree.column("Item", width=140)
        self.inventory_tree.heading("Type", text="Type")
        self.inventory_tree.column("Type", width=80)
        self.inventory_tree.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        self.inv_action_frame = ttk.Frame(self.left_panel)
        self.inv_action_frame.pack(fill=tk.X, padx=2, pady=2)

        # 3. Right Panel: Status & Menus (Width 300)
        self.right_panel = ttk.Frame(self.main_container, width=300, relief=tk.RIDGE, borderwidth=2)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=2, pady=2)
        self.right_panel.pack_propagate(False)

        self.right_notebook = ttk.Notebook(self.right_panel)
        self.right_notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Actions
        self.action_tab = ttk.Frame(self.right_notebook)
        self.right_notebook.add(self.action_tab, text="Actions")
        self.action_frame = ttk.Frame(self.action_tab)
        self.action_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab 2: Character Status (Moved from old Left Panel)
        self.status_tab = ttk.Frame(self.right_notebook)
        self.right_notebook.add(self.status_tab, text="Status")

        # Status Content
        self.basic_info_label = ttk.Label(self.status_tab, text="No Character", font=('Helvetica', 10, 'bold'))
        self.basic_info_label.pack(pady=(5, 5))

        self.status_bars_frame = ttk.Frame(self.status_tab)
        self.status_bars_frame.pack(fill=tk.X, padx=5, pady=5)

        def create_bar(label, color):
            frame = ttk.Frame(self.status_bars_frame)
            frame.pack(fill=tk.X, pady=2)
            lbl = ttk.Label(frame, text=f"{label}: 0/0", font=('Consolas', 9))
            lbl.pack(anchor="w")
            s_name = f"{label}.Horizontal.TProgressbar"
            self.style.configure(s_name, background=color)
            bar = ttk.Progressbar(frame, style=s_name, length=100, mode='determinate')
            bar.pack(fill=tk.X)
            return lbl, bar

        self.hp_label, self.hp_bar = create_bar("HP", "#ff5555")
        self.mp_label, self.mp_bar = create_bar("MP", "#5555ff")
        self.sp_label, self.sp_bar = create_bar("SP", "#55ff55")
        self.wp_label, self.wp_bar = create_bar("WP", "#aa55ff")

        self.status_text = tk.Text(self.status_tab, wrap=tk.WORD, height=10, bg="#2b2b2b", fg="#e0e0e0", relief=tk.FLAT, state=tk.DISABLED, font=('Consolas', 9))
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab 3: Quests
        self.quest_tab = ttk.Frame(self.right_notebook)
        self.right_notebook.add(self.quest_tab, text="Quests")
        self.quest_list = tk.Text(self.quest_tab, wrap=tk.WORD, state=tk.DISABLED, bg="#2b2b2b", fg="#e0e0e0", font=('Consolas', 9))
        self.quest_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab 4: Char Details
        self.char_detail_tab = ttk.Frame(self.right_notebook)
        self.right_notebook.add(self.char_detail_tab, text="Details")
        self.character_details = tk.Text(self.char_detail_tab, wrap=tk.WORD, state=tk.DISABLED, bg="#2b2b2b", fg="#e0e0e0", font=('Consolas', 9))
        self.character_details.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 4. Center Panel (Map)
        self.center_frame = ttk.Frame(self.main_container)
        self.center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2, pady=2)

        # We need a bottom frame for Log
        self.bottom_frame = ttk.Frame(self.center_frame, height=150)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.bottom_frame.pack_propagate(False)

        self.log_text = tk.Text(self.bottom_frame, wrap=tk.WORD, state=tk.DISABLED, font=('Georgia', 11), bg="#1e1e1e", fg="#cccccc")
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scroll = ttk.Scrollbar(self.bottom_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.configure(yscrollcommand=log_scroll.set)

        self.log_text.tag_config("info", foreground="#cccccc")
        self.log_text.tag_config("combat", foreground="#ff5555")
        self.log_text.tag_config("gain", foreground="#55ff55")
        self.log_text.tag_config("event", foreground="#55aaff")
        self.log_text.tag_config("error", foreground="#ffaaff")

        # Local Map takes remaining space
        self.local_map = LocalMapWidget(self.center_frame)
        self.local_map.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # 5. World Map Overlay (GPS)
        # We place it inside center_frame (or local_map)
        self.world_map = MapWidget(self.local_map, self.engine, width=200, height=200)
        self.world_map.set_mode('mini')
        # Place at top-right corner
        self.world_map.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

    def log(self, message, tag="info"):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n", tag)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def clear_actions(self):
        for widget in self.action_frame.winfo_children():
            widget.destroy()

    def get_button_style(self, text):
        t = text.lower()
        if any(x in t for x in ["attack", "fight", "flee", "combat", "encounter", "ability"]):
            return "Combat.TButton"
        if any(x in t for x in ["inspect", "talk", "interact", "look", "bond", "absorb", "quest", "stage", "start"]):
            return "Interact.TButton"
        if any(x in t for x in ["train", "craft", "gather", "rest", "recover", "heal", "consume", "practice", "rank up"]):
            return "Growth.TButton"
        if any(x in t for x in ["inventory", "buy", "sell", "market", "trade", "loot", "awaken", "stone", "item", "found"]):
            return "Value.TButton"
        if any(x in t for x in ["exit", "back", "cancel", "save", "load", "menu", "game"]):
            return "System.TButton"
        return "TButton"

    def add_action_button(self, text, command):
        style = self.get_button_style(text)
        btn = ttk.Button(self.action_frame, text=text, command=command, style=style)
        btn.pack(fill=tk.X, pady=2)
        return btn

    def update_status_display(self):
        if not self.engine.character:
            self.basic_info_label.config(text="No Character Loaded")
            self.status_text.config(state=tk.NORMAL)
            self.status_text.delete("1.0", tk.END)
            self.status_text.config(state=tk.DISABLED)
            return

        char = self.engine.character

        # Basic Info
        self.basic_info_label.config(text=f"{char.name} ({char.race}) - Rank: {char.rank}")

        # Bars
        self.hp_bar['maximum'] = char.max_health
        self.hp_bar['value'] = char.current_health
        self.hp_label.config(text=f"HP: {char.current_health:.0f}/{char.max_health:.0f}")

        self.mp_bar['maximum'] = char.max_mana
        self.mp_bar['value'] = char.current_mana
        self.mp_label.config(text=f"MP: {char.current_mana:.0f}/{char.max_mana:.0f}")

        self.sp_bar['maximum'] = char.max_stamina
        self.sp_bar['value'] = char.current_stamina
        self.sp_label.config(text=f"SP: {char.current_stamina:.0f}/{char.max_stamina:.0f}")

        self.wp_bar['maximum'] = char.max_willpower
        self.wp_bar['value'] = char.current_willpower
        self.wp_label.config(text=f"WP: {char.current_willpower:.0f}/{char.max_willpower:.0f}")

        # Text Details (Attributes & Effects)
        text = ""
        if char.status_effects:
            text += "Status Effects:\n"
            for e in char.status_effects:
                text += f"[{e.name} {e.duration}]\n"
            text += "-"*10 + "\n"

        text += "Attributes:\n"
        for attr in char.attributes.values():
            text += f" {attr.name[:3]}: {attr.value:.1f} ({attr.rank})\n"

        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete("1.0", tk.END)
        self.status_text.insert(tk.END, text)
        self.status_text.config(state=tk.DISABLED)

        # Update tabs
        self.update_character_tab()
        self.update_inventory_tab()
        self.update_quest_tab()

        # Update maps
        if not self.engine.current_section:
             self.engine.load_location_section(char.current_location)

        self.local_map.render(self.engine.current_section, char)
        self.world_map.refresh() # Updates mini-map dot

    def update_inventory_tab(self):
        if not self.engine.character: return

        # Save selection
        selected_iid = self.inventory_tree.selection()

        # Clear existing
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)

        # Populate
        for i, item in enumerate(self.engine.character.inventory):
            # Determine type
            itype = "Item"
            if hasattr(item, 'type'): itype = "Essence"
            elif hasattr(item, 'function'): itype = "Stone"
            # Add to tree
            self.inventory_tree.insert("", tk.END, iid=str(i), values=(item.name, itype))

        # Restore selection if possible
        if selected_iid and self.inventory_tree.exists(selected_iid[0]):
            self.inventory_tree.selection_set(selected_iid[0])
        else:
            # Clear action frame if selection lost
            for widget in self.inv_action_frame.winfo_children():
                widget.destroy()

        # Bind selection
        self.inventory_tree.bind("<<TreeviewSelect>>", self.on_inventory_select)

    def on_inventory_select(self, event):
        selected = self.inventory_tree.selection()
        if not selected: return

        idx = int(selected[0])
        # Update action buttons for this item
        for widget in self.inv_action_frame.winfo_children():
            widget.destroy()

        # Check index validity (race condition safety)
        if idx >= len(self.engine.character.inventory): return

        item = self.engine.character.inventory[idx]
        ttk.Label(self.inv_action_frame, text=f"Selected: {item.name}", font=('Helvetica', 9, 'bold')).pack(anchor='w', pady=(0,5))

        # Actions based on type
        if hasattr(item, 'type'): # Essence
             ttk.Button(self.inv_action_frame, text="Absorb (Bond)", command=lambda: self.absorb_essence_dialog(idx), style="Interact.TButton").pack(fill=tk.X, pady=2)
        elif hasattr(item, 'function'): # Stone
             ttk.Button(self.inv_action_frame, text="Use (Awaken)", command=self.show_awaken_options, style="Value.TButton").pack(fill=tk.X, pady=2)
        elif hasattr(item, 'effect_type'): # Consumable
             ttk.Button(self.inv_action_frame, text="Consume", command=lambda: self.perform_consume(idx), style="Growth.TButton").pack(fill=tk.X, pady=2)

        # Generic Inspect
        if hasattr(item, 'description'):
             ttk.Button(self.inv_action_frame, text="Inspect", command=lambda: self.log(f"{item.name}: {item.description}", "info"), style="Interact.TButton").pack(fill=tk.X, pady=2)

    def update_quest_tab(self):
        if not self.engine.character: return

        self.quest_list.config(state=tk.NORMAL)
        self.quest_list.delete("1.0", tk.END)

        active = [q for q in self.engine.character.quests.values() if q.status == "Active"]
        if not active:
            self.quest_list.insert(tk.END, "No active quests.\n")
        else:
            for qp in active:
                quest = self.engine.data_loader.get_quest(qp.quest_id)
                self.quest_list.insert(tk.END, f"• {quest.title}\n", "event")
                # Show current stage description
                stage = quest.stages.get(qp.current_stage_id)
                if stage:
                     self.quest_list.insert(tk.END, f"  {stage['description']}\n\n")

        self.quest_list.config(state=tk.DISABLED)

    def update_character_tab(self):
        if not self.engine.character: return

        char = self.engine.character
        text = f"XP: {char.current_xp}\n"
        text += f"Dram: {char.currency}\n\n"

        text += "Essences & Abilities:\n"
        for ess_name, slots in char.abilities.items():
            text += f"- {ess_name}:\n"
            for ab in slots:
                if ab:
                    text += f"  • {ab.name} (Lvl {ab.level}, Rank {ab.rank})\n"
                else:
                    text += "  • [Empty]\n"
            text += "\n"

        self.character_details.config(state=tk.NORMAL)
        self.character_details.delete("1.0", tk.END)
        self.character_details.insert(tk.END, text)
        self.character_details.config(state=tk.DISABLED)

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
        self.right_notebook.select(self.action_tab)

        self.log("\n--- You are in a safe location ---", "info")

        self.add_action_button("Inspect Area (Interaction)", self.handle_interaction)
        self.add_action_button("Train Attribute", self.show_train_options)
        self.add_action_button("Adventure (Combat)", self.start_combat_encounter)
        self.add_action_button("Inventory", lambda: self.right_notebook.select(self.inventory_tab))
        self.add_action_button("Awaken Ability", self.show_awaken_options)

        # New buttons
        self.add_action_button("Gather Resources", self.perform_gather)
        self.add_action_button("Rest (Recover)", self.perform_rest)
        self.add_action_button("Visit Market", self.show_market_ui)
        self.add_action_button("Crafting", self.show_crafting_ui)

        # Check for available quests
        if self.engine.quest_mgr.get_available_quests(self.engine.character):
             self.add_action_button("Find New Quests", self.show_available_quests)

        self.add_action_button("Quests", lambda: self.right_notebook.select(self.quest_tab))
        self.add_action_button("Save Game", self.save_game_dialog)
        self.add_action_button("Main Menu", self.show_main_menu)

    def perform_rest(self):
        msg = self.engine.rest()
        self.log(msg, "event")
        self.update_status_display()

    def perform_gather(self):
        msg = self.engine.gather_resources()
        self.log(msg, "event")
        self.update_status_display()

    def perform_consume(self, idx):
        msg = self.engine.use_consumable(idx)
        self.log(msg, "event")
        self.update_status_display()

    def show_market_ui(self):
        self.clear_actions()
        self.add_action_button("<< Back", self.enter_hub)
        self.log("\n--- Market ---", "info")

        # Shop Inventory
        stock = self.engine.get_shop_inventory()
        if not stock:
            self.log("Market is empty today.", "info")
        else:
            self.log("Items for sale:", "info")
            for item in stock:
                price = getattr(item, 'price', getattr(item, 'value', 0))
                txt = f"Buy {item.name} ({price} Dram)"
                self.add_action_button(txt, lambda i=item: self.perform_buy(i))

        # Sell Options (simplified: link to Inventory tab or specific sell list)
        self.add_action_button("Sell Item (Select from Inventory)", self.show_sell_options)

    def perform_buy(self, item):
        msg = self.engine.buy_item(item)
        tag = "gain" if "Bought" in msg else "error"
        self.log(msg, tag)
        self.update_status_display()

    def show_sell_options(self):
        self.clear_actions()
        self.add_action_button("<< Back", self.show_market_ui)
        self.log("Select item to sell:", "info")

        char = self.engine.character
        if not char.inventory:
            self.log("Inventory empty.", "info")
            return

        for i, item in enumerate(char.inventory):
            val = getattr(item, 'price', getattr(item, 'value', 0)) // 2
            txt = f"Sell {item.name} ({val} Dram)"
            self.add_action_button(txt, lambda idx=i: self.perform_sell(idx))

    def perform_sell(self, idx):
        msg = self.engine.sell_item(idx)
        tag = "gain" if "Sold" in msg else "error"
        self.log(msg, tag)
        self.update_status_display()
        self.show_sell_options() # Refresh list

    def show_crafting_ui(self):
        self.clear_actions()
        self.add_action_button("<< Back", self.enter_hub)
        self.log("\n--- Crafting ---", "info")

        recipes = self.engine.get_craftable_recipes()
        for r_name in recipes:
            self.add_action_button(f"Craft {r_name}", lambda r=r_name: self.perform_craft(r))

    def perform_craft(self, recipe_name):
        msg = self.engine.craft_item(recipe_name)
        tag = "gain" if "Crafted" in msg else "error"
        self.log(msg, tag)
        self.update_status_display()

    def show_train_options(self):
        self.clear_actions()
        self.add_action_button("<< Back", self.enter_hub)

        def train(attr):
            msg = self.engine.train_attribute(attr)
            self.log(msg, "gain")
            self.update_status_display()
            self.show_train_options() # Refresh to update costs

        for attr_name in ["Power", "Speed", "Spirit", "Recovery"]:
            cost = self.engine.get_attribute_training_cost(attr_name)
            attr = self.engine.character.attributes.get(attr_name)
            rank = attr.rank if attr else "?"

            # Button Text
            text = f"Train {attr_name} ({rank}) - Cost: {cost} XP"

            # Check affordability
            can_afford = self.engine.character.current_xp >= cost

            if can_afford:
                self.add_action_button(text, lambda a=attr_name: train(a))
            else:
                self.add_action_button(f"{text} (Not Enough XP)", lambda: self.log("Not enough XP.", "error"))

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
                    txt = f"{ab.name} (Lvl {ab.level}) [{ab.xp:.0f}/{ab.max_xp:.0f} XP]"
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
        self.right_notebook.select(self.inventory_tab)

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
            # Inventory list updates automatically via update_status_display

        ttk.Button(popup, text="Power", command=lambda: confirm("Power")).pack()
        ttk.Button(popup, text="Speed", command=lambda: confirm("Speed")).pack()
        ttk.Button(popup, text="Spirit", command=lambda: confirm("Spirit")).pack()
        ttk.Button(popup, text="Recovery", command=lambda: confirm("Recovery")).pack()

    def show_awaken_options(self):
        self.clear_actions()
        self.add_action_button("<< Back", self.enter_hub)

        char = self.engine.character
        # Filter for Awakening Stones
        # We need to keep track of the REAL index in the inventory
        stones = []
        for i, item in enumerate(char.inventory):
            if hasattr(item, 'function'): # AwakeningStone identifier
                stones.append((i, item))

        if not stones:
            self.log("No Awakening Stones in inventory.", "error")
            return

        self.log("\n--- Awaken Ability: Select Stone ---", "info")
        for idx, stone in stones:
            self.add_action_button(f"{stone.name} ({stone.function})", lambda i=idx: self.select_stone_for_awakening(i))

    def select_stone_for_awakening(self, stone_index):
        self.clear_actions()
        self.add_action_button("<< Back", self.show_awaken_options)

        char = self.engine.character
        # Verify stone still exists (edge case)
        if stone_index >= len(char.inventory):
            self.show_awaken_options()
            return

        stone = char.inventory[stone_index]
        self.log(f"\nSelected Stone: {stone.name}", "event")
        self.log("Select Essence to bond with:", "info")

        # List Essences
        essences = char.get_all_essences()
        if not essences:
            self.log("No Essences bonded!", "error")
            return

        for ess in essences:
            self.add_action_button(f"{ess.name}", lambda e=ess.name: self.select_essence_for_awakening(stone_index, e))

    def select_essence_for_awakening(self, stone_index, essence_name):
        self.clear_actions()
        self.add_action_button("<< Back", lambda: self.select_stone_for_awakening(stone_index))

        self.log(f"\nSelected Essence: {essence_name}", "event")
        self.log("Select a Slot:", "info")

        char = self.engine.character
        slots = char.abilities.get(essence_name)
        if not slots:
            self.log("Error accessing ability slots.", "error")
            return

        for i in range(5):
            occupant = slots[i]
            if occupant:
                self.add_action_button(f"Slot {i+1}: {occupant.name} (Occupied)", lambda: None)
            else:
                self.add_action_button(f"Slot {i+1}: [Empty]", lambda s=i: self.select_slot_for_awakening(stone_index, essence_name, s))

    def select_slot_for_awakening(self, stone_index, essence_name, slot_index):
        result = self.engine.awaken_ability(essence_name, stone_index, slot_index)

        tag = "event" if "Awakened" in result or "Success" in result else "error"
        self.log(result, tag)

        # Refresh status and return to Hub or Awakening menu
        self.update_status_display()
        self.show_awaken_options()

    def show_available_quests(self):
        self.clear_actions()
        self.add_action_button("<< Back", self.enter_hub)
        self.right_notebook.select(self.action_tab)

        char = self.engine.character
        available = self.engine.quest_mgr.get_available_quests(char)

        def start(q_id):
            res = self.engine.quest_mgr.start_quest(char, q_id)
            self.log(res, "event")
            self.update_quest_tab() # Update the tab
            self.enter_hub() # Return to hub actions

        if not available:
            self.log("No new quests available.", "info")
            self.enter_hub()
            return

        self.log("Select a quest to start:", "info")
        for q in available:
            self.add_action_button(f"Start: {q.title}", lambda qid=q.id: start(qid))

    # --- COMBAT ---

    def start_combat_encounter(self):
        import random
        monsters = self.engine.get_monsters_for_location(self.engine.character.current_location)
        if not monsters:
            self.log("No monsters found here!", "error")
            return

        self.current_monster = random.choice(monsters)

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
