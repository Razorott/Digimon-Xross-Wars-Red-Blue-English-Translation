"""Export Digidex profiles whose punctuation needs contextual screen review."""
from __future__ import annotations

import csv
from pathlib import Path

from build import collect_messages, translate_records
from xros_text import ROOT, Rom, rom_paths


def main():
    records = collect_messages(Rom(rom_paths()['blue']))
    translated = translate_records(records)
    base = ROOT / 'translations'
    reviewed = [record for record in translated.values()
                if record['category'] == 'Digimon profiles'
                and "'" in record['authored_english']]
    pending = [record for record in translated.values()
               if record['category'] == 'Digimon profiles' and "'" in record['english']]
    output = base / 'profile_punctuation_review.tsv'
    with output.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle, delimiter='\t')
        writer.writerow(['id', 'japanese', 'authored_english', 'runtime_english', 'status'])
        for record in sorted(reviewed, key=lambda record: record['id']):
            writer.writerow([record['id'], record['source'].replace('\n', '<br>'),
                             record['authored_english'].replace('\n', '<br>'),
                             record['english'].replace('\n', '<br>'),
                             'ready for route QA' if record not in pending else 'punctuation pending'])
    queue = base / 'profile_punctuation_queue.tsv'
    with queue.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle, delimiter='\t')
        writer.writerow(['id', 'japanese', 'current_english', 'review'])
        for record in sorted(pending, key=lambda record: record['id']):
            writer.writerow([record['id'], record['source'].replace('\n', '<br>'),
                             record['english'].replace('\n', '<br>'),
                             'Rewrite possessive/contraction in context; emulator-check'])
    print(f'{len(reviewed)} reviewed profiles; {len(pending)} pending punctuation: {output}')


if __name__ == '__main__':
    main()
