"""Relocate four retail turn-order functions into reserved native storage.

The extended turn order and reserved actor allocation support twelve actors.
Targeting, commands and opponent-party construction still need separate
integration. This does not enable PvP.
"""
import hashlib
import struct

START, END = 0x021F3D60, 0x021F3FBC
ENTRIES = (START, 0x021F3F1C, 0x021F3F38, 0x021F3F94)
LITERALS = {0x021F3F0C, 0x021F3F10, 0x021F3F14, 0x021F3F18, 0x021F3F90}


def branch(site, target, link=False, condition=14):
    distance = target - site - 8
    assert distance % 4 == 0 and -(1 << 25) <= distance < (1 << 25)
    return (condition << 28) | 0x0A000000 | (int(link) << 24) | ((distance >> 2) & 0xFFFFFF)


def transplant(overlay, base, module, module_base, symbols):
    destination = symbols['xwb_order_program']
    source = overlay[START - base:END - base]
    assert len(source) == 0x25C
    program = bytearray(source)
    edits = []

    def change(address, expected, value, reason):
        offset = address - START
        before = struct.unpack_from('<I', program, offset)[0]
        assert expected is None or before == expected, (hex(address), hex(before))
        struct.pack_into('<I', program, offset, value)
        edits.append({'source': hex(address), 'destination': hex(destination + offset),
                      'before': hex(before), 'after': hex(value), 'reason': reason})

    for address in range(START, END, 4):
        word = struct.unpack_from('<I', source, address - START)[0]
        if address in LITERALS or (word & 0x0E000000) != 0x0A000000:
            continue
        displacement = word & 0xFFFFFF
        if displacement & 0x800000:
            displacement -= 0x1000000
        target = address + 8 + displacement * 4
        if START <= target < END:
            target = destination + target - START
        elif target == 0x021F7B30:
            target = symbols['xwb_order_get_context']
        change(address, word, branch(destination + address - START, target,
               bool(word & 0x01000000), word >> 28), 'relocate branch or context accessor')

    change(0x021F3D8C, 0xE352000A, 0xE352000D, 'thirteen entries including sentinel')
    change(0x021F3E50, 0xE3580009,
           branch(destination + 0xF0, symbols['xwb_order_compare_actor'], True),
           'nine actors normally; twelve only during wireless battle')
    for address, original in ((0x021F3F00, 0xE1C017B4),
                              (0x021F3F28, 0xE1D117F4),
                              (0x021F3F60, 0xE1D237F4),
                              (0x021F3FA0, 0xE1D117F4)):
        change(address, original, (original & ~0xF0F) | 0x80C, 'cursor after thirteen entries')
    change(0x021F3F40, 0xE2801F5D, 0xE2801F63, 'cursor address 0x18c plus 0x800')
    # ARM rotated immediate 0x63 rotated right30 equals0x18c.
    installed = bytearray(module)
    offset = destination - module_base
    assert installed[offset:offset + 4] == b'\xff' * 4
    assert installed[offset + 4:offset + len(program)] == bytes(len(program) - 4)
    installed[offset:offset + len(program)] = program
    hooked = bytearray(overlay)
    hooks = []
    for entry in ENTRIES:
        target = destination + entry - START
        original = struct.unpack_from('<I', hooked, entry - base)[0]
        assert original in (0xE92D4FF0, 0xE92D4008, 0xE92D4010)
        struct.pack_into('<I', hooked, entry - base, branch(entry, target))
        hooks.append({'entry': hex(entry), 'target': hex(target), 'before': hex(original)})
    restrictions = []
    for site, original_target, helper in (
            (0x021F8E40, 0x02205354, 'xwb_ring_open'),
            (0x021F8E98, 0x022054EC, 'xwb_ring_selection'),
            (0x021F8498, 0x022123B8, 'xwb_all_tactics_pressed')):
        original = struct.unpack_from('<I', hooked, site - base)[0]
        assert original == branch(site, original_target, True)
        struct.pack_into('<I', hooked, site - base, branch(site, symbols[helper], True))
        restrictions.append({'site': hex(site), 'retail_target': hex(original_target),
                             'adapter': helper, 'target': hex(symbols[helper])})
    # The retail battle initializer clears nine 0x1A0-byte actors. Relocation
    # reserves twelve records, so clear all twelve before a new battle. This
    # only extends the clear within the separately reserved actor allocation.
    init_size_site = 0x021F7B54 - base
    original_init_size = struct.unpack_from('<I', hooked, init_size_site)[0]
    expected_init_size = 0xE3A02EEA  # mov r2, #0xEA0 (9 * 0x1A0)
    expanded_init_size = 0xE3A02D4E  # mov r2, #0x1380 (12 * 0x1A0)
    assert original_init_size == expected_init_size, hex(original_init_size)
    struct.pack_into('<I', hooked, init_size_site, expanded_init_size)
    return bytes(hooked), bytes(installed), {
        'status': 'twelve-slot actor initialization and turn-order capacity only; no playable PvP',
        'source_sha256': hashlib.sha256(source).hexdigest(),
        'destination': hex(destination), 'size': len(program), 'hooks': hooks, 'edits': edits,
        'normal_actor_limit': 9, 'wireless_actor_limit': 12, 'cursor_offset': '0x98c',
        'actor_initialization': {'site': hex(0x021F7B54),
            'before': hex(original_init_size), 'after': hex(expanded_init_size),
            'records_cleared': 12, 'record_size': 0x1A0},
        'private_context': hex(symbols['xwb_order_context']),
        'wireless_restriction_hooks': restrictions}
