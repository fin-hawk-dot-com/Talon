import tkinter as tk
import os
from typing import Tuple

class MapWidget(tk.Canvas):
    def __init__(self, parent, engine, width=400, height=400, **kwargs):
        super().__init__(parent, width=width, height=height, bg="#111111", highlightthickness=0, **kwargs)
        self.engine = engine
        # Load locations once; assuming static map data for now
        self.locations = self.engine.data_loader.get_all_locations()

        # Map logical 0-1000 to canvas width/height with padding
        self.logical_width = 1000
        self.logical_height = 1000
        self.padding = 40

        self.node_radius = 6
        self.player_radius = 5
        self.player_img = None
        self.last_affinity = None

        # Cache coordinates for quick lookup: name -> (x, y)
        self.loc_coords = {}
        for loc in self.locations:
            # Default to 500,500 if missing (though we fixed this)
            x = getattr(loc, 'x', 500)
            y = getattr(loc, 'y', 500)
            self.loc_coords[loc.name] = (x, y)

        # Bind resize event
        self.bind("<Configure>", self.on_resize)

        # Initial draw
        self.draw_map()

    def on_resize(self, event):
        self.draw_map()

    def transform_coords(self, lx: int, ly: int) -> Tuple[float, float]:
        # Scale to fit canvas
        w = self.winfo_width()
        h = self.winfo_height()

        # Fallback if not yet mapped
        if w <= 1: w = int(self['width'])
        if h <= 1: h = int(self['height'])

        usable_w = w - 2 * self.padding
        usable_h = h - 2 * self.padding

        cx = self.padding + (lx / self.logical_width) * usable_w
        cy = self.padding + (ly / self.logical_height) * usable_h
        return cx, cy

    def draw_map(self):
        self.delete("all")

        # 1. Connections
        drawn_connections = set()

        for loc in self.locations:
            sx, sy = self.transform_coords(getattr(loc, 'x', 500), getattr(loc, 'y', 500))

            for neighbor_name in loc.connected_locations:
                if neighbor_name in self.loc_coords:
                    nx, ny = self.loc_coords[neighbor_name]

                    # Sort names to create a unique key for the pair (undirected edge)
                    key = tuple(sorted((loc.name, neighbor_name)))
                    if key not in drawn_connections:
                        dx, dy = self.transform_coords(nx, ny)
                        self.create_line(sx, sy, dx, dy, fill="#444444", width=2, tags="conn")
                        drawn_connections.add(key)

        # 2. Nodes
        for loc in self.locations:
            cx, cy = self.transform_coords(getattr(loc, 'x', 500), getattr(loc, 'y', 500))

            # Determine Color
            color = "#888888" # Default
            rank = loc.danger_rank

            # Color coding by Danger Rank
            if rank == "Iron": color = "#aaaaaa"      # Light Grey
            elif rank == "Bronze": color = "#cd7f32"  # Bronze
            elif rank == "Silver": color = "#c0c0c0"  # Silver
            elif rank == "Gold": color = "#ffd700"    # Gold
            elif rank == "Diamond": color = "#00ffff" # Cyan/Diamond

            # Special override for specific Regions or Types
            if loc.region == "Void": color = "#9400d3" # Purple

            # Draw Node
            r = self.node_radius
            if loc.type == "City": r += 2 # Make cities slightly bigger

            self.create_oval(cx - r, cy - r, cx + r, cy + r,
                             fill=color, outline="#ffffff", width=1, tags=("node", loc.name))

            # Labels for Cities or special nodes
            if loc.type in ["City", "Village", "Outpost"]:
                 self.create_text(cx, cy - 15, text=loc.name, fill="white", font=("Helvetica", 8))

        # 3. Player Marker & HUD
        self.update_player()

    def load_player_image(self):
        char = self.engine.character
        if not char: return

        if self.player_img and self.last_affinity == char.affinity:
            return

        self.last_affinity = char.affinity
        # Try loading specific affinity avatar
        filename = f"{char.affinity}.png"
        path = os.path.join("assets", "avatars", filename)

        # Fallback to General if specific not found
        if not os.path.exists(path):
             path = os.path.join("assets", "avatars", "General.png")

        if os.path.exists(path):
            try:
                self.player_img = tk.PhotoImage(file=path)
                # Note: No easy resize in raw Tkinter without subsample/zoom integers
                # We assume assets are sized correctly (e.g. 32x32)
            except Exception as e:
                print(f"Failed to load avatar: {e}")
                self.player_img = None
        else:
            self.player_img = None

    def update_player(self):
        self.delete("player")
        self.delete("hud")

        char = self.engine.character
        if not char: return

        # Load Image if needed
        self.load_player_image()

        curr_name = char.current_location
        if curr_name in self.loc_coords:
            lx, ly = self.loc_coords[curr_name]
            px, py = self.transform_coords(lx, ly)

            if self.player_img:
                self.create_image(px, py, image=self.player_img, tags="player")
            else:
                # Fallback: Draw a distinct marker (Target icon style)
                r = self.player_radius
                # Outer ring
                self.create_oval(px - r - 3, py - r - 3, px + r + 3, py + r + 3,
                                 outline="#ff3333", width=2, tags="player")
                # Inner dot
                self.create_oval(px - r, py - r, px + r, py + r,
                                 fill="#ff3333", outline="white", width=1, tags="player")

        # Draw HUD on top
        self.draw_hud()

    def draw_hud(self):
        char = self.engine.character
        if not char: return

        # Dimensions
        w = self.winfo_width()
        if w <= 1: w = int(self['width'])
        h = self.winfo_height()
        if h <= 1: h = int(self['height'])

        # Config
        bar_width = 120
        bar_height = 10
        gap = 5
        x_start = 10
        y_start = h - 10 - (4 * (bar_height + gap)) # Bottom Left corner

        # Helper to draw bar
        def draw_bar(idx, current, max_val, color, label):
            y = y_start + idx * (bar_height + gap)

            # BG
            self.create_rectangle(x_start, y, x_start + bar_width, y + bar_height,
                                  fill="#222222", outline="#444444", tags="hud")

            # Fill
            if max_val > 0:
                pct = max(0, min(1, current / max_val))
                fill_w = int(bar_width * pct)
                if fill_w > 0:
                    self.create_rectangle(x_start, y, x_start + fill_w, y + bar_height,
                                          fill=color, outline="", tags="hud")

            # Text (Overlay or Side)
            self.create_text(x_start + bar_width + 5, y + bar_height/2,
                             text=f"{label} {int(current)}", anchor="w", fill="white", font=("Consolas", 8), tags="hud")

        draw_bar(0, char.current_health, char.max_health, "#ff3333", "HP")
        draw_bar(1, char.current_mana, char.max_mana, "#3388ff", "MP")
        draw_bar(2, char.current_stamina, char.max_stamina, "#33ff33", "SP")
        draw_bar(3, char.current_willpower, char.max_willpower, "#aa33ff", "WP")

    def refresh(self):
        # Triggered externally to update player position
        self.update_player()
