#include "wireless_actor_adapter.h"
#include "wireless_party.h"

#define XWB_ACTOR_SIZE 0x1A0u
#define XWB_SAVED_SIZE 0x80u
#define XWB_ACTOR_COUNT 12u
#define XWB_LOCAL_COUNT 6u

static xwb_u16 read16(const xwb_u8 *p) {
    return (xwb_u16)((xwb_u16)p[0] | (xwb_u16)p[1] << 8);
}

static void copy_bytes(xwb_u8 *destination, const xwb_u8 *source,
                       unsigned length) {
    unsigned i;
    for (i = 0; i < length; ++i) destination[i] = source[i];
}

int xwb_build_opponent_actors(xwb_u8 actors[XWB_ACTOR_COUNT * XWB_ACTOR_SIZE],
                              const xwb_u8 records[768],
                              const xwb_u8 formation[XWB_LOCAL_COUNT]) {
    xwb_u8 templates[3][XWB_ACTOR_SIZE];
    unsigned i, mask = 0;
    xwb_u8 *actor_bytes = actors;

    if (!actors || !records || !formation ||
        xwb_validate_party_records(records) != XWB_OK) return XWB_INVALID;

    for (i = 0; i < XWB_LOCAL_COUNT; ++i) {
        unsigned position = formation[i];
        if (position >= XWB_LOCAL_COUNT || (mask & (1u << position)))
            return XWB_INVALID;
        mask |= 1u << position;
    }

    /* Snapshot all three initialized enemy templates before writing any of
     * the six opponent slots. An encounter can have fewer than three enemies;
     * use the first initialized enemy as the fallback template for empty slots. */
    for (i = 0; i < 3; ++i) {
        const xwb_u8 *source = actor_bytes + (6u + i) * XWB_ACTOR_SIZE;
        if (!read16(source + 0x14)) source = actor_bytes + 6u * XWB_ACTOR_SIZE;
        if (!read16(source + 0x14)) return XWB_NOT_READY;
        copy_bytes(templates[i], source, XWB_ACTOR_SIZE);
    }

    /* Copy the matching positional template into the newly reserved rearguard
     * actor records. The active 6-8 templates stay in place until all six
     * roster entries have been validated and applied. */
    for (i = 3; i < XWB_LOCAL_COUNT; ++i) {
        xwb_u8 *destination = actor_bytes + (6u + i) * XWB_ACTOR_SIZE;
        copy_bytes(destination, templates[i - 3], XWB_ACTOR_SIZE);
    }

    for (i = 0; i < XWB_LOCAL_COUNT; ++i) {
        unsigned position = formation[i];
        xwb_u8 *destination = actor_bytes + (6u + position) * XWB_ACTOR_SIZE;
        if (xwb_apply_saved_record_fields(destination,
                records + i * XWB_SAVED_SIZE) != XWB_OK) return XWB_INVALID;
    }

    return XWB_OK;
}
