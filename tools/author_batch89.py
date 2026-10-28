"""Translate party/bank notices, recruitment responses, and service messages, entry 14."""
from __future__ import annotations

import json

from build import collect_messages, translate_records
from translation_queue import category
from xros_text import ROOT, Rom, rom_paths


DIALOGUE = {
    0: "DeadlyAxemon joined your team.",
    1: "Greymon joined your team.",
    2: "MailBirdramon joined your team.",
    3: "All right. I'm counting on you.",
    4: "Okay!♪",
    5: "Understood. Let's work together.",
    6: "I'll show you what I can do.",
    7: "Got it.",
    8: "I'll burn them all to ashes!",
    9: "Understood. I'll lend you a hand.",
    10: "Dorumon was added to the party!",
    11: "Sparrowmon was added to the party!",
    12: "Beelzemon was added to the party!",
    13: "SkullKnightmon was added to the party!",
    14: "DeadlyAxemon was added to the party!",
    15: "Greymon was added to the party!",
    16: "MailBirdramon was added to the party!",
    17: "Dorumon was sent to the DigiBank!",
    18: "Sparrowmon was sent to the DigiBank!",
    19: "Beelzemon was sent to the DigiBank!",
    20: "SkullKnightmon was sent to the DigiBank!",
    21: "DeadlyAxemon was sent to the DigiBank!",
    22: "Greymon was sent to the DigiBank!",
    23: "MailBirdramon was sent to the DigiBank!",
    24: "...Hmm, all right.",
    25: "...Oh, that's too bad.",
    26: "...Hmm, that's fine.",
    27: "...A foolish choice.",
    28: "...Understood.",
    29: "You're not going to recruit me?!",
    30: "...Hmph.",
    32: "^0 was added to the party!",
    34: "^0 was sent to the DigiBank!",
    35: "Want to make me your ally?♪",
    39: "Will you make me your ally?",
    40: "You're really going to recruit me?!",
    45: "Will you let me join you?",
    46: "Will you make me one of your friends?",
    48: "You're going to let me join, right?♪",
    51: "Will you recruit me?",
    52: "Are you sure you want me as an ally...?",
    53: "Are you going to make me your ally?",
    56: "You're going to recruit me?!",
    57: "Want me to join you?",
    60: "Would you let me join you?",
    61: "Want to make me your ally?",
    64: "I'm counting on you!♪",
    89: "I look forward to working with you.",
    99: "Oh, okay. See you around!",
    105: "...All right, then. Bye!",
    107: "I see... That's too bad.",
    108: "Oh... Well, it can't be helped!",
    109: "Hmm. So be it.",
    114: "Aww, that's disappointing!",
    116: "Okay, see you later!",
    118: "Understood.",
    123: "Yes, show me!",
    124: "No, don't show me.",
    125: "Activate the DigiLab?",
    128: "Activate the DigiFarm?",
    131: "Will this work if I turn on the power...? ...No, it won't start. The switch is on... Is there no energy supply?",
    132: "...It won't power on. ...Is there not enough energy?",
    139: "Taiki, are you all right? Don't push yourself!",
    140: "That's right! Fight smart, not hard, and win! You can do it, Taiki!",
    141: "Yeah, leave it to me!",
    142: "Are you okay, Taiki?",
    143: "You were having a pretty bad nightmare. Did you have a rough dream?",
    144: "Sorry, everyone. I'm okay now!",
    145: "Be careful! Don't overdo it!",
    146: "If you have any questions, ask us or Patamon. We're counting on you, Taiki Kudo!",
    147: "Hang in there, Taiki...!",
    148: "We're counting on you, General! We know we can rely on you!",
    149: "I'm all right now! I won't lose this time!",
    150: "Hey, Taiki! This is the Service Counter. Want to use a Summon Ticket from the Reload Challenge to call a Digimon?",
    151: "Yes, summon one.",
    152: "No, don't summon one.",
    153: "Come back when you get another Summon Ticket!",
    165: "Lord Numemon wants to give you an item!",
    167: "Want an item?!",
    194: "Oh, hello! I'll give you an item!",
}


def main() -> None:
    destination = ROOT / "translations/batch89.json"
    if destination.exists():
        raise FileExistsError(destination)
    records = collect_messages(Rom(rom_paths()["blue"]))
    existing = translate_records(records)
    blocks = []
    for index, english in DIALOGUE.items():
        key = f"MSG/MESPAK02.PAK:014:{index:05d}"
        if key not in records or key in existing:
            raise ValueError(f"Missing or already translated source: {key}")
        row = records[key]
        if category(row) != "Story and dialogue":
            raise ValueError(f"Unexpected translation category for {key}")
        blocks.append({
            "archive": row["archive"], "entry": row["entry"],
            "start": row["index"], "category": "Story and dialogue",
            "english": [english],
            "sources": ["Original Japanese ROM"] + (["https://world.digimoncard.com/cards/?card_no=EX10-027&search=true"] if index in (0, 14, 21) else []),
            "review_note": "Party and DigiBank status messages, recruit responses, service counter, and recovery dialogue. Dynamic party-name token ^0 is preserved. DeadlyAxemon follows the official English card spelling." if index in (0, 14, 21) else "Party and DigiBank status messages, recruit responses, service counter, and recovery dialogue. Dynamic party-name token ^0 is preserved.",
        })
    if len(blocks) != 80:
        raise ValueError(f"Expected 80 dialogue strings, got {len(blocks)}")
    destination.write_text(json.dumps({
        "description": "Translate party/bank messages, recruitment responses, service counter, and recovery dialogue in MESPAK02 entry 14.",
        "blocks": blocks,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(destination), "slots": len(blocks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
