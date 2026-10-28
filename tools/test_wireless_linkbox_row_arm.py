"""Check the experimental fifth Link Box row against the retail UI ABI.

The test stubs the three existing text/draw functions and runs the production
helper on ARM946. It does not install the helper in ARM9 or test the rendered
menu in-game.
"""
import hashlib
import json
import struct
import subprocess
from test_wireless_coordinator_arm import Arm
from xros_text import ROOT
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_CPSR, UC_ARM_REG_LR, UC_ARM_REG_PC,
    UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3,
    UC_ARM_REG_R4, UC_ARM_REG_R5, UC_ARM_REG_R6, UC_ARM_REG_R7,
    UC_ARM_REG_R8, UC_ARM_REG_R9, UC_ARM_REG_R10, UC_ARM_REG_R11,
    UC_ARM_REG_R12, UC_ARM_REG_SP)

OUT = ROOT / 'build/experimental/wireless_linkbox_row_arm'
TEXT, DRAW, FINISH = 0x02001000, 0x02001020, 0x02001040
OWNER, ROWS, TEXT_OBJECT = 0x02080000, 0x02090000, 0x020A0000
HOOK_STACK, CONFIG, RESUME = 0x023E0000, 0x020B0000, 0x020D4420


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    zig = ROOT / '.tools/ziglang/ziglang/zig.exe'
    objects = []
    for source, name, defines in (
        ('native/wireless_linkbox.c', 'linkbox', [
            f'-DXWB_UI_TEXT_FN={TEXT:#x}u', f'-DXWB_UI_DRAW_FN={DRAW:#x}u',
            f'-DXWB_UI_FINISH_FN={FINISH:#x}u']),
        ('native/wireless_linkbox_test.c', 'test', []),
    ):
        obj = OUT / f'{name}.o'
        subprocess.run([str(zig), 'cc', '-target', 'arm-freestanding-eabi',
            '-mcpu=arm946e_s', '-marm', '-ffreestanding', '-fno-builtin',
            '-fno-stack-protector', '-fno-unwind-tables',
            '-fno-asynchronous-unwind-tables', '-Os', '-Wall', '-Wextra',
            '-Werror', *defines, '-c', str(ROOT / source), '-o', str(obj)],
            check=True, cwd=ROOT)
        objects.append(obj)
    elf = OUT / 'linkbox_row.elf'
    subprocess.run([str(zig), 'build-exe', *(str(obj) for obj in objects),
        '-target', 'arm-freestanding-eabi', '-mcpu', 'arm946e_s',
        '-O', 'ReleaseSmall', '-fno-compiler-rt', '-fno-entry',
        '--no-gc-sections', '-fno-strip', '--script',
        str(ROOT / 'native/wireless_linkbox_test.ld'),
        '-femit-bin=' + str(elf)], check=True, cwd=ROOT)
    return elf


