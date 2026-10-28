import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TutorialChoiceLabelTests(unittest.TestCase):
    def test_digilab_and_battle_help_choices_fit_single_menu_line(self):
        expected = {
            92: {
                157: "DigiLab help", 158: "Digimon List", 159: "DigiFusion",
                160: "Jogress Up", 161: "Melody Playback", 162: "List features",
                163: "Place Digimon", 164: "Move Digimon", 165: "View status",
                166: "Melody return", 167: "Party", 168: "DigiBank",
                169: "Expedition Team", 182: "Training/jobs", 183: "Farm Islands",
                184: "DigiReports", 185: "Training", 186: "Jobs", 187: "Farm Islands",
                188: "Farm Goods", 189: "Terrain/BGM", 190: "DigiReports",
                191: "Change moves",
            },
            93: {
                2: "Battle strategy", 3: "Move effects", 4: "Other topics",
                5: "Commands", 6: "Formations", 7: "Health Down?",
                8: "Special effects", 9: "Melody capture", 10: "Attributes",
                11: "EXP", 12: "Strategy", 13: "Choosing moves", 14: "Other commands",
                15: "Vanguard", 16: "Rearguard", 17: "Reserve", 18: "Power/Conserve",
                19: "Guard/Escape", 20: "All Strategy", 21: "Commands",
                22: "DigiXross", 23: "Formations", 24: "Items", 41: "Nothing now",
            },
        }
        for batch, labels in expected.items():
            data = json.loads((ROOT / f"translations/batch{batch}.json").read_text(encoding="utf-8"))
            actual = {}
            target_entry = 16 if batch == 92 else 17
            for block in data["blocks"]:
                if block["archive"] != "MSG/MESPAK02.PAK" or block["entry"] != target_entry:
                    continue
                for offset, text in enumerate(block["english"]):
                    actual[block["start"] + offset] = text
            for index, label in labels.items():
                with self.subTest(batch=batch, index=index):
                    self.assertEqual(actual[index], label)
                    self.assertLessEqual(len(label), 15)
                    self.assertNotIn("\n", label)


if __name__ == "__main__":
    unittest.main()
