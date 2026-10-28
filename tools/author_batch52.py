"""Translate the Sky Fortress item-shop notice and first Knuckle Coast encounter."""
from __future__ import annotations

import json
import textwrap

from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

TEXTS = {
153: "ROG might be there, so we'd better get ready.",
154: "You may have noticed, but Penmon in the Central Room seems to sell healing and equipment items! We'll keep helping Patamon here!",
155: "Be careful, Taiki. Don't push yourself too hard! If your HP or MP gets low outside, look for a Tent Point and rest in the healing bed inside. You'll feel better!",
156: "To travel, go to the Skyport at the back of the Commander Room and ride with the Digimon Flight Team.",
157: "All right, Taiki! Let's go! We'll ride with the Digimon Flight Team and fly, fly, fly!",
158: "I didn't know you liked flying so much, brother...",
159: "I do not like it...",
160: "But this is kind of exciting! All right, let's go!",
161: "You're not from the Elestou Zone...! You must be with ROG! Were you waiting for us...?",
162: "Oh, Spadamon, keeper of the Elestou Zone's secrets. You should have stayed hidden. Coming here to be captured is so pitifully comical... How foolish! Pukuku!",
163: "That's exactly what Lord Pukumon says! There's no way this fool knows the secret of the Legendary Ancient Weapons... He doesn't look like he knows a thing!",
164: "But if this weak little Spadamon really does know the secret, we'll just grab him right away!",
165: "...These fish are flapping their mouths like they own the place.",
166: "Grr... Those guys make me so mad! I'm not weak anymore!",
167: "Pukumon! What is ROG after? Why are you trying to capture Spadamon?",
168: "ROG's goal? Pukuku! Isn't it obvious? World domination! Once we find the Legendary Ancient Weapons, ROG will rule the world as we please!",
169: "Magnificent! What a rousing speech! Just as expected of our Lord Pukumon!",
170: "ROG's Splash Leader, Lord Pukumon the Prickle!",
171: "Pukuku!",
172: "World domination...? You torment the Digimon of this Zone for that? I won't let you get away with it!",
173: "I'll soon shut that insolent mouth of yours! Pukuku!",
174: "How could I, Lord Pukumon, lose to a bunch like you...? This is hilarious! Pukuku!",
175: "What's so funny?!",
176: "...Spadamon will never give up! Everything is for our ROG leader, Lord ZD Millenniummon!",
178: "...I remember! The Legendary Ancient Weapons are said to have terrifying power: in an angel's hands, they save the world; in a demon's, they destroy it... I thought that was just an old Elestou Zone legend, but ROG came here to find those weapons!",
179: "Destroy the world...? No... That can't be... But why would Spadamon know such an important secret?",
180: "Maybe there's been some mistake. A huge secret like that wouldn't be known by a weak-looking guy like Spadamon... It'd be someone kingly, like me!",
181: "...Huh? Did I say something weird?",
182: "Ha ha ha... He doesn't mean any harm...",
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
                       "review_note": "Story, item-shop, and travel dialogue translated directly from Japanese; named features follow the project glossary."})
        review.append({"id": key, "japanese": row["source"], "english": english})
    path = ROOT / "translations/batch52.json"
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps({"description": "Translate the Sky Fortress travel preparation and Pukumon confrontation.", "blocks": blocks}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "translations/review_batch52.json").write_text(json.dumps({"batch": 52, "translated_slots": len(blocks), "groups": review}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Batch 52 review", "", "This batch covers the item-shop and Tent Point hints, travel to Knuckle Coast, and Pukumon's explanation of ROG's goal. Japanese dialogue is the primary source; character names and game terms follow the project glossary.", "", "| ID | Japanese | English |", "|---|---|---|"]
    for row in review:
        jp = row["japanese"].replace("<0A>", "<br>").replace("|", "\\|")
        en = row["english"].replace("\n", "<br>").replace("|", "\\|")
        lines.append(f"| `{row['id']}` | {jp} | {en} |")
    (ROOT / "translations/review_batch52.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"batch": 52, "translated_slots": len(blocks)}, ensure_ascii=False))

if __name__ == "__main__":
    main()
