"""Exercise six-record opponent actor construction on ARM946.

This verifies actor-record population and formation mapping only. It does not
construct engine-owned scene objects, launch the game battle, or test radio.
"""
import hashlib
import json
import struct
import subprocess

from xros_text import ROOT
from test_wireless_coordinator_arm import Arm

OUT = ROOT / 'build/experimental/wireless_actor_adapter_arm'
ACTORS = 0x02200000
RECORDS = 0x02202000
FORMATION = 0x02203000
ACTOR_SIZE = 0x1A0


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    zig = ROOT / '.tools/ziglang/ziglang/zig.exe'
    objects = []
    for source in ('wireless_battle', 'wireless_party', 'wireless_actor_adapter'):
        obj = OUT / (source + '.o')
        subprocess.run([str(zig), 'cc', '-target', 'arm-freestanding-eabi',
            '-mcpu=arm946e_s', '-marm', '-ffreestanding', '-fno-builtin',
            '-fno-stack-protector', '-fno-unwind-tables',
            '-fno-asynchronous-unwind-tables', '-Os', '-Wall', '-Wextra',
            '-Werror', '-c', str(ROOT / f'native/{source}.c'), '-o', str(obj)],
            check=True, cwd=ROOT)
        objects.append(obj)
    elf = OUT / 'actor_adapter.elf'
    subprocess.run([str(zig), 'build-exe', *(str(obj) for obj in objects),
        '-target', 'arm-freestanding-eabi', '-mcpu', 'arm946e_s',
        '-O', 'ReleaseSmall', '-fno-compiler-rt', '-fno-entry',
        '--no-gc-sections', '-fno-strip', '--script',
        str(ROOT / 'native/wireless_actor_adapter_test.ld'),
        '-femit-bin=' + str(elf)], check=True, cwd=ROOT)
    return elf


def make_record(index):
    record = bytearray(0x80)
    name = f'RIVAL{index}'.encode('ascii')
    record[:len(name)] = name
    struct.pack_into('<H', record, 0x12, 0x100 + index)
    struct.pack_into('<4H', record, 0x1E, 100 + index, 200 + index,
                     50 + index, 100 + index)
    struct.pack_into('<5H', record, 0x26, 40 + index, 60 + index,
                     30 + index, 70 + index, 20 + index)
    struct.pack_into('<4H', record, 0x34, 0x1100 + index, 0x1200 + index,
                     0x1300 + index, 0x1400 + index)
    struct.pack_into('<4H', record, 0x44, 0x2100 + index, 0x2200 + index,
                     0x2300 + index, 0x2400 + index)
    struct.pack_into('<H', record, 0x4C, 0x3100 + index)
    struct.pack_into('<I', record, 0x74, 0xA000 + index)
    return bytes(record)


def main():
    elf = build()
    arm = Arm(elf, expected_symbols=None)
    records = b''.join(make_record(i) for i in range(6))
    formation = bytes((5, 2, 4, 0, 3, 1))
    seed = bytearray(12 * ACTOR_SIZE)
    for actor in range(12):
        start = actor * ACTOR_SIZE
        seed[start:start + ACTOR_SIZE] = bytes([0x30 + actor]) * ACTOR_SIZE
    for slot in range(3):
        struct.pack_into('<H', seed, (6 + slot) * ACTOR_SIZE + 0x14, 0x80 + slot)

    arm.uc.mem_write(ACTORS, bytes(seed))
    arm.uc.mem_write(RECORDS, records)
    arm.uc.mem_write(FORMATION, formation)
    assert arm.call('xwb_build_opponent_actors', ACTORS, RECORDS, FORMATION) == 0
    result = bytes(arm.uc.mem_read(ACTORS, len(seed)))

    # The original player's six battle actor records remain untouched.
    assert result[:6 * ACTOR_SIZE] == seed[:6 * ACTOR_SIZE]
    # Remote roster members land in their selected formation positions.
    expected_position = {record_index: formation[record_index]
                         for record_index in range(6)}
    for record_index, position in expected_position.items():
        actor = result[(6 + position) * ACTOR_SIZE:(7 + position) * ACTOR_SIZE]
        record = records[record_index * 0x80:(record_index + 1) * 0x80]
        assert struct.unpack_from('<H', actor, 0x14)[0] == 0x100 + record_index
        assert actor[0x1A:0x1A + 18] == record[:18]
        assert struct.unpack_from('<I', actor, 0xE4)[0] == 100 + record_index
        assert struct.unpack_from('<H', actor, 0xEA)[0] == 50 + record_index
        assert struct.unpack_from('<HHHH', actor, 0xFA) == tuple(
            0x1100 + record_index + n * 0x100 for n in range(4))
        assert struct.unpack_from('<HHHH', actor, 0x10A) == tuple(
            0x2100 + record_index + n * 0x100 for n in range(4))
        assert struct.unpack_from('<H', actor, 0x13C)[0] == 0x3100 + record_index
        assert struct.unpack_from('<H', actor, 0x140)[0] == 0x3100 + record_index

    # The extra three actor records inherit each original opposing position's
    # untouched bytes, proving all source templates were copied before overlay.
    for position in range(3):
        source = seed[(6 + position) * ACTOR_SIZE:(7 + position) * ACTOR_SIZE]
        target = result[(9 + position) * ACTOR_SIZE:(10 + position) * ACTOR_SIZE]
        assert target[0x00:0x14] == source[0x00:0x14]
        assert target[0x16:0x1A] == source[0x16:0x1A]
        assert target[0x30:0x44] == source[0x30:0x44]
        assert target[0x58:0xE0] == source[0x58:0xE0]
        assert target[0xEC:0xFA] == source[0xEC:0xFA]
        assert target[0x102:0x10A] == source[0x102:0x10A]
        assert target[0x112:0x13C] == source[0x112:0x13C]

    # Invalid formations and malformed records fail before any actor write.
    invalid_formation = bytes((0, 0, 2, 3, 4, 5))
    arm.uc.mem_write(ACTORS, bytes(seed))
    arm.uc.mem_write(FORMATION, invalid_formation)
    before = bytes(arm.uc.mem_read(ACTORS, len(seed)))
    assert arm.call('xwb_build_opponent_actors', ACTORS, RECORDS, FORMATION) == -1
    assert bytes(arm.uc.mem_read(ACTORS, len(seed))) == before

    malformed = bytearray(records)
    struct.pack_into('<H', malformed, 0x12, 0)
    arm.uc.mem_write(RECORDS, bytes(malformed))
    arm.uc.mem_write(FORMATION, formation)
    assert arm.call('xwb_build_opponent_actors', ACTORS, RECORDS, FORMATION) == -1
    assert bytes(arm.uc.mem_read(ACTORS, len(seed))) == before
    assert bytes(arm.uc.mem_read(RECORDS, len(records))) == bytes(malformed)

    report = {
        'status': 'ARM946 opponent actor adapter checks passed',
        'coverage': [
            'six remote saved records populate opponent actor slots6-11',
            'formation permutation maps roster members to engine positions',
            'trained stats, HP/MP and opaque move/equipment fields are retained',
            'local actor records and input records remain unchanged',
            'invalid formations and malformed records cause no actor writes',
            'new slots9-11 inherit original opponent actor defaults',
        ],
        'limitations': 'No in-game actor-construction hook, scene-object creation, opponent UI, command execution, or wireless match is tested.',
        'elf_sha256': hashlib.sha256(elf.read_bytes()).hexdigest(),
    }
    (OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
