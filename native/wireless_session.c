#include "wireless_session.h"
#include "wireless_party.h"
#include "wireless_transport.h"

#define SESSION_MAGIC 0x31574258u /* "XBW1" little-endian */
#define SESSION_RETRY_FRAMES 180u
#define SESSION_MAX_RETRIES 5u

typedef struct xwb_session_runtime {
    unsigned state, side, pending, retries;
    unsigned remote_complete, lobby_ready, tx_index, rx_index;
    unsigned action_available, action_wait_result;
    xwb_u32 session, pending_sequence, deadline, ack_sequence;
    xwb_u32 last_start_sequence, expected_result_id, expected_result_digest;
    xwb_u32 expected_result_rng_state, last_result_id, last_result_digest, last_result_rng_state;
    xwb_u32 last_action_id, last_remote_action_id;
    xwb_u32 local_update_sequence;
    xwb_u32 last_remote_formation_sequence, last_remote_music_sequence;
    xwb_u32 transfer_id;
    xwb_u8 local[768], wire[96], pending_type, pending_length;
    xwb_u8 pending_payload[72], ack_due;
    xwb_u8 last_remote_formation[6], last_remote_music;
    xwb_u8 has_remote_formation, has_remote_music;
    xwb_u8 local_update_kind;
    xwb_action remote_action;
    xwb_team_transfer remote;
    xwb_match match;
} xwb_session_runtime;

static xwb_session_runtime runtime;
static int fail_session(int error) {
    runtime.state = XWB_SESSION_FAILED;
    xwb_transport_detach();
    return error;
}

