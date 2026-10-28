# Digimon Story: Super Xros Wars English Translation v1.0

## A note from the creator

I made this patch with help from ChatGPT Codex, supervising and reviewing parts of the translation myself. I have waited many years to play this game in English. It was part of my childhood, and I wanted to understand its dialogue and story, so I decided to translate it with Codex's help. I hope this project helps someone else enjoy the game, too. I know some parts may not be perfect, and I can improve them over time. For now, I can understand the game and experience its story. Thank you so much for helping me make this possible!

## Scope

This patch-only release is based on the stable batch125 UI build, carries Red's yellow Reserve formation pads forward, and includes the batch126 DigiLab/DigiFarm/battle-help choice-label fix. Wireless battle experiments are excluded. Both versions contain English in all 15,674 extracted message slots (100% of that inventory). This is not a claim that every Japanese graphic is translated or that every route has completed a playthrough review.

The release includes interface recolors: Blue's red UI accents are blue, its Vanguard battle pads are blue, Rearguard pads purple, and enemy pads dark red. Red's Sky Fort interiors use warm red/orange palettes, and its Reserve formation pads are yellow. Japanese animated attack-effect graphics remain as requested.

The DigiLab, DigiFarm, and battle-help menu choices have been shortened to one line (15 characters maximum); explanatory dialogue is unchanged. The batch126 ROMs pass structural validation. The corrected menu screens have not yet received a fresh emulator screenshot check, so their visual fit should be confirmed in game.

## Files

The local release candidate directory is `build/release/v1.0/`:

- `Digimon_Super_Xros_Wars_Blue_English_v1.0.ups`
- `Digimon_Super_Xros_Wars_Red_English_v1.0.ups`
- `manifest.json` (source, patch, and target SHA-256 values)

These are UPS patches, not ROM images. Apply the matching patch to a legally obtained clean Japanese ROM with Floating IPS (Flips) or another UPS-compatible patcher. The expected source SHA-256 for each edition is in the manifest; mismatched ROMs should be rejected by the patcher. Do not apply the Blue patch to Red or vice versa.

The public project repository excludes generated ROMs, source ROMs, extracted assets, save files, and QA emulator data. This release distributes UPS patches rather than ROM images.

## Verification

- Batch126 Blue and Red builds: structural validation passed; 15,674/15,674 message slots translated; no over-width lines.
- UPS generation: both patches reconstructed their exact batch126 target ROMs and passed source, target, and patch CRC checks.
- The source ROMs remained untouched.
- Runtime boot, tutorial-menu screenshot review for this checksum, and full-route review remain pending.
- Wireless battle is not part of v1.0.
