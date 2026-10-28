"""Check adapter ABI against the retail callback setter/getters in ARM946.

Native send/busy operations are intercepted. This is not a radio test; discovery,
connection, actual transmission, packet retries and disconnection are untested.
"""
import json
import struct
from xros_text import ROOT, Rom, u32
from build_native_integration_probe import compile_bridge
from test_wireless_coordinator_arm import Arm, BUFFER, PAYLOAD, VIEW
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_LR, UC_ARM_REG_PC
from xros_program import codeCompression

CONTEXT = 0x02320000
RECEIVE = 0x02321000
SESSION = 0x12345678


def main():
    directory = ROOT / 'build/experimental/native_transport_abi'
    directory.mkdir(parents=True, exist_ok=True)
    compile_bridge(directory, include_transport=True)
    arm = Arm(directory / 'game_bridge.elf', expected_symbols=None)
    rom = Rom(ROOT / 'build/Digimon_Super_Xros_Wars_Blue_English_batch124.nds')
    table = u32(rom.data, 0x50) + 64
    file_id = u32(rom.data, table + 24)
    start, end = struct.unpack_from('<II', rom.data, rom.fat_offset + file_id * 8)
    # The original native wrapper/getter/setter code runs unmodified. It also
    # restores the area where ELF page headers overlap the retail SDK address.
    arm.uc.mem_write(0x0221BF80, codeCompression.decompress(rom.data[start:end]))
    def write(address, value):
        arm.uc.mem_write(address, struct.pack('<I', value))
    def read(address):
        return struct.unpack('<I', arm.uc.mem_read(address, 4))[0]
    write(0x02223460, CONTEXT)
    write(0x02220A90, 0x02220A98)
    write(0x02220B80 + 0x4C, 4)
    write(0x02220B80 + 0x34, 0)
    write(CONTEXT + 0xC, RECEIVE)
    write(CONTEXT + 0x10, 8192)
    write(CONTEXT + 0x14, 0x02010000)
    write(CONTEXT + 0x18, 0xCAFE1234)
    runtime = {'busy': 0, 'send_result': 1, 'sent': []}
    def native_call(uc, address, size, userdata):
        if address == 0x0221E1D8:
            uc.reg_write(UC_ARM_REG_R0, runtime['busy'])
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
        elif address == 0x0221E190:
            tag = uc.reg_read(UC_ARM_REG_R0)
            pointer = uc.reg_read(UC_ARM_REG_R1)
            length = uc.reg_read(UC_ARM_REG_R2)
            runtime['sent'].append({'tag': tag, 'pointer': pointer,
                                    'bytes': bytes(uc.mem_read(pointer, length))})
            uc.reg_write(UC_ARM_REG_R0, runtime['send_result'])
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
    arm.uc.hook_add(UC_HOOK_CODE, native_call)
    call = arm.call
    assert call('xwb_transport_get_side') == 0
    write(0x02220B80 + 0x34, 1)
    assert call('xwb_transport_get_side') == 1
    write(0x02220B80 + 0x34, 0)
    assert call('xwb_transport_bind', 1, SESSION) == -5  # native role mismatch
    assert call('xwb_transport_bind', 0, 0) == -1
    assert call('xwb_transport_bind', 0, SESSION) == 0
    callback, user = read(CONTEXT + 0x14), read(CONTEXT + 0x18)
    assert callback != 0x02010000 and user != 0xCAFE1234
    arm.symbols['sdk_callback'] = callback
    assert call('xwb_transport_bind', 0, SESSION) == -7
    arm.uc.mem_write(PAYLOAD, b'formation')
    assert call('xwb_transport_send', 3, 7, PAYLOAD, 9) == 0
    sent = runtime['sent'][-1]
    assert sent['tag'] == 0x31425758 and len(sent['bytes']) == 33
    stable = bytes(arm.uc.mem_read(sent['pointer'], 96))
    runtime['busy'] = 1
    assert call('xwb_transport_send', 3, 8, PAYLOAD, 9) == -7
    assert len(runtime['sent']) == 1
    assert bytes(arm.uc.mem_read(sent['pointer'], 96)) == stable
    runtime['busy'] = 0
    # Simulate the retail callback's five-argument calling convention. The first
    # argument is native packet sequence, not a peer ID. Bind establishes role.
    for sequence in range(4):
        assert call('xwb_encode', BUFFER, 96, 3, 1, SESSION, sequence, PAYLOAD, 9) == 33
        call('sdk_callback', sequence, 0x31425758, BUFFER, 33, user)
    # A full ring reports an overflow rather than silently overwriting commands.
    call('sdk_callback', 4, 0x31425758, BUFFER, 33, user)
    assert call('xwb_transport_dropped') == 1
    assert call('xwb_transport_take', VIEW, 32) == -1
    for sequence in range(4):
        assert call('xwb_transport_take', VIEW, 96) == 33
        packet = bytes(arm.uc.mem_read(VIEW, 33))
        assert struct.unpack_from('<I', packet, 12)[0] == sequence
    assert call('xwb_transport_take', VIEW, 96) == -5
    # Valid CRC with an incorrect sender role is still rejected.
    assert call('xwb_encode', BUFFER, 96, 3, 0, SESSION, 9, PAYLOAD, 9) == 33
    call('sdk_callback', 9, 0x31425758, BUFFER, 33, user)
    assert call('xwb_transport_dropped') == 2
    assert call('xwb_transport_detach') == 0
    assert read(CONTEXT + 0x14) == 0x02010000 and read(CONTEXT + 0x18) == 0xCAFE1234
    assert call('xwb_transport_send', 3, 9, PAYLOAD, 9) == -5
    # The child may receive a host HELLO before learning the session nonce.
    write(0x02220B80 + 0x34, 1)
    assert call('xwb_transport_get_side') == 1
    assert call('xwb_transport_bind', 1, 0) == 0
    callback, user = read(CONTEXT + 0x14), read(CONTEXT + 0x18)
    arm.symbols['sdk_callback'] = callback
    assert call('xwb_transport_send', 1, 0, PAYLOAD, 9) == -5
    assert call('xwb_encode', BUFFER, 96, 1, 0, SESSION, 0, PAYLOAD, 9) == 33
    call('sdk_callback', 0, 0x31425758, BUFFER, 33, user)
    assert call('xwb_transport_take', VIEW, 96) == 33
    assert call('xwb_transport_set_session', SESSION) == 0
    assert call('xwb_transport_detach') == 0
    # Reused overlay addresses are rejected without invoking their functions.
    write(0x0221D4A8, 0xE59CC000)
    assert call('xwb_transport_bind', 1, SESSION) == -5
    result = {'status': 'Native callback setter/getter ABI checks passed on ARM946',
        'arm_function_calls': arm.calls,
        'scope': 'Retail getters/callback setter executed; send and busy APIs intercepted. No real radio transmission, discovery, retry or complete match test.'}
    (directory / 'test_report.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