static xwb_u32 read32(const xwb_u8 *p) {
    return (xwb_u32)p[0] | (xwb_u32)p[1] << 8 |
           (xwb_u32)p[2] << 16 | (xwb_u32)p[3] << 24;
}
static void write32(xwb_u8 *p, xwb_u32 v) {
    p[0] = (xwb_u8)v; p[1] = (xwb_u8)(v >> 8);
    p[2] = (xwb_u8)(v >> 16); p[3] = (xwb_u8)(v >> 24);
}
static xwb_u16 read16(const xwb_u8 *p) { return (xwb_u16)(p[0] | (xwb_u16)p[1] << 8); }
static void write16(xwb_u8 *p, xwb_u16 v) { p[0] = (xwb_u8)v; p[1] = (xwb_u8)(v >> 8); }
static int valid_formation(const xwb_u8 *positions) {
    unsigned i, mask = 0;
    for (i = 0; i < 6; ++i) {
        unsigned position = positions[i];
        if (position >= 6 || (mask & (1u << position))) return 0;
        mask |= 1u << position;
    }
    return 1;
}
static void decode_action(xwb_action *a, const xwb_u8 *p) {
    a->round = read32(p); a->action_id = read32(p + 4);
    a->result_digest = read32(p + 8); a->rng_state = read32(p + 12);
    a->actor = p[16]; a->kind = p[17]; a->move_slot = p[18];
    a->target_side = p[19]; a->target_slot = p[20]; a->flags = p[21];
    a->skill_id = read16(p + 22);
}
static void encode_action(xwb_u8 *p, const xwb_action *a) {
    write32(p, a->round); write32(p + 4, a->action_id);
    write32(p + 8, a->result_digest); write32(p + 12, a->rng_state);
    p[16] = a->actor; p[17] = a->kind; p[18] = a->move_slot;
    p[19] = a->target_side; p[20] = a->target_slot; p[21] = a->flags;
    write16(p + 22, a->skill_id);
}
static int same_action(const xwb_action *a, const xwb_action *b) {
    return a->round == b->round && a->action_id == b->action_id &&
        a->result_digest == b->result_digest && a->rng_state == b->rng_state &&
        a->actor == b->actor && a->kind == b->kind && a->move_slot == b->move_slot &&
        a->target_side == b->target_side && a->target_slot == b->target_slot &&
        a->flags == b->flags && a->skill_id == b->skill_id;
}
static xwb_u32 records_crc(const xwb_u8 *p, unsigned length) {
    unsigned i, bit;
    xwb_u32 crc = 0xFFFFFFFFu;
    for (i = 0; i < length; ++i) {
        crc ^= p[i];
        for (bit = 0; bit < 8; ++bit)
            crc = (crc >> 1) ^ ((0u - (crc & 1u)) & 0xEDB88320u);
    }
    return ~crc;
}
static int set_local_lobby(void) {
    static const xwb_u8 identity[6] = {0,1,2,3,4,5};
    if (xwb_set_team(&runtime.match, runtime.side, records_crc(runtime.local, 768)) != XWB_OK ||
        xwb_set_formation(&runtime.match, runtime.side, identity) != XWB_OK) return XWB_INVALID;
    return XWB_OK;
}
static int set_remote_lobby(void) {
    static const xwb_u8 identity[6] = {0,1,2,3,4,5};
    xwb_u32 digest;
    if (xwb_validate_party_records(runtime.remote.records) != XWB_OK ||
        xwb_team_digest(&runtime.remote, &digest) != XWB_OK ||
        xwb_set_team(&runtime.match, runtime.side ^ 1u, digest) != XWB_OK ||
        xwb_set_formation(&runtime.match, runtime.side ^ 1u, identity) != XWB_OK) return XWB_INVALID;
    runtime.lobby_ready = 1;
    return XWB_OK;
}
static xwb_u32 make_transfer_id(void) {
    xwb_u32 id = runtime.session ^ (runtime.side ? 0x47535431u : 0x484F5354u);
    return id ? id : 1;
}
static int queue_packet(unsigned type, xwb_u32 sequence,
                        const xwb_u8 *payload, unsigned length) {
    unsigned i;
    if (runtime.pending || length > sizeof(runtime.pending_payload)) return XWB_NOT_READY;
    runtime.pending_type = (xwb_u8)type;
    runtime.pending_sequence = sequence;
    runtime.pending_length = (xwb_u8)length;
    for (i = 0; i < length; ++i) runtime.pending_payload[i] = payload[i];
    runtime.pending = 1;
    runtime.retries = 0;
    runtime.deadline = 0;
    return XWB_OK;
}
static int queue_ack(xwb_u32 sequence) {
    runtime.ack_sequence = sequence;
    runtime.ack_due = 1;
    return XWB_OK;
}
static int queue_hello(void) {
    xwb_u8 hello[8];
    write32(hello, SESSION_MAGIC);
    hello[4] = 1; /* protocol */
    hello[5] = 6; /* party size */
    hello[6] = 0x80; hello[7] = 0; /* opaque record stride */
    return queue_packet(XWB_HELLO, 0, hello, sizeof(hello));
}
static int queue_team_chunk(void) {
    xwb_u8 chunk[72];
    int n;
    if (runtime.tx_index >= 12) return XWB_NOT_READY;
    n = xwb_team_chunk(runtime.local, runtime.transfer_id, runtime.tx_index, chunk);
    if (n != (int)sizeof(chunk)) return XWB_INVALID;
    return queue_packet(XWB_TEAM, runtime.tx_index + 1, chunk, sizeof(chunk));
}
static int send_ack_if_due(void) {
    xwb_u8 payload[4];
    int result;
    if (!runtime.ack_due || xwb_transport_radio_busy()) return XWB_NOT_READY;
    write32(payload, runtime.ack_sequence);
    result = xwb_transport_send(XWB_ACK, runtime.ack_sequence, payload, sizeof(payload));
    if (result == XWB_OK) runtime.ack_due = 0;
    return result;
}
static int send_pending(xwb_u32 frame) {
    int result;
    if (!runtime.pending || xwb_transport_radio_busy()) return XWB_NOT_READY;
    result = xwb_transport_send(runtime.pending_type, runtime.pending_sequence,
                                runtime.pending_payload, runtime.pending_length);
    if (result == XWB_OK) {
        runtime.deadline = frame + SESSION_RETRY_FRAMES;
        return XWB_OK;
    }
    return result;
}
static int receive_one(void) {
    xwb_packet_view packet;
    int n = xwb_transport_take(runtime.wire, sizeof(runtime.wire));
    int accepted;
    if (n == XWB_NOT_READY) return XWB_NOT_READY;
    if (n < 0) return n;
    accepted = xwb_decode(runtime.wire, (unsigned)n, runtime.session,
                          runtime.side ^ 1u, &packet);
    if (accepted != XWB_OK) return accepted;

    if (packet.type == XWB_HELLO) {
        if (runtime.side != 1 || (runtime.session && runtime.session != packet.session) ||
            packet.sequence || packet.length != 8 ||
            read32(packet.payload) != SESSION_MAGIC || packet.payload[4] != 1 ||
            packet.payload[5] != 6 || packet.payload[6] != 0x80 || packet.payload[7])
            return XWB_INVALID;
        if (!runtime.session) {
            runtime.session = packet.session;
            if (xwb_transport_set_session(runtime.session) != XWB_OK ||
                xwb_init(&runtime.match, runtime.session) != XWB_OK) return XWB_NOT_READY;
            runtime.transfer_id = make_transfer_id();
            {
                xwb_u32 remote_id = runtime.session ^ 0x484F5354u;
                if (!remote_id) remote_id = 1;
                if (xwb_team_reset(&runtime.remote, remote_id) != XWB_OK || set_local_lobby())
                    return XWB_INVALID;
            }
        }
        queue_ack(packet.sequence);
        runtime.state = XWB_SESSION_EXCHANGING;
        return XWB_OK;
    }
    if (packet.type == XWB_ACK) {
        if (packet.length != 4 || !runtime.pending ||
            packet.sequence != runtime.pending_sequence ||
            read32(packet.payload) != runtime.pending_sequence) return XWB_STALE;
        runtime.pending = 0;
        runtime.retries = 0;
        runtime.deadline = 0;
        if (runtime.pending_type == XWB_HELLO) {
            if (runtime.side == 0) runtime.tx_index = 0;
        } else if (runtime.pending_type == XWB_TEAM) {
            ++runtime.tx_index;
            if (runtime.tx_index == 12 && runtime.remote_complete)
                runtime.state = XWB_SESSION_TEAMS_READY;
        }
        return XWB_OK;
    }
    if (packet.type == XWB_TEAM) {
        unsigned chunk_index;
        if (packet.length != 72 || packet.sequence < 1 || packet.sequence > 12)
            return XWB_INVALID;
        chunk_index = packet.sequence - 1;
        if (chunk_index > runtime.rx_index) return XWB_STALE;
        if (chunk_index < runtime.rx_index) {
            accepted = xwb_team_accept(&runtime.remote, packet.payload, packet.length);
            if (accepted < 0) return accepted;
            queue_ack(packet.sequence);
            return XWB_OK;
        }
        accepted = xwb_team_accept(&runtime.remote, packet.payload, packet.length);
        if (accepted < 0) return accepted;
        ++runtime.rx_index;
        queue_ack(packet.sequence);
        if (accepted == 1) {
            runtime.remote_complete = 1;
            if (set_remote_lobby()) return XWB_INVALID;
            runtime.state = runtime.tx_index == 12 ? XWB_SESSION_TEAMS_READY : XWB_SESSION_EXCHANGING;
        }
        return XWB_OK;
    }
    if (packet.type == XWB_FORMATION_PACKET) {
        unsigned i;
        if (packet.length != 6) return XWB_INVALID;
        if (runtime.has_remote_formation &&
            packet.sequence == runtime.last_remote_formation_sequence) {
            for (i = 0; i < 6; ++i)
                if (packet.payload[i] != runtime.last_remote_formation[i]) return XWB_INVALID;
            queue_ack(packet.sequence);
            return XWB_OK;
        }
        if (runtime.state < XWB_SESSION_TEAMS_READY) return XWB_PHASE;
        /* Two players can edit different formations at once. If both local
         * revisions advanced from the same base, merge the peer's team field
         * into that revision instead of treating the other edit as stale. */
        if (packet.sequence == runtime.match.revision &&
            runtime.local_update_sequence == packet.sequence &&
            (runtime.local_update_kind == XWB_FORMATION_PACKET ||
             runtime.local_update_kind == XWB_MUSIC_PACKET)) {
            if (!valid_formation(packet.payload)) return XWB_INVALID;
            for (i = 0; i < 6; ++i)
                runtime.match.formation[runtime.side ^ 1u][i] = packet.payload[i];
            runtime.match.formations |= 1u << (runtime.side ^ 1u);
            runtime.match.ready = 0;
            runtime.last_remote_formation_sequence = packet.sequence;
            for (i = 0; i < 6; ++i) runtime.last_remote_formation[i] = packet.payload[i];
            runtime.has_remote_formation = 1;
            runtime.local_update_kind = 0;
            queue_ack(packet.sequence);
            return XWB_OK;
        }
        if (packet.sequence == runtime.match.revision &&
            (runtime.match.formations & (1u << (runtime.side ^ 1u)))) {
            for (i = 0; i < 6; ++i)
                if (packet.payload[i] != runtime.match.formation[runtime.side ^ 1u][i])
                    return XWB_STALE;
            runtime.last_remote_formation_sequence = packet.sequence;
            for (i = 0; i < 6; ++i) runtime.last_remote_formation[i] = packet.payload[i];
            runtime.has_remote_formation = 1;
            queue_ack(packet.sequence);
            return XWB_OK;
        }
        if (packet.sequence != runtime.match.revision + 1) return XWB_STALE;
        accepted = xwb_set_formation(&runtime.match, runtime.side ^ 1u, packet.payload);
        if (accepted != XWB_OK) return accepted;
        if (packet.sequence != runtime.match.revision) return XWB_STALE;
        runtime.last_remote_formation_sequence = packet.sequence;
        for (i = 0; i < 6; ++i) runtime.last_remote_formation[i] = packet.payload[i];
        runtime.has_remote_formation = 1;
        runtime.local_update_kind = 0;
        queue_ack(packet.sequence);
        return XWB_OK;
    }
    if (packet.type == XWB_MUSIC_PACKET) {
        if (runtime.side != 1 || packet.length != 5 || packet.payload[0] >= XWB_MUSIC_COUNT)
            return XWB_INVALID;
        if (runtime.has_remote_music && packet.sequence == runtime.last_remote_music_sequence) {
            if (packet.payload[0] != runtime.last_remote_music ||
                read32(packet.payload + 1) + 1 != packet.sequence) return XWB_INVALID;
            queue_ack(packet.sequence);
            return XWB_OK;
        }
        if (packet.sequence == runtime.match.revision && runtime.match.music == packet.payload[0]) {
            if (read32(packet.payload + 1) + 1 != packet.sequence) return XWB_INVALID;
            runtime.last_remote_music_sequence = packet.sequence;
            runtime.last_remote_music = packet.payload[0];
            runtime.has_remote_music = 1;
            queue_ack(packet.sequence);
            return XWB_OK;
        }
        /* A guest formation edit may advance its revision concurrently with
         * the host's music choice. Both are disjoint lobby fields. */
        if (packet.sequence == runtime.match.revision &&
            runtime.local_update_sequence == packet.sequence &&
            runtime.local_update_kind == XWB_FORMATION_PACKET &&
            read32(packet.payload + 1) + 1 == packet.sequence) {
            runtime.match.music = packet.payload[0];
            runtime.match.ready = 0;
            runtime.last_remote_music_sequence = packet.sequence;
            runtime.last_remote_music = packet.payload[0];
            runtime.has_remote_music = 1;
            runtime.local_update_kind = 0;
            queue_ack(packet.sequence);
            return XWB_OK;
        }
        if (packet.sequence != runtime.match.revision + 1) return XWB_STALE;
        if (read32(packet.payload + 1) != runtime.match.revision) return XWB_STALE;
        accepted = xwb_select_music(&runtime.match, 0, packet.payload[0]);
        if (accepted != XWB_OK || runtime.match.revision != packet.sequence) return XWB_STALE;
        runtime.last_remote_music_sequence = packet.sequence;
        runtime.last_remote_music = packet.payload[0];
        runtime.has_remote_music = 1;
        runtime.local_update_kind = 0;
        queue_ack(packet.sequence);
        return XWB_OK;
    }
    if (packet.type == XWB_READY_PACKET) {
        if (packet.length != 5 || packet.payload[0] > 1) return XWB_INVALID;
        accepted = xwb_set_ready(&runtime.match, runtime.side ^ 1u,
                                 packet.payload[0], read32(packet.payload + 1));
        if (accepted != XWB_OK) return accepted;
        queue_ack(packet.sequence);
        return XWB_OK;
    }
    if (packet.type == XWB_START) {
        if (packet.length != 4) return XWB_INVALID;
        if (runtime.match.phase == XWB_BATTLE && packet.sequence == runtime.last_start_sequence) {
            queue_ack(packet.sequence);
            return XWB_OK;
        }
        if (runtime.side != 1 || xwb_start(&runtime.match, 0, read32(packet.payload)) != XWB_OK)
            return XWB_NOT_READY;
        runtime.last_start_sequence = packet.sequence;
        runtime.state = XWB_SESSION_BATTLE;
        queue_ack(packet.sequence);
        return XWB_OK;
    }
    if (packet.type == XWB_ROUND_PACKET) {
        xwb_u32 round;
        if (runtime.side != 1 || packet.length != 4) return XWB_INVALID;
        round = read32(packet.payload);
        if (round == runtime.match.round && packet.sequence == round) {
            queue_ack(packet.sequence);
            return XWB_OK;
        }
        if (round != runtime.match.round + 1 || packet.sequence != round) return XWB_STALE;
        accepted = xwb_next_round(&runtime.match, 0);
        if (accepted != XWB_OK || runtime.match.round != round) return XWB_PHASE;
        queue_ack(packet.sequence);
        return XWB_OK;
    }
    if (packet.type == XWB_COMMAND) {
        xwb_action incoming;
        if (runtime.match.phase != XWB_BATTLE || packet.length != 24) return XWB_PHASE;
        decode_action(&incoming, packet.payload);
        if (incoming.round != runtime.match.round || incoming.action_id != packet.sequence ||
            incoming.actor >= 6 || incoming.kind > XWB_ACTION_DIGIXROSS ||
            incoming.target_side > 1 || incoming.target_slot >= 6 || incoming.flags)
            return XWB_INVALID;
        if (incoming.action_id <= runtime.last_action_id) {
            if (incoming.action_id == runtime.last_action_id) {
                if (incoming.action_id != runtime.last_remote_action_id ||
                    !same_action(&runtime.remote_action, &incoming)) return XWB_INVALID;
                queue_ack(packet.sequence);
                return XWB_OK;
            }
            return XWB_STALE;
        }
        if (incoming.action_id != runtime.last_action_id + 1) return XWB_STALE;
        if (incoming.kind == XWB_ACTION_DIGIXROSS) {
            if (!xwb_can_digixross(&runtime.match, packet.sender) ||
                xwb_commit_digixross(&runtime.match, 0, packet.sender) != XWB_OK) return XWB_PHASE;
        }
        if (runtime.action_available) {
            if (!same_action(&runtime.remote_action, &incoming)) return XWB_INVALID;
        } else {
            runtime.remote_action = incoming;
            runtime.action_available = 1;
            runtime.last_action_id = incoming.action_id;
            runtime.last_remote_action_id = incoming.action_id;
        }
        queue_ack(packet.sequence);
        return XWB_OK;
    }
    if (packet.type == XWB_RESULT) {
        if (packet.length != 12 || read32(packet.payload) != packet.sequence) return XWB_INVALID;
        if (!runtime.action_wait_result && packet.sequence == runtime.last_result_id &&
            read32(packet.payload + 4) == runtime.last_result_digest &&
            read32(packet.payload + 8) == runtime.last_result_rng_state) {
            queue_ack(packet.sequence);
            return XWB_OK;
        }
        if (!runtime.action_wait_result || packet.sequence != runtime.expected_result_id) return XWB_STALE;
        if (read32(packet.payload + 4) != runtime.expected_result_digest ||
            read32(packet.payload + 8) != runtime.expected_result_rng_state) {
            runtime.state = XWB_SESSION_FAILED;
            return XWB_CRC;
        }
        runtime.action_wait_result = 0;
        runtime.last_result_id = packet.sequence;
        runtime.last_result_digest = read32(packet.payload + 4);
        runtime.last_result_rng_state = read32(packet.payload + 8);
        queue_ack(packet.sequence);
        return XWB_OK;
    }
    if (packet.type == XWB_ABORT) {
        return fail_session(XWB_PHASE);
    }
    return XWB_INVALID;
}

