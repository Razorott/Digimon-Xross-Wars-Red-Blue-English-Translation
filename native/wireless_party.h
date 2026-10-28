#ifndef XWB_WIRELESS_PARTY_H
#define XWB_WIRELESS_PARTY_H
#include "wireless_battle.h"

/* Copy the current first six party positions, in formation order, from the
 * game's stable save-record pool. `order` holds nine 8-byte entries whose
 * first word is the record's stable ID; each saved record stores that ID at
 * offset 0x74. The output is untouched unless all six entries validate. */
int xwb_capture_formation_party(const volatile xwb_u8 *records,
                                unsigned record_count,
                                const volatile xwb_u8 *order,
                                xwb_u8 out[768]);

/* Validate the six opaque records received from the other DS before they are
 * admitted to the lobby. Equipment and other unknown bytes remain opaque and
 * are retained verbatim for the later battle adapter. */
int xwb_validate_party_records(const xwb_u8 records[768]);

/* Retail RAM locations verified in fresh Blue and Red formation-screen QA
 * states. This does not write to either saved-party record or the save file. */
int xwb_capture_local_party(xwb_u8 out[768]);

#endif
