#include "wireless_battle.h"

#define XWB_TAG 0x31425758u
#define XWB_VERSION 1u
#define XWB_HEADER 24u
#define XWB_PAYLOAD 72u

static int valid(const xwb_match *m) {
    return m && m->tag == XWB_TAG && m->session;
}
static int lobby(const xwb_match *m) {
    if (!valid(m)) return XWB_INVALID;
    return m->phase == XWB_FORMATION ? XWB_OK : XWB_PHASE;
}
static void changed(xwb_match *m) {
    ++m->revision;
    /* Avoid a wrap-around accidentally matching a stale ready confirmation. */
    if (!m->revision) m->phase = XWB_ABORTED;
    m->ready = 0;
}
unsigned xwb_sizeof_match(void) { return sizeof(xwb_match); }
int xwb_init(xwb_match *m, xwb_u32 session) {
    unsigned i;
    xwb_u8 *p = (xwb_u8 *)m;
    if (!m || !session) return XWB_INVALID;
    for (i = 0; i < sizeof(*m); ++i) p[i] = 0;
    m->tag = XWB_TAG;
    m->session = session;
    m->revision = 1;
    m->phase = XWB_FORMATION;
    return XWB_OK;
}
int xwb_set_team(xwb_match *m, unsigned side, xwb_u32 digest) {
    int status = lobby(m);
    if (status) return status;
    if (side > 1) return XWB_INVALID;
    if ((m->teams & (1u << side)) && m->team_digest[side] == digest) return XWB_OK;
    m->team_digest[side] = digest;
    m->teams |= 1u << side;
    m->formations &= ~(1u << side);
    changed(m);
    return XWB_OK;
}
int xwb_set_formation(xwb_match *m, unsigned side, const xwb_u8 positions[6]) {
    unsigned i, mask = 0, differs = 0;
    int status = lobby(m);
    if (status) return status;
    if (side > 1 || !positions) return XWB_INVALID;
    if (!(m->teams & (1u << side))) return XWB_NOT_READY;
    for (i = 0; i < 6; ++i) {
        unsigned n = positions[i];
        if (n >= 6 || (mask & (1u << n))) return XWB_INVALID;
        mask |= 1u << n;
        differs |= m->formation[side][i] != n;
    }
    if (!differs && (m->formations & (1u << side))) return XWB_OK;
    for (i = 0; i < 6; ++i) m->formation[side][i] = positions[i];
    m->formations |= 1u << side;
    changed(m);
    return XWB_OK;
}
int xwb_select_music(xwb_match *m, unsigned caller, unsigned music) {
    int status = lobby(m);
    if (status) return status;
    if (caller > 1 || music >= XWB_MUSIC_COUNT) return XWB_INVALID;
    if (caller != 0) return XWB_HOST_ONLY;
    if (m->music != music) {
        m->music = music;
        changed(m);
    }
    return XWB_OK;
}
int xwb_set_ready(xwb_match *m, unsigned side, unsigned ready, xwb_u32 revision) {
    int status = lobby(m);
    if (status) return status;
    if (side > 1 || ready > 1) return XWB_INVALID;
    if (revision != m->revision) return XWB_STALE;
    if (m->teams != 3 || m->formations != 3) return XWB_NOT_READY;
    if (ready) m->ready |= 1u << side;
    else m->ready &= ~(1u << side);
    return XWB_OK;
}
int xwb_start(xwb_match *m, unsigned caller, xwb_u32 revision) {
    int status = lobby(m);
    if (status) return status;
    if (caller > 1) return XWB_INVALID;
    if (caller) return XWB_HOST_ONLY;
    if (revision != m->revision) return XWB_STALE;
    if (m->teams != 3 || m->formations != 3 || m->ready != 3) return XWB_NOT_READY;
    m->phase = XWB_BATTLE;
    m->round = 1;
    m->xross_used = 0;
    return XWB_OK;
}
int xwb_next_round(xwb_match *m, unsigned caller) {
    if (!valid(m) || caller > 1) return XWB_INVALID;
    if (caller) return XWB_HOST_ONLY;
    if (m->phase != XWB_BATTLE) return XWB_PHASE;
    if (m->round == 0xFFFFFFFFu) { m->phase = XWB_ABORTED; return XWB_INVALID; }
    ++m->round;
    return XWB_OK;
}
int xwb_can_digixross(const xwb_match *m, unsigned side) {
    return valid(m) && side < 2 && m->phase == XWB_BATTLE && m->round > 1 &&
           !(m->xross_used & (1u << side));
}
int xwb_commit_digixross(xwb_match *m, unsigned caller, unsigned side) {
    if (!valid(m) || side > 1 || caller > 1) return XWB_INVALID;
    if (caller) return XWB_HOST_ONLY;
    if (!xwb_can_digixross(m, side)) return XWB_PHASE;
    m->xross_used |= 1u << side;
    return XWB_OK;
}
xwb_u32 xwb_digixross_damage(xwb_u32 damage) {
    xwb_u32 reduced;
    if (!damage) return 0;
    /* floor(0.9 * damage) without overflow, with normal minimum-one damage. */
    reduced = damage - damage / 10u - (damage % 10u != 0);
    return reduced ? reduced : 1;
}
int xwb_finish(xwb_match *m, unsigned caller) {
    if (!valid(m) || caller > 1) return XWB_INVALID;
    if (caller) return XWB_HOST_ONLY;
    if (m->phase != XWB_BATTLE) return XWB_PHASE;
    m->phase = XWB_FINISHED;
    return XWB_OK;
}
int xwb_abort(xwb_match *m) {
    if (!valid(m)) return XWB_INVALID;
    m->phase = XWB_ABORTED;
    m->ready = 0;
    return XWB_OK;
}

