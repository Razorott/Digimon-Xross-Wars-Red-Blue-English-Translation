"""Build and exercise the freestanding ARM9 lobby/rule/packet component.

No game hooks, radio calls or save writes occur. This must not be reported as
a playable wireless match. The ELF address belongs only to this CPU harness.
"""
import hashlib
import itertools
import json
import random
import struct
import subprocess
import sys
import zlib
from xros_text import ROOT
sys.path.insert(0, str(ROOT / '.tools/python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_ARM, UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2,
    UC_ARM_REG_R3, UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_CPSR, UC_CPU_ARM_946)

OUT = ROOT / 'build/experimental/wireless_battle_native'
MATCH, BUFFER, PAYLOAD, VIEW = 0x02300000, 0x02301000, 0x02302000, 0x02303000
TEAM, RECORDS = 0x02304000, 0x02305000
RETURN, STACK = 0x023FF000, 0x023EF000


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    zig = ROOT / '.tools/ziglang/ziglang/zig.exe'
    obj, elf = OUT / 'coordinator.o', OUT / 'coordinator.elf'
    subprocess.run([str(zig), 'cc', '-target', 'arm-freestanding-eabi',
        '-mcpu=arm946e_s', '-marm', '-ffreestanding', '-fno-builtin',
        '-fno-stack-protector', '-fno-unwind-tables', '-fno-asynchronous-unwind-tables',
        '-Os', '-Wall', '-Wextra', '-Werror', '-c', str(ROOT / 'native/wireless_battle.c'),
        '-o', str(obj)], check=True, cwd=ROOT)
    subprocess.run([str(zig), 'build-exe', str(obj), '-target', 'arm-freestanding-eabi',
        '-mcpu', 'arm946e_s', '-O', 'ReleaseSmall', '-fno-compiler-rt', '-fno-entry',
        '--no-gc-sections', '-fno-strip', '--script', str(ROOT / 'native/wireless_battle.ld'),
        '-femit-bin=' + str(elf)], check=True, cwd=ROOT)
    return elf


class Arm:
    def __init__(self, path, expected_symbols=21):
        data = path.read_bytes()
        h = struct.unpack_from('<16sHHIIIIIHHHHHH', data)
        assert h[0][:6] == b'\x7fELF\x01\x01' and h[2] == 40
        self.uc = Uc(UC_ARCH_ARM, UC_MODE_ARM)
        self.uc.ctl_set_cpu_model(UC_CPU_ARM_946)
        self.uc.mem_map(0x02000000, 0x400000)
        for i in range(h[10]):
            kind, offset, address, _, size, memsize, _, _ = struct.unpack_from('<8I', data, h[5] + i * h[9])
            if kind == 1:
                assert 0x02000000 <= address <= address + memsize <= 0x02300000
                self.uc.mem_write(address, data[offset:offset + size])
        sections = [struct.unpack_from('<10I', data, h[6] + i * h[11]) for i in range(h[12])]
        self.symbols = {}
        for section in sections:
            if section[1] != 2:
                continue
            strings = sections[section[6]]
            names = data[strings[4]:strings[4] + strings[5]]
            for offset in range(section[4], section[4] + section[5], section[9]):
                name, value, _, info, _, index = struct.unpack_from('<IIIBBH', data, offset)
                symbol = names[name:].split(b'\0', 1)[0].decode('ascii')
                if index and symbol.startswith('xwb_') and '.' not in symbol:
                    self.symbols[symbol] = value
        if expected_symbols is not None:
            assert len(self.symbols) == expected_symbols, self.symbols
        self.calls = 0
        self.stopped = False
        def stop(uc, address, size, userdata):
            if address == RETURN:
                self.stopped = True
                uc.emu_stop()
        self.uc.hook_add(UC_HOOK_CODE, stop)

    def call(self, name, *args):
        assert len(args) <= 8
        self.uc.reg_write(UC_ARM_REG_CPSR, 0xD3)
        self.uc.reg_write(UC_ARM_REG_SP, STACK)
        self.uc.reg_write(UC_ARM_REG_LR, RETURN)
        for register, value in zip((UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3), args + (0,) * 4):
            self.uc.reg_write(register, value)
        if len(args) > 4:
            self.uc.mem_write(STACK, struct.pack('<' + 'I' * (len(args) - 4), *args[4:]))
        self.stopped = False
        self.uc.emu_start(self.symbols[name], RETURN + 4, count=200000)
        assert self.stopped, name
        self.calls += 1
        return struct.unpack('<i', struct.pack('<I', self.uc.reg_read(UC_ARM_REG_R0)))[0]

    def state(self):
        return bytes(self.uc.mem_read(MATCH, 44))

    def word(self, offset):
        return struct.unpack_from('<I', self.state(), offset)[0]


def main():
    elf = build()
    arm = Arm(elf)
    call = arm.call
    assert call('xwb_sizeof_match') == 44
    assert call('xwb_init', MATCH, 0) == -1
    assert call('xwb_init', MATCH, 0x12345678) == 0
    assert call('xwb_start', MATCH, 0, arm.word(8)) == -5
    for side in range(2):
        assert call('xwb_set_team', MATCH, side, 1234 + side) == 0
        arm.uc.mem_write(PAYLOAD, bytes(range(6)))
        assert call('xwb_set_formation', MATCH, side, PAYLOAD) == 0
    # Every permutation is legal, and duplicates/out-of-range slots are rejected
    # without changing the match. Captures both placement and validation edges.
    for permutation in itertools.permutations(range(6)):
        arm.uc.mem_write(PAYLOAD, bytes(permutation))
        assert call('xwb_set_formation', MATCH, 0, PAYLOAD) == 0
    for positions in ([0, 0, 2, 3, 4, 5], [0, 1, 2, 3, 4, 6], [255, 1, 2, 3, 4, 5]):
        before = arm.state()
        arm.uc.mem_write(PAYLOAD, bytes(positions))
        assert call('xwb_set_formation', MATCH, 0, PAYLOAD) == -1
        assert arm.state() == before
    for music in range(7):
        for side in range(2):
            assert call('xwb_set_ready', MATCH, side, 1, arm.word(8)) == 0
        before = arm.state()
        assert call('xwb_select_music', MATCH, 1, music) == -3
        assert arm.state() == before
        old_music = before[40]
        old_revision = arm.word(8)
        assert call('xwb_select_music', MATCH, 0, music) == 0
        if old_music != music:
            assert arm.state()[38] == 0
            assert call('xwb_set_ready', MATCH, 0, 1, old_revision) == -4
    for side in range(2):
        assert call('xwb_set_ready', MATCH, side, 1, arm.word(8)) == 0
    assert call('xwb_start', MATCH, 1, arm.word(8)) == -3
    assert call('xwb_start', MATCH, 0, arm.word(8)) == 0
    for side in range(2):
        assert call('xwb_can_digixross', MATCH, side) == 0
        assert call('xwb_commit_digixross', MATCH, 0, side) == -2
    assert call('xwb_next_round', MATCH, 1) == -3
    assert call('xwb_next_round', MATCH, 0) == 0
    for side in range(2):
        assert call('xwb_can_digixross', MATCH, side) == 1
        assert call('xwb_commit_digixross', MATCH, 1, side) == -3
        assert call('xwb_commit_digixross', MATCH, 0, side) == 0
        assert call('xwb_commit_digixross', MATCH, 0, side) == -2
    assert call('xwb_set_formation', MATCH, 0, PAYLOAD) == -2
    assert call('xwb_select_music', MATCH, 0, 0) == -2
    assert call('xwb_finish', MATCH, 0) == 0
    assert call('xwb_can_digixross', MATCH, 0) == 0
    assert call('xwb_abort', MATCH) == 0

    rng = random.Random(0x58574231)
    for damage in list(range(200)) + [0x7FFFFFFF, 0xFFFFFFFE, 0xFFFFFFFF] + [rng.randrange(2 ** 32) for _ in range(200)]:
        actual = call('xwb_digixross_damage', damage) & 0xFFFFFFFF
        assert actual == (max(1, damage * 9 // 10) if damage else 0), (damage, actual)
    packets = []
    for length in range(73):
        payload = rng.randbytes(length)
        if length:
            arm.uc.mem_write(PAYLOAD, payload)
        arm.uc.mem_write(BUFFER, b'\xA5' * 112)
        result = call('xwb_encode', BUFFER, 96, 7, 1, 0x12345678, length, PAYLOAD, length)
        assert result == 24 + length
        packet = bytes(arm.uc.mem_read(BUFFER, result))
        expected = struct.pack('<I H B B I I H H', 0x31425758, 1, 7, 1, 0x12345678, length, length, 0)
        crc = zlib.crc32(expected + payload)
        assert packet == expected + struct.pack('<I', crc) + payload
        assert bytes(arm.uc.mem_read(BUFFER + result, 112 - result)) == b'\xA5' * (112 - result)
        assert call('xwb_decode', BUFFER, result, 0x12345678, 1, VIEW) == 0
        assert call('xwb_decode', BUFFER, result, 0x12345679, 1, VIEW) == -4
        assert call('xwb_decode', BUFFER, result, 0x12345678, 0, VIEW) == -1
        packets.append(packet)
    # Reject each single-bit corruption of a maximum-size packet. An invalid
    # decode cannot leave a partially filled output view for the engine to use.
    packet = packets[-1]
    for index in range(len(packet)):
        for bit in range(8):
            corrupted = bytearray(packet)
            corrupted[index] ^= 1 << bit
            arm.uc.mem_write(BUFFER, bytes(corrupted))
            arm.uc.mem_write(VIEW, b'\xA5' * 16)
            assert call('xwb_decode', BUFFER, len(packet), 0x12345678, 1, VIEW) < 0
            assert bytes(arm.uc.mem_read(VIEW, 16)) == b'\xA5' * 16
    for length in list(range(24)) + [97, 0xFFFFFFFF]:
        assert call('xwb_decode', BUFFER, length, 0x12345678, 1, VIEW) == -1
    assert call('xwb_sizeof_team_transfer') == 784
    assert call('xwb_team_reset', TEAM, 0) == -1
    assert call('xwb_team_reset', TEAM, 0xAABBCCDD) == 0
    assert call('xwb_team_digest', TEAM, VIEW) == -5
    records = rng.randbytes(768)
    arm.uc.mem_write(RECORDS, records)
    order = list(range(12))
    rng.shuffle(order)
    for count, index in enumerate(order):
        assert call('xwb_team_chunk', RECORDS, 0xAABBCCDD, index, PAYLOAD) == 72
        fragment = bytes(arm.uc.mem_read(PAYLOAD, 72))
        assert fragment == struct.pack('<IHH', 0xAABBCCDD, index * 64, 768) + records[index * 64:index * 64 + 64]
        assert call('xwb_team_accept', TEAM, PAYLOAD, 72) == int(count == 11)
        assert call('xwb_team_accept', TEAM, PAYLOAD, 72) == int(count == 11)
        before = bytes(arm.uc.mem_read(TEAM, 784))
        corrupted = bytearray(fragment)
        corrupted[8] ^= 1
        arm.uc.mem_write(PAYLOAD, bytes(corrupted))
        assert call('xwb_team_accept', TEAM, PAYLOAD, 72) == -1
        assert bytes(arm.uc.mem_read(TEAM, 784)) == before
        arm.uc.mem_write(PAYLOAD, fragment)
    assert bytes(arm.uc.mem_read(TEAM + 16, 768)) == records
    assert call('xwb_team_digest', TEAM, VIEW) == 0
    assert struct.unpack('<I', arm.uc.mem_read(VIEW, 4))[0] == zlib.crc32(records)
    before = bytes(arm.uc.mem_read(TEAM, 784))
    for offset, total, transfer, length, expected in (
        (0, 768, 0xAABBCCDE, 72, -4), (65, 768, 0xAABBCCDD, 72, -1),
        (768, 768, 0xAABBCCDD, 72, -1), (0, 767, 0xAABBCCDD, 72, -1),
        (0, 768, 0xAABBCCDD, 71, -1)):
        arm.uc.mem_write(PAYLOAD, struct.pack('<IHH', transfer, offset, total) + records[:64])
        assert call('xwb_team_accept', TEAM, PAYLOAD, length) == expected
        assert bytes(arm.uc.mem_read(TEAM, 784)) == before
    assert call('xwb_team_chunk', RECORDS, 0xAABBCCDD, 12, PAYLOAD) == -1
    assert call('xwb_team_reset', TEAM, 0xAABBCCDE) == 0
    assert call('xwb_team_digest', TEAM, VIEW) == -5
    assert bytes(arm.uc.mem_read(TEAM + 16, 768)) == b'\0' * 768

    # The saved-record adapter only overlays fields observed in the six-actor
    # fixture. It must reject impossible health data before touching an actor.
    actor = 0x02306000
    saved = 0x02307000
    src = bytearray(0x80)
    struct.pack_into('<H', src, 0x12, 55)
    struct.pack_into('<HHHH', src, 0x1E, 511, 511, 443, 443)
    for offset, value in ((0x26,79),(0x2C,73),(0x2A,56),(0x28,97),(0x2E,50),
                          (0x34,0x0389),(0x36,0x037B),(0x38,72),(0x3A,450),
                          (0x44,1067),(0x46,1053),(0x48,0xFFFF),(0x4A,0xFFFF),
                          (0x4C,0x3838)):
        struct.pack_into('<H', src, offset, value)
    src[:12] = bytes.fromhex('834a83758365838a83828393')
    arm.uc.mem_write(saved, bytes(src))
    sentinel = b'\xA5' * 0x1A0
    arm.uc.mem_write(actor, sentinel)
    assert call('xwb_apply_saved_record_fields', actor, saved) == 0
    adapted = bytes(arm.uc.mem_read(actor, 0x1A0))
    expected_fields = [(0x14, struct.pack('<H',55)), (0x1A,src[:18]),
        (0x44,struct.pack('<HH',79,79)), (0x48,struct.pack('<HH',73,73)),
        (0x4C,struct.pack('<HH',56,56)), (0x50,struct.pack('<HH',97,97)),
        (0x54,struct.pack('<HH',50,50)), (0xE0,struct.pack('<I',511)),
        (0xE4,struct.pack('<I',511)), (0xE8,struct.pack('<H',443)),
        (0xEA,struct.pack('<H',443)), (0xFA,struct.pack('<HHHH',0x389,0x37B,72,450)),
        (0x10A,struct.pack('<HHHH',1067,1053,0xFFFF,0xFFFF)),
        (0x13C,struct.pack('<H',0x3838)), (0x140,struct.pack('<H',0x3838))]
    covered = set()
    for offset, value in expected_fields:
        assert adapted[offset:offset+len(value)] == value, (hex(offset), adapted[offset:offset+len(value)].hex(), value.hex())
        covered.update(range(offset, offset+len(value)))
    assert all(adapted[i] == sentinel[i] for i in range(0x1A0) if i not in covered)
    assert bytes(arm.uc.mem_read(saved, 0x80)) == bytes(src)
    for offset, value in ((0x12,0),(0x20,0)):
        invalid = bytearray(src)
        struct.pack_into('<H', invalid, offset, value)
        arm.uc.mem_write(saved, bytes(invalid))
        arm.uc.mem_write(actor, sentinel)
        assert call('xwb_apply_saved_record_fields', actor, saved) == -1
        assert bytes(arm.uc.mem_read(actor, 0x1A0)) == sentinel
    result = {'status': 'ARM9 component execution checks passed', 'arm_function_calls': arm.calls,
              'elf_sha256': hashlib.sha256(elf.read_bytes()).hexdigest(),
              'symbols': {name: hex(address) for name, address in arm.symbols.items()},
              'scope': 'Compiled component only; no game integration, radio transport, actual formation UI, music playback, or multiplayer battle test.'}
    (OUT / 'test_report.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
