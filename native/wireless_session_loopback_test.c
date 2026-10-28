/* Two-endpoint protocol exercise. Transport is an in-memory packet queue,
 * not a radio or emulator wireless test. */
#include "wireless_session.h"

#define PACKET_CAPACITY 96
#define QUEUE_CAPACITY 16

typedef struct packet_slot {
    unsigned length;
    xwb_u8 bytes[PACKET_CAPACITY];
} packet_slot;

static packet_slot queues[2][QUEUE_CAPACITY];
static unsigned queue_head[2], queue_count[2], bound[2], drop_next_ack[2], virtual_frame;
static unsigned corrupt_guest_first_team;
static xwb_u32 transport_session[2];
static xwb_u32 last_ack_sent[2];
static xwb_u8 host_records[768], guest_records[768], copied[768];
static xwb_match host_match, guest_match;
static xwb_action sent, received;
volatile xwb_u32 xwb_test_diag[12];

extern int host_xwb_session_begin(unsigned, xwb_u32, const xwb_u8 *);
extern int host_xwb_session_pump(xwb_u32);
extern int host_xwb_session_get_state(void);
extern int host_xwb_session_copy_remote(xwb_u8 *);
extern int host_xwb_session_get_match(xwb_match *);
extern int host_xwb_session_set_formation(const xwb_u8 *);
extern int host_xwb_session_select_music(unsigned);
extern int host_xwb_session_set_ready(unsigned);
extern int host_xwb_session_start(void);
extern int host_xwb_session_submit_action(const xwb_action *);
extern int host_xwb_session_take_action(xwb_action *);
extern int host_xwb_session_confirm_action(xwb_u32, xwb_u32, xwb_u32);
extern int host_xwb_session_next_round(void);
extern int host_xwb_session_end(void);
extern xwb_u32 host_xwb_session_debug_flags(void);
extern int guest_xwb_session_begin(unsigned, xwb_u32, const xwb_u8 *);
extern int guest_xwb_session_pump(xwb_u32);
extern int guest_xwb_session_get_state(void);
extern int guest_xwb_session_copy_remote(xwb_u8 *);
extern int guest_xwb_session_get_match(xwb_match *);
extern int guest_xwb_session_set_formation(const xwb_u8 *);
extern int guest_xwb_session_select_music(unsigned);
extern int guest_xwb_session_set_ready(unsigned);
extern int guest_xwb_session_start(void);
extern int guest_xwb_session_submit_action(const xwb_action *);
extern int guest_xwb_session_take_action(xwb_action *);
extern int guest_xwb_session_confirm_action(xwb_u32, xwb_u32, xwb_u32);
extern int guest_xwb_session_next_round(void);
extern int guest_xwb_session_end(void);
extern xwb_u32 guest_xwb_session_debug_flags(void);
extern void host_xwb_session_debug_info(xwb_u32 *);
extern void guest_xwb_session_debug_info(xwb_u32 *);

static int transport_bind(unsigned side, xwb_u32 session) {
    if (side > 1) return XWB_INVALID;
    bound[side] = 1;
    transport_session[side] = session;
    return XWB_OK;
}
int host_transport_bind(unsigned side, xwb_u32 session) {
    return side == 0 ? transport_bind(side, session) : XWB_INVALID;
}
int guest_transport_bind(unsigned side, xwb_u32 session) {
    return side == 1 ? transport_bind(side, session) : XWB_INVALID;
}
int host_transport_set_session(xwb_u32 session) {
    if (!session) return XWB_INVALID;
    transport_session[0] = session;
    return XWB_OK;
}
int guest_transport_set_session(xwb_u32 session) {
    if (!session) return XWB_INVALID;
    transport_session[1] = session;
    return XWB_OK;
}
int host_transport_connected(void) { return bound[0] && bound[1]; }
int guest_transport_connected(void) { return bound[0] && bound[1]; }
int host_transport_radio_busy(void) { return 0; }
int guest_transport_radio_busy(void) { return 0; }
unsigned host_transport_dropped(void) { return 0; }
unsigned guest_transport_dropped(void) { return 0; }
int host_transport_detach(void) { return XWB_OK; }
int guest_transport_detach(void) { return XWB_OK; }

