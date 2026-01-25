import pytest
from src.game_engine import GameEngine
from src.models import Character, Attribute

def test_meditation_gains():
    engine = GameEngine()
    # Create a dummy character manually to avoid dependency on data_loader for this unit test if possible
    # But create_character uses data_loader. Let's just instantiate Character directly and attach to engine.

    char = Character(name="Meditator", race="Human")
    # Set attributes
    char.attributes['Spirit'] = Attribute("Spirit", 50.0) # Should give 5 XP
    char.attributes['Recovery'] = Attribute("Recovery", 10.0) # Max HP/SP = 100

    # Recalculate maxes (properties depend on attributes)
    # HP = Recovery * 10 = 100

    # Set current values low
    char.current_health = 50.0
    char.current_mana = 50.0
    char.current_stamina = 50.0
    char.current_willpower = 50.0
    char.current_xp = 0

    engine.character = char

    # Call meditate_tick
    gains = engine.meditate_tick()

    # Verification
    assert gains['xp'] == 5 # 50 * 0.1
    assert char.current_xp == 5

    # Restore is 2% of max. Max HP is 100. 2% is 2.
    assert gains['hp'] == 2.0
    assert char.current_health == 52.0

    # Test capping
    char.current_health = 99.0
    engine.meditate_tick()
    assert char.current_health == 100.0 # Capped at max

    print("Meditation test passed!")

if __name__ == "__main__":
    test_meditation_gains()
