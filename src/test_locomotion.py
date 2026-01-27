import sys
import os
import math

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.mechanics import GameEngine

def test_locomotion():
    engine = GameEngine()
    char = engine.create_character("TestChar", "Human")

    # 1. Check Initialization
    print(f"Initial Location: {char.current_location}")
    print(f"Initial Coords: ({char.x}, {char.y})")

    assert char.x != -1
    assert char.y != -1

    # Greenstone City is at 500, 500
    assert char.x == 500
    assert char.y == 500

    # 2. Test Movement (update_position)
    # Move North (dy = -20)
    engine.update_position(0, -20)
    print(f"After moving North 20: ({char.x}, {char.y})")
    assert char.x == 500
    assert char.y == 480
    assert char.current_location == "Greenstone City" # Still technically at the city logically until arrival elsewhere

    # 3. Test Arrival
    # North Road is at 500, 325.
    # We are at 500, 480. Distance to North Road is 155.
    # Move closer to North Road.
    # Target y = 325.
    # Delta = 325 - 480 = -155.

    msg = engine.update_position(0, -155)
    print(f"Moved to North Road: ({char.x}, {char.y})")
    print(f"Message: {msg}")

    assert char.x == 500
    assert char.y == 325
    assert char.current_location == "North Road"
    assert msg == "Arrived at North Road"

    # 4. Test Clamping
    engine.update_position(0, -1000) # Should hit 0
    print(f"After massive move North: ({char.x}, {char.y})")
    assert char.y == 0

    print("Locomotion Test Passed!")

if __name__ == "__main__":
    test_locomotion()