static int send_packet(unsigned side, unsigned type, xwb_u32 sequence,
                       const xwb_u8 *payload, unsigned length) {
    xwb_u8 bytes[PACKET_CAPACITY];
    xwb_u8 changed[72];
    const xwb_u8 *send_payload = payload;
    unsigned other = side ^ 1u;
    int encoded;
    if (!bound[0] || !bound[1] || !transport_session[side] || queue_count[other] >= QUEUE_CAPACITY)
        return XWB_NOT_READY;
    if (corrupt_guest_first_team && side == 1 && type == XWB_TEAM &&
        sequence == 1 && length == sizeof(changed)) {
        for (unsigned i = 0; i < sizeof(changed); ++i) changed[i] = payload[i];
        /* Keep the packet CRC valid while corrupting the first saved record. */
        changed[8 + 0x12] = 0;
        changed[8 + 0x13] = 0;
        send_payload = changed;
        corrupt_guest_first_team = 0;
    }
    encoded = xwb_encode(bytes, sizeof(bytes), type, side, transport_session[side],
                         sequence, send_payload, length);
    if (encoded < 0) return encoded;
    if (type == XWB_ACK) {
        last_ack_sent[side] = sequence;
        if (drop_next_ack[side]) { drop_next_ack[side] = 0; return XWB_OK; }
    }
    {
        unsigned at = (queue_head[other] + queue_count[other]) % QUEUE_CAPACITY;
        queues[other][at].length = (unsigned)encoded;
        for (unsigned i = 0; i < (unsigned)encoded; ++i) queues[other][at].bytes[i] = bytes[i];
        ++queue_count[other];
    }
    return XWB_OK;
}
int host_transport_send(unsigned type, xwb_u32 sequence, const xwb_u8 *payload, unsigned length) {
    return send_packet(0, type, sequence, payload, length);
}
int guest_transport_send(unsigned type, xwb_u32 sequence, const xwb_u8 *payload, unsigned length) {
    return send_packet(1, type, sequence, payload, length);
}
static int take_packet(unsigned side, xwb_u8 *out, unsigned capacity) {
    packet_slot *slot;
    unsigned i;
    if (!out || !queue_count[side]) return XWB_NOT_READY;
    slot = &queues[side][queue_head[side]];
    if (slot->length > capacity) return XWB_INVALID;
    for (i = 0; i < slot->length; ++i) out[i] = slot->bytes[i];
    i = slot->length;
    queue_head[side] = (queue_head[side] + 1) % QUEUE_CAPACITY;
    --queue_count[side];
    return (int)i;
}
int host_transport_take(xwb_u8 *out, unsigned capacity) { return take_packet(0, out, capacity); }
int guest_transport_take(xwb_u8 *out, unsigned capacity) { return take_packet(1, out, capacity); }

static int pump_pair(unsigned frames) {
    unsigned i;
    for (i = 0; i < frames; ++i) {
        ++virtual_frame;
        if (host_xwb_session_pump(virtual_frame) < 0 || guest_xwb_session_pump(virtual_frame) < 0)
            return -1;
    }
    return XWB_OK;
}
static void capture_diag(void) {
    host_xwb_session_debug_info((xwb_u32 *)&xwb_test_diag[0]);
    guest_xwb_session_debug_info((xwb_u32 *)&xwb_test_diag[4]);
    xwb_test_diag[8] = last_ack_sent[0];
    xwb_test_diag[9] = last_ack_sent[1];
    xwb_test_diag[10] = queue_count[0];
    xwb_test_diag[11] = queue_count[1];
}

static void write16(xwb_u8 *p, xwb_u16 value) {
    p[0] = (xwb_u8)value;
    p[1] = (xwb_u8)(value >> 8);
}
static void write32(xwb_u8 *p, xwb_u32 value) {
    p[0] = (xwb_u8)value;
    p[1] = (xwb_u8)(value >> 8);
    p[2] = (xwb_u8)(value >> 16);
    p[3] = (xwb_u8)(value >> 24);
}
static void make_party(xwb_u8 records[768], unsigned uid_base, unsigned species_base) {
    unsigned i;
    for (i = 0; i < 6; ++i) {
        xwb_u8 *record = records + i * 0x80;
        record[0] = (xwb_u8)'D';
        record[1] = (xwb_u8)'i';
        record[2] = (xwb_u8)'g';
        record[3] = (xwb_u8)'i';
        record[4] = (xwb_u8)('0' + i);
        write16(record + 0x12, (xwb_u16)(species_base + i));
        write16(record + 0x1E, (xwb_u16)(90 + i));
        write16(record + 0x20, (xwb_u16)(100 + i));
        write16(record + 0x22, (xwb_u16)(40 + i));
        write16(record + 0x24, (xwb_u16)(50 + i));
        write32(record + 0x74, (xwb_u32)(uid_base + i));
    }
}
static int exchange_action(unsigned sender, unsigned expected_id) {
    unsigned frame;
    int got;
    for (frame = 0; frame < 32; ++frame) {
        if (pump_pair(1) != XWB_OK) return -1;
        got = sender ? host_xwb_session_take_action(&received) : guest_xwb_session_take_action(&received);
        if (got == XWB_OK) {
            if (received.action_id != expected_id || received.round != sent.round ||
                received.actor != sent.actor || received.kind != sent.kind ||
                received.move_slot != sent.move_slot || received.target_side != sent.target_side ||
                received.target_slot != sent.target_slot || received.skill_id != sent.skill_id ||
                received.result_digest != sent.result_digest || received.rng_state != sent.rng_state)
                return -2;
            got = sender ? host_xwb_session_confirm_action(received.action_id,
                       received.result_digest, received.rng_state) :
                       guest_xwb_session_confirm_action(received.action_id,
                       received.result_digest, received.rng_state);
            if (got != XWB_OK) return -3;
        } else if (got != XWB_NOT_READY) return -4;
    }
    return XWB_OK;
}

