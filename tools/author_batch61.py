"""Author the next reviewed battle-description and NPC-dialogue batch."""
from __future__ import annotations

import json
import textwrap
from pathlib import Path

from build import collect_messages, translate_records
from translation_queue import category
from xros_text import ROOT, Rom, rom_paths


DESCRIPTIONS = {
    (6, 0): "Sweet-talks nearby foes.\nMay cause Confusion.",
    (6, 1): "Reads a foe's intent,\nraising one ally's Defense\nand Speed.",
    (6, 2): "Fires a compressed\nelectric bolt at a foe.",
    (6, 3): "Slashes a foe in a wild\nflurry. Deals dark damage.",
    (6, 4): "Stabs a foe with the\nmagic spear Balmung.\nDeals dark damage.",
    (6, 5): "Pummels a foe with fiery\npunches and kicks.\nDeals fire damage.",
    (6, 6): "Fires alluring energy at\nnearby foes. May cause\nConfusion.",
    (6, 7): "Envelops nearby foes in\nmystic water mist. Deals\npoison damage.",
    (6, 8): "Scatters potent poison\npowder over a foe. Deals\npoison damage.",
    (6, 9): "Fires a strange beam\nfrom its eyes at nearby\nfoes.",
    (6, 10): "Dances and scatters\nfragrant pollen over a foe.\nMay cause Confusion.",
    (6, 11): "A soothing song paralyzes\nnearby foes. May also\ncause Sleep.",
    (6, 12): "Calls down healing rain\nto restore allies' HP.",
    (6, 13): "Cures allies' status\nailments and restores HP.",
    (6, 14): "Restores allies' HP with\na healing light.",
    (6, 15): "Uses machine power to\ncure allies' status ailments\nand restore HP.",
    (6, 16): "Revives allies with the\nhealing power of the earth.",
    (6, 17): "Revives one ally with a\nlight full of compassion.",
    (6, 18): "Cures one ally's status\nailments and restores HP.",
    (6, 19): "Cures allies' status\nailments with a sea tsunami\nand restores HP.",
    (6, 20): "Brings one ally back from\nthe world of the dead.",
    (6, 21): "Restores one ally's HP\nwith an electric current.",
    (6, 22): "Cures allies' status\nailments with a healing wind\nand restores HP.",
    (6, 23): "Revives one ally with a\nradiant light.",
    (6, 24): "Cures allies' status\nailments with a light wave\nand restores HP.",
    (6, 25): "Nanomachines cure allies'\nstatus ailments and restore\nHP.",
    (6, 26): "Slashes a foe with the\nlarge shuriken on its back.\nDeals Light damage.",
    (6, 27): "Cross-slashes a foe with\ntwo holy swords.",
    (6, 28): "Breathes fire on a foe.\nDeals fire damage.",
    (6, 29): "Traps nearby foes in a\nspace-time stone. May cause\ninstant death.",
    (6, 30): "Blasts nearby foes with a\nwave of light. Deals Light\ndamage.",
    (6, 31): "Slices a foe with a huge\nanchor. May cause\nConfusion.",
    (6, 32): "Melts a foe with a rainbow\nheat ray. Deals poison\ndamage.",
    (6, 33): "Slashes at light speed\nwith two swords. Greatly\nraises Melody Capture rate.",
    (6, 34): "Freezes nearby foes in an\nabsolute-zero blizzard. May\ncause Paralysis.",
    (6, 35): "Sets off a fierce flash\nexplosion near foes. Lowers\ntheir Defense.",
    (6, 36): "Swings the crane on its\nback and smashes a foe.",
    (6, 37): "Traps and destroys nearby\nfoes in another dimension.\nMay cause instant death.",
    (6, 38): "Teleports a dark sword\nthrough nearby foes.",
    (6, 39): "Fires dark arrows from\nboth Evil Eyes. May cause\ninstant death.",
    (6, 40): "Swallows nearby foes in an\nunderwater whirlpool.",
    (6, 41): "Fires a dark orb to\ndestroy nearby foes.",
    (6, 42): "Summons a hellbeast to\nattack a foe. Deals dark\ndamage.",
    (6, 43): "Burns nearby foes with\nvengeful hellfire. Deals\nfire damage.",
    (6, 44): "Destroys nearby foes' data\nwith dark gas.",
    (6, 45): "Finds nearby foes'\ncoordinates and sends them\nto another world. May cause\nConfusion.",
    (6, 46): "Fires dark matter to\nerase nearby foes. Deals\ndark damage.",
    (6, 47): "Pierces a foe without\nmercy with its right-arm\nlance.",
    (6, 48): "Fires dark bullets from\nBerenjena. Deals dark\ndamage.",
    (6, 49): "Buries a foe beyond\nspace and time. May cause\nParalysis.",
    (7, 0): "Fires high-temperature\ndark beams from both\nshoulders.",
    (7, 1): "Scorches nearby foes with\nthe flames of holy light.",
    (7, 2): "Speeds up a foe's body\nclock, causing it to age.\nMay cause instant death.",
    (7, 3): "Fires beams at nearby foes\nfrom a holy shield. May\ncause instant death.",
    (7, 4): "Slashes with a sword and\na fiery shock wave. Deals\nfire damage.",
    (7, 5): "Envelops nearby foes in\nthe darkness of death. May\ncause instant death.",
    (7, 6): "Slashes nearby foes with\na kudagitsune familiar.\nDeals water damage.",
    (7, 7): "Cuts a foe with the divine\nsword Burtgang.",
    (7, 8): "Sweeps nearby foes with a\nbroom. Lowers their\nDefense.",
    (7, 9): "Gathers atmospheric\nenergy and blasts nearby\nfoes. Deals fire damage.",
    (7, 10): "Fires an energy wave from\na cannon. Deals electric\ndamage.",
    (7, 11): "Fires gathered light at\nnearby foes. Lowers their\nIntelligence.",
    (7, 12): "Fuses energy in both hands\nand burns a foe. Deals fire\ndamage.",
    (7, 13): "Amplifies light and blasts\nnearby foes. Deals Light\ndamage.",
    (7, 14): "Rains light-infused candy\non nearby foes. May cause\nSleep.",
    (7, 15): "Charges with its whole\nbody in flames. Lowers the\nfoe's Speed.",
    (7, 16): "Slashes nearby foes with\nthe holy sword Omega Blade.",
    (7, 17): "Strikes nearby foes with\nelectric shocks from three\narms. Deals electric damage.",
    (7, 18): "Smashes a foe with a\nbullet-shaped hammer.\nDeals fire damage.",
    (7, 19): "Destroys data with a dark\ncomputer virus. Deals dark\ndamage.",
    (7, 20): "Unleashes its full energy\nto burn a foe. May cause\ninstant death.",
    (7, 21): "Burns nearby foes with\nflames from its mouth.",
    (7, 22): "Scorches a foe with vile\nflames. May cause instant\ndeath.",
    (7, 23): "Rams a foe with its\nradiant, full-metal body.",
    (7, 24): "Explodes sacred energy to\nknock down nearby foes.",
    (7, 25): "Blasts nearby foes with a\ngiant missile. Lowers their\nSpeed.",
    (7, 26): "Bombards nearby foes with\nits full arsenal. Lowers\ntheir Speed.",
    (7, 27): "Pierces nearby foes with a\nrain of spikes.",
    (7, 28): "Fires an ultra-high-voltage\nelectric orb.",
    (7, 29): "Gathers electric power to\nslice through foes and the\nspace around them.",
    (7, 30): "Unleashes all its energy\nin an explosion. Deals fire\ndamage.",
    (7, 31): "Gathers electric power in\nits horn and fires at nearby\nfoes.",
    (7, 32): "Burns nearby foes with a\nblazing beam.",
    (7, 33): "Slashes with light-powered\nblades on both arms. Lowers\nthe foe's Speed.",
    (7, 34): "Fires energy torpedoes at\nnearby foes. Deals fire\ndamage.",
    (7, 35): "Cuts with the giant sword\nRyuzanmaru. Deals poison\ndamage.",
    (7, 36): "Rends a foe with huge,\nrazor-sharp claws. Deals\nfighting damage.",
    (7, 37): "Hurls a Battle Axe at\nnearby foes.",
    (7, 38): "Slashes nearby foes with\nthe Otoko Damashii dagger.\nDeals fire damage.",
    (7, 39): "Channels water through\nMjolnir to smash a foe.",
    (7, 40): "Sharpens its electric whip\nand thrusts its tip into a\nfoe.",
    (7, 41): "Binds a foe and shocks it.\nMay cause Paralysis.",
    (7, 42): "Hurls a lightning spear to\nbring down divine\npunishment.",
    (7, 43): "Hurls a spear infused with\ndark power.",
    (7, 44): "Fires a light arrow from\nthe holy bow Muspelheim.",
    (7, 45): "Blasts nearby foes with\nhigh-voltage energy.",
    (7, 46): "Breathes freezing air to\nfreeze a foe. May cause\nParalysis.",
    (7, 47): "Fires dark-energy orbs at\nnearby foes.",
    (7, 48): "Freezes a foe after\nslashing it with an\nabsolute-zero sword.",
    (7, 49): "Fires a water-infused\nspear with a will of its own.\nDeals poison damage.",
}

