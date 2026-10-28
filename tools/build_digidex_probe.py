"""Build a disposable Blue ROM with all English text but original graphics.

Used only to isolate the Digidex freeze from the graphics localization pass.
The output is written under build/qa and does not alter the supplied ROMs.
"""
from __future__ import annotations

import collections
import argparse
import json

from build import collect_messages, encode_translation, replace_files, translate_records
from name_layout import apply_display_names, apply_move_names
from xros_font import Font, english_font
from xros_program import localize_program
from xros_text import Messages, ROOT, Pak, Rom, rom_paths


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-messages", action="store_true")
    parser.add_argument("--no-fonts", action="store_true")
    parser.add_argument("--no-program", action="store_true")
    parser.add_argument("--original-message", action="append", default=[])
    parser.add_argument("--original-index-range", action="append", default=[])
    args = parser.parse_args()
    ranges = []
    for spec in args.original_index_range:
        archive, entry, span = spec.rsplit(":", 2)
        start, end = (int(value) for value in span.split("-", 1))
        ranges.append((archive, int(entry), start, end))
    original = Rom(rom_paths()["blue"])
    records = collect_messages(original)
    translated = translate_records(records)

    fonts = Pak(original.file("FONT_NFTR.PAK"))
    changed_fonts = {}
    for index in range(fonts.count):
        standard, count = english_font(fonts.file(index))
        if count:
            changed_fonts[index] = standard
    display_fonts = [Font(changed_fonts.get(i, fonts.file(i))) for i in (0, 5)]
    apply_display_names(translated, display_fonts)
    apply_move_names(translated, display_fonts)

    edits = collections.defaultdict(lambda: collections.defaultdict(dict))
    for record in translated.values():
        edits[record["archive"]][record["entry"]][record["index"]] = encode_translation(record)
    replacements = {}
    if not args.no_messages:
        for name, entries in edits.items():
            if name in args.original_message:
                continue
            pak = Pak(original.file(name))
            entry_replacements = {}
            for entry, strings in entries.items():
                filtered = {
                    index: payload for index, payload in strings.items()
                    if not any(a == name and e == entry and start <= index < end
                               for a, e, start, end in ranges)
                }
                if filtered:
                    entry_replacements[entry] = Messages(pak.file(entry)).rebuild(filtered)
            if entry_replacements:
                replacements[name] = pak.rebuild(entry_replacements)
    if not args.no_fonts:
        replacements["FONT_NFTR.PAK"] = fonts.rebuild(changed_fonts)
    program = None if args.no_program else localize_program(original)[0]
    payload, operations = replace_files(original, replacements, program)

    suffix = "no_graphics"
    if args.no_messages:
        suffix += "_no_messages"
    if args.no_fonts:
        suffix += "_no_fonts"
    if args.no_program:
        suffix += "_no_program"
    for name in args.original_message:
        suffix += "_" + name.replace("/", "_").replace(".PAK", "").lower()
    for name, entry, start, end in ranges:
        suffix += f"_idx_{name.rsplit('/', 1)[-1][:2].lower()}{entry}_{start}_{end}"
    output = ROOT / f"build/qa/Digimon_Super_Xros_Wars_Blue_{suffix}_probe.nds"
    output.write_bytes(payload)
    patched = Rom(output)
    for name in original.files:
        expected = replacements.get(name, original.file(name))
        if patched.file(name) != expected:
            raise ValueError(f"Probe ROM verification failed for {name}")
    print(json.dumps({
        "output": str(output),
        "bytes": len(payload),
        "graphics": "original",
        "messages": "original" if args.no_messages else "English",
        "fonts": "original" if args.no_fonts else "English glyphs",
        "program": "original" if args.no_program else "localized strings",
        "translations": len(translated),
        "changed_files": [x["file"] for x in operations],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
