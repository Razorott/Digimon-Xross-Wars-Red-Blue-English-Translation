"""Blue-only palette swaps for the game's interface assets."""
from __future__ import annotations

import colorsys
import json
import struct
from pathlib import Path

from xros_text import Pak, ROOT
from graphics import palette, render_cell


# The pause-menu atlas (198) includes all function-button animation cells.
# The remaining entries cover cards, frame strips and battle banners/pads.
UI_PANEL_SPRITES = (74, 125, 126, 146, 198, 199, 208, 209, 213, 215, 218, 220, 1974, 1977, 1983, 2218)

# Palette IDs are independent of NCGR/NSCR IDs. Runtime measurements identify
# farm overlay 53/54, stats 84, formation 102, and shared list/shop frame 228.
# Entry 51 is scenery, not the battle palette, and must remain original.
UI_BG_PALETTES = tuple(range(11)) + (16, 19, 53, 54, 78, 79, 84, 85, 87, 88, 91,
    96, 98, 101, 102, 103, 104, 105, 107, 111, 112, 116, 117, 118,
    120, 121, 122, 130, 131, 136, 137, 166, 228)


def _force_hue(value: int, degrees: float, minimum_saturation: float = 0) -> int:
    r, g, b = value & 31, (value >> 5) & 31, (value >> 10) & 31
    _, saturation, brightness = colorsys.rgb_to_hsv(r / 31, g / 31, b / 31)
    rgb = colorsys.hsv_to_rgb(degrees / 360, max(saturation, minimum_saturation), brightness)
    rr, gg, bb = (round(x * 31) for x in rgb)
    return rr | (gg << 5) | (bb << 10)


def _swap_hue(value: int) -> int | None:
    r, g, b = value & 31, (value >> 5) & 31, (value >> 10) & 31
    hue, saturation, brightness = colorsys.rgb_to_hsv(r / 31, g / 31, b / 31)
    degrees = hue * 360
    if saturation < 0.05:
        return None
    if degrees <= 25 or degrees >= 340:
        hue = 215 / 360  # red slot panels become blue
    else:
        return None
    nr, ng, nb = colorsys.hsv_to_rgb(hue, saturation, brightness)
    rr, gg, bb = (round(x * 31) for x in (nr, ng, nb))
    return rr | (gg << 5) | (bb << 10)


def theme_color(archive: str, entry: int, slot: int, value: int) -> int | None:
    bank, color = divmod(slot, 16)
    if color == 0:  # Nitro transparency/key color must stay untouched.
        return None
    if archive == 'BG_NCLR.PAK':
        # Both copies of the DigiFarm Xros Loader overlay share this red ramp.
        if entry in (53, 54):
            return _force_hue(value, 215) if color in (5, 6, 7) else None
        # Position-change UI shares a single palette: red (2-5), orange
        # (6-8), and slate Reserve frames (9-12), measured in the emulator.
        if entry == 102 and 6 <= color <= 8:
            return _force_hue(value, 278)
        if entry == 102 and 9 <= color <= 12:
            return _force_hue(value, 140, .65)
        # Formation atlas: bank 0 is Vanguard, 2 is Rearguard, 3 Reserve.
        if entry == 101 and bank == 2 and 3 <= color <= 8:
            return _force_hue(value, 278)
        if entry == 101 and bank == 3 and 3 <= color <= 15:
            return _force_hue(value, 140, .65)
        # Shared formation/battle panel atlases carry their own copies.
        if entry in (103, 118) and bank == 3 and 2 <= color <= 8:
            return _force_hue(value, 140, .65)
        if entry == 118 and bank == 4 and 2 <= color <= 8:
            return _force_hue(value, 278)
        if entry == 103 and bank == 5 and 12 <= color <= 15:
            return _force_hue(value, 278)
        if entry in (3, 4, 7) and 8 <= color <= 15:
            return _force_hue(value, 278)
        if entry in (120, 121, 131, 166):
            r, g, b = value & 31, value >> 5 & 31, value >> 10 & 31
            h, s, _ = colorsys.rgb_to_hsv(r / 31, g / 31, b / 31)
            if s >= .05 and (h * 360 < 65 or h * 360 >= 340):
                return _force_hue(value, 215)
    else:
        if entry in (1974, 1977):
            r, g, b = value & 31, value >> 5 & 31, value >> 10 & 31
            h, s, v = colorsys.rgb_to_hsv(r / 31, g / 31, b / 31)
            if s >= .12 and 280 <= h * 360 < 340:
                rr, gg, bb = (round(c * 31) for c in colorsys.hsv_to_rgb(0, max(s, .75), v * .65))
                return rr | gg << 5 | bb << 10
        if entry == 1974 and 5 <= color <= 7:
            return _force_hue(value, 278)
        if entry == 1983 and bank == 0 and 3 <= color <= 7:
            return _force_hue(value, 278)
    return _swap_hue(value)


