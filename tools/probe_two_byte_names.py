"""Build a disposable all-name DigiDex probe from the latest English Blue ROM."""
from __future__ import annotations
import argparse
import json
from build import replace_files
from name_layout import pixels
from xros_font import Font, two_byte_latin_font
from xros_text import ROOT, Messages, Pak, Rom


def fullwidth(value: str) -> str:
    return ''.join('\u3000' if char == ' ' else chr(ord(char) + 0xfee0)
                   for char in value)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', type=int, default=179)
    parser.add_argument('--end', type=int, default=651)
    parser.add_argument('--no-font-alias', action='store_true')
    parser.add_argument('--override', help='ASCII display label for the first selected name')
    parser.add_argument('--alnum-only', action='store_true')
    args = parser.parse_args()
    rom = Rom(ROOT / 'build/Digimon_Super_Xros_Wars_Blue_English_batch102.nds')
    font_pak = Pak(rom.file('FONT_NFTR.PAK'))
    font_edits = {}
    for index in range(font_pak.count):
        font_edits[index] = (font_pak.file(index) if args.no_font_alias
                             else two_byte_latin_font(font_pak.file(index))[0])
    fonts = [Font(font_edits[index]) for index in (0, 5)]
    name_pak = Pak(rom.file('MSG/MESPAK00.PAK'))
    names = json.loads((ROOT / 'translations/display_name_layout.json').read_text(encoding='utf-8'))
    name_edits = {}
    for row in names:
        index = int(row['id'].split(':')[-1])
        if not args.start <= index < args.end:
            continue
        display = (args.override if args.override is not None and index == args.start
                   else row['display'])
        if args.alnum_only:
            display = display.replace('.', '').replace(' ', '')
        text = fullwidth(display)
        if not args.no_font_alias and pixels(text, fonts) > 60:
            raise ValueError(f"Overwide {row['display']}: {pixels(text, fonts)}")
        payload = text.encode('cp932')
        if len(payload) != 2 * len(display):
            raise ValueError(f"Non-two-byte text: {row['display']}")
        name_edits[index] = payload
    replacements = {}
    if not args.no_font_alias:
        replacements['FONT_NFTR.PAK'] = font_pak.rebuild(font_edits)
    if name_edits:
        name_entry = Messages(name_pak.file(0)).rebuild(name_edits)
        replacements['MSG/MESPAK00.PAK'] = name_pak.rebuild({0: name_entry})
    out, _ = replace_files(rom, replacements)
    suffix = f'{args.start}_{args.end}' + ('_noalias' if args.no_font_alias else '')
    if args.override is not None:
        suffix += '_' + args.override.replace(' ', '_').replace('.', 'dot')
    if args.alnum_only:
        suffix += '_alnum'
    dest = ROOT / f'build/qa/digidex_fullwidth_{suffix}.nds'
    dest.write_bytes(out)
    print(json.dumps({'rom':str(dest),'names':len(name_edits),'bytes':len(out)}))


if __name__ == '__main__':main()
