# Item-name audit (batch 61)

The Japanese item table uses Digimon names as short inventory labels for two different item types. The paired descriptions reveal what each item does, so I kept those compact labels and translated the descriptions instead of adding long suffixes that could crowd the inventory.

| Item-table IDs | Japanese source | Finding | Paired description |
|---|---|---|---|
| `MSG/MESPAK00.PAK:000:03827`–`03841` | Digimon names from Leviamon through Omnimon | DigiMemory items. The Japanese description table labels these as memory entries; the specific descriptions say the DigiMemory disappears after one battle use. | `MSG/MESPAK04.PAK:029:00034`–`00048` |
| `MSG/MESPAK00.PAK:000:04428`–`04498` | 71 Digimon names | Service Counter gift tickets. Each paired description says to hand in the ticket at the Service Counter to receive a gift from that Digimon. The 21 descriptions in entry 41 are newly translated in batch 61; entry 42's 50 are already translated. | `MSG/MESPAK04.PAK:041:00029`–`00049`; `MSG/MESPAK04.PAK:042:00000`–`00049` |
| `MSG/MESPAK00.PAK:000:03966` | `クダピアス` | **Kudamon Earring**. This is an equipment name meaning Kudamon's earring/piercing, not a Kudamon creature item. The existing Western species spelling is retained. | Item name only; no separate description entry was found. |

The audit found no reason to replace the DigiMemory or gift-ticket labels with longer names. Their information panels identify the item type and use, and adding “DigiMemory” or “Gift Ticket” to every label would make several names harder to fit in the inventory list.

The 71-ticket wording follows the same English pattern used by the translated tickets in entry 42: `Gift from: [Digimon] / Redeem at Service Counter.` Western spellings come from the project glossary and its linked English references; `Kurisarimon`, for example, is the spelling used on Bandai's [English card page](https://world.digimoncard.com/cards/?card_no=BT22-057&search=true).
