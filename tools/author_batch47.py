"""Translate the first story scene after rescuing Spadamon."""
from __future__ import annotations

import json
import textwrap

from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

TEXTS = {
3: "We’re with you! We’ll fight by your side! Let’s go!",
4: "Spadamon!! I’m glad you’re safe!",
5: "Ba... Badamon! Bada-mooon!! Thank goodness! I thought you were dead!",
6: "Hey! Don’t say something so awful! You got away from those ROG guys too, Spadamon! And who are these Digimon...? Um, who are you?",
7: "We’re Xros Heart! We came from another Zone. Spadamon said he wanted to save you, so we decided to help!",
8: "I see... So that’s what happened. Thank you so much! You’re an amazing team! I’m glad you were here to protect Spadamon. If ROG had caught him, things would have been much, much worse!",
9: "Worse...? Wait, that guy we just beat said all of ROG was looking for Spadamon... What does that mean?",
10: "I... I don’t know either! I’ve actually lost my memories... I can’t remember anything from before I started living with Patamon. Maybe I know the secret of this Zone... H-hey, I’m only joking!",
11: "Hey, hey, hey! Are you okay?!",
12: "But... ROG sounds like a pretty big organization. It can’t be for nothing if they’re searching with this many people. Spadamon, you really don’t remember anything?",
13: "B-but I really don’t remember... Everyone says I’ll remember naturally once I get stronger, but I’ve been running away all this time, so I never get stronger... Heh!",
14: "Grrr! I’ve had enough! Taiki and I will toughen you up, whether you like it or not!",
15: "Ha ha! I can’t tell if you’re strong or weak. But the voice that called us here was real. I could feel how badly you wanted to save your friends!",
16: "Oh, right! We can talk later! Those ROG guys started up the DigiLab system... They’re going to run a fusion experiment in the Central Room next door!",
17: "Hmm? What do you mean, fusion? Is it DigiXross?",
18: "...DigiXross?\nNo, the DigiLab combines Digimon to make them even stronger! It’s a really useful system when it’s used properly. But those guys don’t know how it works... They’ll force your square-shaped friend into the experiment!",
19: "I’m coming with you, too! Let’s hurry to the Central Room!",
20: "Why’d they bring such a huge lump here? He’s heavy, big, and looks slow. Stubborn and hard to handle, too. And besides, our personalities kind of overlap...",
21: "How do they?! We’re not even one micron alike!",
22: "Oh, shut up, all of you! Hurry up and carry him over to that machine! I’m going to absorb his power and bulk! No one’s ever calling me a chicken again!",
23: "Hey... There are two machines here. Which one is it?",
24: "W-which one...? How should I know? The database only says it’s a machine here. Almost all the Digimon ran off, so we can’t ask them. Maybe we should catch that Spadamon and squeeze the answer out of him...?",
25: "Idiot! If you find him, hand him over to Lord Minotaurmon! Figure this out yourselves. Think of a clue!",
26: "I think it’s a secret system found only in this Zone. It mixes Digimon together and makes them a lot stronger.",
27: "If you touch the switch in front of the machine... it lights up with a flash and goes beep-boop! That’s what I heard.",
28: "...So which of these two looks like that machine?",
29: "They both kind of look like it... Actually, neither one really does.",
30: "What’s with all this ‘flash’ and ‘beep-boop’ stuff? Are you messing with me? That’s not a clue at all! How am I supposed to tell? Whatever, just try one!",
31: "You’re talking like it’s someone else’s problem! What if you mess with it and combine them the wrong way? If you’re so sure, you two try it! One’s squishy and one’s rock-hard. Put them together and divide by two, and you’ll get a nice, soft result!",
32: "You’re the one talking nonsense, birdbrain! Keep spouting that garbage and I’ll pluck that crest right off your head!",
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
                       "review_note": "Dialogue translated directly from the Japanese scene; character names and DigiLab/DigiXross terminology follow project style."})
        review.append({"id": key, "japanese": row["source"], "english": english})
    path = ROOT / "translations/batch47.json"
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps({"description": "Translate the next scene of story dialogue after Spadamon is rescued.", "blocks": blocks}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "translations/review_batch47.json").write_text(json.dumps({"batch": 47, "translated_slots": len(blocks), "groups": review}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Batch 47 review", "", "This scene follows the rescue of Spadamon and leads into the ROG DigiLab fusion experiment. Japanese dialogue is the primary source; names and project terminology follow the established style guide.", "", "| ID | Japanese | English |", "|---|---|---|"]
    for row in review:
        jp = row["japanese"].replace("<0A>", "<br>").replace("|", "\\|")
        en = row["english"].replace("\n", "<br>").replace("|", "\\|")
        lines.append(f"| `{row['id']}` | {jp} | {en} |")
    (ROOT / "translations/review_batch47.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"batch": 47, "translated_slots": len(blocks)}, ensure_ascii=False))

if __name__ == "__main__":
    main()
