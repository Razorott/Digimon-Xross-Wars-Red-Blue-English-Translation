# Digimon Story: Super Xros Wars English Translation v1.0

This is a patch-only release for the Blue and Red versions. It does not include ROM images, saves, extracted assets, or wireless battle experiments.

## A note from the creator

I used ChatGPT Codex to translate the game and supervised several parts myself. I have waited so many years to play this game in English. It is part of my childhood, and I wanted to understand the dialogue and story, so I decided to make this translation with Codex's help. I hope it helps someone else in some way, even though it was made with AI and my supervision. Some parts surely aren't the best, but I hope I can fix them sometime soon. For now, I can play and understand the game. Thank you so much!

## What changed

- English text is present in all 15,674 extracted message slots in each version. This covers the extracted text inventory, not every graphic or a complete playthrough review.
- DigiLab, DigiFarm, and battle-help option labels were shortened to fit one line.
- Blue: red interface accents became blue; battle Vanguard pads are blue, Rearguard pads are purple, and enemy pads are dark red.
- Red: Sky Fort interior palettes use warm red/orange tones, and Reserve formation pads are yellow.
- Japanese graphics remain in some places, including animated attack effects. Wireless battle is unfinished and excluded.

## Apply a patch

1. Obtain a clean Japanese ROM for the version you own.
2. Verify its SHA-256 against the matching `source_sha256` in [manifest.json](manifest.json).
3. Apply the matching `.ups` file from the GitHub v1.0 release using Floating IPS (Flips) or another UPS-compatible patcher.
4. Use the Blue patch only with Blue, and the Red patch only with Red.

The patches were round-trip tested against their target builds. Runtime boot, screenshot review of the corrected tutorial menus for this checksum, and complete route review remain pending. See the project [README](../../README.md) for repository details and limitations.
