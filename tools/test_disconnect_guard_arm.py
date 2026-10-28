"""Execute the original and guarded ARM error-routing paths in Unicorn.

The WM reset function is intercepted, not simulated. This tests instructions and
state transitions only; it does not establish a working wireless connection.
"""
import json
import struct
import sys
from xros_text import ROOT, Rom, rom_paths, u32
sys.path.insert(0, str(ROOT / '.tools/python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_ARM, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R5, UC_ARM_REG_R7, UC_ARM_REG_R9, UC_ARM_REG_LR, UC_ARM_REG_PC
from local_wireless_disconnect import guarded_overlay, codeCompression, BASE, CAVE, ERROR_SITE, RESUME, RESET


def run_path(binary, state, error):
    uc = Uc(UC_ARCH_ARM, UC_MODE_ARM)
    uc.mem_map(0x02000000, 0x400000)
    uc.mem_write(BASE, binary)
    context = 0x02300000
    before = bytearray(b'\xA5' * 0x40)
    struct.pack_into('<II', before, 0x20, state, 0)
    uc.mem_write(context, bytes(before))
    uc.reg_write(UC_ARM_REG_R5, 14)
    uc.reg_write(UC_ARM_REG_R7, error)
    uc.reg_write(UC_ARM_REG_R9, context)
    resets = []
    stopped = []
    def code(machine, address, size, data):
        if address == RESET:
            resets.append(address)
            # Mimic only a return from the existing reset API. The radio and
            # buffers are untouched; real SDK asynchronous behaviour is untested.
            machine.reg_write(UC_ARM_REG_R0, 1)
            machine.reg_write(UC_ARM_REG_PC, machine.reg_read(UC_ARM_REG_LR))
        elif address == RESUME:
            stopped.append(address)
            machine.emu_stop()
    uc.hook_add(UC_HOOK_CODE, code)
    uc.emu_start(ERROR_SITE, RESUME + 4, count=100)
    assert stopped == [RESUME], 'Guard did not return to original dispatcher'
    after = bytes(uc.mem_read(context, 0x40))
    for i in range(0x40):
        if not 0x20 <= i < 0x28:
            assert after[i] == before[i], f'Unexpected context write at {i}'
    return {'state': u32(after, 0x20), 'error': u32(after, 0x24), 'reset_calls': len(resets)}


def main():
    results = []
    for version, path in rom_paths().items():
        rom = Rom(path)
        table = u32(rom.data, 0x50) + 2 * 32
        fid = u32(rom.data, table + 24)
        a, b = struct.unpack_from('<II', rom.data, rom.fat_offset + fid * 8)
        original = codeCompression.decompress(rom.data[a:b])
        packed, manifest = guarded_overlay(rom)
        guarded = codeCompression.decompress(packed)
        for state in range(15):
            for error in (0, 1, 20, 27, 31):
                old = run_path(original, state, error)
                new = run_path(guarded, state, error)
                expected = state if not error else 13 if state in (12, 13) else 14
                assert new['state'] == expected, (version, state, error, new)
                assert new['error'] == error
                assert new['reset_calls'] == int(bool(error))
                if state not in (12, 13) or not error:
                    assert new == old, (version, state, error, old, new)
                else:
                    assert old['state'] == 14, 'Original did not reproduce closing-state override'
                results.append({'version': version, 'initial_state': state, 'transport_error': error, 'original': old, 'guarded': new})
    out = ROOT / 'build/qa/local_wireless_session/disconnect_guard_arm_test.json'
    out.write_text(json.dumps({'cases_passed': len(results), 'scope': 'ARM execution with reset API intercepted; not a radio test', 'cases': results}, indent=2) + '\n')
    print(len(results), 'ARM instruction cases passed')


if __name__ == '__main__':
    main()