static xwb_u32 read32(const xwb_u8 *p) {
    return (xwb_u32)p[0] | (xwb_u32)p[1] << 8 | (xwb_u32)p[2] << 16 | (xwb_u32)p[3] << 24;
}
static void write32(xwb_u8 *p, xwb_u32 n) {
    p[0] = n; p[1] = n >> 8; p[2] = n >> 16; p[3] = n >> 24;
}
static xwb_u16 read16(const xwb_u8 *p) { return (xwb_u16)(p[0] | (xwb_u16)p[1] << 8); }
static void write16(xwb_u8 *p, xwb_u16 n) { p[0] = (xwb_u8)n; p[1] = (xwb_u8)(n >> 8); }

int xwb_apply_saved_record_fields(xwb_u8 actor[0x1A0], const xwb_u8 saved[0x80]) {
    static const xwb_u8 saved_stat_offsets[] = {0x26, 0x2C, 0x2A, 0x28, 0x2E};
    static const xwb_u8 actor_stat_offsets[][2] = {
        {0x44, 0x46}, {0x48, 0x4A}, {0x4C, 0x4E}, {0x50, 0x52}, {0x54, 0x56}
    };
    unsigned i;
    xwb_u16 species, hp, max_hp, mp, max_mp;
    if (!actor || !saved) return XWB_INVALID;
    species = read16(saved + 0x12);
    hp = read16(saved + 0x1E); max_hp = read16(saved + 0x20);
    mp = read16(saved + 0x22); max_mp = read16(saved + 0x24);
    if (!species || !max_hp || hp > max_hp || !max_mp || mp > max_mp)
        return XWB_INVALID;

    write16(actor + 0x14, species);
    for (i = 0; i < 18; ++i) actor[0x1A + i] = saved[i];
    write32(actor + 0xE4, hp); write32(actor + 0xE0, max_hp);
    write16(actor + 0xEA, mp); write16(actor + 0xE8, max_mp);
    for (i = 0; i < 5; ++i) {
        xwb_u16 value = read16(saved + saved_stat_offsets[i]);
        write16(actor + actor_stat_offsets[i][0], value);
        write16(actor + actor_stat_offsets[i][1], value);
    }
    /* The two four-halfword ranges are copied verbatim. Their semantic
     * labels are intentionally not guessed here. */
    for (i = 0; i < 4; ++i) {
        write16(actor + 0xFA + i * 2, read16(saved + 0x34 + i * 2));
        write16(actor + 0x10A + i * 2, read16(saved + 0x44 + i * 2));
    }
    write16(actor + 0x13C, read16(saved + 0x4C));
    write16(actor + 0x140, read16(saved + 0x4C));
    return XWB_OK;
}

