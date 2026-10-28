"""Exercise two native session controllers through an in-memory packet link.

This checks protocol logic only. It does not emulate Nintendo radio, the game
battle engine, Link Box UI, or a live two-console match.
"""
import hashlib
import json
import struct
import subprocess
import sys
from xros_text import ROOT
sys.path.insert(0, str(ROOT / '.tools/python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_ARM, UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_R0, UC_ARM_REG_SP, UC_ARM_REG_LR,
    UC_ARM_REG_CPSR, UC_CPU_ARM_946)

OUT = ROOT / 'build/experimental/wireless_session_loopback_arm'
BASE = 0x022234A0
RETURN, STACK = 0x023FF000, 0x023EF000
SESSION_API = ('begin pump get_state copy_remote get_match set_formation '
               'select_music set_ready start submit_action take_action '
               'confirm_action next_round end').split()
TRANSPORT_API = ('bind get_side set_session send take detach dropped connected radio_busy').split()


def compile_object(zig, source, target, defines=()):
    output = OUT / f'{target}.o'
    subprocess.run([str(zig), 'cc', '-target', 'arm-freestanding-eabi',
        '-mcpu=arm946e_s', '-marm', '-ffreestanding', '-fno-builtin',
        '-fno-stack-protector', '-fno-unwind-tables', '-fno-asynchronous-unwind-tables',
        '-Os', '-Wall', '-Wextra', '-Werror', *defines, '-c', str(ROOT / source),
        '-o', str(output)], check=True, cwd=ROOT)
    return output


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    zig = ROOT / '.tools/ziglang/ziglang/zig.exe'
    objects = [compile_object(zig, 'native/wireless_battle.c', 'battle'),
               compile_object(zig, 'native/wireless_party.c', 'party')]
    for side in ('host', 'guest'):
        defines = []
        for name in SESSION_API:
            defines.append(f'-Dxwb_session_{name}={side}_xwb_session_{name}')
        for name in TRANSPORT_API:
            defines.append(f'-Dxwb_transport_{name}={side}_transport_{name}')
        defines.append('-DXWB_SESSION_TEST')
        defines.append(f'-Dxwb_session_debug_flags={side}_xwb_session_debug_flags')
        defines.append(f'-Dxwb_session_debug_info={side}_xwb_session_debug_info')
        objects.append(compile_object(zig, 'native/wireless_session.c', side + '_session', defines))
    objects.append(compile_object(zig, 'native/wireless_session_loopback_test.c', 'loopback'))
    elf = OUT / 'loopback.elf'
    subprocess.run([str(zig), 'build-exe', *(str(obj) for obj in objects),
        '-target', 'arm-freestanding-eabi', '-mcpu', 'arm946e_s', '-O', 'ReleaseSmall',
        '-fno-compiler-rt', '-fno-entry', '--no-gc-sections', '-fno-strip',
        '--script', str(ROOT / 'native/wireless_session_loopback_test.ld'),
        '-femit-bin=' + str(elf)], check=True, cwd=ROOT)
    return elf


def run(elf):
    data = elf.read_bytes()
    header = struct.unpack_from('<16sHHIIIIIHHHHHH', data)
    uc = Uc(UC_ARCH_ARM, UC_MODE_ARM)
    uc.ctl_set_cpu_model(UC_CPU_ARM_946)
    uc.mem_map(0x02000000, 0x400000)
    for i in range(header[10]):
        kind, offset, address, _, size, memsize, _, _ = struct.unpack_from(
            '<8I', data, header[5] + i * header[9])
        if kind == 1:
            assert 0x02000000 <= address <= address + memsize <= 0x02400000
            uc.mem_write(address, data[offset:offset + size])
    symbols = {}
    sections = [struct.unpack_from('<10I', data, header[6] + i * header[11])
                for i in range(header[12])]
    for section in sections:
        if section[1] != 2: continue
        strings = sections[section[6]]
        names = data[strings[4]:strings[4] + strings[5]]
        for offset in range(section[4], section[4] + section[5], section[9]):
            name, value, _, _, _, index = struct.unpack_from('<IIIBBH', data, offset)
            symbol = names[name:].split(b'\0', 1)[0].decode('ascii')
            if index and symbol in ('xwb_test_main', 'xwb_test_diag'): symbols[symbol] = value
    assert 'xwb_test_main' in symbols and 'xwb_test_diag' in symbols
    stopped = False
    def stop(engine, address, _size, _user):
        nonlocal stopped
        if address == RETURN:
            stopped = True
            engine.emu_stop()
    uc.hook_add(UC_HOOK_CODE, stop)
    uc.reg_write(UC_ARM_REG_CPSR, 0xD3)
    uc.reg_write(UC_ARM_REG_SP, STACK)
    uc.reg_write(UC_ARM_REG_LR, RETURN)
    uc.emu_start(symbols['xwb_test_main'], RETURN + 4, count=5000000)
    if not stopped:
        raise RuntimeError('ARM loopback test did not return')
    code = struct.unpack('<i', struct.pack('<I', uc.reg_read(UC_ARM_REG_R0)))[0]
    diag = struct.unpack('<12I', uc.mem_read(symbols['xwb_test_diag'], 48))
    return code, diag


def main():
    elf = build()
    code, diag = run(elf)
    if code:
        raise AssertionError(f'two-session loopback failed at checkpoint {code}; diagnostic={diag}')
    report = {'status': 'Two independent ARM946 session controllers passed an in-memory loopback match.',
        'checks': ['HELLO and six-record transfer both directions',
                   'simultaneous formation edits and concurrent host music/guest formation',
                   'lost lobby acknowledgement retry with duplicate-safe merge',
                   'both ready and host start',
                   'host and guest action transfer plus matching result/RNG confirmation',
                   'host round advance', 'one DigiXross per side after round1',
                   'duplicate DigiXross rejection', 'session cleanup',
                   'malformed remote saved record rejected before lobby readiness'],
        'limitations': 'Packet queues replace radio. Actions are acknowledged with supplied digests; no game battle engine is called. No live emulator, DS, or 3DS match was tested.',
        'elf_sha256': hashlib.sha256(elf.read_bytes()).hexdigest(),
        'checkpoint': code}
    (OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
