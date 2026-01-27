import math
import pytest

def calculate_movement_vector(pressed_keys, step_size):
    dx, dy = 0, 0
    if pressed_keys.get('w'): dy -= 1
    if pressed_keys.get('s'): dy += 1
    if pressed_keys.get('a'): dx -= 1
    if pressed_keys.get('d'): dx += 1

    if dx != 0 or dy != 0:
        length = math.sqrt(dx*dx + dy*dy)
        dx = (dx / length) * step_size
        dy = (dy / length) * step_size

    return dx, dy

def calculate_auto_move(current_pos, target_pos, step_size):
    cx, cy = current_pos
    tx, ty = target_pos
    dx, dy = 0, 0
    arrived = False

    dist = math.sqrt((tx-cx)**2 + (ty-cy)**2)
    if dist < step_size:
        arrived = True
        return (tx, ty), arrived
    else:
        dx = (tx - cx) / dist * step_size
        dy = (ty - cy) / dist * step_size
        return (cx + dx, cy + dy), arrived

def test_diagonal_movement_normalization():
    step = 3.0
    keys = {'w': True, 'd': True}
    dx, dy = calculate_movement_vector(keys, step)

    # Expected: dx positive, dy negative. Magnitude = step
    assert dx > 0
    assert dy < 0
    magnitude = math.sqrt(dx**2 + dy**2)
    assert abs(magnitude - step) < 0.0001

    # Check exact values: 3 * (1/sqrt(2)) = 2.1213
    assert abs(dx - 2.1213) < 0.001

def test_cardinal_movement():
    step = 5.0
    keys = {'s': True}
    dx, dy = calculate_movement_vector(keys, step)
    assert dx == 0
    assert dy == step

def test_conflicting_movement():
    step = 5.0
    keys = {'w': True, 's': True} # Cancel out
    dx, dy = calculate_movement_vector(keys, step)
    assert dx == 0
    assert dy == 0

def test_auto_move_logic():
    start = (0, 0)
    target = (10, 10)
    step = 2.0

    # First step
    new_pos, arrived = calculate_auto_move(start, target, step)
    assert not arrived
    # Direction is (1, 1). Distance is sqrt(200) = 14.14
    # Unit vector is (1/sqrt(2), 1/sqrt(2)) = (0.707, 0.707)
    # Step vector = (1.414, 1.414)
    assert abs(new_pos[0] - 1.414) < 0.01
    assert abs(new_pos[1] - 1.414) < 0.01

def test_auto_move_arrival():
    start = (9.0, 9.0)
    target = (10.0, 10.0)
    step = 2.0 # Distance is 1.414, so step > distance

    new_pos, arrived = calculate_auto_move(start, target, step)
    assert arrived
    assert new_pos == target
