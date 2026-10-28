"""Read-only ARM/overlay audit for native local wireless battle integration.

Requires Capstone in .tools/python. Reports candidates, never patches code.
"""
import hashlib
import json
import re
import struct
import sys
from xros_text import ROOT, Rom, rom_paths, u32
sys.path.insert(0, str(ROOT / '.tools/python'))
from ndspy import codeCompression
from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM


def binaries(rom):
    offset, _, ram, size = struct.unpack_from('<4I', rom.data, 0x20)
    result = [('ARM9', ram, codeCompression.decompress(rom.data[offset:offset + size]))]
    table, length = struct.unpack_from('<II', rom.data, 0x50)
    for index in range(length // 32):
        row = struct.unpack_from('<8I', rom.data, table + index * 32)
        a, b = struct.unpack_from('<II', rom.data, rom.fat_offset + row[6] * 8)
        payload = rom.data[a:b]
        if row[7] & 0x1000000:
            payload = codeCompression.decompress(payload)
        result.append((f'overlay{index}', row[1], payload))
    return result


def audit(rom):
    bins = binaries(rom)
    wireless = next(x for x in bins if x[0] == 'overlay2')
    _, start, code = wireless
    strings = {start + m.start(): m.group().decode('ascii') for m in re.finditer(rb'[ -~]{8,}', code)}
    md = Cs(CS_ARCH_ARM, CS_MODE_ARM)
    md.skipdata = True
    calls, pointers, xrefs = [], [], []
    for name, base, data in bins:
        function = base
        for ins in md.disasm(data, base):
            if ins.mnemonic == 'push' and 'lr' in ins.op_str:
                function = ins.address
            if ins.mnemonic in ('bl', 'blx') and ins.op_str.startswith('#'):
                target = int(ins.op_str[1:], 0)
                if start <= target < start + len(code):
                    calls.append({'binary': name, 'caller_candidate': hex(function), 'instruction': hex(ins.address), 'target': hex(target)})
            if name == 'overlay2' and ins.mnemonic.startswith('ldr'):
                match = re.search(r'\[pc(?:, #(-?0x[0-9a-f]+|-?[0-9]+))?\]', ins.op_str)
                if match:
                    relative = int(match.group(1) or '0', 0)
                    pos = ins.address + 8 + relative - base
                    if 0 <= pos <= len(data) - 4:
                        target = u32(data, pos)
                        if target in strings:
                            xrefs.append({'function_candidate': hex(function), 'instruction': hex(ins.address), 'literal': hex(target), 'text': strings[target]})
        if name == 'ARM9':
            for pos in range(0, len(data) - 3, 4):
                value = u32(data, pos)
                if start <= value < start + len(code):
                    pointers.append({'slot': hex(base + pos), 'target': hex(value)})
    return {'rom_sha256': hashlib.sha256(rom.data).hexdigest(),
            'binaries': [{'name': name, 'ram': hex(base), 'uncompressed_size': len(data), 'sha256': hashlib.sha256(data).hexdigest()} for name, base, data in bins],
            'wireless_overlay': {'index': 2, 'ram': hex(start), 'size': len(code), 'identification': 'Embedded WH_SYSSTATE and WM_STATECODE strings, parent/child scan, MP port receive/send, data-sharing diagnostics'},
            'wireless_literals': [{'address': hex(a), 'text': text} for a, text in strings.items()],
            'literal_xrefs': xrefs, 'direct_calls_into_wireless': calls, 'ARM9_pointer_candidates': pointers,
            'limits': 'ARM decode only; function starts are prologue-based candidates. Overlay 2 shares its RAM base with overlays 3/4/5, so a branch into that address range is NOT proof of a wireless call. In particular the 0x020562cc region loads overlay4. No calling convention, packet schema, party layout, command dispatcher, or link-battle handler is established by this audit.'}


def main():
    out = ROOT / 'build/qa/batch124/local_wireless_audit.json'
    report = {version: audit(Rom(path)) for version, path in rom_paths().items()}
    dusk = ROOT / 'build/backups/Digimon Dusk/Digimon World - Dusk (USA).nds'
    if dusk.exists():
        rom = Rom(dusk)
        report['dusk_reference'] = {'sha256': hashlib.sha256(rom.data).hexdigest(), 'binaries': [{'name': n, 'ram': hex(a), 'size': len(d), 'WH_state_strings': b'WH_SYSSTATE' in d, 'battle_effect_reference': b'BTLEFF' in d} for n, a, d in binaries(rom)], 'use': 'Read-only architecture reference; code has not been transplanted.'}
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(out)
    for version in ('blue', 'red'):
        d = report[version]
        print(version, 'direct calls', len(d['direct_calls_into_wireless']), 'literal xrefs', len(d['literal_xrefs']), 'pointers', len(d['ARM9_pointer_candidates']))


if __name__ == '__main__':
    main()