int xwb_session_begin(unsigned side, xwb_u32 session, const xwb_u8 records[768]) {
    unsigned i;
    xwb_u8 *bytes = (xwb_u8 *)&runtime;
    if (side > 1 || !records || (side == 0 && !session) || (side == 1 && session) ||
        xwb_validate_party_records(records) != XWB_OK) return XWB_INVALID;
    for (i = 0; i < sizeof(runtime); ++i) bytes[i] = 0;
    runtime.side = side;
    runtime.session = session;
    runtime.state = XWB_SESSION_CONNECTING;
    for (i = 0; i < 768; ++i) runtime.local[i] = records[i];
    if (xwb_transport_bind(side, session) != XWB_OK) {
        runtime.state = XWB_SESSION_FAILED;
        return XWB_NOT_READY;
    }
    if (side == 0) {
        xwb_u32 remote_id = session ^ 0x47535431u;
        if (!remote_id) remote_id = 1;
        if (xwb_init(&runtime.match, session) != XWB_OK ||
            xwb_team_reset(&runtime.remote, remote_id) != XWB_OK) {
            runtime.state = XWB_SESSION_FAILED;
            xwb_transport_detach();
            return XWB_INVALID;
        }
        if (set_local_lobby()) {
            runtime.state = XWB_SESSION_FAILED;
            xwb_transport_detach();
            return XWB_INVALID;
        }
        runtime.transfer_id = make_transfer_id();
        runtime.state = XWB_SESSION_EXCHANGING;
        if (queue_hello() != XWB_OK) return XWB_NOT_READY;
    }
    return XWB_OK;
}

