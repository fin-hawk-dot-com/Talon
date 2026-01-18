import random
from src.models import Essence, AwakeningStone

class NarrativeGenerator:
    """
    Generates flavor text for game events to enhance immersion.
    """

    TRAINING_TEMPLATES = {
        "Power": [
            "You strain your muscles against the heavy resistance, feeling the fibers tear and rebuild stronger.",
            "You strike the training dummy with full force, the impact reverberating through your bones.",
            "You channel your aura into your limbs, forcing them to move with explosive power.",
            "The weight of the world feels a little lighter as you push your limits."
        ],
        "Speed": [
            "You blur through the obstacle course, your movements becoming a seamless flow.",
            "You practice your footwork, cutting through the air with razor-sharp precision.",
            "The world seems to slow down around you as you push your reflexes to the edge.",
            "You dodge imagined attacks, your body reacting before your mind even processes the threat."
        ],
        "Spirit": [
            "You sit in deep meditation, expanding your senses to feel the flow of ambient mana.",
            "You focus your will, compressing your aura until it feels dense as steel.",
            "You recite the ancient mantras, feeling the resonance within your soul.",
            "Your mind wanders through the astral currents, sharpening your connection to the arcane."
        ],
        "Recovery": [
            "You endure the scorching heat and freezing cold, tempering your body like forged steel.",
            "You focus on your breathing, willing your vitality to knit together minor strains.",
            "You push your stamina to the brink of collapse, teaching your body to persist.",
            "You allow the ambient essence to wash over you, revitalizing your weary cells."
        ]
    }

    RANK_UP_TEMPLATES = {
        "Iron": "A metallic tang fills your mouth. Your aura solidifies, shedding the frailty of mortality. You have forged your foundation in Iron.",
        "Bronze": "A heavy resonance hums within you. Your power deepens, becoming as enduring and weighty as Bronze. You are no longer easily moved.",
        "Silver": "A clear, ringing tone echoes in your soul. Impurities are purged, leaving behind a conduit of pure, conducting Silver. The world's essence flows through you freely.",
        "Gold": "A radiant warmth floods your being. You shine with an internal light, your presence commanding and incorruptible. You have achieved the luster of Gold.",
        "Diamond": "Pressure builds until you feel you might shatter, then... clarity. You are hard, multifaceted, and unbreakable. You are Diamond.",
    }

    @staticmethod
    def get_training_narrative(attribute: str, value: float) -> str:
        templates = NarrativeGenerator.TRAINING_TEMPLATES.get(attribute, ["You train hard."])
        base_text = random.choice(templates)

        # Add intensity based on value (rank approximation)
        intensity = ""
        if value > 300: # Gold+
            intensity = " The very air distorts around your exertion."
        elif value > 200: # Silver
            intensity = " Your movements leave faint afterimages of essence."
        elif value > 100: # Iron/Bronze
            intensity = " You can feel the essence permeating your flesh."

        return f"{base_text}{intensity}"

    @staticmethod
    def get_rank_up_narrative(new_rank: str, context: str = "Attribute") -> str:
        base = NarrativeGenerator.RANK_UP_TEMPLATES.get(new_rank, f"You have reached the rank of {new_rank}!")
        return f"\n*** BREAKTHROUGH ***\n{base}\nYour {context} has advanced to {new_rank} Rank!"

    @staticmethod
    def get_awakening_narrative(essence: Essence, stone: AwakeningStone, ability_name: str) -> str:
        return (
            f"\nYou press the {stone.name} against your chest. It dissolves into light, "
            f"drawn into the vortex of your {essence.name} essence.\n"
            f"Concepts of {stone.function} merge with the nature of {essence.name}...\n"
            f"Pain flashes through you, followed by a sudden understanding.\n"
            f"You have awakened: {ability_name}!"
        )

    @staticmethod
    def get_confluence_narrative(confluence_essence: Essence) -> str:
        return (
            f"\n*** CONFLUENCE MANIFESTATION ***\n"
            f"The energies of your base essences collide, swirling into a chaotic storm within your soul.\n"
            f"Slowly, order emerges from the chaos. A new, higher power takes form.\n"
            f"The {confluence_essence.name} has manifested!\n"
            f"\"{confluence_essence.description}\""
        )
