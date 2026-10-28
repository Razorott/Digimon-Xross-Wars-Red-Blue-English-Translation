"""Read connection/formation text from the supplied Dusk and World DS ROMs.

Only the Latin letter ranges, space and newline are decoded. Other glyphs and
control parameters remain '?'. These are mechanic references, not translation
authorities for Xros Wars. Neither source ROM is modified.
"""
import hashlib
import json
import re
import struct
from xros_text import ROOT, Rom, u32


def read_strings(data, lower):
    if len(data) < 4:
        return []
    first = u32(data)
    if first % 4 or not 4 <= first <= len(data):
        return []
    offsets = [u32(data, i) for i in range(0, first, 4)] + [len(data)]
    result = []
    upper = lower - 26
    for index, (a, b) in enumerate(zip(offsets, offsets[1:])):
        if not first <= a <= b <= len(data) or (b - a) % 2:
            continue
        letters = []
        for value, in struct.iter_unpack('<H', data[a:b]):
            if value == 0xFFFF:
                break
            if value == 0:
                letters.append(' ')
            elif value == 0xFFFD:
                letters.append(' / ')
            elif upper <= value < upper + 26:
                letters.append(chr(65 + value - upper))
            elif lower <= value < lower + 26:
                letters.append(chr(97 + value - lower))
            else:
                letters.append('?')
        result.append((index, ''.join(letters)))
    return result


def main():
    matches, sources = [], {}
    for key, path in (
        ('dusk', ROOT / 'build/backups/Digimon Dusk/Digimon World - Dusk (USA).nds'),
        ('world_ds', ROOT / 'build/backups/Digimon World DS/Digimon World DS (USA).nds')):
        rom = Rom(path)
        sources[key] = {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(rom.data).hexdigest()}
        tables = []
        if key == 'dusk':
            pak = rom.file('dat/MSG.PAK')
            count = u32(pak)
            assert u32(pak, 4) == 4 + count * 8
            for i in range(count):
                a, size = struct.unpack_from('<II', pak, 4 + i * 8)
                if size & 0x80000000:
                    size &= 0x7FFFFFFF
                    assert a + size <= len(pak)
                    tables.append((f'dat/MSG.PAK:{i}', pak[a:a + size]))
        else:
            tables = [(name, rom.file(name)) for name in rom.files
                      if name.lower().startswith('dat/msg/') and name.lower().endswith('.sdb')]
        for table, data in tables:
            for index, text in read_strings(data, 0x3A if key == 'dusk' else 0x6A):
                if re.search(r'\b(?:wireless\w*|formation|battle start|start battle)\b', text, re.I):
                    matches.append({'game': key, 'table': table, 'index': index, 'text_partial_charset': text})
    result = {'scope': 'Partial inferred Latin glyph decode of original reference ROM text; punctuation/control glyphs unverified.',
              'sources': sources, 'matches': matches}
    path = ROOT / 'build/qa/wireless_battle_engine/reference_wireless_text.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'matches': len(matches), 'reference': str(path.relative_to(ROOT))}))


if __name__ == '__main__':
    main()
