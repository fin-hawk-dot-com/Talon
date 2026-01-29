import tkinter as tk
import os
from src.models import MapSection, Character

class LocalMapWidget(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg="#111111", highlightthickness=0, **kwargs)
        self.section = None
        self.player = None
        self.tile_size = 20
        self.bind("<Configure>", self.on_resize)
        self.bind("<Motion>", self.on_mouse_move)

        # HUD Assets
        self.hud_imgs = {}
        self.load_hud_images()

        # Player Assets
        self.player_img = None
        self.last_affinity = None

        # Colors map
        self.colors = {
            "wall": "#444444",
            "floor": "#222222",
            "floor_detail": "#2a2a2a",
            "grass": "#1a331a",
            "grass_high": "#224422",
            "tree": "#004400",
            "rock": "#555555",
            "water": "#000088",
            "path": "#3a3a2a",
            "gate": "#00aaaa",
            "door": "#553311"
        }

    def render(self, section: MapSection, player: Character):
        self.section = section
        self.player = player
        self.draw()

    def on_resize(self, event):
        if self.section:
            self.draw()

    def on_mouse_move(self, event):
        # Simple tooltip logic
        self.delete("tooltip")
        if not self.section: return

        # Reverse transform
        w = self.winfo_width()
        h = self.winfo_height()
        rows = self.section.height
        cols = self.section.width

        ts = self.tile_size
        offset_x = (w - cols * ts) / 2
        offset_y = (h - rows * ts) / 2

        gx = int((event.x - offset_x) / ts)
        gy = int((event.y - offset_y) / ts)

        tile = self.section.get_tile(gx, gy)
        if tile:
            text = ""
            if tile.entity:
                text = str(tile.entity)
            elif tile.exit_to:
                text = f"Exit to {tile.exit_to}"
            elif tile.type == "tree":
                text = "Tree"

            if text:
                self.create_text(event.x + 10, event.y - 10, text=text, fill="white", anchor="sw", tags="tooltip", font=("Arial", 10, "bold"))

    def draw(self):
        self.delete("all")
        if not self.section: return

        # Calculate tile size
        w = self.winfo_width()
        h = self.winfo_height()
        if w <= 1: w = 800
        if h <= 1: h = 600

        rows = self.section.height
        cols = self.section.width

        ts_x = w / cols
        ts_y = h / rows
        self.tile_size = min(ts_x, ts_y)

        # Center the map
        total_w = cols * self.tile_size
        total_h = rows * self.tile_size
        offset_x = (w - total_w) / 2
        offset_y = (h - total_h) / 2

        # Optimization: Only draw if visible? (Canvas handles occlusion well enough for 40x30)

        for y, row in enumerate(self.section.tiles):
            for x, tile in enumerate(row):
                x1 = offset_x + x * self.tile_size
                y1 = offset_y + y * self.tile_size
                x2 = x1 + self.tile_size
                y2 = y1 + self.tile_size

                # Draw Tile Base
                color = self.colors.get(tile.type, tile.color)
                self.create_rectangle(x1, y1, x2, y2, fill=color, outline="", tags="tile")

                # Procedural Tile Details
                if tile.type == "wall":
                    # Bricks
                    self.create_line(x1, y1+self.tile_size/2, x2, y1+self.tile_size/2, fill="#333333", width=1, tags="tile")
                    self.create_line(x1+self.tile_size/2, y1, x1+self.tile_size/2, y1+self.tile_size/2, fill="#333333", width=1, tags="tile")
                    self.create_line(x1+self.tile_size/4, y1+self.tile_size/2, x1+self.tile_size/4, y2, fill="#333333", width=1, tags="tile")
                    self.create_line(x1+3*self.tile_size/4, y1+self.tile_size/2, x1+3*self.tile_size/4, y2, fill="#333333", width=1, tags="tile")

                elif tile.type in ["grass", "grass_high"]:
                    # Grass tufts
                    import random
                    # Use deterministic random based on coords
                    rd = random.Random(x * 1000 + y)
                    for _ in range(3):
                        gx = rd.uniform(x1+2, x2-2)
                        gy = rd.uniform(y1+2, y2-2)
                        self.create_line(gx, gy, gx-2, gy-4, fill="#00cc00", width=1, tags="tile")
                        self.create_line(gx, gy, gx+2, gy-4, fill="#00cc00", width=1, tags="tile")

                elif tile.type == "water":
                    # Waves
                    self.create_arc(x1+2, y1+5, x2-2, y2-5, start=0, extent=180, style=tk.ARC, outline="#4444ff", width=1, tags="tile")
                    self.create_arc(x1+2, y1+10, x2-2, y2, start=0, extent=180, style=tk.ARC, outline="#4444ff", width=1, tags="tile")

                elif tile.type == "floor":
                    # Noise/Speckles
                    self.create_oval(x1+5, y1+5, x1+6, y1+6, fill="#333333", outline="", tags="tile")
                    self.create_oval(x2-6, y2-6, x2-5, y2-5, fill="#333333", outline="", tags="tile")

                # Draw Detail Symbol (Overlay)
                if tile.type == "tree":
                    # Detailed Tree
                    # Trunk
                    self.create_rectangle(x1+self.tile_size*0.4, y1+self.tile_size*0.6, x2-self.tile_size*0.4, y2, fill="#442200", outline="", tags="tile")
                    # Foliage
                    self.create_oval(x1, y1, x2, y1+self.tile_size*0.8, fill="#006600", outline="#004400", tags="tile")
                elif tile.type == "rock":
                    # Detailed Rock
                    self.create_oval(x1+2, y1+5, x2-2, y2-2, fill="#555555", outline="#333333", tags="tile")
                    self.create_text((x1+x2)/2, (y1+y2)/2, text=".", fill="#222222", font=("Arial", 10), tags="tile")

                # Draw Exit
                if tile.exit_to:
                     self.create_rectangle(x1, y1, x2, y2, fill=self.colors["gate"], outline="white", width=1)
                     # self.create_text((x1+x2)/2, (y1+y2)/2, text="EXIT", font=("Arial", int(self.tile_size/3)), fill="white")

                # Draw Entity/Symbol
                if tile.entity:
                    # NPC/POI
                    fill = "#FF00FF" if tile.symbol == "N" else "#FFFF00"
                    self.create_oval(x1+4, y1+4, x2-4, y2-4, fill=fill, outline="black", width=1)
                    # Label
                    # self.create_text((x1+x2)/2, y1-5, text=str(tile.entity), fill="white", font=("Arial", 8))

        # Draw Player
        if self.player and self.player.grid_x != -1:
            px = offset_x + self.player.grid_x * self.tile_size
            py = offset_y + self.player.grid_y * self.tile_size
            self.draw_player(px, py, self.tile_size)

        # Draw HUD
        self.draw_hud()

    def load_player_image(self):
        if not self.player: return

        if self.player_img and self.last_affinity == self.player.affinity:
            return

        self.last_affinity = self.player.affinity
        # Try loading specific affinity avatar
        filename = f"{self.player.affinity}.png"
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

    def draw_player(self, x, y, size):
        self.load_player_image()

        # Priority 1: Image
        if self.player_img:
            # Center image
            self.create_image(x + size/2, y + size/2, image=self.player_img, tags="player")
            return

        # Priority 2: Detailed Procedural Shape based on Affinity
        affinity = self.player.affinity if self.player else "General"
        cx, cy = x + size/2, y + size/2
        r = size/2 - 2

        if affinity == "Warrior":
            # Red Shield & Sword
            self.create_rectangle(x+4, y+4, x+size-4, y+size-4, fill="#880000", outline="#aaaaaa", width=2, tags="player")
            # Cross
            self.create_line(x+4, y+4, x+size-4, y+size-4, fill="#aaaaaa", width=2, tags="player")
            self.create_line(x+size-4, y+4, x+4, y+size-4, fill="#aaaaaa", width=2, tags="player")

        elif affinity == "Mage":
            # Blue Orb/Staff
            self.create_oval(cx-r, cy-r, cx+r, cy+r, fill="#2222ff", outline="#ffff00", width=2, tags="player")
            # Star inside
            self.create_text(cx, cy, text="★", fill="white", font=("Arial", int(size/1.5)), tags="player")

        elif affinity == "Rogue":
            # Green Cloak / Triangle
            points = [cx, y+2, x+size-2, y+size-2, x+2, y+size-2]
            self.create_polygon(points, fill="#006600", outline="#000000", width=1, tags="player")
            # Dagger line
            self.create_line(cx, y+size/2, cx, y+size-2, fill="silver", width=2, tags="player")

        elif affinity == "Guardian":
            # Silver Shield (Tower)
            self.create_rectangle(x+size*0.2, y+2, x+size*0.8, y+size-2, fill="#aaaaaa", outline="gold", width=2, tags="player")
            self.create_line(x+size*0.2, y+size*0.4, x+size*0.8, y+size*0.4, fill="gold", width=1, tags="player")

        elif affinity == "Support":
            # White Cross/Heart
            self.create_oval(cx-r, cy-r, cx+r, cy+r, fill="#ffffff", outline="#00ff00", width=2, tags="player")
            self.create_text(cx, cy, text="+", fill="#00ff00", font=("Arial", int(size), "bold"), tags="player")

        else: # General or Fallback
            # White Oval with @
            self.create_oval(x+2, y+2, x+size-2, y+size-2, fill="white", outline="#00aaff", width=2, tags="player")
            self.create_text(cx, cy, text="@", fill="black", font=("Arial", int(size/1.5), "bold"), tags="player")

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

    def draw_hud(self):
        char = self.player
        if not char: return

        # Dimensions
        w = self.winfo_width()
        if w <= 1: w = int(self['width']) if 'width' in self.keys() else 800
        h = self.winfo_height()
        if h <= 1: h = int(self['height']) if 'height' in self.keys() else 600

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
