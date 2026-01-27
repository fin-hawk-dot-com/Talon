# Assets and Sprites Documentation

This document lists the visual assets required for the game's Map HUD and Avatar system. These assets should be placed in the `assets/avatars/` directory.

## File Specifications
*   **Format:** PNG (Portable Network Graphics)
*   **Transparency:** Yes (Alpha channel required)
*   **Recommended Size:** 32x32 pixels or 64x64 pixels (Square aspect ratio)

## Character Avatars
These sprites represent the player on the world map based on their chosen Affinity (Class).

| Object Name | Filename | Layer | Description / Likeness |
| :--- | :--- | :--- | :--- |
| **Warrior Avatar** | `Warrior.png` | Player | A sturdy icon representing physical might. Could be a crossed sword and shield, or a helm with a red plume. Metallic colors (silver, iron) with red accents. |
| **Mage Avatar** | `Mage.png` | Player | A mystical icon representing arcane power. A staff glowing with blue energy, or an open tome with magical runes floating above it. Blue, purple, and gold colors. |
| **Rogue Avatar** | `Rogue.png` | Player | A stealthy icon representing speed and cunning. A hooded cowl, dual daggers, or a cloak billowing in shadow. Dark grey, black, and green accents. |
| **Guardian Avatar** | `Guardian.png` | Player | A defensive icon representing protection. A large tower shield, a fortress silhouette, or a heavy helm. Gold, white, and blue steel colors. |
| **Support Avatar** | `Support.png` | Player | A helpful icon representing healing and aid. A potion flask, a caduceus, or a radiant hand. White, green, and soft yellow colors. |
| **General Avatar** | `General.png` | Player | A balanced, versatile icon. A simple traveler's pack, a compass, or a plain sword. Brown leather and neutral earth tones. This is the default fallback. |

## Map HUD Elements
*(Currently handled procedurally via code, but can be replaced by sprites in future updates. Place these in `assets/ui/`)*

| Object Name | Filename | Layer | Description / Likeness |
| :--- | :--- | :--- | :--- |
| **Health Bar Frame** | `HUD_HP_Frame.png` | UI | Ornate red frame for the health bar. |
| **Mana Bar Frame** | `HUD_MP_Frame.png` | UI | Ornate blue frame for the mana bar. |
| **Stamina Bar Frame** | `HUD_SP_Frame.png` | UI | Ornate green frame for the stamina bar. |
| **Willpower Bar Frame** | `HUD_WP_Frame.png` | UI | Ornate purple/gold frame for the willpower bar. |
