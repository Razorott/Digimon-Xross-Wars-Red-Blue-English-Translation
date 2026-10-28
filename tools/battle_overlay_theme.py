"""Blue battle UI ramps embedded in overlay 0, outside the NCLR archives."""
import colorsys
import struct
import sys
from xros_text import ROOT, u32
from blue_battle_theme import _force_hue
sys.path.insert(0, str(ROOT / '.tools/python'))
from ndspy import codeCompression

PALETTE_START = 0x26758
PALETTE_SIZE = 12 * 7 * 2


def recolor_battle_overlay(rom):
    table = u32(rom.data, 0x50)
    file_id = u32(rom.data, table + 24)
    a, b = struct.unpack_from('<II', rom.data, rom.fat_offset + file_id * 8)
    original = codeCompression.decompress(rom.data[a:b])
    if original[PALETTE_START:PALETTE_START + 14].hex() != 'ff7fc4202c003400990cfa185c25':
        raise ValueError('Battle UI ramp signature changed')
    data = bytearray(original)
    changes = []
    for row in range(12):
        if row in (7, 10):
            continue  # neutral spare/status ramps
        for color in range(7):
            pos = PALETTE_START + (row * 7 + color) * 2
            value = struct.unpack_from('<H', original, pos)[0]
            if value in (32767, 8388):
                continue
            if row in (2, 5, 8, 11):
                rgb = ((value & 31) / 31, (value >> 5 & 31) / 31, (value >> 10 & 31) / 31)
                _, s, v = colorsys.rgb_to_hsv(*rgb)
                rr, gg, bb = (round(c * 31) for c in colorsys.hsv_to_rgb(0, max(s, .75), v * .65))
                replacement = rr | gg << 5 | bb << 10
            else:
                replacement = _force_hue(value, 278 if row in (1, 4) else 215)
            struct.pack_into('<H', data, pos, replacement)
            changes.append({'offset': pos, 'row': row, 'color': color, 'from': value, 'to': replacement})
    # No executable instruction, pointer, or other overlay data may change.
    restored = bytearray(data)
    restored[PALETTE_START:PALETTE_START + PALETTE_SIZE] = original[PALETTE_START:PALETTE_START + PALETTE_SIZE]
    if restored != original:
        raise ValueError('Unexpected battle overlay edit')
    packed = codeCompression.compress(bytes(data))
    if codeCompression.decompress(packed) != data:
        raise ValueError('Battle overlay compression roundtrip failed')
    return packed, changes