def main():
    elf = build()
    arm = Arm(elf, expected_symbols=None)
    owner_symbol = arm.symbols['xwb_test_owner']
    arm.uc.mem_write(owner_symbol + 0x2c, struct.pack('<I', ROWS))
    arm.uc.mem_write(ROWS, b'\xA5' * 0x190)
    for address in (TEXT, DRAW, FINISH):
        arm.uc.mem_write(address, struct.pack('<I', 0xE12FFF1E))  # bx lr

    calls = []
    def mock_calls(uc, address, _size, _user):
        if address == TEXT:
            calls.append(('text', uc.reg_read(UC_ARM_REG_R0),
                          uc.reg_read(UC_ARM_REG_R1)))
            uc.reg_write(UC_ARM_REG_R0, TEXT_OBJECT)
        elif address == DRAW:
            sp = uc.reg_read(UC_ARM_REG_SP)
            extra = struct.unpack('<2I', uc.mem_read(sp, 8))
            calls.append(('draw', uc.reg_read(UC_ARM_REG_R0),
                          uc.reg_read(UC_ARM_REG_R1),
                          uc.reg_read(UC_ARM_REG_R2),
                          uc.reg_read(UC_ARM_REG_R3), *extra))
        elif address == FINISH:
            calls.append(('finish', uc.reg_read(UC_ARM_REG_R0)))

    arm.uc.hook_add(UC_HOOK_CODE, mock_calls)
    assert arm.call('xwb_test_main') == 0
    expected = [
        ('text', 21, 106),
        ('draw', ROWS + 0x140, 0, 0, 0, 3, TEXT_OBJECT),
        ('finish', ROWS + 0x140),
    ]
    assert calls == expected, calls
    assert bytes(arm.uc.mem_read(ROWS, 0x190)) == b'\xA5' * 0x190

    # Exercise the new protocol-backed lobby flow: connection completion opens
    # the lobby, formation edits alter a six-position permutation, the host
    # cycles music and readiness, and Start advances the session to battle.
    match = bytearray(44)
    struct.pack_into('<6I', match, 0, 0x31425758, 0x1234, 1, 1, 0, 0)
    match[24:36] = bytes((0, 1, 2, 3, 4, 5, 0, 1, 2, 3, 4, 5))
    match[36:44] = bytes((3, 3, 0, 1, 0, 0, 0, 0))
    arm.uc.mem_write(arm.symbols['xwb_test_match'], bytes(match))
    for symbol, value in (
        ('xwb_test_session_state', 3), ('xwb_test_side', 0),
        ('xwb_test_start_count', 0), ('xwb_test_end_count', 0),
        ('xwb_test_music_count', 0), ('xwb_test_ready_count', 0),
        ('xwb_test_formation_count', 0),
    ):
        arm.uc.mem_write(arm.symbols[symbol], struct.pack('<I', value))
    root = arm.symbols['xwb_test_root']
    arm.uc.mem_write(root + 0x20, struct.pack('<I', 0x7D0))
    arm.uc.mem_write(root + 0x54, struct.pack('<I', ROWS))
    calls.clear()
    assert arm.call('xwb_test_update_ui') == 0
    assert ('text', 21, 108) in calls
    drawn = len(calls)
    assert arm.call('xwb_test_update_ui') == 0
    assert len(calls) == drawn, 'stable lobby must not redraw its row objects every frame'
    arm.uc.mem_write(root + 0x20, struct.pack('<I', 0x3E8))
    assert arm.call('xwb_test_update_ui') == 0
    assert len(calls) == drawn, 'non-menu parent state must not touch borrowed child rows'
    arm.uc.mem_write(root + 0x20, struct.pack('<I', 0x7D0))
    assert arm.call('xwb_test_update_ui') == 0
    assert len(calls) > drawn, 'returning to the action menu must redraw its current state'
    calls.clear()
    assert arm.call('xwb_test_dispatch', 4) == 1  # Open lobby.
    assert ('text', 21, 109) in calls and ('text', 21, 110) in calls
    assert ('text', 21, 140) in calls  # Neither player is ready yet.
    assert arm.call('xwb_test_dispatch', 0) == 1  # Open formation editor.
    assert arm.call('xwb_test_dispatch', 1) == 1  # Swap V1/V2.
    positions = bytes(arm.uc.mem_read(arm.symbols['xwb_test_match'] + 24, 6))
    assert positions == bytes((1, 0, 2, 3, 4, 5)), positions
    assert struct.unpack('<I', arm.uc.mem_read(arm.symbols['xwb_test_formation_count'], 4))[0] == 1
    assert arm.call('xwb_test_dispatch', 4) == 1  # Done.
    assert arm.call('xwb_test_dispatch', 1) == 1  # Host selects next theme.
    assert arm.uc.mem_read(arm.symbols['xwb_test_match'] + 40, 1) == b'\x01'
    assert arm.call('xwb_test_dispatch', 2) == 1  # Ready.
    assert arm.uc.mem_read(arm.symbols['xwb_test_match'] + 38, 1) == b'\x01'
    assert ('text', 21, 129) in calls  # Host ready.
    arm.uc.mem_write(arm.symbols['xwb_test_match'] + 38, b'\x03')
    assert arm.call('xwb_test_update_ui') == 0
    assert ('text', 21, 141) in calls  # Both players ready.
    assert arm.call('xwb_test_dispatch', 3) == 1  # Start packet.
    assert struct.unpack('<I', arm.uc.mem_read(arm.symbols['xwb_test_session_state'], 4))[0] == 4
    assert arm.call('xwb_test_dispatch', 4) == 1  # Leave armed panel.
    assert struct.unpack('<I', arm.uc.mem_read(arm.symbols['xwb_test_end_count'], 4))[0] == 1
    arm.uc.mem_write(arm.symbols['xwb_test_session_state'], struct.pack('<I', 3))
    arm.uc.mem_write(arm.symbols['xwb_test_side'], struct.pack('<I', 1))
    arm.uc.mem_write(arm.symbols['xwb_test_match'] + 36, b'\x03')
    assert arm.call('xwb_test_dispatch', 4) == 1  # Reopen as guest.
    assert arm.call('xwb_test_dispatch', 1) == 1  # Guest cannot change theme.
    assert struct.unpack('<I', arm.uc.mem_read(arm.symbols['xwb_test_music_count'], 4))[0] == 1
    assert arm.call('xwb_test_dispatch', 3) == 1  # Guest cannot send START.
    assert struct.unpack('<I', arm.uc.mem_read(arm.symbols['xwb_test_start_count'], 4))[0] == 1
    assert ('text', 21, 142) in calls  # The guest waits for the host.
    assert arm.call('xwb_test_dispatch', 4) == 1

    # Execute the actual naked trampoline called from the ARM9 constructor.
    # It must preserve the constructor's register state, draw row five, replay
    # the displaced config-copy instructions and resume at the retail address.
    config = (0x11112222, 0x33334444, 0x55556666, 0x77778888)
    arm.uc.mem_write(0x020D4454, struct.pack('<I', CONFIG))
    arm.uc.mem_write(CONFIG, struct.pack('<4I', *config))
    seed = {
        UC_ARM_REG_R0: 0x10101010, UC_ARM_REG_R1: 0x11111111,
        UC_ARM_REG_R2: 0x12121212, UC_ARM_REG_R3: 0x13131313,
        UC_ARM_REG_R4: 0x14141414, UC_ARM_REG_R5: 0x15151515,
        UC_ARM_REG_R6: 0x16161616, UC_ARM_REG_R7: 0x17171717,
        UC_ARM_REG_R8: owner_symbol, UC_ARM_REG_R9: 0x19191919,
        UC_ARM_REG_R10: 0x20202020, UC_ARM_REG_R11: 0x21212121,
        UC_ARM_REG_R12: 0x22222222, UC_ARM_REG_SP: HOOK_STACK,
        UC_ARM_REG_LR: 0x023FF000, UC_ARM_REG_CPSR: 0xD3,
    }
    for register, value in seed.items():
        arm.uc.reg_write(register, value)
    calls.clear()
    arm.uc.emu_start(arm.symbols['xwb_linkbox_render_battle_row_hook'], RESUME,
                     count=20000)
    assert arm.uc.reg_read(UC_ARM_REG_PC) == RESUME, ('renderer hook did not resume the retail constructor: '
                            f'pc={arm.uc.reg_read(UC_ARM_REG_PC):#x} calls={calls}')
    regs = [UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3]
    assert tuple(arm.uc.reg_read(reg) for reg in regs) == config
    for register in (UC_ARM_REG_R4, UC_ARM_REG_R5, UC_ARM_REG_R7,
                     UC_ARM_REG_R8, UC_ARM_REG_R9, UC_ARM_REG_R10,
                     UC_ARM_REG_R11, UC_ARM_REG_R12):
        assert arm.uc.reg_read(register) == seed[register], hex(register)
    assert arm.uc.reg_read(UC_ARM_REG_SP) == HOOK_STACK
    assert arm.uc.reg_read(UC_ARM_REG_LR) == seed[UC_ARM_REG_LR]
    assert arm.uc.reg_read(UC_ARM_REG_R6) == HOOK_STACK + 8
    assert bytes(arm.uc.mem_read(HOOK_STACK + 8, 16)) == struct.pack('<4I', *config)
    assert calls == expected, calls

    # Exercise the retail handler's five-way result adapter and the two
    # modulo-five keyboard hooks with exact ARM register-state assertions.
    context = OWNER + 0x100
    arm.uc.mem_write(context + 0x34, struct.pack('<I', 4))
    arm.uc.reg_write(UC_ARM_REG_R4, context)
    arm.uc.reg_write(UC_ARM_REG_R5, 0)
    arm.uc.reg_write(UC_ARM_REG_R6, 0)
    arm.uc.reg_write(UC_ARM_REG_R7, 1)
    arm.uc.reg_write(UC_ARM_REG_R9, 2)
    arm.uc.reg_write(UC_ARM_REG_R0, 4)
    arm.uc.emu_start(arm.symbols['xwb_linkbox_five_choice_result_hook'],
                     0x020D469C, count=1000)
    assert arm.uc.reg_read(UC_ARM_REG_PC) == 0x020D469C
    assert arm.uc.reg_read(UC_ARM_REG_R9) == 4
    assert arm.uc.reg_read(UC_ARM_REG_R5) == 1  # Selecting current action confirms it.

    arm.uc.mem_write(context + 0x34, struct.pack('<I', 3))
    arm.uc.reg_write(UC_ARM_REG_R6, 0)
    arm.uc.reg_write(UC_ARM_REG_R9, 3)
    arm.uc.reg_write(UC_ARM_REG_R0, 5)
    arm.uc.emu_start(arm.symbols['xwb_linkbox_five_choice_result_hook'],
                     0x020D469C, count=1000)
    assert arm.uc.reg_read(UC_ARM_REG_R6) == 1  # Back is now result 5.
    assert arm.uc.reg_read(UC_ARM_REG_R9) == 3

    for hook, start, expected_selection, resume in (
        ('xwb_linkbox_five_choice_up_hook', 0, 4, 0x020D4740),
        ('xwb_linkbox_five_choice_up_hook', 3, 2, 0x020D4740),
        ('xwb_linkbox_five_choice_down_hook', 4, 0, 0x020D4788),
        ('xwb_linkbox_five_choice_down_hook', 3, 4, 0x020D4788),
    ):
        arm.uc.reg_write(UC_ARM_REG_R0, 1)
        arm.uc.reg_write(UC_ARM_REG_R9, start)
        arm.uc.emu_start(arm.symbols[hook], resume, count=1000)
        assert arm.uc.reg_read(UC_ARM_REG_PC) == resume
        assert arm.uc.reg_read(UC_ARM_REG_R9) == expected_selection

    arm.uc.mem_write(context + 0x34, struct.pack('<I', 4))
    arm.uc.reg_write(UC_ARM_REG_R4, context)
    arm.uc.emu_start(arm.symbols['xwb_linkbox_battle_dispatch_hook'],
                     0x020D49FC, count=1000)
    assert arm.uc.reg_read(UC_ARM_REG_PC) == 0x020D49FC
    assert struct.unpack('<I', arm.uc.mem_read(context + 0x1c, 4))[0] == 0x7D0
    assert struct.unpack('<I', arm.uc.mem_read(context + 0x38, 4))[0] == 0x15
    request_count = arm.symbols['xwb_test_request_count']
    assert struct.unpack('<I', arm.uc.mem_read(request_count, 4))[0] == 1

    report = {
        'status': 'ARM946 checks pass for row rendering, parent-state UI lifetime/cache, lobby open, formation-pair edits, host music/readiness/start dispatch, leave action, five-choice cursor/back mapping, modulo-five navigation, and retail connection prompt routing.',
        'calls': [list(call) for call in calls],
        'row_stride': 0x50, 'row_index': 4, 'message_entry': 21,
        'message_id': 106, 'lobby_messages': '108-142',
        'limitations': 'Hooks are tested in isolation and statically installed in experimental TEST ROMs. Start advances the wireless protocol but does not launch or synchronize the game battle engine. Runtime confirmation of connection, lobby rendering, and a complete two-system match is still pending.',
        'elf_sha256': hashlib.sha256(elf.read_bytes()).hexdigest(),
    }
    (OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
