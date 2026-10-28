"""Translate the route from Elestou Zone into Lost Space, MESPAK02 entry 10."""
from __future__ import annotations

import json

from build import collect_messages, translate_records
from translation_queue import category
from xros_text import ROOT, Rom, rom_paths


DIALOGUE = {
    96: "Thanks, Phoenixmon. You really helped us out.",
    99: "I'm so glad you made it back, Taiki and the others. What a relief!",
    118: "The Digimon who hid when ROG attacked might come back now. Let's wait for them at Sky Fort!",
    123: "You lot are Xros Heart, right? You won't get past us!",
    124: "We were sent to guard the secret entrance... We're Barbamon's Bloody Elite of the Shadow Guard! Deathmon and Boltmon! ...Boluu!",
    125: "W-what is this?! Could this lead to Lost Space?!",
    126: "You! How did you know about this?!",
    127: "I knew it, Taiki! Lost Space is just ahead!",
    128: "We have to defeat Barbamon! Get out of our way!",
    129: "Vooool-Bolboluu! We won't let you through!",
    130: "Your resistance is pointless! Lord Barbamon has already found a place in the Ω Area of Lost Space!",
    131: "We'll gather in the Ω Area and Armamon will absorb us! We'll become the strongest weapon! Boluu! We can't wait to crush you! Bolbolboluu!",
    132: "We're out of time! Let's get to Lost Space!",
    133: "Wait a minute!",
    134: "This Warp Gate isn't on the map. Maybe the data in Elestou Zone has been distorted. I don't know if Barbamon did this... If we go into Lost Space, we have to be ready for anything...",
    135: "What is it, Spadamon? Getting scared?",
    136: "N-no! Of course not! I just want us to be completely prepared!",
    137: "Spadamon is right. Let's make sure we're ready before we go.",
    138: "Stop right there! You won't pass!",
    139: "We were sent to guard the gate to the Ω Area... We're Barbamon's Last Heaven Elite of the Shadow Guard! SlashAngemon and LordKnightmon!",
    140: "Get out of our way! We have to stop Barbamon!",
    141: "We can't allow that. Lord Barbamon is busy preparing to revive Armamon.",
    142: "If they're here, the Ω Area must be close! Let's take them out!",
    143: "Barbamon is just ahead. I'm counting on you, Taiki!",
    144: "You won't reach the Ω Area! This is where you disappear!",
    145: "Guh... Lord... Barbamon... I'm... sorry...",
    146: "Everything... was... for Lord Barbamon... to rule... the world... We... were to become... weapons...",
    147: "The Ω Area is beyond this Warp Gate, right?",
    148: "Yeah... I think so.",
    149: "That Shadow Guard said Barbamon is preparing to revive Armamon.",
    150: "If Barbamon gets Armamon as a weapon, this could turn into a disaster!",
    151: "Armamon... It was a Weapon Digimon, like me... For Dynasmon's sake, too... We must never break its seal!",
    152: "Right. We'll stop Barbamon and protect the peace of this Zone. Let's go to the Ω Area!",
    153: "Compound System. Digicore load initiated. Data fixed at 72%. 28% remaining until limit.",
    154: "Minotaurmon, Pukumon! Add Minervamon to the load.",
    155: "Data input complete. Load increased to 84%.",
    156: "Good. IceDevimon, Arukenimon, and Pharaohmon, too. Load ZeedMillenniummon last.",
    157: "There he is! That's Barbamon!",
    158: "What is he doing?!",
    159: "No...! This is bad! System Ω is running!",
    160: "What?!",
    161: "Stop, Barbamon!",
    162: "Oh... You survived, Xros Heart... Spadamon.",
    163: "Don't touch System Ω! Get away from it now!",
    164: "Spadamon... Your memories have returned, and you know what this system does... Yes! This is the miracle machine that will revive Armamon: System Ω!",
    165: "Stop, Barbamon! Don't you understand?! Armamon could destroy this Zone... No, the entire Digital World!",
    166: "Hah! That power is exactly what I need in a weapon! With Armamon, the Digital World will be mine! Spadamon, you're a Weapon Digimon too. Remember the joy of serving someone strong!",
    167: "It doesn't matter how strong someone is if they're evil! We Weapon Digimon don't exist to destroy things. We fight to protect what matters! If a Weapon Digimon forgets that duty, no one can stop its rampage!",
    168: "Why are the weak so foolish...? Dynasmon seems to have restored memories you didn't need. He was destroyed by Armamon, after all... Useless scrap data.",
    169: "Don't you dare talk about Dynasmon like that!",
    170: "Why get angry when I call something useless scrap data? If Dynasmon's Digicore hadn't been damaged, his data might have been useful enough to replace one of ROG's leaders...",
    171: "ROG's leader Digimon...? What did you do with their data?!",
    172: "System Ω needed Digicores with dark hearts to revive Armamon. I controlled ZeedMillenniummon with its illusion technique and made it gather ROG's leader Digimon. By the way... the Digicore you see on your left belongs to ZeedMillenniummon.",
    173: "How dare you! You sacrificed other Digimon's lives for someone like you!",
    174: "In the Digital World, the weak are swallowed by the strong. Why can't you understand something so obvious? Some of you are useless, too. I'm giving them the chance to be reborn as something stronger.",
    175: "That's nonsense! None of our friends are useless! And after feeding your own allies to Armamon, you're all alone now! You can't beat us!",
    176: "Three weaklings are still weak... But what if my power became threefold?",
    177: "W-what?! Barbamon multiplied!",
    178: "There should be no one else in the world but me. Barbamon after Barbamon, all identical in skill, personality, height, weight,even the shape of our toes,will fill the world. And at the top will stand me, the one who owns Armamon!",
    179: "In one sense, we're all originals. In another, we're all copies.",
    180: "Now suffer attacks that are identical in every way!",
    181: "We did it! We beat him! We made it in time...!",
    182: "No. It's already too late.",
    183: "My Armamon is awakening now!",
    184: "Arise, Armamon! Become my sword!",
    185: "Final data input: 98%... 99%... 100%. Compound limit reached. Armamon restored.",
    186: "...That's Armamon?!",
    187: "It looks nothing like Spadamon...",
    188: "Heh... Heh-heh... Hahahaha! Magnificent! I never imagined it would be this powerful!",
    189: "I am Armamon. Are you the one who awakened me?",
    190: "Yes! I am! I obtained you so I could claim the entire Digital World!",
    191: "That's right, Armamon! Let's test that blade! Start by cutting down every Digimon in Elestou Zone!",
    192: "What?!",
    193: "Now that the strongest Weapon Digimon has returned, Elestou Zone is worthless to me! At least let me enjoy one last thing...!",
    194: "Hurry, Armamon! First, become my weapon...",
    195: "If my owner wishes it, ruling the Digital World is certainly possible. You're right about that; there's no problem at all... The problem is your vulgar behavior.",
    196: "W-what?! Armamon, what are you saying?!",
    197: "You want to own me... You want the Digital World... You want and want and want... You want everything. Such greed does not suit my tastes.",
    198: "...Wait, Armamon... What are you...",
    199: "You've failed, Barbamon. I'm afraid it's time to say goodbye. You don't have what it takes to be my master.",
}


