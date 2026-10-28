# Story and anime coherence notes

Checked 2026-10-25 against the game text and official franchise summaries. This is a translation reference, not a claim that every game event is anime canon.

## What the official summaries establish

Bandai Namco's official *Super Xros Wars Blue & Red* story page describes Taiki's growing Xros Heart team, then says a mysterious Melody sends them to the previously unseen Elestou Zone, where they meet Spadamon. It also says the story-related characters differ between Red and Blue. This is a new game adventure with a version-specific story cast, rather than a straight retelling of a single anime arc.

Toei's official episode 1 synopsis says Taiki is pulled into another world where the Bagura Army is attacking Shoutmon's village. Its episode 29 synopsis later describes the Sword Zone and a confrontation involving Xros Heart, Blue Flare, and Tactimon. These are useful anchors for the anime's opening and later conflict, but neither synopsis places the game at an exact episode.

## Current game passage (through batch 61)

The local Japanese script establishes the game-specific conflict and locations. The opening introduces the Elestou Zone, ROG, Sky Fort, and Spadamon. In the story entries translated in batch 34, residents discuss ZeedMillenniummon using Earth Fort's Zone-scanning radar, ask Taiki to defeat ROG at Crystal Volcano, and encourage the team before its confrontation with ROG's boss. Later lines reference Shadow Guard taking a tower and ROG moving toward Sky Garden.

Batch 59 continues after Cutemon's rescue. The team learns ROG is seeking Lost Space and the Legendary Ancient Weapons, finds Nene under ROG's influence, and follows her search for Sparrowmon. Arukenimon uses ZeedMillenniummon's illusion to control Sparrowmon and lure Spadamon, but the party frees him. Spadamon then recalls Dynasmon as the keeper of the Condenser Towers and a legendary warrior. The next route leads through Kumonos Ruins to Papyrus Desert, where Pharaohmon the Grave is introduced as a ROG Shining Leader.

Batch 60 follows the Pharaohmon confrontation: he transforms into Anubismon, reveals ROG has found the seal of the Legendary Ancient Weapons, and points the team toward activating the Condenser Systems. The script then returns to Sky Fortress, introduces Earth Fortress and Crystal Volcano, and has Kiriha and MailBirdramon attempt to connect to Lost Space. After the connection fails, Taiki encounters Kiriha searching for the weapons; the story proceeds toward Earth Fortress, where a ROG leader absorbs Minotaurmon to gain power. These events are present in the Japanese game script and preserve the game's own continuity.

Batch 61 adds nearby NPC dialogue rather than advancing the main plot: a save terminal appears broken, residents thank Taiki's team for reclaiming Sky Fortress and restoring a Condenser Tower, and shopkeepers greet visitors at Skull City, Kumonos City, and Papyrus City. These lines fit the established post-rescue setting and do not alter the events above.

These events fit the official game's premise of a new Zone adventure. The anime episode synopses do not list ROG, the Elestou Zone, or Spadamon, so the translation keeps those game-specific names and events intact instead of substituting anime names or plot beats. The available official summaries do not establish an exact episode-by-episode placement for this game story; that remains unconfirmed.

## Translation decisions

- Keep Taiki, Akari, Zenjiro, Kiriha, and Nene, per the user's choice. The Western *Digimon Fusion* dub uses localized human names; the project follows the original Japanese names.
- Keep the game's own names, including Elestou Zone, ROG, Sky Fort, Earth Fort, Crystal Volcano, Shadow Guard, and Spadamon.
- The game uses the short label `ZD Millenniummon` in its Japanese text. Story dialogue uses the official English species spelling **ZeedMillenniummon**, confirmed on Bandai's English card page. Narrow HUD labels retain their separately reviewed compact display form.
- The Piedmon quiz's Western move names were cross-checked individually. **BeastKing Fist** and **Flower Cannon** use the English *Dawn/Dusk* move-list spellings; **Ice Arrow**, **Toy Flame**, and **Mega Flame** use established Western game/card references. The four earlier battle entries for `フラウカノン` were corrected from the provisional “Flau Cannon” to **Flower Cannon**.

## Sources

- [Bandai Namco official game story page](https://digimon-gameportal.bn-ent.net/product/xros_wars/story/) (Japanese page; the official synopsis and Blue/Red distinction are presented as image text).
- Toei Animation official anime summaries: [episode 1](https://lineup.toei-anim.co.jp/ja/tv/digimon_xw/episode/1/) and [episode 29](https://lineup.toei-anim.co.jp/ja/tv/digimon_xw/episode/29/) (Japanese pages).
- [Bandai English card page for ZeedMillenniummon](https://world.digimoncard.com/cards/?card_no=BT19-101&search=true).
- [English *Dawn/Dusk* move-name extraction](https://raw.githubusercontent.com/joaomlsantos/Digimon-World-Dawn-Dusk-Research-Notes/master/move_name_lst.txt), a community transcription of licensed game text; entries include `BeastKing Fist` and `Flower Cannon`.
- [Seadramon attack reference](https://wikimon.net/Seadramon) for Ice Arrow; [ToyAgumon attack reference](https://wikimon.net/Toy_Agumon) for Toy Flame.
- [Bandai English card list](https://world.digimoncard.com/cards/?category=522018&search=true) includes the Mega Flame card name.

## QA boundary

This check compares the official series/game summaries with translated local game-script passages. It does not establish the game's exact anime timeline or canon status. Batch 61's ROMs pass the boot smoke check, but its later-story scenes, Digidex profiles, and technique descriptions still need in-game review. The user-reported Digidex black screen was not exercised by the startup smoke test; reproducing it requires the user's save or savestate. The emulator evidence and output checksums are recorded in [batch 61 QA](../build/qa/validation_batch61.json).
