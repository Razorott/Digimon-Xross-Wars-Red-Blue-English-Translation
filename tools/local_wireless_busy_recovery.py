"""Experimental bounded recovery for a shutdown stalled in WH_BUSY.

Uses the game's asynchronous WH_Reset path; never frees SDK buffers directly.
The real local-radio behavior must be tested before this is a stable patch.
"""
import hashlib
import struct
from local_wireless_disconnect import (BASE, DEBUG_START, DEBUG_END, branch,
                                      codeCompression)
from xros_text import u32

GET_STATE = 0x0221D4A8
RESET_RADIO = 0x0221DC18
BUSY_LIMIT = 300
COUNTER = DEBUG_END - 4


def arm_immediate(value):
    for rotation in range(16):
        for byte in range(256):
            shift = rotation * 2
            decoded = ((byte >> shift) | (byte << (32 - shift))) & 0xFFFFFFFF if shift else byte
            if decoded == value:
                return rotation << 8 | byte
    raise ValueError('Not an ARM immediate')


def busy_recovery_overlay(rom):
    table = u32(rom.data, 0x50) + 2 * 32
    if struct.unpack_from('<4I', rom.data, table) != (2, BASE, 19456, 10528):
        raise ValueError('Unexpected wireless overlay')
    fid = u32(rom.data, table + 24)
    start, end = struct.unpack_from('<II', rom.data, rom.fat_offset + fid * 8)
    original = codeCompression.decompress(rom.data[start:end])
    if u32(original, DEBUG_START - BASE) != 0xE5993020:
        raise ValueError('Expected unmodified wireless diagnostic block')
    # This block runs after the session pointer check and before the original
    # per-frame dispatcher. Only caller-saved registers r0-r3 are changed.
    words = []
    labels = {}
    relocations = []
    def emit(word):
        words.append(word)
    def label(name):
        labels[name] = DEBUG_START + len(words) * 4
    def jump(name, condition=14):
        relocations.append((len(words), name, condition))
        emit(0)
    def counter_instruction(load, register):
        address = DEBUG_START + len(words) * 4
        delta = COUNTER - address - 8
        assert 0 <= delta < 4096
        emit((0xE59F0000 if load else 0xE58F0000) | register << 12 | delta)
    emit(0xE5990020)  # ldr r0,[r9,#0x20]
    emit(0xE350000D)  # cmp r0,#13
    jump('clear', 1)
    emit(branch(DEBUG_START + len(words) * 4, GET_STATE, link=True))
    emit(0xE3500003)  # WH_BUSY only
    jump('clear', 1)
    counter_instruction(True, 1)
    emit(0xE3510000 | arm_immediate(BUSY_LIMIT))
    jump('resume', 2)  # saturated: do not submit duplicate asynchronous resets
    emit(0xE2811001)
    counter_instruction(False, 1)
    emit(0xE3510000 | arm_immediate(BUSY_LIMIT))
    jump('resume', 1)
    emit(branch(DEBUG_START + len(words) * 4, RESET_RADIO, link=True))
    jump('resume')
    label('clear')
    emit(0xE3A00000)
    counter_instruction(False, 0)
    label('resume')
    emit(branch(DEBUG_START + len(words) * 4, DEBUG_END))
    for index, name, condition in relocations:
        words[index] = branch(DEBUG_START + index * 4, labels[name], condition=condition)
    assert DEBUG_START + len(words) * 4 <= COUNTER
    data = bytearray(original)
    for address in range(DEBUG_START, DEBUG_END, 4):
        struct.pack_into('<I', data, address - BASE, 0xE1A00000)
    struct.pack_into('<' + 'I' * len(words), data, DEBUG_START - BASE, *words)
    struct.pack_into('<I', data, COUNTER - BASE, 0)
    restored = bytearray(data)
    restored[DEBUG_START - BASE:DEBUG_END - BASE] = original[DEBUG_START - BASE:DEBUG_END - BASE]
    assert restored == original
    packed = codeCompression.compress(bytes(data))
    assert codeCompression.decompress(packed) == data
    return packed, {
        'status': 'experimental; real two-instance recovery unverified',
        'source_overlay_sha256': hashlib.sha256(original).hexdigest(),
        'edited_overlay_sha256': hashlib.sha256(data).hexdigest(),
        'allowed_ranges': [[hex(DEBUG_START), hex(DEBUG_END)]],
        'unchanged_decompressed_size': len(data), 'unchanged_bss_size': 10528,
        'behaviour': 'After 300 consecutive update calls in session13 and WH_BUSY, issue the original asynchronous WH_Reset once. Reset counter outside that condition. Original completion callbacks and buffer ownership remain in control.',
        'limitation': 'A stuck reset callback will still wait safely. No forced heap cleanup. No wireless battle mode. Update count is not a wall-clock timeout.',
    }
