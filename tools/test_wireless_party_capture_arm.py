"""Test safe six-member capture from the game's current formation IDs.

Runs the freestanding extractor on ARM946. When the Blue/Red QA RAM dumps are
present, it also validates both real saved-party layouts from formation-screen
states. No cartridge saves or ROM data are written.
"""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

from xros_text import ROOT
from test_wireless_coordinator_arm import Arm

OUT = ROOT / 'build/experimental/wireless_party_capture_arm'
RECORDS = 0x02080000
ORDER = 0x02084000
OUTPUT = 0x02085000
RECORD_SIZE = 0x80
RECORD_COUNT = 108
ORDER_ADDRESS = 0x021F2EF4
RECORD_ADDRESS = 0x021F0700
FORMATION_IDS = [5, 11, 38, 34, 40, 43, 7, 16, 22]
SAMPLE_DUMPS = {
    'Blue': ROOT / 'build/qa/party_formation_trace/formation_fixed.bin',
    'Blue after a formation swap': ROOT / 'build/qa/party_formation_trace/formation_after_swap.bin',
    'Red': ROOT / 'build/qa/party_formation_trace/red_formation.bin',
}


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    zig = ROOT / '.tools/ziglang/ziglang/zig.exe'
    obj, elf = OUT / 'party.o', OUT / 'party.elf'
    subprocess.run([str(zig), 'cc', '-target', 'arm-freestanding-eabi',
        '-mcpu=arm946e_s', '-marm', '-ffreestanding', '-fno-builtin',
        '-fno-stack-protector', '-fno-unwind-tables', '-fno-asynchronous-unwind-tables',
        '-Os', '-Wall', '-Wextra', '-Werror', '-c', str(ROOT / 'native/wireless_party.c'),
        '-o', str(obj)], check=True, cwd=ROOT)
    subprocess.run([str(zig), 'build-exe', str(obj), '-target', 'arm-freestanding-eabi',
        '-mcpu', 'arm946e_s', '-O', 'ReleaseSmall', '-fno-compiler-rt', '-fno-entry',
        '--no-gc-sections', '-fno-strip', '--script', str(ROOT / 'native/wireless_party_capture_test.ld'),
        '-femit-bin=' + str(elf)], check=True, cwd=ROOT)
    return elf


def valid_record(record):
    species = struct.unpack_from('<H', record, 0x12)[0]
    hp, max_hp, mp, max_mp = struct.unpack_from('<4H', record, 0x1E)
    name = record[:18]
    i = length = 0
    while i < 18 and name[i]:
        char = name[i]
        i += 1
        if 0x20 <= char <= 0x7E:
            length += 1
        elif 0x81 <= char <= 0x9F or 0xE0 <= char <= 0xFC:
            if i >= 18 or not (0x40 <= name[i] <= 0xFC) or name[i] == 0x7F:
                return False
            i += 1
            length += 2
        else:
            return False
    return bool(length and 0 < species <= 0x7FF and max_hp and max_mp and
                hp <= max_hp and mp <= max_mp)


def expected_party(records, ids):
    result = []
    for uid in ids:
        matches = [records[i * RECORD_SIZE:(i + 1) * RECORD_SIZE]
                   for i in range(RECORD_COUNT)
                   if struct.unpack_from('<I', records, i * RECORD_SIZE + 0x74)[0] == uid
                   and valid_record(records[i * RECORD_SIZE:(i + 1) * RECORD_SIZE])]
        assert len(matches) == 1, (uid, len(matches))
        result.extend(matches[0])
    return bytes(result)


def capture(arm, records, ids):
    order = bytearray(9 * 8)
    for i, uid in enumerate(ids):
        struct.pack_into('<I', order, i * 8, uid)
    arm.uc.mem_write(RECORDS, records)
    arm.uc.mem_write(ORDER, bytes(order))
    arm.uc.mem_write(OUTPUT, b'\xA5' * 768)
    status = arm.call('xwb_capture_formation_party', RECORDS, RECORD_COUNT, ORDER, OUTPUT)
    return status, bytes(arm.uc.mem_read(OUTPUT, 768)), bytes(order)