int xwb_session_pump(xwb_u32 frame) {
    int result;
    if (runtime.state == XWB_SESSION_IDLE || runtime.state == XWB_SESSION_FAILED)
        return XWB_PHASE;
    if (!xwb_transport_connected()) {
        return fail_session(XWB_NOT_READY);
    }
    result = receive_one();
    if (result < 0 && result != XWB_NOT_READY && result != XWB_STALE) {
        return fail_session(result);
    }
    if (runtime.ack_due) send_ack_if_due();
    if (runtime.pending && !xwb_transport_radio_busy()) {
        if (!runtime.deadline || (xwb_u32)(frame - runtime.deadline) < 0x80000000u) {
            if (runtime.deadline && ++runtime.retries > SESSION_MAX_RETRIES) {
                return fail_session(XWB_NOT_READY);
            }
            result = send_pending(frame);
        }
    }
    if (runtime.state == XWB_SESSION_EXCHANGING && !runtime.pending && !runtime.ack_due &&
        runtime.tx_index < 12 && (runtime.side == 0 || runtime.remote_complete))
        queue_team_chunk();
    if (runtime.match.phase == XWB_FORMATION && runtime.remote_complete && runtime.lobby_ready && runtime.tx_index == 12 &&
        !runtime.pending && !runtime.ack_due)
        runtime.state = XWB_SESSION_TEAMS_READY;
    return XWB_OK;
}

