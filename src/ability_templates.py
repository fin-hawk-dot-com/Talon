from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class AbilityTemplate:
    name_pattern: str
    description_pattern: str
    required_stone_function: str
    required_essence_tags: List[str]  # Empty list means "Generic"
    affinity: Optional[str]  # "Power", "Speed", "Spirit", "Recovery" or None
    tags: List[str] = field(default_factory=list) # Tags to add to the ability (e.g. "Fire", "Projectile")
    weight: int = 10

# A large registry of templates to provide depth and variety
ABILITY_TEMPLATES = [
    # --- Generic/Fallback ---
    AbilityTemplate("{essence} Strike", "Strikes the enemy with physical force imbued with {essence}.", "Melee Attack", [], None, ["Melee"], weight=5),
    AbilityTemplate("{essence} Bolt", "Fires a bolt of {essence} energy at the target.", "Ranged Attack", [], "Spirit", ["Projectile", "Ranged"], weight=5),
    AbilityTemplate("{essence} Shield", "Surrounds the user in a protective layer of {essence}.", "Defense", [], "Recovery", ["Buff", "Shield"], weight=5),
    AbilityTemplate("{essence} Trap", "Sets a trap that releases {essence} when triggered.", "Area Denial", [], "Spirit", ["Trap"], weight=5),

    # --- Elemental (Fire, Water, Air, Earth, Lightning) ---
    # Fire
    AbilityTemplate("Flame Strike", "A burning strike that sears the target's flesh.", "Melee Attack", ["Fire"], "Power", ["Melee", "Fire", "Burn"], weight=20),
    AbilityTemplate("Fireball", "Hurls a ball of exploding fire.", "Ranged Attack", ["Fire"], "Power", ["Projectile", "Fire", "AoE"], weight=20),
    AbilityTemplate("Cauterize", "Uses intense heat to seal wounds, healing at a cost of pain.", "Defense", ["Fire"], "Recovery", ["Heal", "Fire"], weight=15),
    AbilityTemplate("Inferno Wall", "Creates a wall of roaring flames.", "Terrain Control", ["Fire"], "Power", ["Wall", "Fire"], weight=20),
    AbilityTemplate("Heat Haze", "Distorts the air with heat to mislead attacks.", "Defense", ["Heat"], "Speed", ["Evasion", "Illusion"], weight=15),

    # Water
    AbilityTemplate("Tidal Crash", "A heavy wave of water crashes down on the target.", "Melee Attack", ["Water"], "Power", ["Melee", "Water", "Blunt"], weight=20),
    AbilityTemplate("Aqua Jet", "Shoots a high-pressure jet of water.", "Ranged Attack", ["Water"], "Speed", ["Projectile", "Water", "Pierce"], weight=20),
    AbilityTemplate("Fluid Motion", "Allows the user to move like flowing water.", "Mobility", ["Flow"], "Speed", ["Buff", "Speed"], weight=20),
    AbilityTemplate("Rejuvenating Mist", "A mist that slowly closes wounds.", "Defense", ["Water"], "Recovery", ["Heal", "Water"], weight=20),

    # Earth
    AbilityTemplate("Stone Fist", "Encases the hand in stone for a devastating punch.", "Melee Attack", ["Earth"], "Power", ["Melee", "Earth", "Blunt"], weight=20),
    AbilityTemplate("Rock Throw", "Hurls a large boulder at the enemy.", "Ranged Attack", ["Earth"], "Power", ["Projectile", "Earth", "Blunt"], weight=20),
    AbilityTemplate("Earthen Armor", "Coats the body in rock armor.", "Defense", ["Earth"], "Recovery", ["Buff", "Armor", "Earth"], weight=20),
    AbilityTemplate("Quicksand Trap", "Turns the ground into a trap that snares enemies.", "Area Denial", ["Earth"], "Spirit", ["Trap", "Earth", "Root"], weight=20),

    # Air
    AbilityTemplate("Wind Blade", "Slashes with a blade of compressed air.", "Melee Attack", ["Air"], "Speed", ["Melee", "Air", "Slash"], weight=20),
    AbilityTemplate("Gale Blast", "Blasts the enemy back with a gust of wind.", "Ranged Attack", ["Air"], "Power", ["Projectile", "Air", "Knockback"], weight=20),
    AbilityTemplate("Wind Walk", "Moves swiftly on currents of air.", "Mobility", ["Air"], "Speed", ["Buff", "Speed", "Air"], weight=20),
    AbilityTemplate("Suffocate", "Draws the air out of the target's lungs.", "Execute", ["Air"], "Spirit", ["DoT", "Air"], weight=15),

    # Lightning
    AbilityTemplate("Thunder Punch", "A punch charged with electricity.", "Melee Attack", ["Lightning"], "Power", ["Melee", "Lightning", "Stun"], weight=20),
    AbilityTemplate("Lightning Bolt", "Strikes the target with a bolt from the sky.", "Ranged Attack", ["Lightning"], "Spirit", ["Ranged", "Lightning"], weight=20),
    AbilityTemplate("Flash Step", "Teleports instantly in a flash of light.", "Mobility", ["Lightning"], "Speed", ["Teleport", "Lightning"], weight=25),
    AbilityTemplate("Static Field", "Charges the area with static, damaging moving foes.", "Area Denial", ["Lightning"], "Spirit", ["AoE", "Lightning"], weight=20),

    # --- Physical/Body (Might, Swift, Blood, Iron) ---
    # Might
    AbilityTemplate("Titanic Blow", "A strike with overwhelming physical force.", "Melee Attack", ["Might"], "Power", ["Melee", "Physical"], weight=25),
    AbilityTemplate("Shockwave", "Slams the ground to create a shockwave.", "Ranged Attack", ["Might"], "Power", ["AoE", "Physical"], weight=20),
    AbilityTemplate("Unstoppable Charge", "Rushes forward, knocking aside obstacles.", "Mobility", ["Might"], "Power", ["Charge", "Physical"], weight=20),
    AbilityTemplate("Iron Skin", "Hardens the skin to resist damage.", "Defense", ["Might"], "Recovery", ["Buff", "Defense"], weight=20),

    # Swift
    AbilityTemplate("Rapid Strikes", "Delivers a flurry of quick blows.", "Melee Attack", ["Swift"], "Speed", ["Melee", "Multi-Hit"], weight=25),
    AbilityTemplate("Blur", "Moves so fast the user becomes a blur.", "Defense", ["Swift"], "Speed", ["Evasion"], weight=20),
    AbilityTemplate("Quick Shot", "Fires a projectile before the enemy can react.", "Ranged Attack", ["Swift"], "Speed", ["Ranged", "Fast"], weight=20),

    # Blood
    AbilityTemplate("Exsanguinate", "Causes the target to bleed profusely.", "Melee Attack", ["Blood"], "Spirit", ["Melee", "Bleed"], weight=20),
    AbilityTemplate("Blood Spear", "Forms a spear from blood and hurls it.", "Ranged Attack", ["Blood"], "Power", ["Projectile", "Blood"], weight=20),
    AbilityTemplate("Vampiric Touch", "Drains health from the enemy on touch.", "Drain/Sustain", ["Blood"], "Recovery", ["Melee", "Drain", "Heal"], weight=25),
    AbilityTemplate("Boil Blood", "Causes the enemy's blood to boil.", "Execute", ["Blood"], "Spirit", ["DoT", "Internal"], weight=20),

    # --- Abstract (Dark, Light, Dimension, Sin) ---
    # Dark
    AbilityTemplate("Shadow Strike", "Attacks from the shadows, bypassing armor.", "Melee Attack", ["Dark"], "Speed", ["Melee", "Dark", "Pierce"], weight=20),
    AbilityTemplate("Dark Bolt", "Fires a bolt of pure darkness.", "Ranged Attack", ["Dark"], "Spirit", ["Projectile", "Dark"], weight=20),
    AbilityTemplate("Shadow Cloak", "Wraps the user in shadows to hide.", "Defense", ["Dark"], "Spirit", ["Stealth", "Dark"], weight=20),
    AbilityTemplate("Shadow Step", "Steps through shadows to appear elsewhere.", "Mobility", ["Dark"], "Speed", ["Teleport", "Dark"], weight=25),

    # Light
    AbilityTemplate("Smite", "Strikes with holy light.", "Melee Attack", ["Light"], "Power", ["Melee", "Holy"], weight=20),
    AbilityTemplate("Sunbeam", "Burns the target with focused light.", "Ranged Attack", ["Light"], "Spirit", ["Ranged", "Holy", "Fire"], weight=20),
    AbilityTemplate("Blinding Flash", "Blinds enemies with a burst of light.", "Area Denial", ["Light"], "Speed", ["Debuff", "Light"], weight=20),
    AbilityTemplate("Sanctuary", "Creates a zone of healing light.", "Terrain Control", ["Light"], "Recovery", ["AoE", "Heal", "Holy"], weight=20),

    # Dimension
    AbilityTemplate("Spatial Slice", "Cuts through the fabric of space.", "Melee Attack", ["Dimension"], "Power", ["Melee", "Dimension", "Pierce"], weight=25),
    AbilityTemplate("Phase Shift", "Phases out of reality to avoid harm.", "Defense", ["Dimension"], "Spirit", ["Invulnerable", "Dimension"], weight=25),
    AbilityTemplate("Portal", "Opens a portal to traverse distance.", "Mobility", ["Dimension"], "Spirit", ["Teleport", "Dimension"], weight=25),
    AbilityTemplate("Reality Anchor", "Prevents enemies from teleporting.", "Area Denial", ["Dimension"], "Power", ["Debuff", "Dimension"], weight=20),

    # --- Artificial (Technology, Gun) ---
    # Gun
    AbilityTemplate("Magical Bullet", "Fires a bullet imbued with magic.", "Ranged Attack", ["Gun"], "Speed", ["Ranged", "Projectile"], weight=25),
    AbilityTemplate("Snipe", "Takes aim for a guaranteed critical hit.", "Execute", ["Gun"], "Spirit", ["Ranged", "Crit"], weight=20),
    AbilityTemplate("Bullet Storm", "Unleashes a hail of bullets.", "Multi-Hit", ["Gun"], "Speed", ["AoE", "Ranged"], weight=20),

    # Technology
    AbilityTemplate("Analyze", "Scans the target for weaknesses.", "Perception", ["Technology"], "Spirit", ["Debuff", "Intel"], weight=25),
    AbilityTemplate("Overclock", "Temporarily boosts all stats but causes damage.", "Celestial/Augment", ["Technology"], "Power", ["Buff", "Self-Damage"], weight=20),
    AbilityTemplate("Automated Turret", "Deploys a turret to attack enemies.", "Summoning", ["Technology"], "Spirit", ["Summon", "Ranged"], weight=25),
]
