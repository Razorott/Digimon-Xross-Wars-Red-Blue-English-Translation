from pathlib import Path
import json
from xros_text import ROOT
from build_native_integration_probe import compile_bridge
from test_wireless_coordinator_arm import Arm, RETURN
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R4, UC_ARM_REG_R6, UC_ARM_REG_PC, UC_ARM_REG_LR, UC_ARM_REG_CPSR

OUT = ROOT / 'build/experimental/wireless_actor_scene_hook_arm'

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    compile_bridge(OUT, include_transport=True, extended_order=True, include_session=True)
    arm = Arm(OUT / 'game_bridge.elf', expected_symbols=None)
    calls = []
    resume = {}
    def route(uc, address, size, userdata):
        if address == arm.symbols['xwb_prepare_remote_actors']:
            calls.append('prepare')
            uc.reg_write(UC_ARM_REG_R0, 1)
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
        elif address == 0x022169F0:
            resume['scene_r6'] = uc.reg_read(UC_ARM_REG_R6)
            uc.reg_write(UC_ARM_REG_PC, RETURN)
        elif address == 0x02216A14:
            uc.reg_write(UC_ARM_REG_PC, RETURN)
    arm.uc.hook_add(UC_HOOK_CODE, route)

    assert arm.call('xwb_prepare_remote_setup_hook') == 0
    assert calls == ['prepare']
    assert resume['scene_r6'] == arm.symbols['xwb_actor_storage']

    phase = arm.symbols['xwb_live_match'] + 39
    ready = arm.symbols['xwb_remote_actors_ready']
    def check_limit(battle, is_ready, index, expected_carry):
        arm.uc.mem_write(phase, bytes([2 if battle else 1]))
        arm.uc.mem_write(ready, int(is_ready).to_bytes(4, 'little'))
        arm.uc.reg_write(UC_ARM_REG_R4, index)
        arm.call('xwb_actor_setup_limit_hook')
        carry = (arm.uc.reg_read(UC_ARM_REG_CPSR) >> 29) & 1
        assert carry == expected_carry, (battle, is_ready, index, carry)
    check_limit(True, True, 11, 0)  # cmp 11,12: continue
    check_limit(True, False, 10, 1) # cmp 10,9: stop
    check_limit(False, True, 10, 1) # stale readiness cannot extend ordinary scenes

    report = {
        'status': 'ARM946 remote scene hook checks passed',
        'checks': [
            'remote actor preparation runs before per-actor finalization',
            'displaced actor base load is replayed before retail resume',
            'twelve actor records are allowed only after successful preparation during battle',
            'ordinary scenes keep a nine actor limit even with stale readiness',
        ],
        'limitation': 'Hook ABI only; no scene renderer, live Link Box, or wireless match executed.',
    }
    (OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()

