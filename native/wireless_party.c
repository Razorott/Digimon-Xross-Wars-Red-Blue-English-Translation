#include "wireless_party.h"

#define XWB_SAVED_RECORD_SIZE 0x80u
#define XWB_SAVED_UID_OFFSET  0x74u
#define XWB_RECORD_SPECIES    0x12u
#define XWB_RECORD_HP         0x1Eu
#define XWB_RECORD_MAX_HP     0x20u
#define XWB_RECORD_MP         0x22u
#define XWB_RECORD_MAX_MP     0x24u
#define XWB_RECORD_NAME_SIZE  18u
#define XWB_POSITION_STRIDE   8u
#define XWB_PARTY_SIZE        6u

static xwb_u16 load16(const volatile xwb_u8 *p) {
    return (xwb_u16)((xwb_u16)p[0] | (xwb_u16)p[1] << 8);
}

static xwb_u32 load32(const volatile xwb_u8 *p) {
    return (xwb_u32)p[0] | (xwb_u32)p[1] << 8 |
           (xwb_u32)p[2] << 16 | (xwb_u32)p[3] << 24;
}

/* Names in records use CP932. Reject zero-length and control/broken byte
 * sequences so IDs from uninitialized save RAM cannot resolve as Digimon. */
static int valid_name(const volatile xwb_u8 *name) {
    unsigned i = 0;
    unsigned length = 0;
    while (i < XWB_RECORD_NAME_SIZE && name[i]) {
        xwb_u8 c = name[i++];
        if (c >= 0x20u && c <= 0x7Eu) {
            ++length;
            continue;
        }
        if ((c >= 0x81u && c <= 0x9Fu) || (c >= 0xE0u && c <= 0xFCu)) {
            xwb_u8 trail;
            if (i >= XWB_RECORD_NAME_SIZE) return 0;
            trail = name[i++];
            if (trail < 0x40u || trail > 0xFCu || trail == 0x7Fu) return 0;
            length += 2;
            continue;
        }
        return 0;
    }
    return length != 0;
}

static int valid_record(const volatile xwb_u8 *record) {
    unsigned species = load16(record + XWB_RECORD_SPECIES);
    unsigned hp = load16(record + XWB_RECORD_HP);
    unsigned max_hp = load16(record + XWB_RECORD_MAX_HP);
    unsigned mp = load16(record + XWB_RECORD_MP);
    unsigned max_mp = load16(record + XWB_RECORD_MAX_MP);
    return species != 0 && species <= 0x07FFu && max_hp != 0 && max_mp != 0 &&
           hp <= max_hp && mp <= max_mp && valid_name(record);
}

int xwb_validate_party_records(const xwb_u8 records[768]) {
    unsigned i, j;
    if (!records) return XWB_INVALID;
    for (i = 0; i < XWB_PARTY_SIZE; ++i) {
        const volatile xwb_u8 *record = records + i * XWB_SAVED_RECORD_SIZE;
        xwb_u32 uid;
        if (!valid_record(record)) return XWB_INVALID;
        uid = load32(record + XWB_SAVED_UID_OFFSET);
        for (j = 0; j < i; ++j) {
            const volatile xwb_u8 *prior = records + j * XWB_SAVED_RECORD_SIZE;
            if (load32(prior + XWB_SAVED_UID_OFFSET) == uid) return XWB_INVALID;
        }
    }
    return XWB_OK;
}

int xwb_capture_formation_party(const volatile xwb_u8 *records,
                                unsigned record_count,
                                const volatile xwb_u8 *order,
                                xwb_u8 out[768]) {
    unsigned selected[XWB_PARTY_SIZE];
    unsigned i, j, matches, match_index;

    if (!records || !order || !out || !record_count || record_count > 256u)
        return XWB_INVALID;

    for (i = 0; i < XWB_PARTY_SIZE; ++i) {
        xwb_u32 uid = load32(order + i * XWB_POSITION_STRIDE);
        matches = 0;
        match_index = 0;
        for (j = 0; j < record_count; ++j) {
            const volatile xwb_u8 *record = records + j * XWB_SAVED_RECORD_SIZE;
            if (load32(record + XWB_SAVED_UID_OFFSET) != uid || !valid_record(record))
                continue;
            ++matches;
            match_index = j;
        }
        if (matches != 1u) return XWB_INVALID;
        for (j = 0; j < i; ++j)
            if (selected[j] == match_index) return XWB_INVALID;
        selected[i] = match_index;
    }

    for (i = 0; i < XWB_PARTY_SIZE; ++i) {
        const volatile xwb_u8 *record = records + selected[i] * XWB_SAVED_RECORD_SIZE;
        for (j = 0; j < XWB_SAVED_RECORD_SIZE; ++j)
            out[i * XWB_SAVED_RECORD_SIZE + j] = record[j];
    }
    return XWB_OK;
}
