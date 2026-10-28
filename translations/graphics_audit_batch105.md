# Graphics audit at batch 105

The build applies 229 localized visual states from `graphics_manifest.json`. These include both title logos, the illustrated intro logo and nine caption frames, DigiLab icons, title and pause menus, status tabs, battle badges, quest results, and several DigiFarm and shop headings. The manifest counts animation states, not unique screens or a percentage of all graphics.

Batch 105 redraws the status carousel's five labels for its 21-pixel spacing. `Stats`, `Moves`, `Trait`, and `Param` occupy one row; `DigiXross` is divided into `Digi` and `Xross`. A 3-by-7 pixel glyph design and a one-pixel dark shadow keep letters separate from the purple UI. The actual status screen was captured at native DS resolution in `build/qa/status_batch105/status_menu.png`.

The Digidex list names use two-byte CP932 Latin codes drawn from compacted native fullwidth glyph slots. This keeps the English list visible while preserving Japanese nicknames already stored in the user's save; the prior added-glyph alias had hidden those nicknames on the party/status screen. The actual Digidex screen was captured in `build/qa/digidex_batch105/digidex_fixed.png`.

The Blue title screen was also captured in `build/qa/title_batch105/title.png`; the `D` in DIGIMON and the BLUE badge are fully visible inside the title area.

For the background audit, `tools/audit_bg_contact.py` rendered 233 indexed `BG_NCGR`/`BG_NCLR`/`BG_NSCR` combinations into `build/graphics/bg_audit/bg_00.png` through `bg_09.png` without decoder errors. Entries 23 and 33–41 show the localized illustrated opening logo and captions. Many other entries show tiles laid out as atlases, partial layers, or incorrect color combinations when paired by index; those contact sheets do not represent finished game screens. Japanese lettering is visible in some atlas renders around indices 58–66 and 84–92, but its runtime context and exact layer pairing are unresolved. Editing those raw atlases without confirming their in-game appearance risks corrupting other screens.

`tools/audit_movie_contact.py` decoded and rendered all 180 image frames across the three `NCGMOVIE` archives without errors. Movie 0 contains an abstract green tunnel; movies 1 and 2 contain repeated stylized white lettering over a digital tunnel. At native resolution that lettering is too distorted and repetitive to identify as a game instruction or a translatable phrase. The movie contact sheets are in `build/graphics/movie_audit/` and remain flagged for runtime context review.

Remaining visual QA: capture those background layers in play, identify any visible Japanese text, translate it in its actual context, and recheck both versions. A complete story, quest, battle, DigiLab, Farm Island, Digidex, and postgame playthrough is also still needed. Until then, there is no defensible whole-game graphics or completion percentage. The verified 100% figure refers only to the extracted message-slot inventory.
