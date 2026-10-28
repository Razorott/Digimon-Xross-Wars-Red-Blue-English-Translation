"""Read Nintendo DS files and Super Xros Wars PAK/message containers.

Uses only the Python standard library. Original ROMs are always read-only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from collections import defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def u32(data, offset=0):
    return struct.unpack_from('<I', data, offset)[0]


def align4(n):
    return (n + 3) & ~3


def lzss_decode(data, expected_size):
    """PAK 2.01's length-prefixed, zero-filled 4K-ring LZSS stream."""
    packed_size = u32(data)
    if packed_size > len(data) - 4:
        raise ValueError('Truncated LZSS stream')
    data = data[4:4 + packed_size]
    ring = bytearray(4096)
    write = 4096 - 18
    out = bytearray()
    pos = 0
    while len(out) < expected_size:
        flags = data[pos]
        pos += 1
        for bit in range(8):
            if flags & (1 << bit):
                values = [data[pos]]
                pos += 1
            else:
                low, high = data[pos:pos + 2]
                pos += 2
                read = low | ((high & 0xf0) << 4)
                length = (high & 15) + 3
                values = None
            if values is not None:
                value = values[0]
                out.append(value)
                ring[write] = value
                write = (write + 1) & 4095
            else:
                for j in range(length):
                    value = ring[(read + j) & 4095]
                    out.append(value)
                    ring[write] = value
                    write = (write + 1) & 4095
                    if len(out) == expected_size:
                        break
            if len(out) == expected_size:
                break
    return bytes(out)


def lzss_encode(data):
    """Encode the game's native ring LZSS, with a verified decode round trip."""
    history=defaultdict(deque);out=bytearray();pos=0
    while pos<len(data):
        flagpos=len(out);out.append(0);flags=0
        for bit in range(8):
            if pos>=len(data):break
            candidates=history[data[pos:pos+3]]
            while candidates and candidates[0]<pos-4096:candidates.popleft()
            length=0;match=0
            for p in reversed(candidates):
                n=3
                while n<18 and pos+n<len(data) and data[p+n]==data[pos+n]:n+=1
                if n>length:length=n;match=p
                if length==18:break
            if length>=3:
                ring=(4078+match)&4095
                out.extend((ring&255,((ring>>8)<<4)|(length-3)))
            else:
                length=1;flags|=1<<bit;out.append(data[pos])
            for p in range(pos,pos+length):
                if p+3<=len(data):history[data[p:p+3]].append(p)
            pos+=length
        out[flagpos]=flags
    result=struct.pack('<I',len(out))+out
    if lzss_decode(result,len(data))!=data:raise ValueError('LZSS encode round trip failed')
    return result


class Rom:
    def __init__(self, path):
        self.path = Path(path)
        self.data = self.path.read_bytes()
        self.code = self.data[12:16].decode('ascii')
        self.fnt_offset, self.fnt_size, self.fat_offset, self.fat_size = struct.unpack_from('<4I', self.data, 0x40)
        self.files = {}
        fnt = self.data[self.fnt_offset:self.fnt_offset + self.fnt_size]

        def directory(dir_id, prefix):
            offset, file_id, _ = struct.unpack_from('<IHH', fnt, (dir_id & 0xfff) * 8)
            while fnt[offset]:
                kind = fnt[offset]
                offset += 1
                length = kind & 0x7f
                name = fnt[offset:offset + length].decode('ascii')
                offset += length
                if kind & 0x80:
                    child = struct.unpack_from('<H', fnt, offset)[0]
                    offset += 2
                    directory(child, prefix + name + '/')
                else:
                    self.files[prefix + name] = file_id
                    file_id += 1

        directory(0xf000, '')

    def file(self, name):
        file_id = self.files[name]
        start, end = struct.unpack_from('<II', self.data, self.fat_offset + file_id * 8)
        if not 0 <= start <= end <= len(self.data):
            raise ValueError(f'Invalid FAT: {name}')
        return self.data[start:end]


class Pak:
    def __init__(self, data):
        self.data = data
        self.count = u32(data)
        if self.count > 100000 or data[4:8] != b'2.01':
            raise ValueError('Unrecognized PAK')
        self.entries = []
        for i in range(self.count):
            offset, unpacked_size, size, flags = struct.unpack_from('<4I', data, 16 + i * 16)
            if offset < 16 + self.count * 16 or offset + size > len(data):
                raise ValueError(f'Invalid PAK entry {i}')
            self.entries.append((offset, size, unpacked_size, flags))

    def file(self, index):
        offset, size, unpacked_size, flags = self.entries[index]
        raw = self.data[offset:offset + size]
        if flags == 0:
            return lzss_decode(raw, unpacked_size)
        if size != unpacked_size or flags != 0x80000000:
            raise ValueError(f'Unsupported PAK compression/flags: {index}')
        return raw

    def rebuild(self, replacements, compress=False):
        """Relocate entries, maintaining their original gaps and metadata."""
        first = self.entries[0][0] if self.entries else len(self.data)
        out = bytearray(self.data[:first])
        for index, (offset, size, unpacked_size, flags) in enumerate(self.entries):
            if index in replacements:
                payload = replacements[index]
                unpacked_size = len(payload)
                flags = 0x80000000
                if compress:
                    packed=lzss_encode(payload)
                    if len(packed)<len(payload):payload=packed;flags=0
            else:
                payload = self.data[offset:offset + size]
            struct.pack_into('<4I', out, 16 + index * 16, len(out), unpacked_size, len(payload), flags)
            out.extend(payload)
            next_offset = self.entries[index + 1][0] if index + 1 < self.count else len(self.data)
            out.extend(self.data[offset + size:next_offset])
        return bytes(out)