int xwb_test_main(void) {
    static const xwb_u8 host_formation[6] = {1,0,2,3,4,5};
    static const xwb_u8 guest_formation[6] = {0,1,2,4,3,5};
    static const xwb_u8 guest_formation_2[6] = {2,1,0,4,3,5};
    unsigned i;
    make_party(host_records, 100, 200);
    make_party(guest_records, 200, 300);
    if (host_xwb_session_begin(0, 0x12345678u, host_records) != XWB_OK ||
        guest_xwb_session_begin(1, 0, guest_records) != XWB_OK) return 1;
    for (i = 1; i <= 400; ++i) {
        if (host_xwb_session_pump(i) < 0 || guest_xwb_session_pump(i) < 0) return 2;
        if (host_xwb_session_get_state() == XWB_SESSION_TEAMS_READY &&
            guest_xwb_session_get_state() == XWB_SESSION_TEAMS_READY) break;
    }
    virtual_frame = i;
    if (i > 400) return 3;
    if (host_xwb_session_copy_remote(copied) != XWB_OK) return 4;
    for (i = 0; i < 768; ++i) if (copied[i] != guest_records[i]) return 5;
    if (guest_xwb_session_copy_remote(copied) != XWB_OK) return 6;
    for (i = 0; i < 768; ++i) if (copied[i] != host_records[i]) return 7;

    /* Both peers can update their own formation at once from the same base. */
    drop_next_ack[1] = 1; /* Lose one formation acknowledgement and test retry. */
    if (host_xwb_session_set_formation(host_formation) != XWB_OK ||
        guest_xwb_session_set_formation(guest_formation) != XWB_OK || pump_pair(220) != XWB_OK)
        return 80;
    if ((host_xwb_session_debug_flags() & 3u) || (guest_xwb_session_debug_flags() & 3u)) {
        capture_diag();
        return 800000 + (host_xwb_session_debug_flags() << 15) +
            (guest_xwb_session_debug_flags() << 10) +
            ((queue_count[0] & 31u) << 5) + (queue_count[1] & 31u);
    }
    /* Host music and guest formation changes are also disjoint concurrent edits. */
    {
        int status = host_xwb_session_select_music(XWB_WORLD_DS_MULTIPLAYER);
        if (status != XWB_OK) {
            capture_diag();
            return 810000 + (host_xwb_session_debug_flags() << 15) +
                (guest_xwb_session_debug_flags() << 10) + (unsigned)(-status);
        }
    }
    if (guest_xwb_session_set_formation(guest_formation_2) != XWB_OK) return 812;
    if (pump_pair(16) != XWB_OK) return 82;
    if (host_xwb_session_set_ready(1) != XWB_OK || guest_xwb_session_set_ready(1) != XWB_OK ||
        pump_pair(16) != XWB_OK || host_xwb_session_start() != XWB_OK || pump_pair(16) != XWB_OK)
        return 9;
    if (host_xwb_session_get_match(&host_match) != XWB_OK ||
        guest_xwb_session_get_match(&guest_match) != XWB_OK ||
        host_match.phase != XWB_BATTLE || guest_match.phase != XWB_BATTLE ||
        host_match.round != 1 || guest_match.round != 1 || host_match.ready != 3 ||
        guest_match.ready != 3 || host_match.music != XWB_WORLD_DS_MULTIPLAYER ||
        guest_match.music != XWB_WORLD_DS_MULTIPLAYER ||
        host_match.formation[0][0] != 1 || host_match.formation[1][0] != 2 ||
        guest_match.formation[0][0] != 1 || guest_match.formation[1][0] != 2) return 10;

    sent.round = 1; sent.action_id = 1; sent.result_digest = 0xAABBCCDD;
    sent.rng_state = 0x10203040; sent.actor = 0; sent.kind = XWB_ACTION_DIGIXROSS;
    sent.move_slot = 1; sent.target_side = 1; sent.target_slot = 2; sent.skill_id = 0x222;
    if (host_xwb_session_submit_action(&sent) != XWB_INVALID ||
        guest_xwb_session_submit_action(&sent) != XWB_INVALID) return 10;
    sent.round = 1; sent.action_id = 1; sent.result_digest = 0xAABBCCDD;
    sent.rng_state = 0x10203040; sent.actor = 2; sent.kind = XWB_ACTION_ATTACK;
    sent.move_slot = 0; sent.target_side = 1; sent.target_slot = 4; sent.skill_id = 0xFFFF;
    if (host_xwb_session_submit_action(&sent) != XWB_OK || exchange_action(0, 1) != XWB_OK)
        return 11;
    sent.round = 1; sent.action_id = 2; sent.result_digest = 0x13579BDF;
    sent.rng_state = 0x2468ACE0; sent.actor = 5; sent.kind = XWB_ACTION_GUARD;
    sent.move_slot = 0; sent.target_side = 0; sent.target_slot = 5; sent.skill_id = 0;
    if (guest_xwb_session_submit_action(&sent) != XWB_OK || exchange_action(1, 2) != XWB_OK)
        return 12;
    if (host_xwb_session_next_round() != XWB_OK || pump_pair(16) != XWB_OK) return 13;
    if (host_xwb_session_get_match(&host_match) != XWB_OK ||
        guest_xwb_session_get_match(&guest_match) != XWB_OK ||
        host_match.round != 2 || guest_match.round != 2) return 14;

    sent.round = 2; sent.action_id = 3; sent.result_digest = 0xABCDEF01;
    sent.rng_state = 0x12344321; sent.actor = 0; sent.kind = XWB_ACTION_DIGIXROSS;
    sent.move_slot = 1; sent.target_side = 1; sent.target_slot = 2; sent.skill_id = 0x222;
    if (host_xwb_session_submit_action(&sent) != XWB_OK || exchange_action(0, 3) != XWB_OK)
        return 15;
    sent.round = 2; sent.action_id = 4; sent.result_digest = 0x456789AB;
    sent.rng_state = 0x98765432; sent.actor = 3; sent.kind = XWB_ACTION_DIGIXROSS;
    sent.move_slot = 2; sent.target_side = 0; sent.target_slot = 1; sent.skill_id = 0x333;
    if (guest_xwb_session_submit_action(&sent) != XWB_OK || exchange_action(1, 4) != XWB_OK)
        return 16;
    sent.action_id = 5;
    if (host_xwb_session_submit_action(&sent) != XWB_INVALID ||
        guest_xwb_session_submit_action(&sent) != XWB_INVALID) return 17;
    if (host_xwb_session_get_match(&host_match) != XWB_OK ||
        guest_xwb_session_get_match(&guest_match) != XWB_OK ||
        host_match.xross_used != 3 || guest_match.xross_used != 3) return 18;

    if (host_xwb_session_end() != XWB_OK || guest_xwb_session_end() != XWB_OK) return 19;

    /* A validly checksummed but malformed remote record must not open the
     * formation lobby. */
    queue_head[0] = queue_head[1] = queue_count[0] = queue_count[1] = 0;
    virtual_frame = 0;
    corrupt_guest_first_team = 1;
    if (host_xwb_session_begin(0, 0x87654321u, host_records) != XWB_OK ||
        guest_xwb_session_begin(1, 0, guest_records) != XWB_OK) return 20;
    for (i = 1; i <= 400; ++i) {
        int host_result = host_xwb_session_pump(i);
        int guest_result = guest_xwb_session_pump(i);
        if (host_result < 0 || guest_result < 0) break;
    }
    if (host_xwb_session_get_state() != XWB_SESSION_FAILED ||
        host_xwb_session_get_match(&host_match) != XWB_OK ||
        host_match.phase != XWB_FORMATION) return 21;
    if (host_xwb_session_end() != XWB_OK || guest_xwb_session_end() != XWB_OK) return 22;
    return 0;
}
