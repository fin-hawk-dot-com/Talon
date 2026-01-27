from typing import List, Dict
from src.models import Character, Quest, QuestProgress, QuestStage, QuestChoice, QuestObjective
from src.data_loader import DataLoader

class QuestManager:
    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader

    def check_for_new_quests(self, character: Character) -> List[Quest]:
        """Returns a list of quests available at the character's current location."""
        available = []
        loc = character.current_location

        # Check all quests
        all_quests = self.data_loader.get_all_quests()

        for q in all_quests:
            # Check if already started or completed
            if q.id in character.quests:
                continue

            # Check location match
            if q.location == loc:
                available.append(q)

        return available

    def get_available_quests(self, character: Character) -> List[Quest]:
        # Return quests that are not started or completed
        all_quests = self.data_loader.get_all_quests()
        available = []
        for q in all_quests:
            if q.id not in character.quests:
                available.append(q)
        return available

    def start_quest(self, character: Character, quest_id: str) -> str:
        if quest_id in character.quests:
            return "Quest already started."

        quest = self.data_loader.get_quest(quest_id)
        if not quest:
            return "Quest not found."

        character.quests[quest_id] = QuestProgress(
            quest_id=quest_id,
            current_stage_id=quest.starting_stage_id,
            status="Active"
        )
        return f"Started quest: {quest.title}"

    def get_quest_status(self, character: Character, quest_id: str) -> str:
        if quest_id not in character.quests:
            return "Not Started"
        return character.quests[quest_id].status

    def make_choice(self, character: Character, quest_id: str, choice_index: int) -> str:
        if quest_id not in character.quests:
            return "Quest not active."

        progress = character.quests[quest_id]
        if progress.status != "Active":
            return f"Quest is {progress.status}."

        quest = self.data_loader.get_quest(quest_id)
        current_stage = quest.stages.get(progress.current_stage_id)

        if not current_stage:
            return "Invalid stage data."

        if choice_index < 0 or choice_index >= len(current_stage.choices):
            return "Invalid choice."

        choice = current_stage.choices[choice_index]

        # Apply consequence (Logic for rewards could go here)
        result_text = choice.consequence

        # Move to next stage
        progress.history.append(progress.current_stage_id)

        if choice.next_stage_id == "COMPLETED":
            progress.status = "Completed"
            progress.current_stage_id = "COMPLETED"
            # Grant rewards
            if quest.rewards:
                 result_text += f"\nRewards: {', '.join(quest.rewards)}"
                 reward_msgs = self._grant_rewards(character, quest.rewards)
                 if reward_msgs:
                     result_text += "\n" + "\n".join(reward_msgs)

        else:
            progress.current_stage_id = choice.next_stage_id

        return result_text

    def check_objectives(self, character: Character, event_type: str, target: str) -> List[str]:
        """Updates quest objectives based on events (e.g. kill, collect)."""
        notifications = []
        for q_id, progress in character.quests.items():
            if progress.status != "Active": continue

            quest = self.data_loader.get_quest(q_id)
            if not quest: continue

            stage = quest.stages.get(progress.current_stage_id)
            if not stage or not stage.objectives: continue

            updated = False
            for obj in stage.objectives:
                if obj.type == event_type and obj.target.lower() == target.lower():
                    key = f"{obj.type}:{obj.target}"
                    current = progress.objectives_progress.get(key, 0)
                    if current < obj.count:
                        progress.objectives_progress[key] = current + 1
                        updated = True
                        notifications.append(f"Quest Update: [{quest.title}] {obj.type} {obj.target} ({current + 1}/{obj.count})")

            if updated:
                # Check if all objectives for this stage are met
                all_met = True
                for obj in stage.objectives:
                    key = f"{obj.type}:{obj.target}"
                    if progress.objectives_progress.get(key, 0) < obj.count:
                        all_met = False
                        break

                if all_met:
                    notifications.append(f"Quest Stage Complete: [{quest.title}] - Objectives Met!")
                    if not stage.choices:
                         # Auto-advance logic for stages without choices (linear)
                         pass
        return notifications

    def _grant_rewards(self, character: Character, rewards: List[str]) -> List[str]:
        # Supported formats:
        # "Essence: <Name>"
        # "Stone: <Name>"
        # "XP: <Amount>"
        # "Lore: <Title>"
        # "Random Essence"
        # "Random Stone"

        msgs = []

        for reward in rewards:
            if reward.startswith("Lore:"):
                lore_title = reward.split(":", 1)[1].strip()
                lore_entry = self.data_loader.get_lore(lore_title)
                if lore_entry:
                    if lore_entry.id not in character.lore:
                        character.lore.append(lore_entry.id)
                        msgs.append(f"Lore Discovered: {lore_entry.title}")
                    else:
                        msgs.append(f"Lore already known: {lore_entry.title}")
                else:
                    msgs.append(f"Unknown Lore reward: {lore_title}")

            elif reward.startswith("Essence:"):
                name = reward.split(":", 1)[1].strip()
                item = self.data_loader.get_essence(name)
                if item:
                    character.inventory.append(item)
                    msgs.append(f"Received Reward: {item.name}")

            elif reward.startswith("Stone:"):
                name = reward.split(":", 1)[1].strip()
                item = self.data_loader.get_stone(name)
                if item:
                    character.inventory.append(item)
                    msgs.append(f"Received Reward: {item.name}")

            elif reward.startswith("XP:"):
                try:
                    amount = int(reward.split(":", 1)[1].strip())
                    character.current_xp += amount
                    msgs.append(f"Received {amount} XP")
                except ValueError:
                    pass

            elif "Essence" in reward: # Fallback for generic strings like "Water Essence"
                # Try to match exact name
                item = self.data_loader.get_essence(reward)
                if not item:
                    # Try stripping " Essence"
                    stripped = reward.replace(" Essence", "").strip()
                    item = self.data_loader.get_essence(stripped)

                if item:
                    character.inventory.append(item)
                    msgs.append(f"Received Reward: {item.name}")
                else:
                    # Give random essence? Or just log
                    msgs.append(f"Reward text: {reward} (Item not found)")

            elif "Stone" in reward:
                item = self.data_loader.get_stone(reward)
                if item:
                    character.inventory.append(item)
                    msgs.append(f"Received Reward: {item.name}")
                else:
                    msgs.append(f"Reward text: {reward} (Item not found)")
            else:
                 msgs.append(f"Reward: {reward}")

        return msgs
