import random
from typing import List, Optional, Tuple, Union
from src.models import Character, Ability, StatusEffect, RANK_INDICES
from src.data_loader import DataLoader

class CombatManager:
    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader

    def process_effects(self, character: Character, opponent: Optional[Character] = None) -> Tuple[List[str], bool]:
        """
        Process active status effects.
        Returns (log_messages, is_stunned)
        """
        log = []
        is_stunned = False
        active_effects = []

        for effect in character.status_effects:
            # Apply Effect
            if effect.type == "DoT":
                character.current_health -= effect.value
                log.append(f"{character.name} takes {effect.value:.1f} damage from {effect.name}!")

                # Leech Logic
                if "Leech" in effect.name and opponent and effect.source_name == opponent.name:
                    if "Mana" in effect.name:
                        restore_amt = effect.value
                        opponent.current_mana = min(opponent.max_mana, opponent.current_mana + restore_amt)
                        log.append(f"{opponent.name} leeched {restore_amt:.1f} Mana from {character.name}!")
                    else:
                        heal_amt = effect.value
                        opponent.current_health = min(opponent.max_health, opponent.current_health + heal_amt)
                        log.append(f"{opponent.name} leeched {heal_amt:.1f} Health from {character.name}!")

            elif effect.type == "CC":
                if "Stun" in effect.name or "Sleep" in effect.name:
                    is_stunned = True
                    log.append(f"{character.name} is {effect.name} and cannot act!")
            elif effect.type == "Heal":
                 character.current_health = min(character.max_health, character.current_health + effect.value)
                 log.append(f"{character.name} heals {effect.value:.1f} from {effect.name}.")

            # Decrement Duration
            effect.duration -= 1
            if effect.duration > 0:
                active_effects.append(effect)
            else:
                log.append(f"{effect.name} on {character.name} has worn off.")

        character.status_effects = active_effects
        return log, is_stunned

    def calculate_hit_chance(self, attacker: Character, defender: Character) -> float:
        # Base 90% chance
        base = 0.90
        # Speed modifier: +1% per 5 Speed difference
        diff = attacker.attributes["Speed"].value - defender.attributes["Speed"].value
        return max(0.2, min(1.0, base + (diff / 500.0)))

    def calculate_crit_chance(self, attacker: Character) -> float:
        # Base 5%
        # Spirit/Perception adds to it
        return 0.05 + (attacker.attributes["Spirit"].value / 1000.0)

    def calculate_damage(self, attacker: Character, defender: Character, is_magical: bool = False, multiplier: float = 1.0) -> Tuple[float, bool, bool]:
        """Returns (damage, is_crit, is_miss)"""
        # Hit Check
        hit_chance = self.calculate_hit_chance(attacker, defender)
        if random.random() > hit_chance:
            return 0.0, False, True # Miss

        damage = 0.0
        if is_magical:
             damage = attacker.attributes["Spirit"].value * 1.5
             defense = defender.attributes["Spirit"].value * 0.5
        else:
             damage = attacker.attributes["Power"].value * 1.5
             defense = defender.attributes["Recovery"].value * 0.5

        damage *= multiplier
        final_damage = max(1.0, damage - defense)

        # Crit Check
        is_crit = False
        if random.random() < self.calculate_crit_chance(attacker):
            final_damage *= 1.5
            is_crit = True

        # Variance
        final_damage *= random.uniform(0.9, 1.1)
        return final_damage, is_crit, False

    def execute_ability(self, user: Character, target: Character, ability: Ability) -> List[str]:
        log = []

        # Check Cooldown
        if ability.current_cooldown > 0:
            return [f"{ability.name} is on cooldown ({ability.current_cooldown} rounds left)!"]

        # Check Cost
        cost = ability.cost
        cost_type = ability.parent_stone.cost_type

        if cost_type == "Mana":
            if user.current_mana < cost:
                return [f"Not enough Mana to use {ability.name}!"]
            user.current_mana -= cost
        elif cost_type == "Stamina":
            if user.current_stamina < cost:
                return [f"Not enough Stamina to use {ability.name}!"]
            user.current_stamina -= cost
        elif cost_type == "Health":
             if user.current_health < cost:
                 return [f"Not enough Health to use {ability.name}!"]
             user.current_health -= cost

        # Set Cooldown
        ability.current_cooldown = ability.cooldown + 1

        # Determine Effect based on Function
        function = ability.parent_stone.function
        rank_mult = 1.0 + (RANK_INDICES[ability.rank] * 0.5)
        level_mult = 1.0 + (ability.level * 0.1)
        power_mult = rank_mult * level_mult

        effect_applied = None

        if "Attack" in function:
            is_magical = "Ranged" in function or "Blast" in ability.parent_stone.name
            dmg, is_crit, is_miss = self.calculate_damage(user, target, is_magical, multiplier=1.5 * power_mult)

            if is_miss:
                log.append(f"{user.name} used {ability.name} but missed!")
            else:
                target.current_health -= dmg
                crit_text = " (CRITICAL!)" if is_crit else ""
                log.append(f"Used {ability.name} on {target.name} for {dmg:.1f} damage{crit_text}!")

                # Apply Status Effects based on Flavor Keywords
                desc = ability.description.lower() + " " + function.lower()
                if "fire" in desc or "burn" in desc or "ember" in ability.parent_essence.name.lower():
                    burn_val = 5.0 * power_mult
                    target.status_effects.append(StatusEffect("Burn", 3, burn_val, "DoT", "Burns the target.", source_name=user.name))
                    effect_applied = "Burn"
                elif "ice" in desc or "frost" in desc or "cold" in ability.parent_essence.name.lower():
                    # Simplified as DoT for now, ideally Speed Debuff
                    chill_val = 3.0 * power_mult
                    target.status_effects.append(StatusEffect("Frostbite", 3, chill_val, "DoT", "Freezes the target.", source_name=user.name))
                    effect_applied = "Frostbite"
                elif "stun" in desc or "shock" in desc:
                     if random.random() < 0.3: # 30% chance to stun
                         target.status_effects.append(StatusEffect("Stun", 1, 0, "CC", "Stunned.", source_name=user.name))
                         effect_applied = "Stun"
                elif "poison" in desc or "venom" in desc:
                     poison_val = 4.0 * power_mult
                     target.status_effects.append(StatusEffect("Poison", 5, poison_val, "DoT", "Poison damage.", source_name=user.name))
                     effect_applied = "Poison"
                elif "bleed" in desc or "blood" in desc or "lacerate" in function.lower():
                     bleed_val = 3.0 * power_mult
                     target.status_effects.append(StatusEffect("Bleed", 3, bleed_val, "DoT", "Bleeding.", source_name=user.name))
                     effect_applied = "Bleed"
                elif "leech" in desc or "drain" in desc or "vampire" in ability.parent_essence.name.lower():
                     if "mana" in desc:
                         leech_val = 2.0 * power_mult
                         target.status_effects.append(StatusEffect("Mana Leech", 3, leech_val, "DoT", "Draining mana.", source_name=user.name))
                         effect_applied = "Mana Leech"
                     else:
                         leech_val = 4.0 * power_mult
                         target.status_effects.append(StatusEffect("Life Leech", 3, leech_val, "DoT", "Draining life.", source_name=user.name))
                         effect_applied = "Life Leech"

                if effect_applied:
                    log.append(f"{ability.name} applied {effect_applied} to {target.name}!")

        elif "Defense" in function:
            heal_amount = user.attributes["Spirit"].value * power_mult
            user.current_health = min(user.max_health, user.current_health + heal_amount)
            log.append(f"Used {ability.name} and restored {heal_amount:.1f} health/shield!")

            # Apply Defensive Buff
            user.status_effects.append(StatusEffect("Regen", 3, heal_amount * 0.2, "Heal", "Regenerating health.", source_name=user.name))
            log.append(f"{user.name} gains Regen!")

        elif "Heal" in function or "Sustain" in function:
             heal_amount = user.attributes["Spirit"].value * power_mult
             user.current_health = min(user.max_health, user.current_health + heal_amount)
             log.append(f"Used {ability.name} and healed for {heal_amount:.1f}!")

        elif "Summon" in function:
             log.append(f"Used {ability.name}! A summon appears to aid you!")

        else:
             dmg, is_crit, is_miss = self.calculate_damage(user, target, is_magical=True, multiplier=1.0 * power_mult)
             if is_miss:
                 log.append(f"{user.name} used {ability.name} but missed!")
             else:
                 target.current_health -= dmg
                 crit_text = " (CRITICAL!)" if is_crit else ""
                 log.append(f"Used {ability.name} on {target.name} for {dmg:.1f} damage{crit_text}!")

        if user.abilities:
             if ability.gain_xp(5):
                 log.append(f"{ability.name} leveled up to {ability.level}!")

        return log

    def combat_round(self, player: Character, enemy: Character, player_action: Union[str, Ability]) -> tuple[List[str], bool]:
        log = []

        # 0. Start of Round Effects
        p_eff_log, p_stunned = self.process_effects(player, opponent=enemy)
        log.extend(p_eff_log)
        e_eff_log, e_stunned = self.process_effects(enemy, opponent=player)
        log.extend(e_eff_log)

        # Check deaths from DoTs
        if player.current_health <= 0:
             log.append("You succumbed to your injuries!")
             return log, True
        if enemy.current_health <= 0:
             log.append(f"{enemy.name} succumbed to injuries!")
             return log, True

        # Decrement Cooldowns for Player
        if player.abilities:
            for ess_name, slots in player.abilities.items():
                for ab in slots:
                    if ab and ab.current_cooldown > 0:
                        ab.current_cooldown -= 1

        # 1. Player Turn
        if not p_stunned:
            if isinstance(player_action, Ability):
                ability_log = self.execute_ability(player, enemy, player_action)
                log.extend(ability_log)
                if ability_log and ("Not enough" in ability_log[0] or "on cooldown" in ability_log[0]):
                    return log, False # Failed action, retry input (handled by UI usually, but here we just return)

            elif player_action == "Attack":
                dmg, is_crit, is_miss = self.calculate_damage(player, enemy, is_magical=False)
                if is_miss:
                    log.append(f"You attacked {enemy.name} but missed!")
                else:
                    enemy.current_health -= dmg
                    crit_text = " CRITICAL HIT!" if is_crit else ""
                    log.append(f"You attacked {enemy.name} for {dmg:.1f} damage.{crit_text}")

            elif player_action == "Flee":
                p_speed = player.attributes["Speed"].value
                e_speed = enemy.attributes["Speed"].value
                chance = 0.5 + (p_speed - e_speed) * 0.01
                if random.random() < chance:
                    log.append("You fled successfully!")
                    return log, True
                else:
                    log.append("Failed to flee!")
        else:
            log.append("You are stunned and cannot act!")

        if enemy.current_health <= 0:
            log.append(f"{enemy.name} has been defeated!")
            return log, True

        # 2. Enemy Turn
        if not e_stunned:
            ai_action = "Attack"
            if random.random() < 0.2:
                ai_action = "Special"

            if ai_action == "Special":
                ability_names = ["Power Strike", "Shadow Blast", "Roar", "Bite"]
                ab_name = random.choice(ability_names)
                is_magical = enemy.attributes["Spirit"].value > enemy.attributes["Power"].value
                dmg, is_crit, is_miss = self.calculate_damage(enemy, player, is_magical=is_magical, multiplier=1.3)

                if is_miss:
                    log.append(f"{enemy.name} used {ab_name} but missed you!")
                else:
                    player.current_health -= dmg
                    crit_text = " (CRITICAL!)" if is_crit else ""
                    log.append(f"{enemy.name} used {ab_name} on you for {dmg:.1f} damage{crit_text}!")

                    # Enemy Special Effect Chance
                    if random.random() < 0.3:
                         player.status_effects.append(StatusEffect("Bleed", 3, 2.0, "DoT", "Bleeding.", source_name=enemy.name))
                         log.append(f"{enemy.name}'s attack caused you to Bleed!")

            else:
                is_magical = enemy.attributes["Spirit"].value > enemy.attributes["Power"].value
                dmg, is_crit, is_miss = self.calculate_damage(enemy, player, is_magical=is_magical)
                atk_type = "magically attacked" if is_magical else "attacked"

                if is_miss:
                    log.append(f"{enemy.name} {atk_type} you but missed!")
                else:
                    player.current_health -= dmg
                    crit_text = " (CRITICAL!)" if is_crit else ""
                    log.append(f"{enemy.name} {atk_type} you for {dmg:.1f} damage{crit_text}.")
        else:
            log.append(f"{enemy.name} is stunned!")

        if player.current_health <= 0:
            log.append("You have been defeated!")
            return log, True

        return log, False

    def check_combat_objectives(self, player: Character, enemy: Character, quest_mgr) -> List[str]:
        """
        Checks for quest objectives related to the defeated enemy.
        Delegates to QuestManager.
        """
        return quest_mgr.check_objectives(player, "kill", enemy.name)
