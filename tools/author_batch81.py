"""Translate the RookChessmon and Garbagemon tower encounters."""
from __future__ import annotations

import json

from build import collect_messages, translate_records
from translation_queue import category
from xros_text import ROOT, Rom, rom_paths


DIALOGUE = {
    90: "Ugh... There has to be a way to drive him away...",
    91: "I know! Hit him with a phrase that really stings! That might make him leave!",
    92: "A way to drive squid away? Wh-what does that even mean?!",
    93: "Here I go... Take this!!",
    94: "Now, Spadamon!",
    95: "Y-your... Your mom is seafood!!",
    96: "Gwaaah!!",
    97: "We did it!!",
    98: "All right!!",
    99: "...Wait. That worked?",
    100: "Well, we beat him, so it worked!",
    102: "How did he know my secret weakness, something I'd never told anyone...? Barbamon is terrifying...",
    103: "No... Maybe he just guessed from your looks? I hear squid makes cats sick.",
    104: "Spadamon does look kind of like a cat, so...",
    105: "I'm not a cat!",
    106: "Come on! Let's move on to the next one!",
    107: "Checkmate!",
    108: "Careful! It's a Shadow Guard!",
    109: "I'm RookChessmon, the Lazy Elite in Lord Barbamon's Shadow Guard, sent to protect this Capacitor Tower! ...Right?",
    110: "Damn, what a ridiculous guy!",
    111: "Is he plotting something...?",
    112: "You're in checkmate, with no moves left! You know you'll lose, so why fight? ...Right?",
    113: "Uh... Checkmate? No moves left...? What does that mean?",
    114: "You don't get it, do you? I'll never lose! And if I never lose, you can't beat me! ...Right?",
    115: "Um... What?",
    116: "Stay alert, Spadamon... Here he comes!",
    117: "How about that? Checkmate!",
    118: "Sorry, but you can't take the King. No matter what, I'm only a Rook... Right?",
    119: "I'm aiming to be the Digimon King! I'm not losing to a Rook!",
    120: "That's a tall order... The real King is Lord Barbamon, who commands the Legendary Weapon Digimon... Right?",
    121: "We won't let that happen!",
    122: "Jumping off a cliff without seeing what's ahead is stupid. Apologize to Lord Barbamon while you can! ...Right?",
    123: "Even if you say that, I'm not changing my mind!",
    124: "If we really reach checkmate, you'll suffer much worse than this! I'll go be absorbed by Lord Barbamon now... Right?",
    125: "Hey! Wait...",
    126: "Barbamon treats us like pawns!",
    127: "He doesn't get it... I'm the one who's going to become Digimon King someday! ...Right?",
    128: "You caught his catchphrase...!",
    129: "Um... Anyway, I'll switch the tower back now.",
    131: "All right! This tower's mode has been switched!",
    132: "Hmm...?",
    133: "What's wrong?",
    134: "Hey, were those all the Capacitor Towers we've seen? Weren't there more somewhere?",
    135: "Now that you mention it... When we defeated Pharaohmon in Papyrus Desert, he said the same thing. Spadamon said there were seven towers, not six.",
    136: "Didn't he just count wrong?",
    137: "...Maybe?",
    138: "Then count them with DigiNoir! First there's Sky Fort, then Knuckle Coast... Ah, I'm getting hungry...",
    139: "Hahaha... Let's keep moving for now.",
    140: "When we get back to Sky Fort, let's ask Patamon and the others. They might know something.",
    141: "One little garbage!",
    142: "Two little garbage!",
    143: "Three little garbage!",
    144: "The three of us jingle together! We're the Heavy-Smell Elite in Lord Barbamon's Shadow Guard, sent to protect this Capacitor Tower... We are the Garbagemons!",
    145: "A Shadow Guard...! Is that the leader trio, or is one of them the real one?",
    146: "W-wait! More importantly... They smell awful!",
    147: "Grimy garbage is filthy garbage!",
    148: "Dirty garbage is odious garbage!",
    149: "Messy garbage is smelly garbage!",
    150: "Frumpy, stinky chunk of garbage!!!",
    151: "I don't understand a word they're saying!",
    152: "D-don't move, you guys... The smell is coming this way...",
    153: "You'll understand in a second, grubby!",
    154: "We'll knock some sense into you with our stink!",
    155: "That smell will seep deep into your memories!",
    156: "Wh-what the heck is that...?",
    157: "I don't understand a word, but their strength and stench are coming through loud and clear!",
    159: "Take that! You're paralyzed!",
    160: "What's wrong, Taiki? You're talking funny.",
    161: "Looks like he's holding his nose because they stink...",
    162: "Laugh at garbage and Lord Barbamon will cry!",
    163: "Garbage piles up into Lord Barbamon!",
}


def main() -> None:
    destination = ROOT / "translations/batch81.json"
    if destination.exists():
        raise FileExistsError(destination)
    records = collect_messages(Rom(rom_paths()["blue"]))
    existing = translate_records(records)
    blocks = []
    for index, english in DIALOGUE.items():
        key = f"MSG/MESPAK02.PAK:009:{index:05d}"
        if key not in records or key in existing:
            raise ValueError(f"Missing or already translated source: {key}")
        row = records[key]
        if category(row) != "Story and dialogue":
            raise ValueError(f"Unexpected translation category for {key}")
        blocks.append({
            "archive": row["archive"], "entry": row["entry"],
            "start": row["index"], "category": "Story and dialogue",
            "english": [english], "sources": ["Original Japanese ROM", "Project Digimon-name glossary"],
            "review_note": "Continuous scene translation. RookChessmon's checkmate and rook wordplay and the Garbagemons' intentionally absurd chant are adapted to preserve the original jokes.",
        })
    destination.write_text(json.dumps({
        "description": "Translate the RookChessmon and Garbagemon Capacitor Tower encounters in MESPAK02 entry 9.",
        "blocks": blocks,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(destination), "slots": len(blocks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
