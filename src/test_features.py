import pytest
from src.mechanics import GameEngine, CombatManager, CraftingManager, MarketManager
from src.models import Character, Attribute, Essence, AwakeningStone, StatusEffect, Consumable

def test_crafting():
    engine = GameEngine()
    char = engine.create_character("TestCrafter", "Human")

    # Manually add materials and test craft
    char.materials["Herbs"] = 2
    # Ensure Water Essence is available
    essence = engine.data_loader.get_essence("Water Essence")
    if not essence:
        pytest.skip("Water Essence not found in data")

    char.inventory.append(essence)

    # Test Crafting Healing Potion
    res = engine.crafting_mgr.craft_item(char, "Healing Potion")
    assert "Crafted Healing Potion" in res
    assert any(isinstance(i, Consumable) and i.name == "Healing Potion" for i in char.inventory)
    assert char.materials["Herbs"] == 0

def test_market():
    engine = GameEngine()
    char = engine.create_character("TestTrader", "Human")
    char.currency = 1000 # Enough to buy

    # Get inventory
    stock = engine.market_mgr.get_shop_inventory("Greenstone City")
    assert len(stock) > 0

    # Buy item
    item_to_buy = stock[0]
    initial_currency = char.currency
    price = getattr(item_to_buy, 'price', getattr(item_to_buy, 'value', 0))

    res = engine.market_mgr.buy_item(char, item_to_buy)
    assert "Bought" in res
    assert item_to_buy in char.inventory
    assert char.currency == initial_currency - price

    # Sell item
    item_idx = len(char.inventory) - 1
    res = engine.market_mgr.sell_item(char, item_idx)
    assert "Sold" in res
    assert len(char.inventory) == 0
    # Sold for half price
    assert char.currency == initial_currency - price + (price // 2)

def test_combat_effects():
    engine = GameEngine()
    p1 = engine.create_character("P1", "Human")
    p2 = engine.create_character("P2", "Orc")

    p1.attributes["Speed"].value = 100
    p2.current_health = 100.0

    # Test Bleed
    # Manually apply bleed
    p2.status_effects.append(StatusEffect("Bleed", 3, 5.0, "DoT", "Bleeding", source_name=p1.name))

    initial_hp = p2.current_health
    engine.combat_mgr.process_effects(p2, opponent=p1)
    assert p2.current_health == initial_hp - 5.0

    # Test Life Leech
    p1.current_health = 50.0
    p1.attributes["Recovery"].value = 100 # High max HP

    p2.status_effects = []
    p2.status_effects.append(StatusEffect("Life Leech", 3, 10.0, "DoT", "Leeching", source_name=p1.name))

    engine.combat_mgr.process_effects(p2, opponent=p1)
    assert p1.current_health == 60.0 # 50 + 10
    assert p2.current_health < initial_hp - 5.0 # Took damage from leech

    # Test Mana Leech
    p1.current_mana = 10.0
    p1.attributes["Spirit"].value = 100 # High max Mana

    p2.status_effects = []
    p2.status_effects.append(StatusEffect("Mana Leech", 3, 5.0, "DoT", "Leeching Mana", source_name=p1.name))

    engine.combat_mgr.process_effects(p2, opponent=p1)
    assert p1.current_mana == 15.0 # 10 + 5
    # Mana leech typically deals damage too (drain) or just drain?
    # Current implementation applies DoT damage AND restores source mana.
    # Effect is type "DoT", so it deals damage.
