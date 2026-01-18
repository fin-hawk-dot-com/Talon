import tkinter as tk
from tkinter import ttk, font
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.mechanics import DataLoader, ConfluenceManager
from src.ability_templates import ABILITY_TEMPLATES

class LibraryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Essence Bound - Library")
        self.root.geometry("1000x700")

        self.loader = DataLoader()
        self.confluence_mgr = ConfluenceManager(self.loader)

        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Main Container
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Notebook (Tabs)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create Tabs
        self.create_mechanics_tab()
        self.create_essences_tab()
        self.create_confluences_tab()
        self.create_stones_tab()
        self.create_templates_tab()
        self.create_bestiary_tab()
        self.create_quests_tab()
        self.create_locations_tab()
        self.create_lore_tab()
        self.create_characters_tab()

    def create_split_view(self, parent, columns):
        """Creates a standard split view with a Treeview on the left and Text detail on the right."""
        paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Left Frame (List)
        left_frame = ttk.Frame(paned, width=400)
        paned.add(left_frame, weight=1)

        # Search Bar
        search_var = tk.StringVar()
        search_entry = ttk.Entry(left_frame, textvariable=search_var)
        search_entry.pack(fill=tk.X, padx=5, pady=5)

        # Treeview
        tree = ttk.Treeview(left_frame, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Right Frame (Details)
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)

        detail_text = tk.Text(right_frame, wrap=tk.WORD, state=tk.DISABLED, padx=10, pady=10)
        detail_text.pack(fill=tk.BOTH, expand=True)

        return tree, detail_text, search_var

    def create_mechanics_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Mechanics")

        text_area = tk.Text(tab, wrap=tk.WORD, padx=10, pady=10)
        text_area.pack(fill=tk.BOTH, expand=True)

        content = """
# System Mechanics

## Ranks
The progression system is divided into major ranks:
- Normal (Rank 0)
- Iron (Rank 1)
- Bronze (Rank 2)
- Silver (Rank 3)
- Gold (Rank 4)
- Diamond (Rank 5)

## Attributes
Characters have 4 main attributes:
- **Power**: Physical strength and damage.
- **Speed**: Movement and reaction time.
- **Spirit**: Magical power and mana pool.
- **Recovery**: Health regeneration and stamina.

## Ability Generation
Abilities are awakened by combining an **Essence** with an **Awakening Stone**.
- **Essence**: Determines the elemental flavor and tags (e.g., Fire, Dark).
- **Awakening Stone**: Determines the function (e.g., Attack, Defense).
- **Template**: The system selects an ability template that matches the Stone's function and the Essence's tags.
        """
        text_area.insert(tk.END, content)
        text_area.config(state=tk.DISABLED)

    def create_essences_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Essences")

        columns = ("Name", "Type", "Rarity")
        tree, detail_text, search_var = self.create_split_view(tab, columns)

        data = sorted(self.loader.essences_data, key=lambda x: x['name'])

        def populate(query=""):
            tree.delete(*tree.get_children())
            for item in data:
                if query and query not in item['name'].lower():
                    continue
                tree.insert("", tk.END, values=(item['name'], item['type'], item['rarity']), tags=(item['name'],))

        populate()
        search_var.trace("w", lambda *args: populate(search_var.get().lower()))

        def on_select(event):
            selected = tree.selection()
            if not selected: return
            # Get item name from values
            item_vals = tree.item(selected[0])['values']
            name = item_vals[0]

            # Find data
            item = next((x for x in data if x['name'] == name), None)
            if item:
                detail_text.config(state=tk.NORMAL)
                detail_text.delete("1.0", tk.END)

                txt = f"Name: {item['name']}\n"
                txt += f"Type: {item['type']}\n"
                txt += f"Rarity: {item['rarity']}\n"
                txt += f"Tags: {', '.join(item['tags'])}\n"
                txt += f"Opposite: {item.get('opposite') or '-'}\n"
                txt += f"Synergy: {', '.join(item.get('synergy', []))}\n"
                txt += "-" * 40 + "\n\n"
                txt += f"Description:\n{item['description']}\n\n"
                txt += f"Visual Prompt:\n{item.get('image_prompt', '')}\n"

                detail_text.insert(tk.END, txt)
                detail_text.config(state=tk.DISABLED)

        tree.bind("<<TreeviewSelect>>", on_select)

    def create_confluences_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Confluences")

        columns = ("Result", "Archetype")
        tree, detail_text, search_var = self.create_split_view(tab, columns)

        data = sorted(self.loader.confluences_data, key=lambda x: x['result'])

        def populate(query=""):
            tree.delete(*tree.get_children())
            for item in data:
                if query and query not in item['result'].lower():
                    continue
                tree.insert("", tk.END, values=(item['result'], item['archetype']))

        populate()
        search_var.trace("w", lambda *args: populate(search_var.get().lower()))

        def on_select(event):
            selected = tree.selection()
            if not selected: return
            item_vals = tree.item(selected[0])['values']
            name = item_vals[0]

            item = next((x for x in data if x['result'] == name), None)
            if item:
                detail_text.config(state=tk.NORMAL)
                detail_text.delete("1.0", tk.END)

                bases = ", ".join(item['bases'])

                txt = f"Confluence: {item['result']}\n"
                txt += f"Archetype: {item['archetype']}\n"
                txt += f"Base Essences: {bases}\n"

                detail_text.insert(tk.END, txt)
                detail_text.config(state=tk.DISABLED)

        tree.bind("<<TreeviewSelect>>", on_select)

    def create_stones_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Awakening Stones")

        columns = ("Name", "Function", "Rarity")
        tree, detail_text, search_var = self.create_split_view(tab, columns)

        data = sorted(self.loader.stones_data, key=lambda x: x['name'])

        def populate(query=""):
            tree.delete(*tree.get_children())
            for item in data:
                if query and query not in item['name'].lower():
                    continue
                tree.insert("", tk.END, values=(item['name'], item['function'], item.get('rarity', 'Common')))

        populate()
        search_var.trace("w", lambda *args: populate(search_var.get().lower()))

        def on_select(event):
            selected = tree.selection()
            if not selected: return
            item_vals = tree.item(selected[0])['values']
            name = item_vals[0]

            item = next((x for x in data if x['name'] == name), None)
            if item:
                detail_text.config(state=tk.NORMAL)
                detail_text.delete("1.0", tk.END)

                txt = f"Name: {item['name']}\n"
                txt += f"Function: {item['function']}\n"
                txt += f"Rarity: {item.get('rarity', 'Common')}\n"
                txt += f"Cooldown: {item.get('cooldown', 'Medium')}\n"
                txt += f"Cost Type: {item.get('cost_type', 'Mana')}\n"
                txt += "-" * 40 + "\n\n"
                txt += f"Description:\n{item['description']}\n\n"
                txt += f"Visual Prompt:\n{item.get('image_prompt', '')}\n"

                detail_text.insert(tk.END, txt)
                detail_text.config(state=tk.DISABLED)

        tree.bind("<<TreeviewSelect>>", on_select)

    def create_templates_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Ability Templates")

        columns = ("Function", "Pattern")
        tree, detail_text, search_var = self.create_split_view(tab, columns)

        data = sorted(ABILITY_TEMPLATES, key=lambda x: x.function)

        def populate(query=""):
            tree.delete(*tree.get_children())
            # Store objects in a parallel list or lookup
            for i, item in enumerate(data):
                if query and query not in item.function.lower():
                    continue
                # We use the index or unique ID to retrieve later. Pattern might be unique enough.
                tree.insert("", tk.END, values=(item.function, item.pattern), iid=str(i))

        populate()
        search_var.trace("w", lambda *args: populate(search_var.get().lower()))

        def on_select(event):
            selected = tree.selection()
            if not selected: return
            idx = int(selected[0])
            item = data[idx]

            detail_text.config(state=tk.NORMAL)
            detail_text.delete("1.0", tk.END)

            tags = ", ".join(item.essence_tags) if item.essence_tags else "None"

            affinities = []
            for k, v in item.affinity_weight.items():
                if v > 1.0:
                    affinities.append(f"{k} ({v})")
            affinity_str = ", ".join(affinities) if affinities else "General"

            txt = f"Function: {item.function}\n"
            txt += f"Pattern: {item.pattern}\n"
            txt += f"Required Tags: {tags}\n"
            txt += f"Affinity Preference: {affinity_str}\n"
            txt += "-" * 40 + "\n\n"
            txt += f"Description Template:\n{item.description_template}\n"

            detail_text.insert(tk.END, txt)
            detail_text.config(state=tk.DISABLED)

        tree.bind("<<TreeviewSelect>>", on_select)

    def create_bestiary_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Bestiary")

        columns = ("Name", "Race", "XP")
        tree, detail_text, search_var = self.create_split_view(tab, columns)

        data = sorted(self.loader.monsters_data, key=lambda x: x['name'])

        def populate(query=""):
            tree.delete(*tree.get_children())
            for item in data:
                if query and query not in item['name'].lower():
                    continue
                tree.insert("", tk.END, values=(item['name'], item['race'], item.get('xp_reward', 0)))

        populate()
        search_var.trace("w", lambda *args: populate(search_var.get().lower()))

        def on_select(event):
            selected = tree.selection()
            if not selected: return
            item_vals = tree.item(selected[0])['values']
            name = item_vals[0]

            item = next((x for x in data if x['name'] == name), None)
            if item:
                detail_text.config(state=tk.NORMAL)
                detail_text.delete("1.0", tk.END)

                attrs = item.get('attributes', {})
                attr_str = f"Power: {attrs.get('Power',0)} | Speed: {attrs.get('Speed',0)} | Spirit: {attrs.get('Spirit',0)} | Recovery: {attrs.get('Recovery',0)}"
                loot = ", ".join(item.get('loot_table', []))

                txt = f"Name: {item['name']}\n"
                txt += f"Race: {item['race']}\n"
                txt += f"XP Reward: {item.get('xp_reward', 0)}\n"
                txt += f"Attributes: {attr_str}\n"
                txt += f"Loot: {loot}\n"
                txt += "-" * 40 + "\n\n"
                txt += f"Description:\n{item['description']}\n\n"
                txt += f"Visual Prompt:\n{item.get('image_prompt', '')}\n"

                detail_text.insert(tk.END, txt)
                detail_text.config(state=tk.DISABLED)

        tree.bind("<<TreeviewSelect>>", on_select)

    def create_quests_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Quests")

        columns = ("Title", "Type")
        tree, detail_text, search_var = self.create_split_view(tab, columns)

        data = sorted(self.loader.quests_data, key=lambda x: x['title'])

        def populate(query=""):
            tree.delete(*tree.get_children())
            for item in data:
                if query and query not in item['title'].lower():
                    continue
                tree.insert("", tk.END, values=(item['title'], item.get('type', 'Side')))

        populate()
        search_var.trace("w", lambda *args: populate(search_var.get().lower()))

        def on_select(event):
            selected = tree.selection()
            if not selected: return
            item_vals = tree.item(selected[0])['values']
            title = item_vals[0]

            item = next((x for x in data if x['title'] == title), None)
            if item:
                detail_text.config(state=tk.NORMAL)
                detail_text.delete("1.0", tk.END)

                rewards = ", ".join(item.get('rewards', []))

                txt = f"Title: {item['title']}\n"
                txt += f"Type: {item.get('type', 'Side')}\n"
                txt += f"Rewards: {rewards}\n"
                txt += "-" * 40 + "\n\n"
                txt += f"Description:\n{item['description']}\n\n"

                # Show stages/objectives roughly
                txt += "Stages:\n"
                for s_id, s_data in item.get('stages', {}).items():
                    txt += f"  - [{s_id}] {s_data['description']}\n"
                    for choice in s_data.get('choices', []):
                         txt += f"      -> {choice['text']} (Leads to {choice['next_stage_id']})\n"

                txt += f"\nVisual Prompt:\n{item.get('image_prompt', '')}\n"

                detail_text.insert(tk.END, txt)
                detail_text.config(state=tk.DISABLED)

        tree.bind("<<TreeviewSelect>>", on_select)

    def create_locations_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Locations")

        columns = ("Name", "Region", "Type")
        tree, detail_text, search_var = self.create_split_view(tab, columns)

        data = sorted(self.loader.locations_data, key=lambda x: x['name'])

        def populate(query=""):
            tree.delete(*tree.get_children())
            for item in data:
                if query and query not in item['name'].lower():
                    continue
                tree.insert("", tk.END, values=(item['name'], item.get('region', 'Unknown'), item['type']))

        populate()
        search_var.trace("w", lambda *args: populate(search_var.get().lower()))

        def on_select(event):
            selected = tree.selection()
            if not selected: return
            item_vals = tree.item(selected[0])['values']
            name = item_vals[0]

            item = next((x for x in data if x['name'] == name), None)
            if item:
                detail_text.config(state=tk.NORMAL)
                detail_text.delete("1.0", tk.END)

                connected = ", ".join(item.get('connected_locations', []))
                resources = ", ".join(item.get('resources', []))
                npcs = ", ".join(item.get('npcs', []))

                txt = f"Name: {item['name']}\n"
                txt += f"Region: {item.get('region', 'Unknown')}\n"
                txt += f"Type: {item['type']}\n"
                txt += f"Danger Rank: {item.get('danger_rank', 'Iron')}\n"
                txt += f"Connected: {connected}\n"
                txt += f"Resources: {resources}\n"
                txt += f"NPCs: {npcs}\n"
                txt += "-" * 40 + "\n\n"
                txt += f"Description:\n{item['description']}\n\n"
                txt += f"Positive Prompt:\n{item['image_prompt_positive']}\n"
                txt += f"Negative Prompt:\n{item['image_prompt_negative']}\n"

                detail_text.insert(tk.END, txt)
                detail_text.config(state=tk.DISABLED)

        tree.bind("<<TreeviewSelect>>", on_select)

    def create_lore_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Lore")

        columns = ("Title", "Category")
        tree, detail_text, search_var = self.create_split_view(tab, columns)

        data = sorted(self.loader.lore_data, key=lambda x: x['title'])

        def populate(query=""):
            tree.delete(*tree.get_children())
            for item in data:
                if query and query not in item['title'].lower():
                    continue
                tree.insert("", tk.END, values=(item['title'], item['category']))

        populate()
        search_var.trace("w", lambda *args: populate(search_var.get().lower()))

        def on_select(event):
            selected = tree.selection()
            if not selected: return
            item_vals = tree.item(selected[0])['values']
            title = item_vals[0]

            item = next((x for x in data if x['title'] == title), None)
            if item:
                detail_text.config(state=tk.NORMAL)
                detail_text.delete("1.0", tk.END)

                txt = f"Title: {item['title']}\n"
                txt += f"Category: {item['category']}\n"
                txt += "-" * 40 + "\n\n"
                txt += f"{item['text']}\n\n"
                txt += f"Visual Prompt:\n{item.get('image_prompt', '')}\n"

                detail_text.insert(tk.END, txt)
                detail_text.config(state=tk.DISABLED)

        tree.bind("<<TreeviewSelect>>", on_select)

    def create_characters_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Characters")

        columns = ("Name", "Race", "Faction")
        tree, detail_text, search_var = self.create_split_view(tab, columns)

        data = sorted(self.loader.characters_data, key=lambda x: x['name'])

        def populate(query=""):
            tree.delete(*tree.get_children())
            for item in data:
                if query and query not in item['name'].lower():
                    continue
                tree.insert("", tk.END, values=(item['name'], item['race'], item.get('faction', 'None')))

        populate()
        search_var.trace("w", lambda *args: populate(search_var.get().lower()))

        def on_select(event):
            selected = tree.selection()
            if not selected: return
            item_vals = tree.item(selected[0])['values']
            name = item_vals[0]

            item = next((x for x in data if x['name'] == name), None)
            if item:
                detail_text.config(state=tk.NORMAL)
                detail_text.delete("1.0", tk.END)

                txt = f"Name: {item['name']}\n"
                txt += f"Race: {item['race']}\n"
                txt += f"Faction: {item.get('faction', 'None')}\n"
                txt += "-" * 40 + "\n\n"
                txt += f"Description:\n{item.get('description', '')}\n\n"
                txt += f"Visual Prompt:\n{item.get('image_prompt', '')}\n"

                detail_text.insert(tk.END, txt)
                detail_text.config(state=tk.DISABLED)

        tree.bind("<<TreeviewSelect>>", on_select)

if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryGUI(root)
    root.mainloop()
