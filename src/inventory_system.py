import random
from typing import Optional, Union, List
from src.models import Character, Essence, AwakeningStone, Consumable
from src.data_loader import DataLoader

class LootManager:
    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader

    def generate_random_loot(self) -> Optional[Union[Essence, AwakeningStone]]:
        """Generates a random Essence or Awakening Stone."""
        roll = random.random()
        if roll < 0.1: # 10% chance for Essence
            essences = self.data_loader.get_all_base_essences()
            if not essences: return None
            name = random.choice(essences)
            return self.data_loader.get_essence(name)
        elif roll < 0.2: # 10% chance for Stone
            stones = self.data_loader.get_all_stones()
            if not stones: return None
            name = random.choice(stones)
            return self.data_loader.get_stone(name)
        else:
            return None

    def get_loot_for_monster(self, monster: Character) -> List[Union[Essence, AwakeningStone]]:
        loot = []
        # 1. Fixed Loot Table
        for item_name in monster.loot_table:
            item = self.data_loader.get_essence(item_name)
            if not item:
                item = self.data_loader.get_stone(item_name)
            if item:
                loot.append(item)

        # 2. Random Drop Chance (based on Rank?)
        # Higher rank = better chance?
        # For now, flat small chance for extra random loot
        random_item = self.generate_random_loot()
        if random_item:
            loot.append(random_item)

        return loot

class CraftingManager:
    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader
        self.recipes = {
            "Healing Potion": {"Herbs": 2, "Water Essence": 1},
            "Mana Potion": {"Herbs": 2, "Crystal Essence": 1},
            "Antidote": {"Herbal Medicine": 1},
            "Iron Skin Elixir": {"Obsidian": 1, "Basic Supplies": 1}
        }

    def gather_resources(self, character: Character, location_name: str) -> str:
        loc = self.data_loader.get_location(location_name)
        if not loc or not loc.resources:
            return "No resources found here."

        if random.random() < 0.6: # 60% chance
            resource = random.choice(loc.resources)
            # Check if resource is an Essence
            essence = self.data_loader.get_essence(resource)
            if essence:
                character.inventory.append(essence)
                return f"Gathered {essence.name}!"
            else:
                # Material
                count = character.materials.get(resource, 0)
                character.materials[resource] = count + 1
                return f"Gathered {resource}!"
        else:
            return "Found nothing."

    def craft_item(self, character: Character, recipe_name: str) -> str:
        recipe = self.recipes.get(recipe_name)
        if not recipe:
            return "Recipe not known."

        # Check materials
        for mat, qty in recipe.items():
            # Check inventory for Essence
            if "Essence" in mat:
                target_name = mat.replace(" Essence", "")
                # Count essences in inventory
                count = sum(1 for i in character.inventory if isinstance(i, Essence) and (i.name == mat or i.name == target_name))
                if count < qty:
                    return f"Not enough {mat} (Need {qty})."
            else:
                if character.materials.get(mat, 0) < qty:
                    return f"Not enough {mat} (Need {qty})."

        # Consume materials
        for mat, qty in recipe.items():
            if "Essence" in mat:
                target_name = mat.replace(" Essence", "")
                removed = 0
                to_remove = []
                for idx, item in enumerate(character.inventory):
                    if isinstance(item, Essence) and (item.name == mat or item.name == target_name):
                        to_remove.append(idx)
                        removed += 1
                        if removed >= qty:
                            break
                # Remove in reverse order
                for idx in sorted(to_remove, reverse=True):
                    character.inventory.pop(idx)
            else:
                character.materials[mat] -= qty

        # Give Result
        consumable = self.data_loader.get_consumable(recipe_name.lower())
        if consumable:
            character.inventory.append(consumable)
            return f"Crafted {consumable.name}!"

        return "Crafted item data not found."

class MarketManager:
    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader

    def get_shop_inventory(self, location_name: str) -> List[Union[Consumable, AwakeningStone, Essence]]:
        # Generate random stock based on location?
        # For simplicity, fixed stock + random rotation
        stock = []

        # Potions
        for name in ["healing potion", "mana potion", "antidote"]:
             item = self.data_loader.get_consumable(name)
             if item: stock.append(item)

        # Random Stones
        all_stones = self.data_loader.get_all_stones()
        for _ in range(3):
            s_name = random.choice(all_stones)
            stone = self.data_loader.get_stone(s_name)
            if stone: stock.append(stone)

        return stock

    def buy_item(self, character: Character, item: Union[Consumable, AwakeningStone, Essence]) -> str:
        price = getattr(item, 'price', getattr(item, 'value', 0))
        if character.currency >= price:
            character.currency -= price
            character.inventory.append(item)
            return f"Bought {item.name} for {price} Dram."
        return "Not enough Dram."

    def sell_item(self, character: Character, inv_index: int) -> str:
        if inv_index < 0 or inv_index >= len(character.inventory):
            return "Invalid item."

        item = character.inventory[inv_index]
        value = getattr(item, 'price', getattr(item, 'value', 0)) // 2 # Sell for half price
        if value < 1: value = 1

        character.currency += value
        character.inventory.pop(inv_index)
        return f"Sold {item.name} for {value} Dram."
