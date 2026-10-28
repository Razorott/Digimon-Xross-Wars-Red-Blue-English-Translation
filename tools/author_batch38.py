"""Finish the outstanding battle-name table using its paired label layout."""
from __future__ import annotations

import csv
import json

from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

DDA = "https://raw.githubusercontent.com/joaomlsantos/Digimon-World-Dawn-Dusk-Research-Notes/master/move_name_lst.txt"
ALGOMON = "https://digimon.net/reference_en/detail.php?directory_name=algomon"
TECHNIQUE = "https://wikimon.net/Digimon_Story:_Super_Xros_Wars_Guide/Technique"
LOCAL = "Original Japanese game text; working English rendering where no Western title was verified."

# The battle table stores a formal name followed by a compact-name table 1,276
# indices later. If the formal slot already has an English name, reuse it for
# its Japanese-abbreviated partner; the build's width pass then fits it to the
# actual battle label width. New formal names are authored here.
BASE_MOVES = {
    1253: "Spinning Sky-Cleaving Slash",
    1260: "Double Crescent Mirage",
    1269: "MasterDramon Claw",
    1270: "GreatDramon Claw",
    1306: "Ascension Halo",
    1310: "Wild Thunder Claw",
    1313: "Digicabolic Steroid",
    1371: "Demon's Disaster",
    1372: "Crimson Lion Dance",
    1404: "Time Unlimited",
    1408: "Gaia Force Dark",
    1410: "Flame Inferno",
    1416: "Time Destroyer",
    1449: "Shining V-Force",
    1458: "Electric Bind",
    1476: "Pandemonium Lost",
    1484: "Breath of Wyvern",
    1485: "Argent Fear",
    1490: "Giga Destroyer II",
    1510: "Forbidden Trident",
    1521: "Great Snow Blow",
    1529: "Stinger Surprise",
    1541: "Koyojou: Kamon Formation",
    1548: "Spiral Raven Claw",
    1552: "Ground Zero Kai",
    1572: "Brain Rapture",
    1574: "Corona Blaze Sword",
    1576: "Full Moon Meteor Impact",
    1577: "Muso Tensho Wing Formation",
    1585: "Distortion Line",
    1589: "Bancho Blade",
    1610: "Absolute Zero Punch",
    1615: "Sticker Blade",
    1632: "Knight of Fire",
    1646: "Stinger Poration",
    1675: "Single HP Heal",
    1676: "Line HP Heal",
    1677: "Great Line HP Heal",
    1678: "Single MP Heal",
    1679: "Line MP Heal",
    1680: "Great Line MP Heal",
    1683: "Single Status Cure",
    1684: "Line Status Cure",
    1685: "Revive",
    1696: "Hyper Prominence",
    1699: "Melting Blood",
    1759: "HP Status Disk",
    1760: "MP Status Disk",
    1761: "Status Cure Disk",
    1927: "Horn Breaker DX",
    1931: "Victorize Boomerang",
    1939: "Breast Eye Wink",
    1944: "Undead Soldier",
    1947: "Ultrasonic Wave",
    1963: "The Shulennen",
    1969: "Platinum Excrement",
    1970: "Splatter Hunting",
    1973: "Aura Dio Grandiorogua",
    1984: "Fireworks Revolution",
    1992: "Diamond Machine Gun",
    1993: "Diamond Hedgehog",
    1997: "Konpeito Hammer",
    1998: "Final Chikurimon",
    2005: "Fire Rock Breaker",
    2009: "Sparking Air Shot",
    2015: "Marching Fishes",
    2023: "Blazing Fire",
    2026: "Knight of Blizzard",
    2028: "Scratch Smash",
    2056: "Zone Black Hole",
    2059: "Ultimate Slicer",
    2060: "Heaven's Judgment",
    2064: "Arrow of Apollo",
    2079: "Tut-Ankh-Ra Ill",
    2085: "Nuts Explosion",
    2104: "Super Positron Laser",
    2108: "Sword of Ruin",
    2109: "Dash Bulthang",
    2110: "Zero Arms: Orochi",
    2111: "Luna Harken Slasher",
    2112: "Meteor Squall Legacy",
    2171: "Double Victory Impact",
    2172: "TBD 00", 2173: "TBD 01", 2175: "TBD 02", 2176: "TBD 03",
    2181: "TBD 06", 2182: "TBD 07", 2184: "TBD 08", 2185: "TBD 09",
    2187: "Rock Damacy Great",
    2192: "Horn Strike Force",
    2193: "Spear Needle Blood",
    2194: "Breast Eye Wave",
    2211: "TBD 29", 2212: "TBD 30", 2213: "TBD 31", 2214: "TBD 32",
    2215: "TBD 33", 2216: "TBD 34",
    2223: "Reserve", 2224: "Reserve", 2225: "Reserve",
    2226: "Reserve", 2227: "Reserve",
    2236: "Single HP Status", 2237: "Single MP Status",
    2238: "Single Status Cure", 2239: "Single HP Cure",
    2240: "Full Status Cure", 2241: "Personality Cure",
    2421: "Time Paradox", 2497: "Chrono DSR", 2498: "Origin Nebula",
    2499: "Test Move 1", 2500: "Test Move 2", 2501: "Test Move 3",
    2502: "Test Move 4", 2503: "Test Move 5",
}

EVIDENCE = {
    1585: (ALGOMON, "The official English Digimon Encyclopedia lists Algomon's attack as Distortion Line."),
    2497: (DDA, "The matching Chrono DSR name appears in the English Digimon World: Dawn/Dusk move-name extraction."),
}


