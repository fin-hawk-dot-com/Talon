import tkinter as tk
from src.models import MapSection, Character

class LocalMapWidget(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg="#111111", highlightthickness=0, **kwargs)
        self.section = None
        self.player = None
        self.tile_size = 20
        self.bind("<Configure>", self.on_resize)
        self.bind("<Motion>", self.on_mouse_move)

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

                # Draw Detail Symbol (optional, low opacity text?)
                if tile.type == "tree":
                    self.create_text((x1+x2)/2, (y1+y2)/2, text="♣", fill="#006600", font=("Arial", int(self.tile_size/1.5)))
                elif tile.type == "rock":
                    self.create_text((x1+x2)/2, (y1+y2)/2, text="▲", fill="#333333", font=("Arial", int(self.tile_size/2)))
                elif tile.type == "water":
                    self.create_text((x1+x2)/2, (y1+y2)/2, text="~", fill="#0000aa", font=("Arial", int(self.tile_size)))

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

            # Avatar
            self.create_oval(px+2, py+2, px+self.tile_size-2, py+self.tile_size-2, fill="white", outline="#00aaff", width=2)
            self.create_text(px+self.tile_size/2, py+self.tile_size/2, text="@", fill="black", font=("Arial", int(self.tile_size/1.5), "bold"))