static xwb_u32 crc_byte(xwb_u32 crc, xwb_u8 byte) {
    unsigned i;
    crc ^= byte;
    for (i = 0; i < 8; ++i) crc = (crc >> 1) ^ ((0u - (crc & 1u)) & 0xEDB88320u);
    return crc;
}
static xwb_u32 packet_crc(const xwb_u8 *p, unsigned payload_length) {
    unsigned i;
    xwb_u32 crc = 0xFFFFFFFFu;
    for (i = 0; i < 20; ++i) crc = crc_byte(crc, p[i]);
    for (i = 0; i < payload_length; ++i) crc = crc_byte(crc, p[XWB_HEADER + i]);
    return ~crc;
}
unsigned xwb_sizeof_team_transfer(void) { return sizeof(xwb_team_transfer); }
int xwb_team_reset(xwb_team_transfer *team, xwb_u32 transfer) {
    unsigned i;
    xwb_u8 *p = (xwb_u8 *)team;
    if (!team || !transfer) return XWB_INVALID;
    for (i = 0; i < sizeof(*team); ++i) p[i] = 0;
    team->tag = 0x31545758u;
    team->transfer = transfer;
    return XWB_OK;
}
int xwb_team_chunk(const xwb_u8 records[768], xwb_u32 transfer, unsigned index,
                   xwb_u8 out[72]) {
    unsigned i, offset;
    if (!records || !out || !transfer || index >= 12) return XWB_INVALID;
    offset = index * 64;
    write32(out, transfer);
    out[4] = offset; out[5] = offset >> 8;
    out[6] = 0; out[7] = 3; /* Fixed total768, little endian. */
    for (i = 0; i < 64; ++i) out[8 + i] = records[offset + i];
    return 72;
}
int xwb_team_accept(xwb_team_transfer *team, const xwb_u8 *payload, unsigned length) {
    unsigned offset, total, index, bit, i;
    xwb_u32 crc;
    if (!team || team->tag != 0x31545758u || !payload || length != 72) return XWB_INVALID;
    if (read32(payload) != team->transfer) return XWB_STALE;
    offset = (unsigned)payload[4] | (unsigned)payload[5] << 8;
    total = (unsigned)payload[6] | (unsigned)payload[7] << 8;
    if (total != 768 || offset >= 768 || (offset & 63)) return XWB_INVALID;
    index = offset >> 6;
    bit = 1u << index;
    if (team->received & bit) {
        for (i = 0; i < 64; ++i)
            if (team->records[offset + i] != payload[8 + i]) return XWB_INVALID;
        return team->received == 0xFFF ? 1 : 0;
    }
    for (i = 0; i < 64; ++i) team->records[offset + i] = payload[8 + i];
    team->received |= bit;
    if (team->received != 0xFFF) return 0;
    crc = 0xFFFFFFFFu;
    for (i = 0; i < 768; ++i) crc = crc_byte(crc, team->records[i]);
    team->digest = ~crc;
    return 1;
}
int xwb_team_digest(const xwb_team_transfer *team, xwb_u32 *digest) {
    if (!team || team->tag != 0x31545758u || !digest) return XWB_INVALID;
    if (team->received != 0xFFF) return XWB_NOT_READY;
    *digest = team->digest;
    return XWB_OK;
}
int xwb_encode(xwb_u8 *out, unsigned capacity, unsigned type, unsigned sender,
               xwb_u32 session, xwb_u32 sequence, const xwb_u8 *payload,
               unsigned length) {
    unsigned i;
    if (!out || !session || sender > 1 || type < XWB_HELLO || type > XWB_ROUND_PACKET ||
        length > XWB_PAYLOAD || capacity < XWB_HEADER + length || (length && !payload)) return XWB_INVALID;
    write32(out, XWB_TAG);
    out[4] = XWB_VERSION; out[5] = 0; out[6] = type; out[7] = sender;
    write32(out + 8, session); write32(out + 12, sequence);
    out[16] = length; out[17] = 0; out[18] = 0; out[19] = 0;
    for (i = 0; i < length; ++i) out[XWB_HEADER + i] = payload[i];
    write32(out + 20, packet_crc(out, length));
    return XWB_HEADER + length;
}
int xwb_decode(const xwb_u8 *wire, unsigned length, xwb_u32 expected_session,
               unsigned expected_sender, xwb_packet_view *out) {
    unsigned payload_length;
    xwb_u32 session;
    if (!wire || !out || expected_sender > 1 || length < XWB_HEADER || length > XWB_HEADER + XWB_PAYLOAD) return XWB_INVALID;
    payload_length = (unsigned)wire[16] | (unsigned)wire[17] << 8;
    session = read32(wire + 8);
    if (read32(wire) != XWB_TAG || wire[4] != XWB_VERSION || wire[5] ||
        wire[6] < XWB_HELLO || wire[6] > XWB_ROUND_PACKET || wire[7] != expected_sender ||
        wire[18] || wire[19] || !session || payload_length > XWB_PAYLOAD ||
        length != XWB_HEADER + payload_length) return XWB_INVALID;
    if (expected_session ? session != expected_session : wire[6] != XWB_HELLO) return XWB_STALE;
    if (read32(wire + 20) != packet_crc(wire, payload_length)) return XWB_CRC;
    out->session = session; out->sequence = read32(wire + 12);
    out->payload = wire + XWB_HEADER; out->length = payload_length;
    out->type = wire[6]; out->sender = wire[7];
    return XWB_OK;
}
