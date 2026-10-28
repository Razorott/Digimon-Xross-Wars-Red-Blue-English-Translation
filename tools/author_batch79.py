"""Translate the Kiriha possession and SkullKnightmon alliance sequence."""
from __future__ import annotations

import json

from build import collect_messages, translate_records
from translation_queue import category
from xros_text import ROOT, Rom, rom_paths


DIALOGUE = {
    3: "Nene... R-run...!",
    4: "Even if you send me away, Xros Heart won't disappear! Everyone in the Zone believes in Taiki and Spadamon... Their feelings are what make Xros Heart!",
    5: "Silence, girl!",
    6: "Nene!!",
    12: "Parrotmon scouted from the sky... Things look bad around Earth Fort.",
    23: "What?! Is... is that true? But we can't let ROG break the seal!",
    29: "Thanks, Parrotmon! We'd better get ready, too!",
    30: "Hey, Taiki... Isn't that Kiriha?",
    31: "Yeah... But something's wrong. I can't just leave him like this.",
    32: "Kiriha... What's wrong? I sense something dark coming from you...",
    33: "...I have to overcome my grief...",
    34: "What's going on with Kiriha? He looks dazed.",
    35: "...I don't know. But this isn't the Kiriha we know.",
    36: "Graaah! Xros Heart... I'll destroy you...!",
    38: "Something's wrong with them! It's like someone is controlling them!",
    39: "Kiriha! What happened?! Where's the blue fire in your heart?! Wake up!",
    40: "Grrraah...!",
    41: "Kiriha... Wh-what happened to me...?",
    42: "Ugh... My head... It feels like it's splitting... Put me back in my Xros Loader for now...",
    43: "...Did they come back to their senses?",
    44: "Like Sparrowmon, who we rescued at Spider Ruins... Someone was controlling them, too?",
    45: "Kiriha! Can you hear me? Do you know who I am?!",
    46: "Kiriha!",
    47: "What happened?! What did they do to you?!",
    48: "Ugh... Taiki... What was I doing...?",
    49: "Someone was controlling you! Who did this to you?!",
    50: "...I see. That black shadow... It took control of me...",
    51: "Was that the black shadow that devoured the ROG leaders?",
    52: "Yes. It appeared before me and asked me to join it so it could claim the Legendary Ancient Weapon...",
    53: "You joined ROG?!",
    54: "Don't underestimate me! I bow to no one! I was investigating ROG's movements in this Zone. They're probably trying to revive the Weapon Digimon... We have to stop them at all costs!",
    56: "...So you're Spadamon.",
    58: "...You have to grow stronger. You need to reclaim what you've lost.",
    59: "Taiki! Why does Kiriha know about Spadamon?!",
    60: "Calm down, Shoutmon. Let's hear him out first...",
    61: "Wait... Kiriha?! Where are you going?!",
    62: "Oh no! Earth Fort is just ahead! He went alone to stop them from breaking the seal!",
    63: "Hey, hey, hey! Charging in unprepared where Zeed Millenniummon is... Even for Kiriha, that's way too reckless!",
    65: "Kiriha, are you all right?! ...Where are they?",
    72: "Taiki, stay out of this! I have a score to settle with him.",
    73: "Calm down, Kiriha! You're not acting like yourself. We need a plan, and your Digimon are exhausted from the last battle...",
    74: "...You're right. I got too fired up... I never thought you'd be the one to point that out.",
    75: "Tell us what you know, too...",
    76: "...ROG wants to revive the Legendary Ancient Weapon in Elestou Zone.",
    78: "The Legendary Ancient Weapon isn't just a weapon... It's a Weapon Digimon that transforms into the strongest weapon.",
    80: "...Yes. That's Elestou Zone's secret. Whoever controls a Weapon Digimon could destroy the world, so this Zone has always been targeted. Dynasmon once protected it alongside the Weapon Digimon... But no one knows where Dynasmon went or why the Weapon Digimon were sealed away.",
    82: "Taiki, we don't have much time! My Digimon were knocked out in that last battle. I need your help to stop Zeed Millenniummon!",
    90: "I mean, 'all the way to chocolate'...?",
    91: "...How far is that supposed to be?",
    107: "...The General of Xros Heart, Taiki Kudo... And the General of Blue Flare, Kiriha Aonuma.",
    109: "B-Barbamon?!",
    110: "You know him, Kiriha?",
    111: "He's a vile Digimon who'll do anything to reach his goal. So that's it...!",
    112: "What's it, Kiriha?",
    113: "Damn it...! Was I under Barbamon's illusion technique when I lost consciousness?!",
    117: "Team Blue Flare... It took some effort to trap you in my illusion, but you went down far too easily. What a disappointment.",
    122: "Everyone, get back! He's after something...",
    124: "Barbamon! Face me!",
    125: "Oh, Kiriha Aonuma... You still have the strength to fight? But you're just a man who can't let go of the past. Do you think someone like you can stop me?",
    129: "Kiriha... R-run!",
    130: "No matter what you do, I will never submit! I'll change this whole world with my own power! ...But for now, I entrust Xros Heart to Taiki!",
    131: "Don't talk big, you brat!",
    132: "Kiriha!!",
    140: "I-I saw lightning strike right in front of me... Then everything went dark, and I passed out. What happened to Barbamon and that girl?",
    141: "Barbamon sent Nene to another Zone... Damn it! I couldn't do anything...!",
    145: "Phoenixmon...! I'm glad the Digimon Air Corps is safe!",
    152: "Is this really the time to ramble about something so unimportant?",
    153: "Do you even understand how this happened? Because you're all such useless fools!",
    154: "SkullKnightmon?! And DeadlyAxemon... Are you the real ones?",
    155: "Of course we are. What are you talking about? You and this Zone are running out of time.",
    156: "If Barbamon has secretly been controlling ROG, then his Shadow Guard have seized the Capacitor Tower. You could say this Zone already belongs to him.",
    157: "Why are SkullKnightmon and the others in this Zone...?",
    158: "We were drawn here by the darkness of Armamon, the Weapon Digimon. That's all...",
    159: "So that's the Digimon Barbamon is trying to revive...",
    160: "Hey! And we're supposed to trust them?!",
    161: "Believe what you like... But what if I told you we could find the Zone where Nene was sent?",
    162: "...What?!",
    163: "Just let us travel with you while we look for Nene. That's a fair deal, isn't it?",
    164: "...You really know where Nene is?",
    165: "I don't expect you to trust us, and I won't explain why. But Barbamon has been using our name without permission... That has displeased us, to say the least.",
    166: "If you don't want our help, that's fine with us.",
    167: "...All right. SkullKnightmon, help us.",
    168: "T-Taiki?!",
    169: "SkullKnightmon and DeadlyAxemon have been with Nene before. We have no other lead right now, so we have to trust them.",
    170: "A wise choice. We'll wait nearby. Call for us if you need anything.",
    182: "...Huh? That's strange. The Shadow Guard are gone.",
    183: "Hellooo!♪",
}


