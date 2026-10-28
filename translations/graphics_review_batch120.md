# Graphics review: batch 120

This pass audits the 17 graphics previews from the previous review:

1. `large_sprite_candidates.png`
2. `sprite_battle_region_1970_2010.png`
3–7. `large_sprite_big_00.png` through `large_sprite_big_04.png`
8–16. `bg_text_candidate_033.png` through `bg_text_candidate_041.png`
17. `battle_button_all_states.png`

The preview sheets contain Digimon artwork as well as lettering. The title logos, X/Y battle labels, and Taiki's battle callouts already have English versions in the current graphics pipeline. The nine intro cards also already had English wording, but the encoder had discarded the palette-bank bit that carries red emphasis. This pass restores the cards' white text, dark ink outline, and red emphasis on Taiki's name, the voice, Digital World, Digimon, King, Shoutmon, Ballistamon, Dorulumon, and the new adventure. The original line layout and positions remain intact.

The remaining Japanese lettering in the audited battle graphics was the brush-effect animation in `SPR_NCER.PAK` entry 1990. Its 20 cells reveal the words in sequence:

| Cells | Japanese | English |
|---|---|---|
| 0–4 | 炎 | FIRE |
| 5–9 | 炎 / 流 | FIRE / FLOW |
| 10–14 | 炎 / 流 / 星 | FIRE / FLOW / STAR |
| 15–19 | 炎 / 流 / 星 / 斬 | FIRE / FLOW / STAR / SLASH |

Each English label is drawn in its existing 64×64 object area with bold white lettering and a dark ink edge. The original cell timing, object positions, canvas size, and monochrome palette are retained; the Japanese pixels are replaced as tile artwork, with no covering panel.

The side-by-side frame audit is `build/qa/attack_effects_batch120.png`. The localized intro cards are rendered in `build/graphics/intro_33.png` through `intro_41.png`. Blue and Red use the same translated graphic assets.