def recolor_blue_ui_panels(rom, preview: bool = False) -> bytes:
    """Recolor red/orange tones in selected sprite palettes; preserve framing."""
    spr = Pak(rom.file('SPR_NCGR.PAK'))
    clr = Pak(rom.file('SPR_NCLR.PAK'))
    cer = Pak(rom.file('SPR_NCER.PAK'))
    changed = {}
    preview_rows = []
    manifest = []
    for index in UI_PANEL_SPRITES:
        nclr = bytearray(clr.file(index))
        if nclr[:4] != b'RLCN':
            raise ValueError(f'Sprite palette {index} is not NCLR')
        size = struct.unpack_from('<I', nclr, 32)[0]
        offset = 24 + struct.unpack_from('<I', nclr, 36)[0]
        values = list(struct.unpack_from(f'<{size // 2}H', nclr, offset))
        altered = []
        for slot, value in enumerate(values):
            replacement = theme_color('SPR_NCLR.PAK', index, slot, value)
            if replacement is not None and replacement != value:
                struct.pack_into('<H', nclr, offset + slot * 2, replacement)
                altered.append({'color': slot, 'from': value, 'to': replacement})
        if not altered:
            raise ValueError(f'No warm colors found in sprite palette {index}')
        changed[index] = bytes(nclr)
        manifest.append({'sprite': index, 'palette_colors_changed': altered})
        if preview:
            from graphics import cells
            count = struct.unpack_from('<H', cer.file(index), 24)[0]
            for bank in range(min(count, 8)):
                if cells(cer.file(index), bank):
                    before = render_cell(spr.file(index), clr.file(index), cer.file(index), bank)
                    after = render_cell(spr.file(index), bytes(nclr), cer.file(index), bank)
                    preview_rows.extend([(f'{index}:{bank} before', before),
                                         (f'{index}:{bank} Blue test', after)])
    if preview:
        from graphics import contact
        contact(preview_rows, ROOT / 'build/qa/blue_ui_sprite_palette_preview.png',
                columns=4, cell=(180, 120))
        (ROOT / 'build/qa/blue_ui_sprite_palette_preview.json').write_text(
            json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return clr.rebuild(changed)


def recolor_blue_ui_background_palettes(rom, preview: bool = False) -> bytes:
    """Shift interface-only BG palettes from red/orange to blue/purple."""
    palette_pack = Pak(rom.file('BG_NCLR.PAK'))
    changed = {}
    manifest = []
    previews = []
    for entry in UI_BG_PALETTES:
        raw = bytearray(palette_pack.file(entry))
        if raw[:4] != b'RLCN':
            raise ValueError(f'UI background palette {entry} is not NCLR')
        size = struct.unpack_from('<I', raw, 32)[0]
        offset = 24 + struct.unpack_from('<I', raw, 36)[0]
        values = list(struct.unpack_from(f'<{size // 2}H', raw, offset))
        altered = []
        for slot, value in enumerate(values):
            replacement = theme_color('BG_NCLR.PAK', entry, slot, value)
            if replacement is not None and replacement != value:
                struct.pack_into('<H', raw, offset + slot * 2, replacement)
                altered.append({'color': slot, 'from': value, 'to': replacement})
        if altered:
            changed[entry] = bytes(raw)
            manifest.append({'palette': entry, 'palette_colors_changed': altered})
            if preview:
                from PIL import Image, ImageDraw
                def swatches(data):
                    colors = palette(data)
                    image = Image.new('RGB', (256, ((len(colors) + 15) // 16) * 12))
                    draw = ImageDraw.Draw(image)
                    for i, color in enumerate(colors):
                        x, y = i % 16 * 16, i // 16 * 12
                        draw.rectangle((x, y, x + 15, y + 11), fill=color[:3])
                    return image
                before = swatches(palette_pack.file(entry))
                after = swatches(bytes(raw))
                previews.extend([(f'BG {entry} before', before),
                                 (f'BG {entry} Blue/Purple', after)])
    if not changed:
        raise ValueError('No red/orange colors found in the UI background palettes')
    if preview:
        from graphics import contact
        contact(previews, ROOT / 'build/qa/blue_ui_background_palette_preview.png',
                columns=4, cell=(256, 144))
        (ROOT / 'build/qa/blue_ui_background_palette_preview.json').write_text(
            json.dumps({'archive': 'BG_NCLR.PAK',
                        'changed_palettes': manifest,
                        'ui_palette_allowlist': list(UI_BG_PALETTES),
                        'note': 'Palette swatches only. NCGR and NSCR IDs are independent; use runtime screenshots to verify screen composition.'},
                       indent=2) + '\n', encoding='utf-8')
    return palette_pack.rebuild(changed)
