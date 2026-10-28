"""Read-only melonDS 1.1 diagnostic state inspection (not a screenshot).

Addresses are specific to the inspected Super Xros Wars builds. Refuses to
interpret the shared overlay address unless the WH getter signature matches.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path


def inspect(path):
    data = Path(path).read_bytes()
    if data[:4] != b'MELN' or len(data) < 16:
        raise ValueError('Not a melonDS state')
    major, minor, length = struct.unpack_from('<HHI', data, 4)
    if (major, minor) != (13, 0) or length != len(data):
        raise ValueError('Unsupported or truncated melonDS state')
    sections = {}
    pos = 16
    while pos < len(data):
        if pos + 16 > len(data):
            raise ValueError('Truncated section header')
        magic, size = struct.unpack_from('<4sI', data, pos)
        if size < 16 or pos + size > len(data) or magic in sections:
            raise ValueError('Invalid section boundary or duplicate')
        sections[magic] = data[pos + 16:pos + size]
        pos += size
    ram = sections[b'NDSG'][4:4 + 0x1000000]
    if len(ram) != 0x1000000:
        raise ValueError('Unexpected RAM section')

    def word(address):
        if not 0x02000000 <= address <= 0x023FFFFC or address % 4:
            raise ValueError('Invalid DS main RAM pointer')
        return struct.unpack_from('<I', ram, address - 0x02000000)[0]

    result = {'file': str(Path(path).resolve()),
              'sha256': hashlib.sha256(data).hexdigest(),
              'format': [major, minor],
              'limitation': 'One frozen diagnostic sample does not establish a loop or successful connection.'}
    for name in (b'ARM9', b'ARM7'):
        result[name.decode() + '_pc'] = hex(struct.unpack_from('<I', sections[name], 8 + 15 * 4)[0])
    expected = [0xE59F0004, 0xE590004C, 0xE12FFF1E, 0x02220B80]
    result['wireless_overlay_present'] = [word(0x0221D4A8 + i * 4) for i in range(4)] == expected
    if not result['wireless_overlay_present']:
        return result
    context = word(0x02223460)
    callback = word(0x02220A90)
    result.update(context_pointer=hex(context), callback_table_pointer=hex(callback),
                  wh_state=word(0x02220B80 + 0x4C))
    if context:
        result.update(session_state=word(context + 0x20), session_error=word(context + 0x24))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('states', type=Path, nargs='+')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = [inspect(path) for path in args.states]
    text = json.dumps(report, indent=2)
    if args.output:
        args.output.write_text(text + '\n', encoding='utf-8')
    print(text)
