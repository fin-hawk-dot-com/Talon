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

        self.node_radius = 8
        self.player_radius = 6
        self.player_img = None
        self.last_affinity = None

        # HUD Assets
        self.hud_imgs = {}
        self.load_hud_images()

        # View State
        self.mode = 'world' # 'world' or 'mini'
        self.zoom = 1.0

        # Cache coordinates for quick lookup: name -> (x, y)
        self.loc_coords = {}
        for loc in self.locations:
            # Default to 500,500 if missing (though we fixed this)
            x = getattr(loc, 'x', 500)
            y = getattr(loc, 'y', 500)
            self.loc_coords[loc.name] = (x, y)

        # Bind resize event
        self.bind("<Configure>", self.on_resize)

        # Tooltip
        self.tooltip_item = None
        self.tooltip_bg = None

        # Callback
        self.on_location_click_callback = None

        # Bind events
        self.bind("<Button-1>", self.on_click)
        self.bind("<Motion>", self.on_mouse_move)

        # Cache for hit testing: list of (loc, screen_x, screen_y, radius)
        self.hit_cache = []

        # Initial draw
        self.draw_map()

    def set_callback(self, callback):
        self.on_location_click_callback = callback

    def on_resize(self, event):
        self.draw_map()

    def on_click(self, event):
        node = self._get_node_at(event.x, event.y)
        if node:
            if self.on_location_click_callback:
                self.on_location_click_callback(node.name)

    def on_mouse_move(self, event):
        node = self._get_node_at(event.x, event.y)
        self.delete("tooltip")

        if node:
            # Show tooltip
            rank = getattr(node, 'danger_rank', 'Unknown')
            text = f"{node.name} ({rank})"
            # Draw bg
            padding = 4

            # Estimate text size (approx)
            w = len(text) * 7
            h = 20

            x, y = event.x + 10, event.y + 10

            # Boundary checks
            if x + w > self.winfo_width(): x -= (w + 20)
            if y + h > self.winfo_height(): y -= (h + 20)

            self.create_rectangle(x, y, x + w, y + h, fill="#333333", outline="#aaaaaa", tags="tooltip")
            self.create_text(x + w/2, y + h/2, text=text, fill="white", font=("Helvetica", 9), tags="tooltip")

            # Highlight node?
            # Maybe later

    def _get_node_at(self, sx, sy):
        for loc, cx, cy, r in self.hit_cache:
            # Simple circle check for all shapes for click detection
            if (sx - cx)**2 + (sy - cy)**2 <= (r + 4)**2: # Add a bit of padding
                return loc
        return None

    def set_mode(self, mode: str):
        if mode not in ['world', 'mini']: return
        self.mode = mode
        self.draw_map()

    def transform_coords(self, lx: int, ly: int) -> Tuple[float, float]:
        # Dimensions
        w = self.winfo_width()
        if w <= 1: w = int(self['width'])
        h = self.winfo_height()
        if h <= 1: h = int(self['height'])

        usable_w = w - 2 * self.padding
        usable_h = h - 2 * self.padding

        if self.mode == 'world':
            # Stretch to fit
            cx = self.padding + (lx / self.logical_width) * usable_w
            cy = self.padding + (ly / self.logical_height) * usable_h
            return cx, cy

        elif self.mode == 'mini':
            # Center on Player
            char = self.engine.character
            px, py = 500, 500
            if char:
                if char.x != -1 and char.y != -1:
                    px, py = char.x, char.y
                elif char.current_location in self.loc_coords:
                    px, py = self.loc_coords[char.current_location]

            # Zoom Factor: 4x zoom compared to world view average scale
            scale_x = usable_w / self.logical_width
            scale_y = usable_h / self.logical_height
            avg_base_scale = (scale_x + scale_y) / 2
            final_scale = avg_base_scale * 4.0

            center_x = w / 2
            center_y = h / 2

            cx = center_x + (lx - px) * final_scale
            cy = center_y + (ly - py) * final_scale
            return cx, cy

        return 0, 0

    def draw_map(self):
        self.delete("all")
        self.hit_cache = []

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
            self.draw_location_node(loc)

        # 3. Player Marker & HUD
        self.update_player()

    def draw_location_node(self, loc):
        cx, cy = self.transform_coords(getattr(loc, 'x', 500), getattr(loc, 'y', 500))
        r = self.node_radius

        # Cache for hit testing
        self.hit_cache.append((loc, cx, cy, r))

        # Colors
        colors = {
            "Iron": "#aaaaaa",
            "Bronze": "#cd7f32",
            "Silver": "#c0c0c0",
            "Gold": "#ffd700",
            "Diamond": "#00ffff",
            "Void": "#9400d3"
        }
        color = colors.get(loc.danger_rank, "#888888")
        if loc.region == "Void": color = "#9400d3"

        # Shape based on Type
        r = self.node_radius

        # Helper to create styled polygon
        def draw_poly(points):
            self.create_polygon(points, fill=color, outline="#ffffff", width=1, tags=("node", loc.name))

        if loc.type == "City":
            # Square
            self.create_rectangle(cx - r, cy - r, cx + r, cy + r, fill=color, outline="#ffffff", width=1, tags=("node", loc.name))

        elif loc.type in ["Village", "Outpost"]:
            # Pentagon (House-ish)
            points = [cx, cy - r, cx + r, cy - r*0.3, cx + r*0.6, cy + r, cx - r*0.6, cy + r, cx - r, cy - r*0.3]
            draw_poly(points)

        elif loc.type == "Dungeon":
            # Diamond
            points = [cx, cy - r, cx + r, cy, cx, cy + r, cx - r, cy]
            draw_poly(points)

        elif loc.type == "Wilderness":
            # Triangle
            points = [cx, cy - r, cx + r, cy + r, cx - r, cy + r]
            draw_poly(points)

        elif loc.type == "Dimension":
            # Star / Spiky (4-point star)
            r2 = r / 2
            points = [cx, cy - r, cx + r2, cy - r2, cx + r, cy, cx + r2, cy + r2, cx, cy + r, cx - r2, cy + r2, cx - r, cy, cx - r2, cy - r2]
            draw_poly(points)

        else:
            # Circle Default
            self.create_oval(cx - r, cy - r, cx + r, cy + r, fill=color, outline="#ffffff", width=1, tags=("node", loc.name))

        # Labels
        # Show labels for Cities always, others only in mini mode or if selected?
        # Let's show all labels in mini mode for clarity, and only major ones in world mode
        show_label = False
        if loc.type in ["City", "Village", "Outpost"]:
            show_label = True
        if self.mode == 'mini':
            show_label = True

        if show_label:
             self.create_text(cx, cy - 15, text=loc.name, fill="white", font=("Helvetica", 8))

    def load_hud_images(self):
        # Load HUD frames
        frames = {
            "HP": "HUD_HP_Frame.png",
            "MP": "HUD_MP_Frame.png",
            "SP": "HUD_SP_Frame.png",
            "WP": "HUD_WP_Frame.png"
        }

        self.hud_imgs = {}
        for key, filename in frames.items():
            path = os.path.join("assets", "ui", filename)
            if os.path.exists(path):
                try:
                    self.hud_imgs[key] = tk.PhotoImage(file=path)
                except Exception as e:
                    print(f"Failed to load HUD asset {filename}: {e}")

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

        # Use exact coordinates if available, otherwise fallback to location
        if char.x != -1 and char.y != -1:
             lx, ly = char.x, char.y
        else:
             curr_name = char.current_location
             if curr_name in self.loc_coords:
                 lx, ly = self.loc_coords[curr_name]
             else:
                 lx, ly = 500, 500 # Fallback

        px, py = self.transform_coords(lx, ly)

        if self.player_img:
            self.create_image(px, py, image=self.player_img, tags="player")
        else:
            # Fallback: Draw a distinct marker (Target icon style)
            r = self.player_radius
            # Use Cyan for high visibility
            self.create_oval(px - r, py - r, px + r, py + r, fill="#00ffff", outline="white", width=2, tags="player")
            # Pulse ring
            self.create_oval(px - r*1.5, py - r*1.5, px + r*1.5, py + r*1.5, outline="#00ffff", width=1, tags="player")

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
        def draw_bar(idx, current, max_val, color, label, frame_key):
            y = y_start + idx * (bar_height + gap)

            # Check for Frame Image
            img = self.hud_imgs.get(frame_key)
            if img:
                # If frame exists, we assume it's a border/overlay.
                # We draw the BG and Fill first, then the Frame.
                # Assuming the frame image matches the bar dimensions or is centered.

                # BG (Procedural)
                self.create_rectangle(x_start, y, x_start + bar_width, y + bar_height,
                                      fill="#222222", outline="", tags="hud")

                # Fill
                if max_val > 0:
                    pct = max(0, min(1, current / max_val))
                    fill_w = int(bar_width * pct)
                    if fill_w > 0:
                        self.create_rectangle(x_start, y, x_start + fill_w, y + bar_height,
                                              fill=color, outline="", tags="hud")

                # Frame Image (Top)
                # We anchor NW to the same start point.
                self.create_image(x_start, y, image=img, anchor="nw", tags="hud")

            else:
                # Procedural Fallback
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

        draw_bar(0, char.current_health, char.max_health, "#ff3333", "HP", "HP")
        draw_bar(1, char.current_mana, char.max_mana, "#3388ff", "MP", "MP")
        draw_bar(2, char.current_stamina, char.max_stamina, "#33ff33", "SP", "SP")
        draw_bar(3, char.current_willpower, char.max_willpower, "#aa33ff", "WP", "WP")

    def refresh(self):
        # In mini mode, player movement changes map center, so we must redraw all connections/nodes
        if self.mode == 'mini':
            self.draw_map()
        else:
            self.update_player()
