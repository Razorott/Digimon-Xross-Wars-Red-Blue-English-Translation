"""Exercise the recovery instructions; intercept the asynchronous reset API.

This is not a wireless test. Models callback completion separately from request.
"""
import json
import struct
import sys
from xros_text import ROOT, Rom, rom_paths
sys.path.insert(0, str(ROOT / '.tools/python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_ARM, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R9, UC_ARM_REG_LR, UC_ARM_REG_PC
from local_wireless_busy_recovery import (busy_recovery_overlay, BASE, DEBUG_START,
                                         DEBUG_END, COUNTER, GET_STATE,
                                         RESET_RADIO, BUSY_LIMIT, codeCompression)


def machine(binary):
    uc = Uc(UC_ARCH_ARM, UC_MODE_ARM)
    uc.mem_map(0x02000000, 0x400000)
    uc.mem_write(BASE, binary)
    uc.reg_write(UC_ARM_REG_R9, 0x02300000)
    runtime = {'wh': 3, 'resets': 0}
    def hook(m, address, size, _):
        if address == GET_STATE:
            m.reg_write(UC_ARM_REG_R0, runtime['wh'])
            m.reg_write(UC_ARM_REG_PC, m.reg_read(UC_ARM_REG_LR))
        elif address == RESET_RADIO:
            runtime['resets'] += 1
            m.reg_write(UC_ARM_REG_PC, m.reg_read(UC_ARM_REG_LR))
        elif address == DEBUG_END:
            m.emu_stop()
    uc.hook_add(UC_HOOK_CODE, hook)
    return uc, runtime


def main():
    results = []
    for version, path in rom_paths().items():
        packed, _ = busy_recovery_overlay(Rom(path))
        binary = codeCompression.decompress(packed)
        for state in range(15):
            for wh in range(11):
                uc, runtime = machine(binary)
                runtime['wh'] = wh
                uc.mem_write(0x02300020, struct.pack('<II', state, 0x12345678))
                uc.mem_write(COUNTER, struct.pack('<I', BUSY_LIMIT - 1))
                uc.emu_start(DEBUG_START, DEBUG_END + 4, count=100)
                assert runtime['resets'] == int(state == 13 and wh == 3)
                assert bytes(uc.mem_read(0x02300020, 8)) == struct.pack('<II', state, 0x12345678)
                counter = struct.unpack('<I', uc.mem_read(COUNTER, 4))[0]
                assert counter == (BUSY_LIMIT if state == 13 and wh == 3 else 0)
                results.append([version, state, wh])
        uc, runtime = machine(binary)
        uc.mem_write(0x02300020, struct.pack('<I', 13))
        for tick in range(BUSY_LIMIT * 3):
            uc.emu_start(DEBUG_START, DEBUG_END + 4, count=100)
            assert runtime['resets'] == int(tick >= BUSY_LIMIT - 1)
        # A subsequent IDLE callback clears the counter, allowing a future
        # independent disconnect to recover. A delayed callback is not forged.
        runtime['wh'] = 1
        uc.emu_start(DEBUG_START, DEBUG_END + 4, count=100)
        assert struct.unpack('<I', uc.mem_read(COUNTER, 4))[0] == 0
    output = ROOT / 'build/qa/local_wireless_session/busy_recovery_arm_test.json'
    output.write_text(json.dumps({'matrix_cases_passed': len(results),
        'scope': 'ARM instructions only; reset intercepted, radio untested',
        'sequences': '900 busy updates per edition: one reset, then simulated IDLE clears counter',
        'cases': results}, indent=2) + '\n')
    print(len(results), 'state matrix cases and both 900-update sequences passed')


if __name__ == '__main__':
    main()
