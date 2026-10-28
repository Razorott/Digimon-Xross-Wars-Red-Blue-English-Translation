"""Author the next batch of battle and item-effect descriptions."""
from __future__ import annotations

import json
import textwrap
from pathlib import Path

from build import collect_messages, translate_records
from translation_queue import category
from xros_text import ROOT, Rom, rom_paths


# Japanese effect descriptions from MESPAK04 entries 8-13. These are concise
# effect summaries, not move-name substitutions. Explicitly named weapons are
# rendered with the project's English romanization style.
DATA = {
    8: [
        "Scatters heart orbs that sap nearby foes' will. May cause Confusion.",
        "Slashes with a holy sword born from its bracelet. Deals Light damage.",
        "Releases mummy gas at foes. Greatly boosts Melody Capture rate.",
        "Fires a supersonic electric wave.",
        "Releases the Gorgon shield's dark shock wave. Deals Poison damage.",
        "Fires a dark-energy orb that explodes near foes.",
        "Ambushes nearby foes with countless dark bats.",
        "Releases evil spirits to attack nearby foes. Deals Poison damage.",
        "Scorches nearby foes with bat-shaped dark power. May cause Blindness.",
        "Unleashes dark energy. Deals electric damage.",
        "Sticks on and detonates a Light-sealed talisman. May cause Paralysis.",
        "Fires electric beams from both hands.",
        "Launches homing missiles from its body. Lowers the foe's Speed.",
        "Stabs with the twin Royal Meister swords. Deals electric damage.",
        "Fires blades of electric energy from its arms.",
        "Throws a bomb shaped like a glove.",
        "Blasts nearby foes with its arm-mounted Psycho Blaster.",
        "Fires energy like a flying dragon's breath.",
        "Fires a Light shock wave from its arm-mounted pile bunker.",
        "Fires a laser from high above and scorches foes. Deals fire damage.",
        "Throws a dark bomb filled with computer viruses.",
        "Fires dark missiles from both arms. Deals dark damage.",
        "Calls a thundercloud and strikes nearby foes with lightning.",
        "Fires a right-arm missile. Engulfs foes in flames, lowering Defense.",
        "Rusts nearby foes with a wave of Light. Deals Poison damage.",
        "Fires fire bullets from its arm-mounted revolver. Deals fire damage.",
        "Fires missiles from both arms to scorch foes. Deals fire damage.",
        "Burns nearby foes with scorching flames.",
        "Turns both hands into guns and fires Light energy. Deals Light damage.",
        "Traps nearby foes in a hallucinatory mist. May cause Confusion.",
        "Calls down meteors on nearby foes.",
        "Pierces a foe with dark power from its arm-mounted rapier.",
        "Slashes nearby foes with electric petals. Lowers Defense.",
        "Unleashes a mighty water dragon at nearby foes.",
        "Slashes nearby foes with electric spider silk. Lowers Speed.",
        "Moves at electric speed and cuts nearby foes. May cause Paralysis.",
        "Slashes with a giant chain sickle filled with dark power.",
        "Destroys nearby foes' data with a Light vibration.",
        "Spins its turbine at high speed for a heavy blow.",
        "Crashes a giant iron ball into nearby foes. Deals physical damage.",
        "Charges nearby foes with a mountain-breaking tackle.",
        "Fires compressed energy in a huge blast. Deals Water damage.",
        "Pierces a foe with a giant horn charged with electricity.",
        "Throws a water-charged trident at a foe. May cause Sleep.",
        "Rends a foe with the sharp claws on both arms.",
        "Strikes with its removed helmet. Greatly raises Melody Capture rate.",
        "Creates a storm around nearby foes. May cause Confusion.",
        "Scorches nearby foes with flames from its chest. Deals fire damage.",
        "Slashes a foe with sharp, electrically charged scissors.",
        "Spins a shining axe to slash nearby foes. Deals Light damage.",
    ],
    9: [
        "Dives at nearby foes and pierces them with its shining horn.",
        "Fires a volley of lasers to scorch nearby foes. Deals Poison damage.",
        "Swings its beloved giant sword with a flash of Light.",
        "Freezes nearby foes with absolute-zero cold. May cause Paralysis.",
        "Blasts nearby foes with the cold raised by its thick fur.",
        "Blows foes away with a tornado of holy earth. May cause Paralysis.",
        "Fires water hardened into crystals. Deals Water damage.",
        "Fires lightning from its head feathers. Lowers Speed.",
        "Strikes nearby foes with lightning from Thor Hammer.",
        "Fires lightning at nearby foes from the blade on its head.",
        "Unleashes a summoned evil god's dark power. Raises Melody Capture rate.",
        "Swallows nearby foes in a flood of bubbles. Deals Water damage.",
        "Slashes with water blades formed by crossing its forepaws.",
        "Fires a destructive dark beam with a roar.",
        "Blasts nearby foes with a Light shock wave. Lowers Speed.",
        "Slices foes with an ultra-fast vacuum wave.",
        "Fires crushing water pressure repeatedly. Deals physical damage.",
        "Fires a beam of Light energy from its mouth.",
        "Fires energy from its body mechanisms. Deals electric damage.",
        "Fires Light-charged feathers in a shock wave.",
        "Rakes a foe with claws hidden inside its hands.",
        "Scorches nearby foes with a legendary monster's power. Lowers Defense.",
        "Summons Light crystals and hurls them at a foe. May cause Paralysis.",
        "Slices nearby foes with a legendary sword of Light. Deals Light damage.",
        "Swallows nearby foes in a whirlwind spun with its staff.",
        "Fires holy energy from its forepaws. Deals dark damage.",
        "Strikes nearby foes with disaster lightning. Lowers Speed.",
        "Uses volcanic power for a lariat. May cause Paralysis.",
        "Gathers energy in its wings and fires flames. Deals fire damage.",
        "Dashes past and slices foes like a gale.",
        "Unleashes a fierce barrage at nearby foes. Deals Poison damage.",
        "Drives in its left claw and charges with a spin.",
        "Draws its katana and strikes with fighting spirit. Lowers Defense.",
        "Delivers an ultra-fast slash with two katanas. Deals physical damage.",
        "Draws a sun with its katana and slashes nearby foes. Lowers Intelligence.",
        "Blasts nearby foes with a giant rocket cannon. Deals dark damage.",
        "Scorches nearby foes with a heat ray from its arm.",
        "Lifts nearby foes with fierce strikes, then knocks them down.",
        "Scorches a foe with a superheated fireball. Deals fire damage.",
        "Corrodes nearby foes with dark breath. May cause instant defeat.",
        "Charges with flames around its body. Lowers Intelligence.",
        "Whips a foe with a giant electric chain.",
        "Rends a foe with claws as hard as steel.",
        "Surprises nearby foes with an electric drill. May cause Confusion.",
        "Stuns nearby foes with an electrified flying kiss.",
        "Shatters nearby foes' minds with dark power. May cause Confusion.",
        "Slashes a foe with claws wreathed in scorching flames.",
        "Charms a foe with a holy heart. May cause Confusion.",
        "Fires a wave of flame energy from its waist cannon.",
        "Traps foes in subspace with a Light sword. May cause instant defeat.",
    ],
    10: [
        "Fires a Light-charged heart at nearby foes. May cause Sleep.",
        "Fires powerful lightning as Light arrows.",
        "Fires seven Light orbs at nearby foes. Lowers Intelligence.",
        "Covers nearby foes in endless darkness. Deals dark damage.",
        "Shatters foes' hearts with a dark crystal. May cause Confusion.",
        "Drains data from a foe's head with a ray gun. Drains MP.",
        "Envelops a foe in a sorrowful cry. May cause Confusion.",
        "Slashes with a greatsword made from a fire sword and shield.",
        "Fires flames filled with dark power. Deals fire damage.",
        "Strikes nearby foes with a Light energy orb.",
        "Unleashes a dark aura from its wings.",
        "Erases foes' will with its staff. Greatly raises Melody Capture rate.",
        "Fires the aura of a flaming lion. Deals fire damage.",
        "Scorches nearby foes with a scorching sun orb.",
        "Dances through foes with Noir Luna. May cause Confusion.",
        "Slashes a foe with a lunar hook. May cause Confusion.",
        "Surrounds nearby foes with an aura and breaks them down with electricity.",
        "Wraps a foe in its tentacles and crushes it. May cause Paralysis.",
        "Destroys nearby foes with a beam that warps space.",
        "Splits the earth with Olympia and destroys a foe. Deals fire damage.",
        "Slashes nearby foes with a Light blade. May cause instant defeat.",
        "Scorches foes with a 100,000-degree beam. Lowers Intelligence.",
        "Slashes nearby foes with the BAN-CHO Blade.",
        "Floods the area with light from Digi-Entelecheia. Restores HP.",
        "Rakes a foe with long, Light-charged claws. May cause Blindness.",
        "Purifies nearby foes with a storm of leaves. May cause Confusion.",
        "Fires a Light-powered energy blast at a foe.",
        "Rains Pickmon on nearby foes. Deals physical damage.",
        "Summons a blue flame dragon to scorch a foe. May cause instant defeat.",
        "Rakes a foe with Light-charged claws.",
        "Punches a foe with a golden fist.",
        "Charges with flames around its body. Lowers Defense.",
        "Scorches a foe with a blast of fire breath.",
        "Knocks down a foe with a powerful headbutt.",
        "Fires a powerful fireball at a foe. Deals fire damage.",
        "Scorches nearby foes with crimson fire breath.",
        "Slashes a foe with a plasma blade. Lowers Speed.",
        "Blows nearby foes away with a giant tornado.",
        "Scorches a foe with an X-shaped energy wave. Lowers ATK.",
        "Burns a foe with an intense heat ray.",
        "Burns a foe with superheated flames.",
        "Blasts a foe with water breath.",
        "Slashes a foe with giant, shrimp-like claws. Deals Water damage.",
        "Strikes a foe with a powerful freezing punch.",
        "Manipulates chi and smashes a foe with water power.",
        "Fires an ink-filled orb at a foe. May cause Blindness.",
        "Slices nearby foes with a spinning disk.",
        "Fires a sharp horn that explodes on impact.",
        "Impales a foe with small blades.",
        "Rakes nearby foes with a giant claw.",
    ],
    11: [
        "Throws an electric flower bud at a foe.",
        "Throws a fireball at Mach speed.",
        "Sweeps nearby foes away with a small tornado.",
        "Hits a foe with a hard bone club.",
        "Destroys nearby foes with a powerful shock wave.",
        "Pounces and bites a foe with sharp fangs.",
        "Sweeps nearby foes away in a Light whirlwind.",
        "Scorches a foe with extreme heat. Deals fire damage.",
        "Spits a large iron ball at a foe. Lowers ATK.",
        "Shoots a foe with a holy Vulcan cannon. Deals Light damage.",
        "Crushes nearby foes beneath its huge body.",
        "Bites a foe with icy fangs. Lowers Defense.",
        "Slashes with Shishioumaru. Boosts Melody Capture rate.",
        "Hurls a polluted, bubble-shaped mass at a foe.",
        "Fires a strange ray from its mouth to defeat a foe.",
        "Scorches a foe with dark flames.",
        "Curses a foe with a powerful spell. May cause instant defeat.",
        "Throws a syringe to drain a foe's blood. Drains HP.",
        "Stretches both arms and pierces a foe with its claws. Deals dark damage.",
        "Calls thunderclouds and strikes with lightning. Deals electric damage.",
        "Destroys nearby foes' data with its tentacles.",
        "Slices a foe with a dark-powered sword.",
        "Scorches nearby foes with powerful flames.",
        "Envelops a foe in sleep-inducing water bubbles. May cause Sleep.",
        "Fires amplified static from its wings. May cause Paralysis.",
        "Slams electrified vines into a foe. May cause Paralysis.",
        "Fires ice-charged arrows at nearby foes.",
        "Draws its katana and cuts a foe in the blink of an eye.",
        "Pierces a foe with electrified spikes on both arms.",
        "Bites a foe with dark, poisonous fangs. Deals Poison damage.",
    ],
    12: {
        0: "Scorches foes with meteor-like feathers. Deals fire damage.",
        1: "Destroys nearby foes in a dark vortex. Deals dark damage.",
        2: "Crushes and buries a foe beneath a giant foot.",
        3: "Slices nearby foes with blades from its back.",
        4: "Rushes in and punches a foe. Deals physical damage.",
        5: "Scorches a foe with the sacred sword Kikurin.",
        6: "Freezes nearby foes in an instant. Deals Light damage.",
        7: "Enthralls nearby foes with darkness. May cause Confusion.",
        8: "Single HP Heal\nDummy text.",
        9: "Line HP Heal\nDummy text.",
        10: "Great Line HP Heal\nDummy text.",
        11: "Single MP Heal\nDummy text.",
        12: "Line MP Heal\nDummy text.",
        13: "Great Line MP Heal\nDummy text.",
        20: "Stabs a foe with a fire-charged horn. Lowers Intelligence.",
        21: "Scalds a foe with hot bubbles from its mouth.",
        22: "Bites a foe with its powerful jaws.",
        23: "Slices a foe with electric scissors.",
        24: "Rains slimy liquid on a foe. Deals Poison damage.",
        25: "Throws a life-sized bomb at nearby foes.",
        26: "Slices nearby foes with blades of dark wind.",
        27: "Bites and tears a foe with sharp fangs.",
        28: "Destroys nearby foes with ice bullets.",
        29: "Scorches foes with a full-arsenal barrage. Deals fire damage.",
        30: "Purifies nearby foes with the sacred spear Gungnir.",
        31: "Destroys nearby foes with dark-energy orbs. Deals Poison damage.",
        32: "Envelops a foe in painful dark smoke. Deals Poison damage.",
        33: "Unleashes all its power to scorch nearby foes. Deals fire damage.",
        34: "Sends nearby foes to a dark dimension. May cause instant defeat.",
        35: "Destroys nearby foes with lightning from eight dragons. Lowers Speed.",
        36: "Purifies the area with holy Light. Raises allies' Defense and Speed.",
        37: "Scorches nearby foes in a full-power explosion. Deals fire damage.",
        38: "Purifies all foes with a great Light explosion.",
        39: "Pierces a foe with a single lightning strike.",
        40: "Shocks all foes with a flying kiss. Lowers Defense.",
        41: "Breaks down nearby foes with digital cell bullets.",
        42: "Pierces and shatters a foe with sharp spikes.",
        43: "Shocks nearby foes with insect-shaped lightning. May cause Blindness.",
        44: "Punches and slashes nearby foes with many arms. Deals physical damage.",
        45: "Traps nearby foes in a magic circle. May cause instant defeat.",
        46: "Destroys nearby foes with Light energy orbs.",
        47: "Pierces a foe with its electric Booster Claw.",
        48: "Envelops nearby foes in darkness and destroys them. Deals dark damage.",
        49: "Purifies foes by sweeping its holy robe's sleeves.",
    },
    13: [
        "Fires needle-like hairs at nearby foes. Deals Poison damage.",
        "Whips a foe with an electric band. May cause Confusion.",
        "Scorches nearby foes with demonic fire. May cause instant defeat.",
        "Crushes nearby foes in a spinning charge. Lowers Speed.",
        "Freezes nearby foes with cryogenic missiles.",
        "Scorches a foe with an energy blast. May cause instant defeat.",
        "Purifies a foe with the sacred sword Gram.",
        "Shocks a foe with a smiling headbutt. Deals electric damage.",
        "Slashes nearby foes with a holy sword. Lowers Intelligence.",
        "Destroys nearby foes with the Behemoth bike. Deals dark damage.",
        "Knocks down a foe with an explosive punch.",
        "Pierces a foe with focused Light. Raises Melody Capture rate.",
        "Freezes nearby foes in an ultra-cold blizzard.",
        "Scorches a foe with the earth sword GeoGrey Sword.",
        "Purifies nearby foes with a tremendous blow.",
        "Pierces a foe with a supersonic water dragon. Lowers Defense.",
        "Shocks and slashes a foe with Ame-no-Ohabari. Deals Water damage.",
        "Purifies a foe with a deadly fist.",
        "Destroys nearby foes with moonlight. May cause Sleep.",
        "Sweeps nearby foes away with dark energy.",
        "Shoots nearby foes with tiny electric needles.",
        "Slices nearby foes with a sharp electric blade.",
        "Impales and destroys a foe with Ambrosius. Deals dark damage.",
        "Encloses nearby foes in dark spheres. May cause Blindness.",
        "Restores allies' HP with the light of Heaven.",
        "Blows dark sand at nearby foes. May cause Blindness.",
        "Whips a foe with a blood-red electric lash. Drains MP.",
        "Revives one ally with the healing power of flowers.",
        "Strikes a foe with a blow filled with a holy heart.",
        "Binds a foe with dark bandages. May cause Paralysis.",
        "Breaks down nearby foes' data with a laser. Deals Light damage.",
        "Destroys a foe with a Sanskrit glyph drawn in dark power.",
        "Blasts nearby foes with a giant firecracker.",
        "Scorches nearby foes with a powerful laser.",
        "Becomes a blue Light dragon and scorches a foe. Deals Light damage.",
        "Erases nearby foes with a purifying roar. May cause Paralysis.",
        "Fires a plasma ball at a foe. Lowers Speed.",
        "Opens a dimensional rift. Raises one ally's Defense and ATK.",
        "Slices a foe with spinning hand-and-foot shuriken.",
        "Crushes a foe while discharging electricity.",
        "Unleashes stored dark power. May cause Sleep.",
        "Slices and purifies a foe with a decisive strike.",
        "Stat HP Disk\n",
        "Stat MP Disk\n",
        "Status Recovery Disk\n",
        "Purifies nearby foes with intense sound waves. May cause Confusion.",
        "Slices a foe with electric claws.",
        "Breaks down foes with bio-missiles from its back. Deals fire damage.",
        "Breathes dark matter at a foe.",
        "Purifies a foe with the Sanskrit glyph 'Ra'. May cause Blindness.",
    ],
}


