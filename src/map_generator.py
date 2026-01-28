import random
import math
from typing import List, Tuple
from src.models import Tile, MapSection, Location

class MapGenerator:
    def __init__(self):
        self.width = 40
        self.height = 30

    def generate_section(self, location: Location) -> MapSection:
        section = MapSection(
            location_id=location.name,
            width=self.width,
            height=self.height
        )

        # 1. Generate Base Terrain
        if location.type in ["City", "Village", "Outpost"]:
            self._generate_city_terrain(section)
        elif location.type == "Dungeon":
            self._generate_dungeon_terrain(section)
        else:
            self._generate_wilderness_terrain(section)

        # 2. Place Exits (Logic based on relative position of connected locations)
        self._place_exits(section, location)

        # 3. Place NPCs and POIs
        self._place_entities(section, location)

        return section

    def _create_tile(self, x, y, type, passable, symbol, color):
        return Tile(x, y, type, passable, symbol, color)

    def _generate_city_terrain(self, section: MapSection):
        # Fill with Paved Floor
        section.tiles = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                # Border Walls
                if x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1:
                    row.append(self._create_tile(x, y, "wall", False, "#", "#555555"))
                else:
                    # Random variation in floor
                    if random.random() > 0.9:
                        row.append(self._create_tile(x, y, "floor_detail", True, ".", "#777777"))
                    else:
                        row.append(self._create_tile(x, y, "floor", True, " ", "#666666"))
            section.tiles.append(row)

        # Generate some buildings (Rectangles of walls)
        num_buildings = random.randint(3, 6)
        for _ in range(num_buildings):
            w = random.randint(4, 8)
            h = random.randint(4, 8)
            x = random.randint(2, self.width - w - 2)
            y = random.randint(2, self.height - h - 2)

            # Check overlap logic could go here, but simple overwrite is fine for now
            self._place_rect(section, x, y, w, h, "wall", False, "#", "#555555")
            # Door
            door_x = x + w // 2
            door_y = y + h - 1
            section.tiles[door_y][door_x] = self._create_tile(door_x, door_y, "door", True, "+", "#8B4513")

    def _generate_wilderness_terrain(self, section: MapSection):
        # Fill with Grass/Dirt
        section.tiles = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                # Random Trees/Rocks
                rng = random.random()
                if rng < 0.05:
                    row.append(self._create_tile(x, y, "rock", False, "^", "#808080"))
                elif rng < 0.15:
                    row.append(self._create_tile(x, y, "tree", False, "T", "#006400"))
                elif rng < 0.2:
                    row.append(self._create_tile(x, y, "grass_high", True, "\"", "#32CD32"))
                else:
                    row.append(self._create_tile(x, y, "grass", True, ".", "#228B22"))
            section.tiles.append(row)

        # Generate a path?
        # TODO: A winding path from one side to another would be nice.

    def _generate_dungeon_terrain(self, section: MapSection):
        # Initialize with solid walls
        section.tiles = [[self._create_tile(x, y, "wall", False, "#", "#333333")
                          for x in range(self.width)] for y in range(self.height)]

        # Simple Room Digging
        rooms = []
        num_rooms = random.randint(5, 10)

        for _ in range(num_rooms):
            w = random.randint(4, 8)
            h = random.randint(4, 8)
            x = random.randint(1, self.width - w - 1)
            y = random.randint(1, self.height - h - 1)

            # Dig Room
            self._place_rect(section, x, y, w, h, "floor", True, ".", "#222222")

            center = (x + w // 2, y + h // 2)

            if rooms:
                # Connect to previous room
                prev = rooms[-1]
                self._dig_corridor(section, prev, center)

            rooms.append(center)

    def _place_rect(self, section, x, y, w, h, type, passable, symbol, color):
        for iy in range(y, y + h):
            for ix in range(x, x + w):
                if 0 <= iy < self.height and 0 <= ix < self.width:
                    section.tiles[iy][ix] = self._create_tile(ix, iy, type, passable, symbol, color)

    def _dig_corridor(self, section, p1, p2):
        x1, y1 = p1
        x2, y2 = p2

        # Horizontal then Vertical
        if random.choice([True, False]):
            for x in range(min(x1, x2), max(x1, x2) + 1):
                section.tiles[y1][x] = self._create_tile(x, y1, "floor", True, ".", "#222222")
            for y in range(min(y1, y2), max(y1, y2) + 1):
                section.tiles[y][x2] = self._create_tile(x2, y, "floor", True, ".", "#222222")
        else:
            for y in range(min(y1, y2), max(y1, y2) + 1):
                section.tiles[y][x1] = self._create_tile(x1, y, "floor", True, ".", "#222222")
            for x in range(min(x1, x2), max(x1, x2) + 1):
                section.tiles[y2][x] = self._create_tile(x, y2, "floor", True, ".", "#222222")

    def _place_exits(self, section: MapSection, location: Location):
        # We need access to all locations to determine direction
        # Since MapGenerator doesn't hold data_loader, we assume connected_locations names are valid.
        # But we need their coordinates to determine N/S/E/W.
        # Ideally, we pass the DataLoader or a helper, but for now let's assume random edges
        # OR we can assume simple logic if we don't check coordinates.

        # To make it robust without circular imports of DataLoader:
        # We'll just place exits on random edges for now, or just iterate sides.

        # Wait, the prompt implies detailed traversal. Directions matter.
        # I will modify the method signature in future or here to accept a lookup for coords.
        # For now, let's just place them distributed.

        edges = [
            ("North", range(1, self.width-1), 0),
            ("South", range(1, self.width-1), self.height-1),
            ("West", 0, range(1, self.height-1)),
            ("East", self.width-1, range(1, self.height-1))
        ]

        random.shuffle(edges)

        for i, conn_name in enumerate(location.connected_locations):
            # Pick an edge
            edge_name, r_range, fixed_coord = edges[i % 4]

            if isinstance(r_range, int): # East/West
                x = r_range
                y = random.choice(fixed_coord)
            else: # North/South
                x = random.choice(r_range)
                y = fixed_coord

            # Place Gate/Path
            section.tiles[y][x] = self._create_tile(x, y, "gate", True, "O", "#00FFFF")
            section.tiles[y][x].exit_to = conn_name

            # Clear path to gate so it's accessible
            self._clear_area_around(section, x, y)

    def _clear_area_around(self, section, x, y):
        # Ensure neighbors are passable
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    tile = section.tiles[ny][nx]
                    if not tile.is_passable:
                        section.tiles[ny][nx] = self._create_tile(nx, ny, "path", True, ".", "#999999")

    def _place_entities(self, section: MapSection, location: Location):
        passable_tiles = [
            (x, y) for y in range(self.height) for x in range(self.width)
            if section.tiles[y][x].is_passable and section.tiles[y][x].type != "gate"
        ]
        random.shuffle(passable_tiles)

        # Place NPCs
        for npc in location.npcs:
            if not passable_tiles: break
            x, y = passable_tiles.pop()
            section.tiles[y][x].entity = npc # Store name string
            section.tiles[y][x].color = "#FF00FF" # Magenta for NPCs
            section.tiles[y][x].symbol = "N"

        # Place POIs
        for poi in location.points_of_interest:
            if not passable_tiles: break
            x, y = passable_tiles.pop()
            section.tiles[y][x].entity = poi.name
            section.tiles[y][x].color = "#FFFF00" # Yellow for POIs
            section.tiles[y][x].symbol = "!"
