"""Translate the Sky Fortress emergency communication and Chibickmon setup."""
from __future__ import annotations

import json
import textwrap

from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

TEXTS = {
183: "Ngh...! Hey, hey, hey... Wh-what is it? What's going on?!",
184: "...What happened all of a sudden, Shoutmon?",
185: "The Pickmon on the Sky Fortress... Ow! My ears!",
186: "Your ears?",
187: "They're yelling something over the emergency channel, but they're panicking and shouting so much... I can't understand a word!",
188: "This looks bad, Taiki!",
189: "Maybe ROG attacked again! Let's hurry back to the Sky Fortress!",
190: "Ah, Taiki! Did you hear the call?",
194: "This is serious, brother! Chibickmon...! That little Pickmon from the Pickmons was kidnapped!",
195: "Kidnapped...? By whom? When? Why? Where did they take it?!",
196: "We don't know...! We don't know what happened... We looked away for just a moment, and it was gone. S-sorry, brother! We were supposed to keep an eye on it...",
197: "Could it have just gotten lost...? Maybe it's playing somewhere?",
198: "No... If even the other Pickmon called out and it didn't answer, it's probably not just lost.",
199: "Actually, the last Digimon to see the little one heard it say, 'Wait up, big sis!' I think it followed someone.",
}

def fit(s: str) -> str:
    return "\n".join("\n".join(textwrap.wrap(line, width=15, break_long_words=True, break_on_hyphens=False)) if line else "" for line in s.split("\n"))

def main() -> None:
    records = collect_messages(Rom(rom_paths()["blue"]))
    done = translate_records(records)
    blocks, review = [], []
    for index, raw in TEXTS.items():
        key = f"MSG/MESPAK02.PAK:003:{index:05d}"
        if key in done:
            raise ValueError(f"Already translated: {key}")
        row = records.get(key)
        if not row or not row["source"].strip():
            raise ValueError(f"Missing story source: {key}")
        english = fit(raw)
        blocks.append({"archive": row["archive"], "entry": 3, "start": index,
                       "category": "Story and dialogue", "english": [english],
                       "sources": ["Original Japanese ROM (local primary source)"],
                       "review_note": "Story dialogue translated directly from Japanese; Chibickmon and other Digimon names use the project naming style."})
        review.append({"id": key, "japanese": row["source"], "english": english})
    path = ROOT / "translations/batch53.json"
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps({"description": "Translate the emergency call and the opening of the Chibickmon search mission.", "blocks": blocks}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "translations/review_batch53.json").write_text(json.dumps({"batch": 53, "translated_slots": len(blocks), "groups": review}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Batch 53 review", "", "This batch finishes the Sky Fortress emergency call and begins the Chibickmon search mission. Japanese dialogue is the primary source; Digimon names follow the project glossary.", "", "| ID | Japanese | English |", "|---|---|---|"]
    for row in review:
        jp = row["japanese"].replace("<0A>", "<br>").replace("|", "\\|")
        en = row["english"].replace("\n", "<br>").replace("|", "\\|")
        lines.append(f"| `{row['id']}` | {jp} | {en} |")
    (ROOT / "translations/review_batch53.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"batch": 53, "translated_slots": len(blocks)}, ensure_ascii=False))

if __name__ == "__main__":
    main()
