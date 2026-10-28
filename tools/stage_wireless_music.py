"""Stage native sequence/bank/wave imports from the user's reference ROMs.

Does not build a ROM or assign unverified battle-theme names to numbered songs.
The staged archive is an integration asset, not proof of runtime playback.
"""
import copy
import hashlib
import json
import sys
from xros_text import ROOT, Rom
sys.path.insert(0, str(ROOT / '.tools/python'))
from ndspy.soundArchive import SDAT


def digest(data):
    return hashlib.sha256(data).hexdigest()


def object_state(obj):
    return obj.save()


def import_sequences(target, source, prefix, indices):
    banks, waves, result = {}, {}, []
    bank_hashes, wave_hashes = {}, {}
    for index in indices:
        name, original = source.sequences[index]
        if original is None:
            raise ValueError('Missing source music sequence')
        player_name, player = source.sequencePlayers[original.playerID]
        if player_name != 'BGM' or vars(player) != vars(target.sequencePlayers[0][1]):
            raise ValueError('Source BGM player requires an explicit compatibility adapter')
        seq = copy.deepcopy(original)
        bank_id = original.bankID
        if bank_id not in banks:
            bank_name, original_bank = source.banks[bank_id]
            if original_bank is None:
                raise ValueError('Missing source instrument bank')
            bank = copy.deepcopy(original_bank)
            for slot, wave_id in enumerate(bank.waveArchiveIDs):
                if wave_id in (None, -1, 0xFFFF):
                    continue
                if not 0 <= wave_id < len(source.waveArchives):
                    raise ValueError('Invalid source wave archive reference')
                if wave_id not in waves:
                    wave_name, wave = source.waveArchives[wave_id]
                    if wave is None:
                        raise ValueError('Missing source wave archive')
                    waves[wave_id] = len(target.waveArchives)
                    target.waveArchives.append((prefix + '_' + wave_name, copy.deepcopy(wave)))
                    wave_hashes[waves[wave_id]] = digest(wave.save()[0])
                bank.waveArchiveIDs[slot] = waves[wave_id]
            banks[bank_id] = len(target.banks)
            target.banks.append((prefix + '_' + bank_name, bank))
            bank_hashes[banks[bank_id]] = digest(original_bank.save()[0])
        seq.bankID = banks[bank_id]
        seq.playerID = 0
        new_index = len(target.sequences)
        target.sequences.append((prefix + '_' + name, seq))
        result.append({'source_sequence_index': index, 'source_symbol': name,
                       'target_sequence_index': new_index, 'target_bank_index': seq.bankID,
                       'source_sseq_sha256': digest(original.save()[0]),
                       'theme_identity': 'unverified numbered music; not assigned to a requested battle theme'})
    return {'sequences': result, 'bank_map': banks, 'wave_map': waves,
            'bank_content_sha256': bank_hashes, 'wave_content_sha256': wave_hashes}


def main():
    directory = ROOT / 'build/experimental/wireless_music'
    directory.mkdir(parents=True, exist_ok=True)
    original_path = ROOT / 'build/Digimon_Super_Xros_Wars_Blue_English_batch124.nds'
    rom = Rom(original_path)
    original_data = rom.file('sound_data.sdat')
    target = SDAT(original_data)
    counts = [len(target.sequences), len(target.banks), len(target.waveArchives)]
    # Keep content and metadata evidence for every existing entry. A new SDAT
    # layout may differ byte-for-byte, but existing assets and indices must not.
    originals = [[(name, object_state(obj) if obj is not None else None) for name, obj in table]
                 for table in (target.sequences, target.banks, target.waveArchives)]
    imports = {}
    for key, path in (
        ('dusk', ROOT / 'build/backups/Digimon Dusk/Digimon World - Dusk (USA).nds'),
        ('world_ds', ROOT / 'build/backups/Digimon World DS/Digimon World DS (USA).nds')):
        source_rom = Rom(path)
        sound_name = next(name for name in source_rom.files if name.lower().endswith('.sdat'))
        source = SDAT(source_rom.file(sound_name))
        selected = [i for i, (name, obj) in enumerate(source.sequences) if name.startswith('bgm')]
        imported = import_sequences(target, source, 'xwb_' + key, selected)
        imported.update(source_rom=str(path.relative_to(ROOT)), source_rom_sha256=digest(source_rom.data),
                        source_sdat_sha256=digest(source_rom.file(sound_name)))
        imports[key] = imported
    data = target.save()
    loaded = SDAT(data)
    for old, table in zip(originals, (loaded.sequences, loaded.banks, loaded.waveArchives)):
        for index, (name, content) in enumerate(old):
            new_name, obj = table[index]
            assert new_name == name
            assert (object_state(obj) if obj is not None else None) == content, index
    # Follow every imported bank and wave reference after the real SDAT round
    # trip; checking only sequence names would miss broken dependencies.
    for imported in imports.values():
        for index, expected_hash in imported['bank_content_sha256'].items():
            assert digest(loaded.banks[index][1].save()[0]) == expected_hash
        for index, expected_hash in imported['wave_content_sha256'].items():
            assert digest(loaded.waveArchives[index][1].save()[0]) == expected_hash
        for entry in imported['sequences']:
            _, seq = loaded.sequences[entry['target_sequence_index']]
            assert digest(seq.save()[0]) == entry['source_sseq_sha256']
            assert seq.bankID == entry['target_bank_index']
            _, bank = loaded.banks[seq.bankID]
            for wave_id in bank.waveArchiveIDs:
                if wave_id not in (None, -1, 0xFFFF):
                    assert loaded.waveArchives[wave_id][1] is not None
    output = directory / 'sound_data_staged.sdat'
    output.write_bytes(data)
    manifest = {'status': 'staged native music dependencies; not installed or playback-tested',
        'baseline': str(original_path.relative_to(ROOT)), 'baseline_sha256': digest(rom.data),
        'original_counts': counts,
        'staged_counts': [len(loaded.sequences), len(loaded.banks), len(loaded.waveArchives)],
        'original_sdat_size': len(original_data), 'staged_sdat_size': len(data),
        'staged_sdat_sha256': digest(data), 'imports': imports,
        'remaining': 'Identify the exact five requested source themes from game playback/code, prune unused staged songs, connect seven host music choices to native BGM playback, then test memory use and both peers.'}
    (directory / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({key: manifest[key] for key in ('status', 'original_counts', 'staged_counts', 'original_sdat_size', 'staged_sdat_size')}, indent=2))


if __name__ == '__main__':
    main()