def main() -> None:
    destination = ROOT / "translations/batch84.json"
    if destination.exists():
        raise FileExistsError(destination)
    records = collect_messages(Rom(rom_paths()["blue"]))
    existing = translate_records(records)
    blocks = []
    for index, english in DIALOGUE.items():
        key = f"MSG/MESPAK02.PAK:010:{index:05d}"
        if key not in records or key in existing:
            raise ValueError(f"Missing or already translated source: {key}")
        row = records[key]
        if category(row) != "Story and dialogue":
            raise ValueError(f"Unexpected translation category for {key}")
        blocks.append({
            "archive": row["archive"], "entry": row["entry"],
            "start": row["index"], "category": "Story and dialogue",
            "english": [english], "sources": ["Original Japanese ROM"],
            "review_note": "Final approach to the Ω Area, Barbamon's activation of System Ω, and the resurrection of Armamon. Weapon Digimon's mission to protect others is kept consistent with the previous Dynasmon scene.",
        })
    if len(blocks) != 80:
        raise ValueError(f"Expected 80 dialogue strings, got {len(blocks)}")
    destination.write_text(json.dumps({
        "description": "Translate the approach to the Ω Area and Armamon's resurrection in MESPAK02 entry 10.",
        "blocks": blocks,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(destination), "slots": len(blocks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