def main() -> None:
    destination = ROOT / "translations/batch79.json"
    if destination.exists():
        raise FileExistsError(destination)
    records = collect_messages(Rom(rom_paths()["blue"]))
    existing = translate_records(records)
    blocks = []
    for index, english in DIALOGUE.items():
        key = f"MSG/MESPAK02.PAK:008:{index:05d}"
        if key not in records or key in existing:
            raise ValueError(f"Missing or already translated source: {key}")
        row = records[key]
        if category(row) != "Story and dialogue":
            raise ValueError(f"Unexpected translation category for {key}")
        blocks.append({
            "archive": row["archive"], "entry": row["entry"],
            "start": row["index"], "category": "Story and dialogue",
            "english": [english], "sources": ["Original Japanese ROM", "Project Digimon-name glossary"],
            "review_note": "Continuous Kiriha and Nene rescue arc. Original human names, westernized Digimon names, and established Zone, ROG, and weapon terms are preserved.",
        })
    if len(blocks) != 87:
        raise ValueError(f"Expected 87 dialogue strings, got {len(blocks)}")
    destination.write_text(json.dumps({
        "description": "Translate the Kiriha possession, Barbamon reveal, and SkullKnightmon alliance in MESPAK02 entry 8.",
        "blocks": blocks,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(destination), "slots": len(blocks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
