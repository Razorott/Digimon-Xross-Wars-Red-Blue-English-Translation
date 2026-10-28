"""Differentially exercise the relocated retail order code on ARM946.

Executes original software float/memcpy routines, not Python replacements.
This tests ordering capacity only, not twelve-actor game UI or radio play.
"""
import json
import random
import struct
from xros_text import ROOT, Rom, u32
from xros_program import codeCompression
from build_native_integration_probe import compile_bridge, MODULE_BASE
from relocate_battle_actors import relocate_battle_actors, ORIGINAL_ACTORS
from extend_native_turn_order import transplant, ENTRIES
from test_wireless_coordinator_arm import Arm, RETURN, STACK
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R4,
    UC_ARM_REG_R5, UC_ARM_REG_R6, UC_ARM_REG_R7, UC_ARM_REG_R8, UC_ARM_REG_R9,
    UC_ARM_REG_R10, UC_ARM_REG_R11, UC_ARM_REG_R12, UC_ARM_REG_PC,
    UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_CPSR)

CONTEXT = 0x02310000


def main():
    directory = ROOT / 'build/experimental/native_turn_order_abi'
    directory.mkdir(parents=True, exist_ok=True)
    module, _, symbols = compile_bridge(directory, extended_order=True)
    rom = Rom(ROOT / 'build/Digimon_Super_Xros_Wars_Blue_English_batch124.nds')
    row = u32(rom.data, 0x50)
    file_id = u32(rom.data, row + 24)
    start, end = struct.unpack_from('<II', rom.data, rom.fat_offset + file_id * 8)
    original = codeCompression.decompress(rom.data[start:end])
    relocated, _ = relocate_battle_actors(rom, symbols['xwb_actor_storage'])
    overlay, installed, report = transplant(codeCompression.decompress(relocated),
        0x021F3D20, module, MODULE_BASE, symbols)
    arm9_start, _, arm9_ram, arm9_size = struct.unpack_from('<4I', rom.data, 0x20)
    arm9 = codeCompression.decompress(rom.data[arm9_start:arm9_start + arm9_size])
    baseline = Arm(directory / 'game_bridge.elf', expected_symbols=None)
    changed = Arm(directory / 'game_bridge.elf', expected_symbols=None)
    for machine, data in ((baseline, original), (changed, overlay)):
        machine.uc.mem_write(arm9_ram, arm9)
        machine.uc.mem_write(0x021F3D20, data)
        for name, address in zip(('build_order', 'current', 'advance', 'at_end'), ENTRIES):
            machine.symbols[name] = address
    changed.uc.mem_write(MODULE_BASE, installed)
    def original_context(uc, address, size, userdata):
        if address == 0x021F7B30:
            uc.reg_write(UC_ARM_REG_R0, CONTEXT)
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
    baseline.uc.hook_add(UC_HOOK_CODE, original_context)
    native_input = {'selection': 0, 'pressed': 1, 'opened': []}
    def menu_calls(uc, address, size, userdata):
        if address == 0x02205354:
            native_input['opened'].append((uc.reg_read(UC_ARM_REG_R0), uc.reg_read(UC_ARM_REG_R1)))
        elif address == 0x022054EC:
            uc.reg_write(UC_ARM_REG_R0, native_input['selection'] & 0xFFFFFFFF)
        elif address == 0x022123B8:
            uc.reg_write(UC_ARM_REG_R0, native_input['pressed'])
        else:
            return
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
    changed.uc.hook_add(UC_HOOK_CODE, menu_calls)
    for phase in (1, 2, 3, 4):
        changed.uc.mem_write(symbols['xwb_live_match'] + 39, bytes([phase]))
        changed.call('xwb_ring_open', 0x1F, 2)
        assert native_input['opened'][-1] == ((0xE, 0x13) if phase == 2 else (0x1F, 2))
        for selection in (-2, -1, 0, 1, 2, 3, 4):
            native_input['selection'] = selection
            assert changed.call('xwb_ring_selection') == (-1 if phase == 2 and selection in (0, 4) else selection)
        assert changed.call('xwb_all_tactics_pressed') == (0 if phase == 2 else 1)
    rng = random.Random(124)
    cases = []

    def actors(count):
        data = bytearray(12 * 0x1A0)
        for index in range(12):
            offset = index * 0x1A0
            struct.pack_into('<h', data, offset + 0x14, index if index < count else -1)
            struct.pack_into('<f', data, offset + 0x90, rng.uniform(1, 999))
            struct.pack_into('<I', data, offset + 0xE4, rng.choice((0, 1, 100, 999)))
            struct.pack_into('<bb', data, offset + 0xEE, rng.randrange(6), rng.randrange(1, 100))
            data[offset + 0xF1] = rng.choice((0, 0, 0, 5))
            struct.pack_into('<h', data, offset + 0x148, rng.randrange(4))
        return data

    def read_entries(machine, context, count):
        return bytes(machine.uc.mem_read(context + 0x924, count * 8))

    for case in range(160):
        count = case % 10
        data = actors(count)
        baseline.uc.mem_write(ORIGINAL_ACTORS, bytes(data[:9 * 0x1A0]))
        changed.uc.mem_write(symbols['xwb_actor_storage'], bytes(data))
        # Canaries around private array and its adjacent globals.
        order_context = symbols['xwb_order_context']
        changed.uc.mem_write(order_context, b'\xa5' * 0x990)
        changed.uc.mem_write(symbols['xwb_live_match'] + 39, b'\x01')
        baseline.call('build_order')
        changed.call('build_order')
        assert read_entries(baseline, CONTEXT, 10) == read_entries(changed, order_context, 10)
        assert changed.uc.mem_read(order_context, 0x924) == b'\xa5' * 0x924
        assert changed.uc.mem_read(order_context + 0x98E, 2) == b'\xa5\xa5'
        for _ in range(11):
            current = baseline.call('current')
            assert changed.call('current') == current
            assert changed.call('at_end') == baseline.call('at_end')
            if current < 0:
                break
            assert changed.call('advance') == baseline.call('advance')
        else:
            raise AssertionError('missing normal battle sentinel')
        cases.append({'case': case, 'actors': count, 'normal_equivalence': True})

    for case in range(80):
        data = actors(12)
        # Include all twelve in order, allow dead actors to test advance skipping.
        for index in range(12):
            data[index * 0x1A0 + 0xF1] = 0
        changed.uc.mem_write(symbols['xwb_actor_storage'], bytes(data))
        changed.uc.mem_write(symbols['xwb_live_match'] + 39, b'\x02')
        changed.call('build_order')
        entries = read_entries(changed, order_context, 13)
        indexes = [struct.unpack_from('<i', entries, i * 8 + 4)[0] for i in range(13)]
        assert sorted(indexes[:12]) == list(range(12)) and indexes[12] == -1
        # Current first may be dead: this is the original caller's contract.
        visited = []
        for _ in range(13):
            current = changed.call('current')
            if current < 0:
                assert changed.call('at_end') == 1
                break
            assert 0 <= current < 12 and current not in visited
            visited.append(current)
            changed.call('advance')
        else:
            raise AssertionError('missing twelve-actor sentinel')
        expected = [i for i in indexes[:12] if struct.unpack_from('<I', data, i * 0x1A0 + 0xE4)[0]]
        if indexes[0] not in expected:
            expected.insert(0, indexes[0])
        assert visited == expected

    # Exercise the session-enabled battle input wrapper itself. In wireless
    # phase it must tick the native session and suppress Tactics; in a normal
    # battle it must leave session transport untouched and preserve retail.
    session_dir = directory / 'session_tick'
    session_dir.mkdir(parents=True, exist_ok=True)
    _, _, session_symbols = compile_bridge(session_dir, include_transport=True,
        extended_order=True, include_session=True)
    session_arm = Arm(session_dir / 'game_bridge.elf', expected_symbols=None)
    tick_calls = []
    retail_calls = []
    def input_tick_calls(uc, address, size, userdata):
        if address == session_symbols['xwb_session_frame_tick']:
            tick_calls.append(address)
            uc.reg_write(UC_ARM_REG_R0, 0)
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
        elif address == 0x022123B8:
            retail_calls.append(address)
            uc.reg_write(UC_ARM_REG_R0, 1)
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
    session_arm.uc.hook_add(UC_HOOK_CODE, input_tick_calls)
    session_arm.uc.mem_write(session_symbols['xwb_live_match'] + 39, b'\x02')
    assert session_arm.call('xwb_all_tactics_pressed') == 0
    assert len(tick_calls) == 1 and not retail_calls
    session_arm.uc.mem_write(session_symbols['xwb_live_match'] + 39, b'\x01')
    assert session_arm.call('xwb_all_tactics_pressed') == 1
    assert len(tick_calls) == 1 and len(retail_calls) == 1

    # The actor loop may install the exchanged roster only at slot6, and a
    # stale ready flag must never leave twelve actors enabled outside battle.
    actor_hook_calls = []
    def prepare_actors(uc, address, size, userdata):
        if address == session_symbols['xwb_prepare_remote_actors']:
            actor_hook_calls.append(address)
            uc.mem_write(session_symbols['xwb_remote_actors_ready'], b'\x01\x00\x00\x00')
            uc.reg_write(UC_ARM_REG_R0, 1)
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
    session_arm.uc.hook_add(UC_HOOK_CODE, prepare_actors)
    ready = session_symbols['xwb_remote_actors_ready']
    live_phase = session_symbols['xwb_live_match'] + 39
    session_arm.uc.mem_write(ready, b'\x00\x00\x00\x00')
    session_arm.uc.mem_write(live_phase, b'\x01')
    session_arm.uc.reg_write(UC_ARM_REG_R8, 11)
    session_arm.call('xwb_order_compare_actor')
    assert not actor_hook_calls
    assert session_arm.uc.reg_read(UC_ARM_REG_CPSR) & (1 << 29)
    session_arm.uc.mem_write(live_phase, b'\x02')
    session_arm.uc.mem_write(ready, b'\x00\x00\x00\x00')
    session_arm.uc.reg_write(UC_ARM_REG_R8, 5)
    session_arm.call('xwb_order_compare_actor')
    assert not actor_hook_calls
    session_arm.uc.reg_write(UC_ARM_REG_R8, 6)
    session_arm.call('xwb_order_compare_actor')
    assert len(actor_hook_calls) == 1
    session_arm.uc.reg_write(UC_ARM_REG_R8, 10)
    session_arm.call('xwb_order_compare_actor')
    assert not session_arm.uc.reg_read(UC_ARM_REG_CPSR) & (1 << 29)
    session_arm.uc.mem_write(live_phase, b'\x01')
    session_arm.uc.reg_write(UC_ARM_REG_R8, 11)
    session_arm.call('xwb_order_compare_actor')
    assert session_arm.uc.reg_read(UC_ARM_REG_CPSR) & (1 << 29)

    preserved = (UC_ARM_REG_R4, UC_ARM_REG_R5, UC_ARM_REG_R6, UC_ARM_REG_R7,
        UC_ARM_REG_R8, UC_ARM_REG_R9, UC_ARM_REG_R10, UC_ARM_REG_R11, UC_ARM_REG_R12)
    expected_registers = [0x14444444 + index * 0x01010101 for index in range(len(preserved))]
    for register, value in zip(preserved, expected_registers):
        session_arm.uc.reg_write(register, value)
    tick_calls.clear()
    resume_state = {}
    def parent_resume(uc, address, size, userdata):
        if address == 0x020D4BAC:
            resume_state['registers'] = [uc.reg_read(register) for register in preserved]
            resume_state['sp'] = uc.reg_read(UC_ARM_REG_SP)
            resume_state['stack'] = bytes(uc.mem_read(resume_state['sp'], 28))
            uc.reg_write(UC_ARM_REG_PC, RETURN)
    session_arm.uc.hook_add(UC_HOOK_CODE, parent_resume)
    assert session_arm.call('xwb_linkbox_pump_hook') == 0
    assert len(tick_calls) == 1
    assert resume_state['registers'] == expected_registers
    assert resume_state['sp'] == STACK - 28
    assert struct.unpack('<7I', resume_state['stack']) == tuple(expected_registers[:5] + [expected_registers[5], RETURN])

    result = {'status': 'passed', 'normal_differential_cases': len(cases),
        'twelve_actor_cases': 80, 'compiled_calls': baseline.calls + changed.calls,
        'retail_float_and_memcpy_executed': True, 'transplant': report,
        'wireless_tactics_and_items_input_gates': 'passed; SDK input calls intercepted',
        'remote_actor_hook': 'prepares exactly at actor6 during battle; stale ready flag keeps ordinary limit9',
        'battle_session_tick': 'called once in wireless phase; not called in ordinary battle',
        'linkbox_parent_pump_hook': 'called once; preserves registers and replays the retail parent prologue before resume',
        'limitations': 'No twelve-actor UI, complete battle, wireless transmission or console verification.'}
    (directory / 'test_report.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items() if key != 'transplant'}, indent=2))


if __name__ == '__main__':
    main()
