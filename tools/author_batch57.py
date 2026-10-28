"""Translate the return to the Sky Fortress and the Dorulumon rescue setup."""
from __future__ import annotations

import json
import textwrap

from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

TEXTS = {
101: "Meow! Amazing! I'm so meow-pressed!",
102: "Hey, are you starting to talk like that weird one?",
103: "The person who calls someone weird is the weird one! You understand?",
104: "A-anyway... We can talk about that later. Everyone's worried, so let's get back to the Sky Fortress.",
105: "Meow, we're home, meow!♪",
106: "Heyyyyy!!",
107: "Don't just stroll in here meowing! Where have you been, kid?!",
108: "I went to play with big sis!♪",
109: "...What?! What are you talking about?! Do you know how worried we were?!",
110: "So worried!!",
111: "Meow-nyo?♪",
112: "Now, now. At least we're glad you found it safe and sound!",
113: "W-well, yeah. It doesn't look like you got mixed up in anything dangerous.",
114: "Though that Digimon looked dangerous in a different way...",
115: "Ah, Taiki! A scary souvenir for you!",
116: "Key item obtained!\nWest Amazon Key",
117: "What is this? Where did it come from?",
118: "The twisty key to Twisting Amazon! Big sis said to give it to Taiki!♪",
119: "Give it to me...? What does that mean? Did that Digimon know us?",
120: "...Wait a second. Was there any other message?",
121: "A message...? Um... Big sis said Cutemon wasn't there!",
122: "...I have no idea what that means...",
123: "Hey, Taiki... I've got a bad feeling. When it says 'Cutemon, Cutemon,' could it mean Cutemon...?",
124: "...But what does 'Cutemon isn't there' mean?",
125: "If Cutemon is there, Dorulumon should be there, too! Let's head to Twisting Amazon!",
126: "We'll keep lecturing this one!",
127: "A lecture!",
128: "Meow...",
129: "The missing friends were Cutemon and Dorulumon, right? I hope we find them safe in Twisting Amazon...",
130: "They'll be fine. I'm sure they're doing all right. Come on! Let's get going!",
131: "...Dorulumon!",
132: "Dorulumon! What are you doing in a place like this?!",
133: "Taiki... Shoutmon... I'm sorry.",
134: "There you go! A huge prey has taken the bait! At last, it's time for the long-awaited puppy show!♪",
135: "If we beat these guys, you'll let Cutemon go, right?",
}

def fit(s: str) -> str:
    return "\n".join("\n".join(textwrap.wrap(line, width=15, break_long_words=True, break_on_hyphens=False)) if line else "" for line in s.split("\n"))

def main() -> None:
    records = collect_messages(Rom(rom_paths()["blue"]))
    done = translate_records(records)
    blocks, review = [], []
    for index, raw in TEXTS.items():
        key = f"MSG/MESPAK02.PAK:004:{index:05d}"
        if key in done:
            raise ValueError(f"Already translated: {key}")
        row = records.get(key)
        if not row or not row["source"].strip():
            raise ValueError(f"Missing story source: {key}")
        english = fit(raw)
        blocks.append({"archive": row["archive"], "entry": 4, "start": index,
                       "category": "Story and dialogue", "english": [english],
                       "sources": ["Original Japanese ROM (local primary source)"],
                       "review_note": "Mission dialogue and key-item text translated directly from Japanese; human character names follow the original-name preference."})
        review.append({"id": key, "japanese": row["source"], "english": english})
    path = ROOT / "translations/batch57.json"
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps({"description": "Translate the Chibickmon reunion and Dorulumon rescue lead-in.", "blocks": blocks}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "translations/review_batch57.json").write_text(json.dumps({"batch": 57, "translated_slots": len(blocks), "groups": review}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Batch 57 review", "", "This batch completes the Chibickmon return, translates the West Amazon Key notice, and leads into the Dorulumon rescue. Japanese dialogue is the primary source; names follow the project glossary and original-name preference.", "", "| ID | Japanese | English |", "|---|---|---|"]
    for row in review:
        jp = row["japanese"].replace("<0A>", "<br>").replace("|", "\\|")
        en = row["english"].replace("\n", "<br>").replace("|", "\\|")
        lines.append(f"| `{row['id']}` | {jp} | {en} |")
    (ROOT / "translations/review_batch57.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"batch": 57, "translated_slots": len(blocks)}, ensure_ascii=False))

if __name__ == "__main__":
    main()