def main() -> None:
    records = collect_messages(Rom(rom_paths()["blue"]))
    prior = translate_records(records)
    all_translations: dict[str, str] = {}
    blocks, review, seen = [], [], set()
    note = ("Attack names are matched to a Western Digimon game or official "
        "English Digimon source when that match is established. Otherwise this "
        "is a working rendering from the Japanese game text. Compact Japanese "
        "counterpart slots reuse their full-name translation and are measured "
        "by the English battle-label fit pass.")

    def add(key: str, english: str, *, source: str | None = None,
            evidence: str = "") -> None:
        if key in prior or key in seen:
            return
        row = records.get(key)
        if row is None or not row["source"].strip():
            raise ValueError(f"Missing move source at {key}")
        source_urls = [source] if source else []
        seen.add(key)
        all_translations[key] = english
        blocks.append({"archive": row["archive"], "entry": row["entry"],
            "start": row["index"], "category": "Battle moves",
            "english": [english], "sources": source_urls, "review_note": note})
        review.append({"id": key, "japanese": row["source"], "english": english,
            "evidence_url": source or LOCAL, "evidence": evidence,
            "review_note": note})

    # Formal technique names.
    for index, english in BASE_MOVES.items():
        key = f"MSG/MESPAK00.PAK:000:{index:05d}"
        if key not in records:
            raise ValueError(f"Expected formal battle name not found: {key}")
        source, evidence = EVIDENCE.get(index, (None, ""))
        add(key, english, source=source, evidence=evidence)

    # Japanese short-name slots are aligned with formal names by +1276. Some
    # pairs were already translated in earlier batches; reuse those as well.
    for row in records.values():
        if row["archive"] != "MSG/MESPAK00.PAK" or row["entry"] != 0:
            continue
        index = row["index"]
        if not 2504 <= index <= 3750:
            continue
        key = row["id"]
        if key in prior or key in seen:
            continue
        base_key = f"MSG/MESPAK00.PAK:000:{index - 1276:05d}"
        english = all_translations.get(base_key)
        base = prior.get(base_key)
        if english is None and base is not None:
            english = base["english"]
            source_url = base.get("sources", [None])[0] if base.get("sources") else None
        else:
            source_url = next((b["sources"][0] for b in blocks
                               if b["archive"] == "MSG/MESPAK00.PAK" and b["start"] == index - 1276
                               and b["sources"]), None)
        if english is None:
            continue
        add(key, english, source=source_url,
            evidence="Paired short label; formal translation retained from its matching battle-table slot.")

    # Remaining unfinished technique slots must be paired or explicitly authored.
    remaining = [r["id"] for r in records.values()
        if r["archive"] == "MSG/MESPAK00.PAK" and r["entry"] == 0
        and 1228 <= r["index"] <= 3750 and r["id"] not in prior and r["id"] not in seen]
    if remaining:
        raise ValueError(f"Untranslated battle-name slots remain: {remaining[:12]} (total {len(remaining)})")

    # These four entries are reserve/place-holder species table labels, not
    # canon Digimon. Keep the wording explicit so they are not mistaken for names.
    queue = list(csv.DictReader((ROOT / "translations/work_queue.tsv").open(
        encoding="utf-8-sig"), delimiter="\t"))
    species_rows = {(r["category"], r["japanese"]): r for r in queue}
    for japanese, english in (("よび", "Reserve"), ("よびわく", "Reserve Slot")):
        group = species_rows.get(("Digimon names", japanese))
        if group is None:
            raise ValueError(f"Missing reserve species label {japanese}")
        for key in group["ids"].split(";"):
            row = records[key]
            blocks.append({"archive": row["archive"], "entry": row["entry"],
                "start": row["index"], "category": "Digimon names",
                "english": [english], "sources": [],
                "review_note": "Translated reserve-slot label; not a canon Digimon species name."})
            review.append({"id": key, "japanese": japanese, "english": english,
                "evidence_url": LOCAL,
                "review_note": "Translated reserve-slot label; not a canon Digimon species name."})
            seen.add(key)

    if len(BASE_MOVES) != 119:
        raise ValueError(f"Expected 119 formal names, authored {len(BASE_MOVES)}")
    out = ROOT / "translations/batch38.json"
    if out.exists():
        raise FileExistsError(out)
    out.write_text(json.dumps({"description": "Finish the outstanding formal and compact battle-name rows, with an audited full-name to short-name offset and the remaining reserve labels.", "blocks": blocks}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "translations/review_batch38.json").write_text(
        json.dumps({"batch": 38, "translated_slots": len(blocks),
                    "formal_names": len(BASE_MOVES), "groups": review},
                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Batch 38 review", "",
        f"Batch 38 adds {len(blocks)} name slots: the remaining formal battle technique names, their paired compact labels, and four reserve-slot labels that are not canon Digimon names.", "",
        "The formal/compact pairing is source-table layout, not a guessed translation: the Japanese short-name table is offset by 1,276 from the formal table. A compact Japanese entry reuses its corresponding full English name, and `name_layout.py` applies the measured English width cap. The official Digimon Encyclopedia verifies Distortion Line; the English Dawn/Dusk move list verifies Chrono DSR. Other new moves are labeled as working renderings in the JSON review when no Western title match was confirmed.", "",
        "| ID | Japanese | English | Evidence |", "|---|---|---|---|"]
    for row in review:
        jp = row["japanese"].replace("\n", "<br>").replace("|", "\\|")
        en = row["english"].replace("\n", "<br>").replace("|", "\\|")
        evidence = row.get("evidence_url", LOCAL)
        lines.append(f"| `{row['id']}` | {jp} | {en} | {evidence} |")
    (ROOT / "translations/review_batch38.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"batch": 38, "translated_slots": len(blocks),
                      "formal_moves": len(BASE_MOVES),
                      "compact_and_reserved": len(blocks) - len(BASE_MOVES)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
