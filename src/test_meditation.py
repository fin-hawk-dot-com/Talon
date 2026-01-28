import sys
import os
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.game_engine import GameEngine
from src.models import Attribute

def test_meditation_regeneration():
    engine = GameEngine()
    char = engine.create_character("Meditator", "Human")

    # Set stats to 50%
    char.current_health = char.max_health * 0.5
    char.current_mana = char.max_mana * 0.5
    char.current_stamina = char.max_stamina * 0.5
    char.current_willpower = char.max_willpower * 0.5

    initial_xp = char.current_xp

    # Perform Tick
    gains = engine.meditate_tick()

    # Check Gains (2%)
    assert gains['hp_gain'] == pytest.approx(char.max_health * 0.02)
    assert gains['mp_gain'] == pytest.approx(char.max_mana * 0.02)
    assert gains['sp_gain'] == pytest.approx(char.max_stamina * 0.02)
    assert gains['wp_gain'] == pytest.approx(char.max_willpower * 0.02)

    # Check updated stats
    assert char.current_health == pytest.approx(char.max_health * 0.52)
    assert char.current_mana == pytest.approx(char.max_mana * 0.52)

    # Check XP Gain
    # Spirit defaults to 10.0 for Normal rank
    # Gain should be max(0.1, 10.0 * 0.05) = 0.5
    assert gains['xp_gain'] == 0.5
    assert char.current_xp == initial_xp + 0.5

def test_meditation_clamping():
    engine = GameEngine()
    char = engine.create_character("FullHealth", "Human")

    # Set stats to max
    char.current_health = char.max_health

    gains = engine.meditate_tick()

    assert char.current_health == char.max_health
    assert gains['current_health'] == char.max_health
