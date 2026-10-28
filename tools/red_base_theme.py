"""Warm Sky Fort interior palettes for Red; no texture or sprite edits."""
import colorsys
import struct
from xros_text import Pak
from blue_battle_theme import _force_hue

# Measured against Central Room, DigiLab/shop and stair-room screenshots.
SKY_FORT_PALETTES = (12, 15, 18)


def recolor_red_base(rom):
    pak = Pak(rom.file('MAP_NCLR.PAK'))
    changed = {}
    for index in SKY_FORT_PALETTES:
        raw = bytearray(pak.file(index))
        if raw[:4] != b'RLCN':
            raise ValueError(f'Interior palette {index} is not NCLR')
        size, relative = struct.unpack_from('<II', raw, 32)
        offset = 24 + relative
        for slot in range(size // 2):
            if slot == 0:
                continue
            value = struct.unpack_from('<H', raw, offset + slot * 2)[0]
            rgb = ((value & 31) / 31, (value >> 5 & 31) / 31, (value >> 10 & 31) / 31)
            h, s, v = colorsys.rgb_to_hsv(*rgb)
            if s < .15 or not 170 <= h * 360 <= 280:
                continue
            # Cyan highlights become warm orange; deeper blue becomes red.
            hue = 18 if h * 360 < 205 else 4
            rr, gg, bb = (round(c * 31) for c in colorsys.hsv_to_rgb(hue / 360, s, v))
            struct.pack_into('<H', raw, offset + slot * 2, rr | gg << 5 | bb << 10)
        changed[index] = bytes(raw)
    return pak.rebuild(changed)


def recolor_red_formation_reserve(rom):
    """Only the slate Reserve ramp in formation palette102 becomes yellow."""
    pak = Pak(rom.file('BG_NCLR.PAK'))
    raw = bytearray(pak.file(102))
    size, relative = struct.unpack_from('<II', raw, 32)
    offset = 24 + relative
    for slot in range(size // 2):
        if 9 <= slot % 16 <= 12:
            value = struct.unpack_from('<H', raw, offset + slot * 2)[0]
            struct.pack_into('<H', raw, offset + slot * 2, _force_hue(value, 52, .70))
    return pak.rebuild({102: bytes(raw)})
