"""Carry the verified Red Reserve palette into current native TEST ROMs.

The released Red125 already contains this UI change. This updates only the
Red palette archive in current wireless-native TEST outputs made from batch124.
"""
import hashlib
import json
import shutil
from pathlib import Path

from build import replace_files
from xros_text import ROOT, Rom


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    blue_checkpoint = ROOT / 'build/backups/ui_checkpoint_batch124_user_hardware_verified/Digimon_Super_Xros_Wars_Blue_English_batch124.nds'
    red_checkpoint = ROOT / 'build/backups/ui_checkpoint_batch124_user_hardware_verified/Digimon_Super_Xros_Wars_Red_English_batch124.nds'
    red_ui = Rom(ROOT / 'build/Digimon_Super_Xros_Wars_Red_English_batch125.nds')
    original = Rom(red_checkpoint)
    assert original.files == red_ui.files
    assert original.file('BG_NCLR.PAK') != red_ui.file('BG_NCLR.PAK')
    assert all(original.file(name) == red_ui.file(name) for name in original.files if name != 'BG_NCLR.PAK')

    backup_root = ROOT / 'build/backups/red_reserve_yellow_wireless_test_rollforward_20261027'
    backup_root.mkdir(parents=True, exist_ok=True)
    manifest_updates = []
    for manifest_path in sorted((ROOT / 'build/experimental').glob('wireless_*/manifest.json')):
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        red = manifest.get('builds', {}).get('Red')
        if not red or not red.get('output'):
            continue
        output = ROOT / Path(red['output'].replace('\\', '/'))
        if not output.is_file():
            continue
        existing_bytes = output.read_bytes()
        if digest(existing_bytes) != red['sha256']:
            raise ValueError(f'Build differs from its recorded checksum: {output}')
        build_rom = Rom(output)
        if build_rom.file('BG_NCLR.PAK') == red_ui.file('BG_NCLR.PAK'):
            continue
        backup = backup_root / f'{output.stem}_pre_palette_{red["sha256"][:12]}{output.suffix}'
        if backup.exists():
            if digest(backup.read_bytes()) != red['sha256']:
                raise ValueError(f'Existing checkpoint has a different checksum: {backup}')
        else:
            shutil.copy2(output, backup)
        if digest(backup.read_bytes()) != red['sha256']:
            raise ValueError(f'Checkpoint copy checksum mismatch: {backup}')
        result, operations = replace_files(build_rom,
            {'BG_NCLR.PAK': red_ui.file('BG_NCLR.PAK')})
        output.write_bytes(result)
        updated = Rom(output)
        if updated.files != build_rom.files:
            raise ValueError(f'File table changed unexpectedly: {output}')
        if updated.file('BG_NCLR.PAK') != red_ui.file('BG_NCLR.PAK'):
            raise ValueError(f'Red UI palette did not carry forward: {output}')
        if any(updated.file(name) != build_rom.file(name) for name in build_rom.files if name != 'BG_NCLR.PAK'):
            raise ValueError(f'Unexpected game asset changed: {output}')
        red['sha256'] = digest(result)
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        manifest_updates.append({'rom': str(output.relative_to(ROOT)), 'sha256': red['sha256'],
            'backup': str(backup.relative_to(ROOT)), 'previous_sha256': digest(existing_bytes),
            'changed_asset': 'BG_NCLR.PAK'})

    report = {'status': 'Red reserve palette carried into current wireless-native test builds',
        'palette_source': 'build/Digimon_Super_Xros_Wars_Red_English_batch125.nds',
        'palette_source_sha256': digest(red_ui.file('BG_NCLR.PAK')),
        'batch124_baseline_roms': {'Blue': digest(Path(blue_checkpoint).read_bytes()),
                                   'Red': digest(Path(red_checkpoint).read_bytes())},
        'updated': manifest_updates}
    destination = backup_root / 'rollforward_report.json'
    destination.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
