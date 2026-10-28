"""Record the batch-01 screenshots reviewed after the final emulator runs.

This records a visual review; it does not automate the judgment or claim a full
playthrough. Rerun the emulator and review new images after any ROM change.
"""
import hashlib
import json
from xros_text import ROOT, rom_paths


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record():
    config = json.loads((ROOT / 'project.json').read_text(encoding='utf-8'))
    result = {
        'review_date': '2026-10-24',
        'emulator': 'Libretro DeSmuME 0.9.12, Windows x64, interpreter, software renderer',
        'core_sha256': sha(ROOT / '.tools/desmume/desmume_libretro.dll'),
        'sequence': 'tools/qa_batch01.json',
        'frames_per_game': 10053,
        'automated_tests': '8 passed with unittest discover -s tests -v',
        'scope': 'Boot, first forest dialogue, speaker names, apostrophe rendering and multi-page text progression. No full playthrough, battle or menu coverage claim.',
        'remaining': ['Rest of translation', 'Japanese graphics', 'Proportional dialogue renderer', 'Narrow UI and dynamic substitutions gameplay QA', 'Full playthrough of both versions'],
        'versions': {}
    }
    reviewed = {
        'blue': ['03_first_dialogue.png', '06_page.png', '12_next_page.png'],
        'red': ['06_page.png']
    }
    for version, original in rom_paths().items():
        report = json.loads((ROOT / f'build/{version}_report.json').read_text(encoding='utf-8'))
        output = ROOT / 'build' / report['output']
        assert sha(original) == config['original_sha256'][version]
        assert sha(output) == report['output_sha256']
        screenshots = []
        for name in reviewed[version]:
            path = ROOT / f'build/qa/{version}_batch01' / name
            screenshots.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path), 'visual_review': 'English legible; no right-edge clipping in this inspected page'})
        result['versions'][version] = {'output_sha256': sha(output), 'original_sha256': sha(original), 'translated_slots': report['translated_slots'], 'process_exit_code': 0, 'screenshots_reviewed': screenshots}
    target = ROOT / 'build/qa/validation.json'
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    record()
