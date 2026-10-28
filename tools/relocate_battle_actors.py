"""Move native actor records into reserved bridge storage, preserving behavior.

This prepares capacity for twelve actors. It does not change the original nine
active slots, targeting, commands, display or turn rules. PvP is not enabled.
"""
import hashlib
import re
import struct
import sys
from xros_text import ROOT, u32
sys.path.insert(0, str(ROOT / '.tools/python'))
from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM
from ndspy import codeCompression

ORIGINAL_ACTORS = 0x0221AFD4
ORIGINAL_SIZE = 9 * 0x1A0


def relocate_battle_actors(rom, target):
    table = u32(rom.data, 0x50)
    index, base, size, bss = struct.unpack_from('<4I', rom.data, table)
    assert (index, base, size, bss) == (0, 0x021F3D20, 160128, 4320)
    assert target % 4 == 0 and target >= 0x022234A0
    file_id = u32(rom.data, table + 24)
    start, end = struct.unpack_from('<II', rom.data, rom.fat_offset + file_id * 8)
    original = codeCompression.decompress(rom.data[start:end])
    sites = {base + i: u32(original, i) for i in range(0, len(original) - 3, 4)
             if ORIGINAL_ACTORS <= u32(original, i) < ORIGINAL_ACTORS + ORIGINAL_SIZE}
    references = {address: [] for address in sites}
    disassembler = Cs(CS_ARCH_ARM, CS_MODE_ARM)
    disassembler.skipdata = True
    for ins in disassembler.disasm(original, base):
        match = re.search(r'\[pc(?:, #(-?0x[0-9a-f]+|-?[0-9]+))?\]', ins.op_str)
        if match:
            literal = ins.address + 8 + int(match.group(1) or '0', 0)
            if literal in sites:
                references[literal].append(ins.address)
    if len(sites) != 419 or any(not refs for refs in references.values()):
        raise ValueError('Actor pointer signature or direct literal references changed')
    data = bytearray(original)
    changes = []
    for address, value in sites.items():
        new_value = target + value - ORIGINAL_ACTORS
        struct.pack_into('<I', data, address - base, new_value)
        changes.append({'literal': hex(address), 'before': hex(value), 'after': hex(new_value),
                        'instruction_references': [hex(ref) for ref in references[address]]})
    restored = bytearray(data)
    for address, value in sites.items():
        struct.pack_into('<I', restored, address - base, value)
    assert restored == original
    packed = codeCompression.compress(bytes(data))
    assert codeCompression.decompress(packed) == data
    return packed, {'status': 'actor storage relocation only; original nine-slot behavior retained',
        'original_base': hex(ORIGINAL_ACTORS), 'reserved_base': hex(target),
        'reserved_capacity': 12, 'active_capacity_unchanged': 9,
        'source_sha256': hashlib.sha256(original).hexdigest(),
        'patched_sha256': hashlib.sha256(data).hexdigest(), 'pointer_changes': changes,
        'verification': 'All419 edited words are directly referenced ARM literal-pool addresses. No instruction, palette or other overlay byte changed.'}
