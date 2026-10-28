"""Translate Armamon's awakening and first confrontation, MESPAK02 entry 11."""
from __future__ import annotations

import json

from build import collect_messages, translate_records
from translation_queue import category
from xros_text import ROOT, Rom, rom_paths


DIALOGUE = {
    0: "W-whaaa...?!",
    1: "What in the world was that?!",
    2: "Hmm... Not bad as weapons.",
    3: "Spadamon! Is that what he means by becoming a weapon?!",
    4: "N-no! Weapon Digimon turn themselves into weapons! Forcing another Digimon to become one is...!",
    5: "Both of you, calm down! Maybe he still remembers protecting this Zone. Let's talk to him first.",
    6: "Armamon! Please, listen to us!",
    7: "I am Armamon. Who are you...?",
    8: "We won't use your power to take over the world. We fought alongside Dynasmon to protect this Zone. Do you remember those days?",
    9: "...So you're Dynasmon's allies.",
    10: "A trace of his data still surrounds you. You must have come into contact with him.",
    11: "Y-yeah! We were Dynasmon's friends,your partner's allies! We're not your enemies!",
    12: "I see. You are Dynasmon's allies... Which means you're my enemies!",
    13: "How did you get that from what we said?!",
    14: "Armamon forgot what Weapon Digimon are meant to do! When Dynasmon sealed him away, he was already like this... Nothing changed!",
    15: "Dynasmon! He discovered my plan... and sealed me away like this!",
    16: "Your plan...?",
    17: "Gather every Digimon in this Zone into System Ω... and turn them into a single weapon! That is my plan!",
    18: "W-what?! You can't turn Digimon who aren't Weapon Digimon into weapons! That's wrong!",
    19: "Nyaaah!",
    20: "Spadamon?! Are you all right?!",
    21: "B-be careful... That attack... turned Barbamon into a weapon... I'm a Weapon Digimon, so... I'm... fine.",
    22: "Seriously...?",
    23: "Stop this, Armamon!",
    24: "Why don't Dynasmon... or any of you... understand how wonderful my plan is?! This is the only way to protect the Zone from every invader! I won't let anyone stand in my way!",
    25: "...Where?",
    26: "Huh?",
    27: "Where are you...?",
    28: "W-what do you mean...?",
    29: "Meow... Why... all of a sudden...?",
    30: "...Where is Dynasmon?",
    31: "Are you all right?!",
    32: "If I weren't a Weapon Digimon, he'd have turned me into a weapon just now...",
    33: "System Ω. Mainframe access. Searching for Dynasmon. Beginning full scan...",
    34: "...Checkpoint 82039... Search complete. Dynasmon: Digimon ID lost. Dynasmon: Digimon ID lost. Last confirmed location: Stealth Canyon.",
    35: "...Armamon... Dynasmon is gone...",
    36: "B-but... Why...?",
    37: "Silence!",
    38: "W-what...? What is Armamon doing?",
    39: "Lost...? Dynasmon! No... It can't be...!",
    40: "What's happening? What is Armamon trying to do?",
    41: "It looks like he's going back into that machine. Maybe he's going to seal himself away again.",
    42: "No... Something feels wrong.",
    43: "Look!",
    44: "Whaaaat?! It can't be...!",
    45: "Spadamon, what is it?!",
    46: "Armamon is using System Ω to absorb data! He said Dynasmon's data was still around us... He must be searching for it!",
    47: "Then he's going to absorb the data here with System Ω and use it to reconstruct Dynasmon...?",
    48: "Can he really do that?!",
    49: "No! Even if he reconstructs the data, it won't be Dynasmon!",
    50: "Why...? How could he not understand that...?",
    51: "Compound System. Free-load sequence initiated. Data owners' functions will be temporarily restricted. Compound System. Free-load sequence initiated. Data owners' functions will be temporarily restricted.",
    52: "Taiki! Are you all right?!",
    53: "S-somehow... What happened...?",
    54: "Taiki! This is bad! Look,quickly!",
    55: "Dynasmon... Where are you...?",
    56: "Is that... Armamon?",
    57: "I've never seen a Digimon that terrifying...!",
    58: "No... That's Ω Armamon Burst Mode! The legendary Weapon Digimon of Elestou Zone...",
    59: "How are we supposed to fight something like that...?",
    60: "Collecting Digimon data: 90384795038910. Acquiring Digimon data: 54395084537. Dynasmon ID: unconfirmed. No trace of Dynasmon detected.",
    61: "Dynasmon... Why... Why don't you understand me...? I still need more data... If I go to Stealth Canyon...",
    62: "Spadamon! We can't let him out of here!",
    63: "I'm a Weapon Digimon, so I might be able to access System Ω... Wait here! I'll try!",
    64: "Security protocol activated. Gate code rejected. Beginning full lockdown of the Ω Area...",
    65: "What...?",
    66: "Ω Area full lockdown complete... Ω Area full lockdown complete...",
    67: "Why...? Why are you stopping me?!",
    68: "Aaaaaaaargh...!",
    69: "I managed to seal off the Ω Area...!",
    70: "What'll happen to him now?!",
    71: "Armamon is fully connected to System Ω. If we leave him alone, he'll swallow Lost Space... and then all of Elestou Zone! Taiki, Shoutmon... This is our final battle! Please, lend me your strength!",
    72: "Of course! We'll defeat him and all three of us will return to Sky Fort! Let's go, everyone!",
    73: "Yeah!",
    74: "Leave it to us!",
    75: "Aaaaaaaaaaaaaaaargh...!",
    76: "...Dyna...smon... Where... are... you...?",
    77: "...Armamon's Digicore abnormality detected... Forced download terminated...",
    78: "Forced termination failed... Abnormality detected in Armamon's Digicore... Digicore damage: 10%...",
    79: "Armamon's Digicore is collapsing! It can't contain all the data flowing into it! It's almost at overflow... There isn't much time!",
    80: "Do we have to erase him completely...? But how can we stop something that huge?!",
    81: "Armamon Digicore damage: 20%... 30%... 40%...",
    82: "...Don't... leave... me...",
    83: "There has to be... something we can do!",
    84: "Armamon Digicore damage: 50%... 70%... 80%...",
    85: "N-no! Overflow is starting!",
    86: "Duuuynasmoooon!",
    87: "Armamon Digicore damage: 90%... 100%... Code Red. Code Red. Evacuate Lost Space immediately...",
    88: "This is bad...! It's a black hole! If it sucks us in, we won't get back out!",
    89: "We have to get out of here!",
    90: "The Warp Gate is broken...?!",
    91: "We sealed off the Ω Area, so we can't use the Gate Disk... ...But I might be able to...",
    92: "Are you two ready?",
    93: "Is there another way back?",
    94: "...Of course! I can use the remaining functions of System Ω to transport you both back to Sky Fort!",
    95: "Then hurry up and say so! You scared me!",
    96: "H-haha... Sorry! It took a while to find the system... But don't worry. You'll both make it back safely!",
    97: "Spadamon... You aren't planning to stay here alone, are you?!",
    98: "What's wrong, Taiki? Why the worried look...? Don't worry. I can stop Armamon...",
    99: "No! I can't leave you behind! There's no way I can do that!",
}


def main() -> None:
    destination = ROOT / "translations/batch85.json"
    if destination.exists():
        raise FileExistsError(destination)
    records = collect_messages(Rom(rom_paths()["blue"]))
    existing = translate_records(records)
    blocks = []
    for index, english in DIALOGUE.items():
        key = f"MSG/MESPAK02.PAK:011:{index:05d}"
        if key not in records or key in existing:
            raise ValueError(f"Missing or already translated source: {key}")
        row = records[key]
        if category(row) != "Story and dialogue":
            raise ValueError(f"Unexpected translation category for {key}")
        blocks.append({
            "archive": row["archive"], "entry": row["entry"],
            "start": row["index"], "category": "Story and dialogue",
            "english": [english], "sources": ["Original Japanese ROM"],
            "review_note": "Armamon's plan and the immediate battle setup, translated in context with the Dynasmon/Spadamon scene.",
        })
    if len(blocks) != 100:
        raise ValueError(f"Expected 100 dialogue strings, got {len(blocks)}")
    destination.write_text(json.dumps({
        "description": "Translate the first half of the final Armamon confrontation in MESPAK02 entry 11.",
        "blocks": blocks,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(destination), "slots": len(blocks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