int xwb_session_get_state(void) { return (int)runtime.state; }
#ifdef XWB_SESSION_TEST
xwb_u32 xwb_session_debug_flags(void) {
    return (runtime.pending ? 1u : 0u) | (runtime.ack_due ? 2u : 0u) |
        ((xwb_u32)(runtime.state & 7u) << 2);
}
void xwb_session_debug_info(xwb_u32 out[4]) {
    if (!out) return;
    out[0] = xwb_session_debug_flags();
    out[1] = runtime.pending_sequence;
    out[2] = runtime.ack_sequence;
    out[3] = runtime.pending_type;
}
#endif
int xwb_session_copy_remote(xwb_u8 records[768]) {
    unsigned i;
    if (!records || !runtime.remote_complete) return XWB_NOT_READY;
    for (i = 0; i < 768; ++i) records[i] = runtime.remote.records[i];
    return XWB_OK;
}
int xwb_session_get_match(xwb_match *out) {
    unsigned i;
    const xwb_u8 *src;
    xwb_u8 *dst;
    if (!out || !runtime.session) return XWB_NOT_READY;
    src = (const xwb_u8 *)&runtime.match; dst = (xwb_u8 *)out;
    for (i = 0; i < sizeof(runtime.match); ++i) dst[i] = src[i];
    return XWB_OK;
}
int xwb_session_set_formation(const xwb_u8 positions[6]) {
    xwb_u8 payload[6];
    unsigned i;
    int result;
    if (!positions || runtime.state < XWB_SESSION_TEAMS_READY || runtime.match.phase != XWB_FORMATION)
        return XWB_PHASE;
    if (runtime.pending || runtime.ack_due) return XWB_NOT_READY;
    for (i = 0; i < 6; ++i) payload[i] = positions[i];
    result = xwb_set_formation(&runtime.match, runtime.side, positions);
    if (result != XWB_OK) return result;
    runtime.local_update_sequence = runtime.match.revision;
    runtime.local_update_kind = XWB_FORMATION_PACKET;
    return queue_packet(XWB_FORMATION_PACKET, runtime.match.revision, payload, sizeof(payload));
}
int xwb_session_select_music(unsigned music) {
    xwb_u8 payload[5];
    int result;
    if (runtime.side != 0) return XWB_HOST_ONLY;
    if (runtime.state < XWB_SESSION_TEAMS_READY || runtime.match.phase != XWB_FORMATION)
        return XWB_PHASE;
    if (runtime.pending || runtime.ack_due) return XWB_NOT_READY;
    result = xwb_select_music(&runtime.match, 0, music);
    if (result != XWB_OK) return result;
    runtime.local_update_sequence = runtime.match.revision;
    runtime.local_update_kind = XWB_MUSIC_PACKET;
    payload[0] = (xwb_u8)music;
    write32(payload + 1, runtime.match.revision - 1);
    return queue_packet(XWB_MUSIC_PACKET, runtime.match.revision, payload, sizeof(payload));
}
int xwb_session_set_ready(unsigned ready) {
    xwb_u8 payload[5];
    int result;
    if (ready > 1 || runtime.state < XWB_SESSION_TEAMS_READY || runtime.match.phase != XWB_FORMATION)
        return XWB_PHASE;
    if (runtime.pending || runtime.ack_due) return XWB_NOT_READY;
    result = xwb_set_ready(&runtime.match, runtime.side, ready, runtime.match.revision);
    if (result != XWB_OK) return result;
    payload[0] = (xwb_u8)ready;
    write32(payload + 1, runtime.match.revision);
    return queue_packet(XWB_READY_PACKET, runtime.match.revision, payload, sizeof(payload));
}
int xwb_session_start(void) {
    xwb_u8 payload[4];
    int result;
    if (runtime.side != 0) return XWB_HOST_ONLY;
    if (runtime.pending || runtime.ack_due || runtime.action_wait_result) return XWB_NOT_READY;
    write32(payload, runtime.match.revision);
    result = xwb_start(&runtime.match, 0, runtime.match.revision);
    if (result != XWB_OK) return result;
    runtime.state = XWB_SESSION_BATTLE;
    runtime.last_start_sequence = runtime.match.revision;
    result = queue_packet(XWB_START, runtime.match.revision, payload, sizeof(payload));
    if (result != XWB_OK) runtime.state = XWB_SESSION_FAILED;
    return result;
}
int xwb_session_submit_action(const xwb_action *action) {
    xwb_u8 payload[24];
    int result;
    if (!action || runtime.state != XWB_SESSION_BATTLE || runtime.match.phase != XWB_BATTLE)
        return XWB_PHASE;
    if (runtime.pending || runtime.ack_due || runtime.action_wait_result) return XWB_NOT_READY;
    if (action->round != runtime.match.round || action->action_id != runtime.last_action_id + 1 ||
        action->actor >= 6 || action->kind > XWB_ACTION_DIGIXROSS || action->target_side > 1 ||
        action->target_slot >= 6 || action->flags ||
        (action->kind == XWB_ACTION_DIGIXROSS && !xwb_can_digixross(&runtime.match, runtime.side)))
        return XWB_INVALID;
    if (action->kind == XWB_ACTION_DIGIXROSS &&
        xwb_commit_digixross(&runtime.match, 0, runtime.side) != XWB_OK) return XWB_PHASE;
    encode_action(payload, action);
    result = queue_packet(XWB_COMMAND, action->action_id, payload, sizeof(payload));
    if (result != XWB_OK) return result;
    runtime.last_action_id = action->action_id;
    runtime.expected_result_id = action->action_id;
    runtime.expected_result_digest = action->result_digest;
    runtime.expected_result_rng_state = action->rng_state;
    runtime.action_wait_result = 1;
    return XWB_OK;
}
int xwb_session_take_action(xwb_action *action) {
    unsigned i;
    const xwb_u8 *src;
    xwb_u8 *dst;
    if (!action || !runtime.action_available) return XWB_NOT_READY;
    src = (const xwb_u8 *)&runtime.remote_action;
    dst = (xwb_u8 *)action;
    for (i = 0; i < sizeof(runtime.remote_action); ++i) dst[i] = src[i];
    runtime.action_available = 0;
    return XWB_OK;
}
int xwb_session_confirm_action(xwb_u32 action_id, xwb_u32 state_digest, xwb_u32 rng_state) {
    xwb_u8 payload[12];
    if (runtime.state != XWB_SESSION_BATTLE || action_id != runtime.last_remote_action_id ||
        !action_id) return XWB_STALE;
    if (runtime.pending || runtime.ack_due) return XWB_NOT_READY;
    if (state_digest != runtime.remote_action.result_digest || rng_state != runtime.remote_action.rng_state) {
        return fail_session(XWB_CRC);
    }
    write32(payload, action_id);
    write32(payload + 4, state_digest);
    write32(payload + 8, rng_state);
    return queue_packet(XWB_RESULT, action_id, payload, sizeof(payload));
}
int xwb_session_next_round(void) {
    xwb_u8 payload[4];
    xwb_u32 round;
    int result;
    if (runtime.side != 0) return XWB_HOST_ONLY;
    if (runtime.state != XWB_SESSION_BATTLE || runtime.pending || runtime.ack_due ||
        runtime.action_wait_result || runtime.action_available) return XWB_NOT_READY;
    result = xwb_next_round(&runtime.match, 0);
    if (result != XWB_OK) return result;
    round = runtime.match.round;
    write32(payload, round);
    result = queue_packet(XWB_ROUND_PACKET, round, payload, sizeof(payload));
    if (result != XWB_OK) runtime.state = XWB_SESSION_FAILED;
    return result;
}
int xwb_session_end(void) {
    xwb_transport_detach();
    {
        xwb_u8 *p = (xwb_u8 *)&runtime;
        unsigned i;
        for (i = 0; i < sizeof(runtime); ++i) p[i] = 0;
    }
    return XWB_OK;
}