def display(raw):
    """Represent bytes without discarding control codes or undecodable bytes."""
    text = raw.decode('cp932', errors='surrogateescape')
    result = []
    for char in text:
        n = ord(char)
        if n < 32 or n == 127:
            result.append(f'<{n:02X}>')
        elif 0xdc80 <= n <= 0xdcff:
            result.append(f'<{n - 0xdc00:02X}>')
        else:
            result.append(char)
    return ''.join(result)


class Messages:
    def __init__(self, data):
        self.data = data
        self.kind, self.count = struct.unpack_from('<II', data)
        if self.kind != 0 or not 0 < self.count <= 100000 or 8 + self.count * 4 > len(data):
            raise ValueError('Not a recognized message table')
        self.offsets = list(struct.unpack_from(f'<{self.count}I', data, 8))
        if self.offsets[0] != 8 + self.count * 4:
            raise ValueError('Unexpected message table prefix')
        if self.offsets != sorted(self.offsets) or self.offsets[-1] >= len(data):
            raise ValueError('Invalid message offsets')
        ends = self.offsets[1:] + [len(data)]
        self.spans = [data[a:b] for a, b in zip(self.offsets, ends)]
        self.raw = [span.rstrip(b'\0') for span in self.spans]
        if any(raw and not span.endswith(b'\0') for raw, span in zip(self.raw, self.spans)):
            raise ValueError('Unterminated message')

    def rebuild(self, replacements):
        out = bytearray(self.data[:self.offsets[0]])
        for index, span in enumerate(self.spans):
            struct.pack_into('<I', out, 8 + index * 4, len(out))
            if index in replacements:
                payload = replacements[index]
                out.extend(payload + b'\0')
                out.extend(b'\0' * (align4(len(out)) - len(out)))
            else:
                out.extend(span)
        return bytes(out)

    def append(self, messages):
        """Append new IDs while preserving every existing message ID and byte.

        This is for game-added UI entries, not a translation rewrite. Existing
        message payloads (including Japanese bytes and control codes) are copied
        verbatim; appended payloads use the next stable IDs after ``count``.
        """
        additions = list(messages)
        if not additions:
            return self.data
        if self.count + len(additions) > 100000:
            raise ValueError('Message table would exceed the supported ID count')
        if any(not isinstance(message, bytes) or b'\0' in message for message in additions):
            raise ValueError('Appended messages must be NUL-free byte strings')
        count = self.count + len(additions)
        prefix_size = 8 + count * 4
        out = bytearray(prefix_size)
        struct.pack_into('<II', out, 0, self.kind, count)
        for index, message in enumerate(self.raw + additions):
            struct.pack_into('<I', out, 8 + index * 4, len(out))
            out.extend(message)
            out.append(0)
            out.extend(b'\0' * (align4(len(out)) - len(out)))
        rebuilt = bytes(out)
        decoded = Messages(rebuilt)
        if decoded.raw[:self.count] != self.raw or decoded.raw[self.count:] != additions:
            raise ValueError('Appended message table failed ID-preservation validation')
        return rebuilt


def rom_paths():
    paths = list((ROOT / 'Original Roms').glob('*.nds'))
    result = {}
    for path in paths:
        with path.open('rb') as f:
            f.seek(12)
            code = f.read(4)
        version = {b'TBFJ': 'blue', b'TLTJ': 'red'}.get(code)
        if version:
            if version in result:
                raise ValueError(f'Multiple original {version} ROMs')
            result[version] = path
    if set(result) != {'blue', 'red'}:
        raise ValueError('Expected original Blue (TBFJ) and Red (TLTJ) ROMs')
    return result


def extract():
    target = ROOT / 'extracted'
    target.mkdir(exist_ok=True)
    report = {}
    for version, path in rom_paths().items():
        rom = Rom(path)
        version_dir = target / version
        version_dir.mkdir(exist_ok=True)
        inventory = []
        records = []
        for name, file_id in sorted(rom.files.items(), key=lambda x: x[1]):
            payload = rom.file(name)
            info = {'name': name, 'file_id': file_id, 'size': len(payload), 'sha256': hashlib.sha256(payload).hexdigest()}
            if payload[4:8] == b'2.01':
                pak = Pak(payload)
                assert pak.rebuild({}) == payload, f'PAK round trip failed: {name}'
                info['entries'] = pak.count
                if name.startswith('MSG/'):
                    tables = []
                    for entry in range(pak.count):
                        data = pak.file(entry)
                        try:
                            messages = Messages(data)
                        except ValueError as exc:
                            tables.append({'entry': entry, 'size': len(data), 'error': str(exc), 'header_hex': data[:32].hex()})
                            continue
                        assert messages.rebuild({}) == data, f'Message round trip failed: {name}/{entry}'
                        tables.append({'entry': entry, 'count': messages.count})
                        for index, raw in enumerate(messages.raw):
                            records.append({'id': f'{name}:{entry:03d}:{index:05d}', 'archive': name, 'entry': entry, 'index': index, 'offset': messages.offsets[index], 'source': display(raw), 'raw_hex': raw.hex(), 'english': ''})
                    info['tables'] = tables
            inventory.append(info)
        (version_dir / 'inventory.json').write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        with (version_dir / 'messages.jsonl').open('w', encoding='utf-8') as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        report[version] = {'rom': path.name, 'sha256': hashlib.sha256(rom.data).hexdigest(), 'message_count': len(records), 'message_tables': sum(len(i.get('tables', [])) for i in inventory), 'unparsed_tables': [i for i in inventory if any('error' in t for t in i.get('tables', []))]}
    (target / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['extract'])
    args = parser.parse_args()
    if args.command == 'extract':
        extract()
