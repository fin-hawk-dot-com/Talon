import tkinter as tk
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

        # 3. Player Marker
        self.update_player()

    def update_player(self):
        self.delete("player")
        char = self.engine.character
        if not char: return

        curr_name = char.current_location
        if curr_name in self.loc_coords:
            lx, ly = self.loc_coords[curr_name]
            px, py = self.transform_coords(lx, ly)

            # Draw a distinct marker (Target icon style)
            r = self.player_radius

            # Outer ring
            self.create_oval(px - r - 3, py - r - 3, px + r + 3, py + r + 3,
                             outline="#ff3333", width=2, tags="player")
            # Inner dot
            self.create_oval(px - r, py - r, px + r, py + r,
                             fill="#ff3333", outline="white", width=1, tags="player")

    def refresh(self):
        # Triggered externally to update player position
        self.update_player()