STORY = {
    "MSG/MESPAK02.PAK:017:00107": (
        "Huh? That's strange... I can usually save here... Did the save terminal break?"
    ),
    "MSG/MESPAK02.PAK:017:00143": (
        "You got Sky Fortress back for us... Thank you so much!\n\n"
        "I'd like to join your team, too! If you don't mind, come talk to me anytime!"
    ),
    "MSG/MESPAK02.PAK:018:00049": (
        "Thanks for taking back Capacitor Tower... You really helped me out, kwa!"
    ),
    "MSG/MESPAK02.PAK:018:00054": (
        "Welcome to the Skull City DigiFarm Shop!\nYeah! Rock you! Bomber!"
    ),
    "MSG/MESPAK02.PAK:018:00062": (
        "Hoge-hoge♪ No one can stop the Donos' song!♪\n"
        "Who could ever silence our voices?\n"
        "Only earthquakes, thunder, volcanic eruptions, smoke... and my mom!♪"
    ),
    "MSG/MESPAK02.PAK:018:00067": (
        "Welcome to the Kumonos City DigiFarm Shop!\nYeah! Howdy! Bomber!"
    ),
    "MSG/MESPAK02.PAK:018:00074": (
        "Welcome to the Papyrus City DigiFarm Shop!\nYeah! Gotcha! Bomber!"
    ),
}