def wrap(text: str, width: int = 26) -> str:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        if not paragraph:
            lines.append("")
        else:
            lines.extend(textwrap.wrap(paragraph, width=width,
                                       break_long_words=False,
                                       break_on_hyphens=False))
    if len(lines) > 3:
        raise ValueError(f"Description exceeds three UI lines: {text!r} -> {lines!r}")
    return "\n".join(lines)


def main() -> None:
    out = ROOT / "translations/batch62.json"
    if out.exists():
        raise FileExistsError(f"Will not overwrite {out}")
    records = collect_messages(Rom(rom_paths()["blue"]))
    already = translate_records(records)
    pending: set[str] = set()
    blocks: list[dict] = []
    reviewed: list[tuple[str, str]] = []
    note = (
        "Effect translated from the original Japanese description. Status, stat, "
        "element, and Melody Capture wording follows the existing English UI; "
        "named weapons are retained in concise romanized form. Source rows with "
        "an intentionally blank description keep that blank line."
    )

    for entry, values in DATA.items():
        indexed = values.items() if isinstance(values, dict) else enumerate(values)
        for index, english in indexed:
            seed = f"MSG/MESPAK04.PAK:{entry:03d}:{index:05d}"
            if seed not in records:
                raise KeyError(f"Unknown message: {seed}")
            row = records[seed]
            if category(row) != "Move and item descriptions":
                raise ValueError(f"Wrong category for {seed}")
            if seed in already:
                raise ValueError(f"Already translated: {seed}")
            aliases = [r for r in records.values()
                       if r["source"] == row["source"]
                       and category(r) == "Move and item descriptions"
                       and r["id"] not in already]
            for alias in aliases:
                if alias["id"] in pending:
                    raise ValueError(f"Duplicate assignment: {alias['id']}")
                pending.add(alias["id"])
                blocks.append({
                    "archive": alias["archive"], "entry": alias["entry"],
                    "start": alias["index"],
                    "category": "Move and item descriptions",
                    "english": [wrap(english)],
                    "sources": ["Original Japanese ROM"],
                    "review_note": note,
                })
            reviewed.append((seed, wrap(english)))

    out.write_text(json.dumps({
        "description": (
            "Translate the next 274 battle-effect and item descriptions from "
            "MESPAK04 entries 8-13, including healing and status disks."
        ),
        "blocks": blocks,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Batch 62 review", "",
        f"Added {len(blocks)} translated slots from {len(reviewed)} reviewed description seeds.",
        "The batch translates battle effects, named weapon references, and six test healing labels directly from the original Japanese. Descriptions are wrapped to 26 characters and capped at three lines.",
        "Names such as Salamon, SkullBaluchimon, SkullMammothmon, and HerculesKabuterimon use the project's official Western name glossary where the species appears in text.",
        "", "| Source ID | English |", "|---|---|",
    ]
    for seed, english in reviewed:
        lines.append(f"| `{seed}` | {english.replace(chr(10), '<br>')} |")
    (ROOT / "translations/review_batch62.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(out), "slots": len(blocks),
                      "seeds": len(reviewed)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
