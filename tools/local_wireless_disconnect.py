"""Experimental shutdown-state guard for the original local wireless overlay.

Not a completed battle mode. Must pass real two-instance link testing before
being promoted to the stable ROMs. It never forces radio buffers to be freed.
"""
import hashlib
import struct
import sys
from xros_text import ROOT, u32
sys.path.insert(0, str(ROOT / '.tools/python'))
from ndspy import codeCompression

BASE = 0x0221BF80
DEBUG_START = 0x0221EC98
DEBUG_END = 0x0221ED58
ERROR_SITE = 0x0221EE20
RESUME = 0x0221EE34
RESET = 0x0221DC60
CAVE = DEBUG_START + 4


def branch(site, target, *, condition=14, link=False):
    relative = target - site - 8
    if relative % 4 or not -(1 << 25) <= relative < (1 << 25):
        raise ValueError('ARM branch target is out of range/alignment')
    return condition << 28 | 0x0A000000 | int(link) << 24 | ((relative >> 2) & 0xFFFFFF)


def guarded_overlay(rom):
    table = u32(rom.data, 0x50) + 2 * 32
    overlay_id, ram, size, bss = struct.unpack_from('<4I', rom.data, table)
    if (overlay_id, ram, size, bss) != (2, BASE, 19456, 10528):
        raise ValueError('Unexpected wireless overlay layout')
    fid = u32(rom.data, table + 24)
    a, b = struct.unpack_from('<II', rom.data, rom.fat_offset + fid * 8)
    original = codeCompression.decompress(rom.data[a:b])
    # Check independently decoded instructions, including the existing reset BL.
    expected = struct.pack('<5I', 0xE3570000,
                           branch(ERROR_SITE + 4, RESUME, condition=0),
                           0xE5897024, branch(ERROR_SITE + 12, RESET, link=True),
                           0xE5895020)
    if original[ERROR_SITE - BASE:ERROR_SITE - BASE + 20] != expected:
        raise ValueError('Wireless error-routing signature changed')
    if u32(original, DEBUG_START - BASE) != 0xE5993020:
        raise ValueError('Wireless diagnostic block signature changed')
    words = [
        0xE3570000,  # cmp r7,#0: no transport error -> unchanged dispatcher
        branch(CAVE + 4, RESUME, condition=0),
        0xE5897024,  # str r7,[r9,#0x24]: keep the actual diagnostic code
        0xE5990020,  # ldr r0,[r9,#0x20]
        0xE240000C,  # sub r0,r0,#12
        0xE3500001,  # cmp r0,#1: states12/13 are already disconnecting
        branch(CAVE + 24, CAVE + 44, condition=9),
        branch(CAVE + 28, RESET, link=True),
        0xE5895020,  # active-session failures retain original state14 routing
        branch(CAVE + 36, RESUME),
        0xE1A00000,
        0xE3A0000D,  # closing failure: continue asynchronous shutdown state13
        0xE5890020,
        branch(CAVE + 52, RESET, link=True),
        branch(CAVE + 56, RESUME),
    ]
    data = bytearray(original)
    for pos in range(DEBUG_START, DEBUG_END, 4):
        struct.pack_into('<I', data, pos - BASE, 0xE1A00000)
    struct.pack_into('<I', data, DEBUG_START - BASE, branch(DEBUG_START, DEBUG_END))
    struct.pack_into('<' + 'I' * len(words), data, CAVE - BASE, *words)
    struct.pack_into('<I', data, ERROR_SITE - BASE, branch(ERROR_SITE, CAVE))
    # This reuses only the seven per-frame debug-print statements. No gameplay
    # packet serialization, save writes, heap allocation, or SDK cleanup code
    # is removed. Existing stop->idle->finalize->free logic still owns cleanup.
    restored = bytearray(data)
    for start, end in ((DEBUG_START, DEBUG_END), (ERROR_SITE, ERROR_SITE + 4)):
        restored[start - BASE:end - BASE] = original[start - BASE:end - BASE]
    if restored != original:
        raise ValueError('Unexpected executable edits outside declared ranges')
    packed = codeCompression.compress(bytes(data))
    if codeCompression.decompress(packed) != data:
        raise ValueError('Guard overlay compression roundtrip failed')
    return packed, {
        'status': 'experimental; requires two-instance link testing',
        'source_overlay_sha256': hashlib.sha256(original).hexdigest(),
        'edited_overlay_sha256': hashlib.sha256(data).hexdigest(),
        'allowed_ranges': [[hex(DEBUG_START), hex(DEBUG_END)], [hex(ERROR_SITE), hex(ERROR_SITE + 4)]],
        'unchanged_decompressed_size': len(data),
        'unchanged_bss_size': bss,
        'behaviour': 'A transport error during state12/13 continues state13 asynchronous shutdown instead of replacing it with state14. Active-session errors retain original routing.',
        'limitation': 'Fix candidate for one confirmed code path; user-reported loop has not yet been reproduced in melonDS. No wireless battle implementation.',
    }