def main():
    elf = build()
    arm = Arm(elf, expected_symbols=None)
    checks = 0

    # Synthetic, deterministic edge case: nine different saved records with
    # their stable IDs, deliberately scattered through the record pool.
    records = bytearray(RECORD_COUNT * RECORD_SIZE)
    slots = [3, 7, 8, 16, 18, 6, 5, 10, 13]
    for i, (slot, uid) in enumerate(zip(slots, FORMATION_IDS)):
        off = slot * RECORD_SIZE
        records[off:off + 6] = f'Digi{i:02d}'.encode('ascii')
        struct.pack_into('<H', records, off + 0x12, 100 + i)
        struct.pack_into('<4H', records, off + 0x1E, 90 + i, 100 + i, 40 + i, 50 + i)
        struct.pack_into('<I', records, off + 0x74, uid)
    status, got, order = capture(arm, bytes(records), FORMATION_IDS)
    assert status == 0 and got == expected_party(bytes(records), FORMATION_IDS[:6])
    assert arm.call('xwb_validate_party_records', OUTPUT) == 0
    assert [struct.unpack_from('<I', order, i * 8)[0] for i in range(9)] == FORMATION_IDS
    assert bytes(arm.uc.mem_read(RECORDS, len(records))) == bytes(records)
    checks += 1

    # Failure paths cannot leave a partial/usable party in the caller buffer.
    for bad_ids in ([FORMATION_IDS[0]] * 6, [9999] + FORMATION_IDS[1:6]):
        _, _, _ = capture(arm, bytes(records), bad_ids)
        # Rewrite the first six order IDs for this negative case.
        order = bytearray(9 * 8)
        for i, uid in enumerate(bad_ids): struct.pack_into('<I', order, i * 8, uid)
        arm.uc.mem_write(ORDER, bytes(order))
        arm.uc.mem_write(OUTPUT, b'\xA5' * 768)
        assert arm.call('xwb_capture_formation_party', RECORDS, RECORD_COUNT, ORDER, OUTPUT) == -1
        assert bytes(arm.uc.mem_read(OUTPUT, 768)) == b'\xA5' * 768
        checks += 1

    # A malformed or duplicated received team is rejected before it can enter
    # the synchronized lobby. Validation never mutates the transfer buffer.
    malformed = bytearray(expected_party(bytes(records), FORMATION_IDS[:6]))
    malformed[0x12:0x14] = b'\0\0'
    arm.uc.mem_write(OUTPUT, bytes(malformed))
    assert arm.call('xwb_validate_party_records', OUTPUT) == -1
    assert bytes(arm.uc.mem_read(OUTPUT, 768)) == bytes(malformed)
    checks += 1
    duplicated = bytearray(expected_party(bytes(records), FORMATION_IDS[:6]))
    duplicated[5 * RECORD_SIZE + 0x74:5 * RECORD_SIZE + 0x78] = duplicated[0x74:0x78]
    arm.uc.mem_write(OUTPUT, bytes(duplicated))
    assert arm.call('xwb_validate_party_records', OUTPUT) == -1
    assert bytes(arm.uc.mem_read(OUTPUT, 768)) == bytes(duplicated)
    checks += 1

    samples = {}
    for edition, path in SAMPLE_DUMPS.items():
        if not path.exists():
            continue
        ram = path.read_bytes()
        assert len(ram) == 0x400000
        records_offset = RECORD_ADDRESS - 0x02000000
        record_bytes = ram[records_offset:records_offset + RECORD_COUNT * RECORD_SIZE]
        order_offset = ORDER_ADDRESS - 0x02000000
        ids = [struct.unpack_from('<I', ram, order_offset + i * 8)[0] for i in range(9)]
        expected = expected_party(record_bytes, ids[:6])
        arm.uc.mem_write(RECORDS, record_bytes)
        order_bytes = ram[order_offset:order_offset + 9 * 8]
        arm.uc.mem_write(ORDER, order_bytes)
        arm.uc.mem_write(OUTPUT, b'\xA5' * 768)
        assert arm.call('xwb_capture_formation_party', RECORDS, RECORD_COUNT, ORDER, OUTPUT) == 0
        actual = bytes(arm.uc.mem_read(OUTPUT, 768))
        assert actual == expected
        assert bytes(arm.uc.mem_read(RECORDS, len(record_bytes))) == record_bytes
        samples[edition] = {'position_ids': ids, 'captured_record_sha256': hashlib.sha256(actual).hexdigest()}
        checks += 1

    report = {
        'status': 'The ARM946 party capture copies the first six current formation records in order and leaves save records unchanged.',
        'synthetic_checks': checks - len(samples),
        'real_formation_samples': samples,
        'limitations': 'Party capture and structural validation pass against Blue and Red QA formation RAM. This does not initialize received records as battle actors or start the session from Link Box.',
        'elf_sha256': hashlib.sha256(elf.read_bytes()).hexdigest(),
    }
    (OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
