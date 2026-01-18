from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class AbilityTemplate:
    pattern: str
    function: str
    description_template: str
    essence_tags: List[str] = field(default_factory=list)
    affinity_weight: Dict[str, float] = field(default_factory=lambda: {"General": 1.0})

# Affinity Types: Warrior, Mage, Rogue, Guardian, Support, General

ABILITY_TEMPLATES = [
    # --- Melee Attack ---
    AbilityTemplate(
        pattern="{essence} Strike",
        function="Melee Attack",
        description_template="Delivers a powerful physical blow infused with {essence}.",
        affinity_weight={"Warrior": 10.0, "Rogue": 5.0, "Guardian": 3.0, "General": 5.0}
    ),
    AbilityTemplate(
        pattern="{essence} Slash",
        function="Melee Attack",
        description_template="A quick cutting attack leaving a trail of {essence}.",
        affinity_weight={"Rogue": 10.0, "Warrior": 5.0, "General": 5.0}
    ),
    AbilityTemplate(
        pattern="{essence} Smash",
        function="Melee Attack",
        description_template="A heavy crushing blow with the weight of {essence}.",
        affinity_weight={"Warrior": 8.0, "Guardian": 8.0, "General": 4.0},
        essence_tags=["Heavy", "Earth", "Metal", "Physical"]
    ),
    AbilityTemplate(
        pattern="{essence} Blade",
        function="Melee Attack",
        description_template="Manifests a weapon of pure {essence} to strike the foe.",
        affinity_weight={"Mage": 5.0, "Warrior": 5.0, "General": 5.0},
        essence_tags=["Elemental", "Energy"]
    ),

    # --- Ranged Attack ---
    AbilityTemplate(
        pattern="{essence} Bolt",
        function="Ranged Attack",
        description_template="Fires a concentrated bolt of {essence} at the target.",
        affinity_weight={"Mage": 10.0, "Rogue": 5.0, "General": 5.0}
    ),
    AbilityTemplate(
        pattern="{essence} Wave",
        function="Ranged Attack",
        description_template="Unleashes a wide wave of {essence} energy.",
        affinity_weight={"Mage": 8.0, "Support": 4.0, "General": 5.0},
        essence_tags=["Liquid", "Gas", "Energy"]
    ),
    AbilityTemplate(
        pattern="{essence} Shot",
        function="Ranged Attack",
        description_template="A precise shot imbued with {essence}.",
        affinity_weight={"Rogue": 10.0, "Warrior": 3.0, "General": 5.0},
        essence_tags=["Physical", "Weapon"]
    ),

    # --- Defense ---
    AbilityTemplate(
        pattern="{essence} Shield",
        function="Defense",
        description_template="Creates a barrier of {essence} to block attacks.",
        affinity_weight={"Guardian": 10.0, "Mage": 5.0, "Support": 8.0, "General": 5.0}
    ),
    AbilityTemplate(
        pattern="{essence} Skin",
        function="Defense",
        description_template="Coats the user's skin in {essence}, increasing durability.",
        affinity_weight={"Warrior": 8.0, "Guardian": 8.0, "General": 5.0},
        essence_tags=["Physical", "Biological", "Earth", "Metal"]
    ),
    AbilityTemplate(
        pattern="{essence} Aura",
        function="Defense",
        description_template="Radiates a protective aura of {essence}.",
        affinity_weight={"Support": 10.0, "Mage": 5.0, "Guardian": 5.0, "General": 5.0},
        essence_tags=["Energy", "Light", "Dark", "Holy"]
    ),

    # --- Area Denial ---
    AbilityTemplate(
        pattern="{essence} Trap",
        function="Area Denial",
        description_template="Sets a hidden trap that releases {essence} when triggered.",
        affinity_weight={"Rogue": 10.0, "Mage": 5.0, "General": 5.0}
    ),
    AbilityTemplate(
        pattern="Field of {essence}",
        function="Area Denial",
        description_template="Covers an area in {essence}, damaging or hindering enemies within.",
        affinity_weight={"Mage": 10.0, "Support": 5.0, "Guardian": 5.0, "General": 5.0}
    ),

    # --- Summoning ---
    AbilityTemplate(
        pattern="Summon {essence} Spirit",
        function="Summoning",
        description_template="Calls forth a spirit composed of {essence}.",
        affinity_weight={"Mage": 10.0, "Support": 5.0, "General": 5.0}
    ),
    AbilityTemplate(
        pattern="{essence} Golem",
        function="Summoning",
        description_template="Constructs a golem from {essence} to fight for you.",
        affinity_weight={"Mage": 8.0, "Guardian": 5.0, "General": 5.0},
        essence_tags=["Earth", "Metal", "Ice", "Solid"]
    ),

    # --- Multi-Hit ---
    AbilityTemplate(
        pattern="{essence} Barrage",
        function="Multi-Hit",
        description_template="Unleashes a rapid-fire volley of {essence} projectiles.",
        affinity_weight={"Mage": 8.0, "Rogue": 8.0, "General": 5.0}
    ),
    AbilityTemplate(
        pattern="Flurry of {essence}",
        function="Multi-Hit",
        description_template="Strikes multiple times in the blink of an eye with {essence}.",
        affinity_weight={"Warrior": 8.0, "Rogue": 10.0, "General": 5.0},
        essence_tags=["Physical", "Speed", "Wind"]
    ),

    # --- Drain/Sustain ---
    AbilityTemplate(
        pattern="{essence} Drain",
        function="Drain/Sustain",
        description_template="Saps energy from the target to fuel {essence}.",
        affinity_weight={"Mage": 8.0, "Rogue": 5.0, "General": 5.0}
    ),
    AbilityTemplate(
        pattern="Feast of {essence}",
        function="Drain/Sustain",
        description_template="Consumes the target's vitality to restore health.",
        affinity_weight={"Warrior": 5.0, "Guardian": 5.0, "Mage": 5.0, "General": 5.0},
        essence_tags=["Blood", "Life", "Dark", "Biological"]
    ),

    # --- Body Mod ---
    AbilityTemplate(
        pattern="{essence} Form",
        function="Body Mod",
        description_template="Transforms the body into {essence}, altering physiology.",
        affinity_weight={"Warrior": 5.0, "Guardian": 5.0, "Mage": 5.0, "General": 5.0}
    ),
    AbilityTemplate(
        pattern="{essence} Eyes",
        function="Body Mod",
        description_template="Mutates the eyes to see {essence} spectrums.",
        affinity_weight={"Rogue": 8.0, "Support": 5.0, "General": 5.0},
        essence_tags=["Perception", "Light", "Dark", "Vision"]
    ),

    # --- Celestial/Augment ---
    AbilityTemplate(
        pattern="Avatar of {essence}",
        function="Celestial/Augment",
        description_template="Channels {essence} to vastly increase attributes.",
        affinity_weight={"Warrior": 5.0, "Mage": 5.0, "General": 5.0}
    ),
    AbilityTemplate(
        pattern="{essence} Blessing",
        function="Celestial/Augment",
        description_template="Grants a holy blessing of {essence} to allies.",
        affinity_weight={"Support": 10.0, "Guardian": 5.0, "General": 5.0},
        essence_tags=["Light", "Life", "Holy", "Recovery"]
    ),

    # --- Mobility ---
    AbilityTemplate(
        pattern="{essence} Step",
        function="Mobility",
        description_template="Uses {essence} to move instantly short distances.",
        affinity_weight={"Rogue": 10.0, "Warrior": 5.0, "Mage": 5.0, "General": 5.0}
    ),
    AbilityTemplate(
        pattern="{essence} Flight",
        function="Mobility",
        description_template="Grants the ability to fly on wings of {essence}.",
        affinity_weight={"Mage": 5.0, "Support": 5.0, "General": 5.0},
        essence_tags=["Air", "Wind", "Wing", "Light"]
    ),

    # --- Replication ---
    AbilityTemplate(
        pattern="{essence} Clone",
        function="Replication",
        description_template="Creates a copy of the user made of {essence}.",
        affinity_weight={"Rogue": 10.0, "Mage": 8.0, "General": 5.0}
    ),
    AbilityTemplate(
        pattern="{essence} Echo",
        function="Replication",
        description_template="Repeats the last action with an echo of {essence}.",
        affinity_weight={"Mage": 8.0, "Support": 5.0, "General": 5.0}
    ),

    # --- Terrain Control ---
    AbilityTemplate(
        pattern="Wall of {essence}",
        function="Terrain Control",
        description_template="Raises a solid wall of {essence}.",
        affinity_weight={"Guardian": 10.0, "Mage": 8.0, "Support": 5.0, "General": 5.0}
    ),
    AbilityTemplate(
        pattern="{essence} Prison",
        function="Terrain Control",
        description_template="Encases the enemy in a structure of {essence}.",
        affinity_weight={"Mage": 8.0, "Guardian": 8.0, "General": 5.0}
    ),

    # --- Perception ---
    AbilityTemplate(
        pattern="{essence} Sight",
        function="Perception",
        description_template="Allows the user to sense {essence} and hidden things.",
        affinity_weight={"Rogue": 10.0, "Support": 8.0, "Mage": 5.0, "General": 5.0}
    ),
    AbilityTemplate(
        pattern="Sense {essence}",
        function="Perception",
        description_template="Detects the presence of {essence} nearby.",
        affinity_weight={"Rogue": 8.0, "Support": 5.0, "General": 5.0}
    ),

    # --- Execute ---
    AbilityTemplate(
        pattern="{essence} Execution",
        function="Execute",
        description_template="Delivers a fatal blow using the power of {essence}.",
        affinity_weight={"Rogue": 10.0, "Warrior": 8.0, "General": 5.0}
    ),
    AbilityTemplate(
        pattern="{essence} Guillotine",
        function="Execute",
        description_template="A merciless strike of {essence} intended to sever.",
        affinity_weight={"Warrior": 10.0, "Rogue": 8.0, "General": 5.0},
        essence_tags=["Physical", "Metal", "Wind"]
    ),
]