TICKETS = {
    29: "Koromon",
    30: "Guilmon",
    31: "Palmon",
    32: "Gomamon",
    33: "DemiDevimon",
    34: "Lopmon",
    35: "Goblimon",
    36: "Lucemon",
    37: "Dracomon",
    38: "Phascomon",
    39: "Devimon",
    40: "Numemon",
    41: "Kabuterimon",
    42: "Bakemon",
    43: "Togemon",
    44: "Guardromon",
    45: "ExVeemon",
    46: "Stingmon",
    47: "Kurisarimon",
    48: "DarkTyrannomon",
    49: "Ikkakumon",
}

def main() -> None:
    out = ROOT / "translations/batch61.json"
    if out.exists():
        raise FileExistsError(f"Will not overwrite {out}")
    records = collect_messages(Rom(rom_paths()["blue"]))
    already = translate_records(records)
    blocks: list[dict] = []
    reviewed: list[tuple[str, str, str, list[str]]] = []
    seen: set[str] = set()

    def add(seed: str, english: str, expected: str, note: str,
            sources: list[str] | None = None, wrap: int | None = None) -> None:
        if seed not in records:
            raise KeyError(f"Unknown message: {seed}")
        row = records[seed]
        if category(row) != expected:
            raise ValueError(f"Unexpected category for {seed}: {category(row)}")
        if seed in already:
            raise ValueError(f"Already translated: {seed}")
        if wrap:
            english = "\n".join(
                "\n".join(textwrap.wrap(line, width=wrap, break_long_words=False,
                                         break_on_hyphens=False)) if line else ""
                for line in english.split("\n")
            )
        aliases = [r for r in records.values()
                   if r["source"] == row["source"] and category(r) == expected
                   and r["id"] not in already]
        for alias in aliases:
            if alias["id"] in seen:
                raise ValueError(f"Duplicate assignment: {alias['id']}")
            seen.add(alias["id"])
            blocks.append({
                "archive": alias["archive"], "entry": alias["entry"],
                "start": alias["index"], "category": expected,
                "english": [english], "sources": sources or ["Original Japanese ROM"],
                "review_note": note,
            })
        reviewed.append((seed, english, note, sources or ["Original Japanese ROM"]))

    move_note = (
        "Translated from the original Japanese battle-effect text. Status, stat, "
        "damage-type, and Melody Capture terms follow the project's established UI wording."
    )
    for (entry, index), english in DESCRIPTIONS.items():
        add(f"MSG/MESPAK04.PAK:{entry:03d}:{index:05d}", english,
            "Move and item descriptions", move_note, wrap=26)

    ticket_note = (
        "The original identifies this as a Service Counter gift ticket. The "
        "species-only inventory label is retained to match the game's short item "
        "name; the description states who gives the gift and where to redeem it."
    )
    for index, name in TICKETS.items():
        item_key = f"MSG/MESPAK00.PAK:000:{4428 + index - 29:05d}"
        if item_key not in already or already[item_key]["english"] != name:
            raise ValueError(f"Ticket recipient does not match the reviewed name table: {item_key}")
        sources = ["Original Japanese ROM", *already[item_key].get("sources", [])]
        add(f"MSG/MESPAK04.PAK:041:{index:05d}",
            f"Gift from:\n{name}\nRedeem at Service Counter.",
            "Move and item descriptions", ticket_note,
            list(dict.fromkeys(sources)))

    story_note = (
        "NPC and area wording translated from the original Japanese story script; "
        "established area names and character voice are preserved."
    )
    for seed, english in STORY.items():
        add(seed, english, "Story and dialogue", story_note,
            ["Original Japanese ROM"], wrap=15)

    out.write_text(json.dumps({
        "description": (
        "Translate 100 additional battle-technique descriptions, 21 gift-ticket "
        "descriptions, and the next NPC dialogue set for Sky Fortress and nearby "
        "DigiFarm shops."
        ),
        "blocks": blocks,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Batch 61 review", "",
        f"Added {len(blocks)} message slots: 100 battle-effect descriptions, "
        f"21 gift-ticket descriptions, and {len(blocks) - 121} story/NPC dialogue slots.",
        "Battle-effect descriptions cover entries 6 and 7 of MESPAK04. Japanese source IDs are retained in the build review; all lines are wrapped to the 26-character UI ceiling.",
        "The story set includes the broken save-terminal remark, Sky Fortress thanks, Kuwagamon's speech tic, and three DigiFarm shop greetings. Ticket recipients use the reviewed Western spellings from the glossary.",
        "",
        "| Seed ID | English | Evidence |",
        "|---|---|---|",
    ]
    for seed, english, note, sources in reviewed:
        cell = english.replace("|", "\\|").replace("\n", "<br>")
        lines.append(f"| `{seed}` | {cell} | {'; '.join(sources)} |")
    (ROOT / "translations/review_batch61.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(out), "slots": len(blocks),
                      "authored_descriptions": len(DESCRIPTIONS),
                      "authored_ticket_descriptions": len(TICKETS),
                      "authored_story_groups": len(STORY)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
