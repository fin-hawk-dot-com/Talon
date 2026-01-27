# Deprecated: This file is kept for backward compatibility.
# Please use src.game_engine, src.data_loader, etc.

from src.data_loader import DataLoader
from src.combat_system import CombatManager
from src.quest_system import QuestManager
from src.inventory_system import LootManager, CraftingManager, MarketManager
from src.training_system import TrainingManager, AbilityGenerator, ConfluenceManager
from src.interaction_system import InteractionManager
from src.game_engine import GameEngine

# Re-exporting for compatibility if needed, though mostly GameEngine is the entry point
