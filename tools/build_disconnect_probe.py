"""Build separate experimental disconnect-guard ROMs from the UI checkpoint.

Stable batch125 builds and backups are never overwritten. This is not a battle
mode build and must not be labelled ready until real local-link tests pass.
"""
import hashlib
import json
import struct
import argparse
from xros_text import ROOT, Rom, u32
from build import replace_files, crc16
from local_wireless_disconnect import guarded_overlay, codeCompression


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--busy-recovery', action='store_true')
    args = parser.parse_args()
    patch = guarded_overlay
    variant = 'disconnect_guard'
    if args.busy_recovery:
        from local_wireless_busy_recovery import busy_recovery_overlay
        patch = busy_recovery_overlay
        variant = 'busy_recovery'
    outdir = ROOT / ('build/experimental/local_wireless_busy_recovery' if args.busy_recovery else 'build/experimental/local_wireless_disconnect')
    outdir.mkdir(parents=True, exist_ok=True)
    results = {}
    for version in ('Blue', 'Red'):
        source = ROOT / f'build/backups/ui_checkpoint_batch125_before_local_wireless/Digimon_Super_Xros_Wars_{version}_English_batch125.nds'
        rom = Rom(source)
        packed, report = patch(rom)
        data, operations = replace_files(rom, {'@overlay/2': packed})
        output = outdir / f'Digimon_Xros_Wars_{version}_{variant}_TEST.nds'
        output.write_bytes(data)
        built = Rom(output)
        assert built.files == rom.files
        assert all(built.file(name) == rom.file(name) for name in rom.files)
        table = u32(rom.data, 0x50) + 2 * 32
        fid = u32(rom.data, table + 24)
        fat = rom.fat_offset + fid * 8
        start, end = struct.unpack_from('<II', data, fat)
        assert data[start:end] == packed
        assert u32(data, table + 28) & 0xFFFFFF == len(packed)
        assert len(codeCompression.decompress(packed)) == 19456
        # Account for every changed byte in the cartridge, not merely the files.
        restored = bytearray(data)
        restored[start:end] = rom.data[start:end]
        for a, b in ((fat, fat + 8), (table + 28, table + 32), (0x80, 0x84), (0x15E, 0x160)):
            restored[a:b] = rom.data[a:b]
        assert restored == rom.data, 'Unaccounted cartridge edit'
        assert crc16(data[:0x15E]) == struct.unpack_from('<H', data, 0x15E)[0]
        save_source = ROOT / f'build/qa/local_wireless_session/{version}_user_before_testing.sav'
        if save_source.exists():
            output.with_suffix('.sav').write_bytes(save_source.read_bytes())
        report.update({'source_checkpoint': str(source.relative_to(ROOT)),
                       'source_checkpoint_sha256': hashlib.sha256(rom.data).hexdigest(),
                       'output': str(output.relative_to(ROOT)),
                       'output_sha256': hashlib.sha256(data).hexdigest(),
                       'structural_validation': 'passed; all named assets and all bytes outside declared overlay/FAT/table/header edits unchanged',
                       'operations': operations,
                       'multiplayer_battle': 'NOT implemented'})
        results[version.lower()] = report
        print(version, output, report['output_sha256'])
    (outdir / 'manifest.json').write_text(json.dumps(results, indent=2) + '\n')


if __name__ == '__main__':
    main()
