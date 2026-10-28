# Digimon Story: Super Xros Wars English Translation

An AI-assisted, fan-made English translation patch project for *Digimon Story: Super Xros Wars Blue* and *Red*. The translation was made with ChatGPT Codex and supervised by the project creator.

## Why I made this patch

I used ChatGPT Codex to translate the game and supervised several parts myself. I have waited so many years to play this game in English. It is part of my childhood, and I wanted to understand the dialogue and story, so I decided to make this translation with Codex's help. I hope it helps someone else, too, even though it was made with AI and my supervision. There are surely parts that are not the best, but I can improve them sometime soon. Now I can understand the game, and that means a lot to me. Thank you so much!

## English Translation v1.0

- English is installed in all **15,674 extracted message slots** in each version. This includes story dialogue, tutorials, menus, items, moves, and Digimon names. That percentage covers the extracted text inventory; it does not mean every graphic is translated or every route has been fully playtested.
- DigiLab, DigiFarm, and battle-help choice labels were shortened to fit on a single line, fixing the clipped tutorial options.
- **Blue recolors:** red UI accents are blue; battle Vanguard pads are blue, Rearguard pads are purple, and enemy pads are dark red.
- **Red recolors:** Sky Fort interior palettes use warm red/orange tones, and Reserve formation pads are yellow.
- Some Japanese graphics remain, including the animated attack-effect frames.
- Wireless battle is not included. Its experimental implementation is unfinished.

## Applying the patch

1. Obtain a clean Japanese ROM for the version you own.
2. Check its SHA-256 against the matching entry in [the v1.0 manifest](release/v1.0/manifest.json).
3. Apply the matching .ups release asset with Floating IPS (Flips) or another UPS-compatible patcher.
4. Use the Blue patch only with Blue, and the Red patch only with Red.

The release provides UPS patches, not ROM images. Original ROMs, save files, extracted assets, and generated ROMs are not included in this repository. See the [v1.0 release notes](translations/release_v1.0.md) for verification details and limitations.

## Project files

- The translations/batch*.json files contain the English text data and stable message IDs.
- The tools folder contains build, translation, patch, and audit tools.
- The tests folder contains structural and layout checks.
- The native folder and [wireless status notes](translations/local_wireless_status.md) document unfinished wireless-battle research and prototypes.

The original Japanese source is read from your own clean ROM during builds. See [AGENTS.md](AGENTS.md) for project conventions and validation limits.

This is an unofficial fan project and is not affiliated with or endorsed by Bandai Namco or Toei Animation.
