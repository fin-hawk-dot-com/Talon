import sys
import os
import unittest

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.mechanics import GameEngine
from src.models import Tile, MapSection

class TestLocomotionSystem(unittest.TestCase):
    def setUp(self):
        self.engine = GameEngine()
        self.engine.create_character("TestHero", "Human")
        # Ensure clean save state
        save_path = os.path.join("data", "saves", "TestHero_save.json")
        if os.path.exists(save_path):
            os.remove(save_path)

    def test_map_generation(self):
        print("\nTesting Map Generation...")
        section = self.engine.load_location_section("Greenstone City")
        self.assertIsNotNone(section)
        self.assertEqual(section.location_id, "Greenstone City")
        self.assertEqual(section.width, 40)
        self.assertEqual(section.height, 30)

        # Check for walls on border
        self.assertEqual(section.tiles[0][0].type, "wall")

        print("Map Generated Successfully.")

    def test_movement_and_collision(self):
        print("\nTesting Movement...")
        section = self.engine.load_location_section("Greenstone City")

        # Place player in known clear spot (center)
        cx, cy = section.width // 2, section.height // 2
        self.engine.character.grid_x = cx
        self.engine.character.grid_y = cy

        # Clear the center tile just in case
        section.tiles[cy][cx].is_passable = True
        section.tiles[cy][cx].type = "floor"
        section.tiles[cy][cx].entity = None

        # Ensure target tile is clear
        section.tiles[cy][cx+1].is_passable = True
        section.tiles[cy][cx+1].type = "floor"
        section.tiles[cy][cx+1].entity = None

        # Move Right
        success, msg = self.engine.move_player_local(1, 0)
        self.assertTrue(success, f"Move failed: {msg}")
        self.assertEqual(self.engine.character.grid_x, cx + 1)

        # Move back
        success, msg = self.engine.move_player_local(-1, 0)
        self.assertTrue(success, f"Move back failed: {msg}")
        self.assertEqual(self.engine.character.grid_x, cx)

        # Place wall next to player
        section.tiles[cy][cx+1].is_passable = False
        section.tiles[cy][cx+1].type = "wall"

        # Try moving into wall
        success, msg = self.engine.move_player_local(1, 0)
        self.assertFalse(success)
        self.assertEqual(self.engine.character.grid_x, cx)
        print("Movement and Collision Checked.")

    def test_travel_and_cache(self):
        print("\nTesting Travel and Caching...")
        section1 = self.engine.load_location_section("Greenstone City")

        # Find an exit
        exit_tile = None
        for y in range(section1.height):
            for x in range(section1.width):
                if section1.tiles[y][x].exit_to:
                    exit_tile = section1.tiles[y][x]
                    break
            if exit_tile: break

        self.assertIsNotNone(exit_tile, "No exits generated in City!")

        # Teleport player next to exit
        # Determine neighbor
        px, py = exit_tile.x, exit_tile.y
        # Try to find valid neighbor to stand on
        valid_pos = None
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                nx, ny = px+dx, py+dy
                if 0 <= nx < section1.width and 0 <= ny < section1.height:
                    if section1.tiles[ny][nx].is_passable and section1.tiles[ny][nx] != exit_tile:
                        valid_pos = (nx, ny)
                        break
            if valid_pos: break

        self.assertIsNotNone(valid_pos, "Could not find spot next to exit")
        self.engine.character.grid_x = valid_pos[0]
        self.engine.character.grid_y = valid_pos[1]

        # Move into exit
        dx = exit_tile.x - valid_pos[0]
        dy = exit_tile.y - valid_pos[1]

        success, msg = self.engine.move_player_local(dx, dy)
        self.assertTrue(success, f"Travel move failed: {msg}")
        self.assertIn("Traveled", msg)

        # Verify location changed
        new_loc = self.engine.character.current_location
        self.assertNotEqual(new_loc, "Greenstone City")

        # Verify new section loaded
        section2 = self.engine.current_section
        self.assertEqual(section2.location_id, new_loc)

        # Verify Cache
        self.assertEqual(len(self.engine.section_cache), 2)
        self.assertEqual(self.engine.section_cache[0], section2)
        self.assertEqual(self.engine.section_cache[1], section1)

        print(f"Traveled to {new_loc}. Cache verified.")

    def test_persistence(self):
        print("\nTesting Save/Load...")
        self.engine.load_location_section("Greenstone City")
        # Move somewhere
        self.engine.character.grid_x = 10
        self.engine.character.grid_y = 10

        save_msg = self.engine.save_game("TestHero_save.json")
        self.assertIn("saved", save_msg)

        # Reset Engine
        new_engine = GameEngine()
        load_msg = new_engine.load_game("TestHero_save.json")
        self.assertIn("loaded", load_msg)

        self.assertEqual(new_engine.character.name, "TestHero")
        self.assertEqual(new_engine.character.grid_x, 10)
        self.assertEqual(new_engine.character.grid_y, 10)

        # Verify cache restored (at least contains the current section)
        self.assertTrue(len(new_engine.section_cache) > 0)
        self.assertEqual(new_engine.section_cache[0].location_id, "Greenstone City")

        print("Persistence Verified.")

if __name__ == "__main__":
    unittest.main()
