#ifndef XWB_WIRELESS_BATTLE_H
#define XWB_WIRELESS_BATTLE_H

typedef unsigned char xwb_u8;
typedef unsigned short xwb_u16;
typedef unsigned int xwb_u32;

enum xwb_status {
    XWB_OK = 0, XWB_INVALID = -1, XWB_PHASE = -2, XWB_HOST_ONLY = -3,
    XWB_STALE = -4, XWB_NOT_READY = -5, XWB_CRC = -6
};
enum xwb_phase { XWB_FORMATION = 1, XWB_BATTLE = 2, XWB_FINISHED = 3, XWB_ABORTED = 4 };
enum xwb_music {
    XWB_XROS_NORMAL, XWB_XROS_BOSS, XWB_DUSK_BOSS, XWB_DUSK_MULTIPLAYER,
    XWB_WORLD_DS_NORMAL, XWB_WORLD_DS_BOSS, XWB_WORLD_DS_MULTIPLAYER,
    XWB_MUSIC_COUNT
};
enum xwb_packet_type {
    XWB_HELLO = 1, XWB_TEAM, XWB_FORMATION_PACKET, XWB_MUSIC_PACKET,
    XWB_READY_PACKET, XWB_START, XWB_COMMAND, XWB_ACK, XWB_RESULT, XWB_ABORT,
    XWB_ROUND_PACKET
};

/* Host-owned canonical lobby state. The transport adapter must bind a sender
 * to its actual peer role; the caller cannot trust a role supplied in a packet.
 * Both teams must be validated by the engine adapter before set_team is called.
 * No native game pointers, saved records, or allocation ownership live here.
 */
typedef struct xwb_match {
    xwb_u32 tag, session, revision, round;
    xwb_u32 team_digest[2];
    xwb_u8 formation[2][6];
    xwb_u8 teams, formations, ready, phase, music, xross_used, reserved[2];
} xwb_match;

typedef struct xwb_packet_view {
    xwb_u32 session, sequence;
    const xwb_u8 *payload;
    xwb_u16 length;
    xwb_u8 type, sender;
} xwb_packet_view;

/* Opaque six-record transfer buffer. Completing this transfer is not engine
 * validation. The adapter must decode approved fields and validate species,
 * moves, equipment and statistics; never memcpy these bytes into a save. */
typedef struct xwb_team_transfer {
    xwb_u32 tag, transfer, digest;
    xwb_u16 received, reserved;
    xwb_u8 records[768];
} xwb_team_transfer;

unsigned xwb_sizeof_match(void);
int xwb_init(xwb_match *m, xwb_u32 session);
int xwb_set_team(xwb_match *m, unsigned side, xwb_u32 digest);
int xwb_set_formation(xwb_match *m, unsigned side, const xwb_u8 positions[6]);
int xwb_select_music(xwb_match *m, unsigned caller, unsigned music);
int xwb_set_ready(xwb_match *m, unsigned side, unsigned ready, xwb_u32 revision);
int xwb_start(xwb_match *m, unsigned caller, xwb_u32 revision);
int xwb_next_round(xwb_match *m, unsigned caller);
int xwb_can_digixross(const xwb_match *m, unsigned side);
int xwb_commit_digixross(xwb_match *m, unsigned caller, unsigned side);
xwb_u32 xwb_digixross_damage(xwb_u32 damage);
int xwb_finish(xwb_match *m, unsigned caller);
int xwb_abort(xwb_match *m);
unsigned xwb_sizeof_team_transfer(void);
int xwb_team_reset(xwb_team_transfer *team, xwb_u32 transfer);
int xwb_team_chunk(const xwb_u8 records[768], xwb_u32 transfer, unsigned index,
                   xwb_u8 out[72]);
int xwb_team_accept(xwb_team_transfer *team, const xwb_u8 *payload, unsigned length);
int xwb_team_digest(const xwb_team_transfer *team, xwb_u32 *digest);

/* Overlay only the saved-record fields verified against live battle actors.
 * `actor` must already be initialized by the game for this species; this does
 * not construct model pointers, status state, or an engine-owned actor. */
int xwb_apply_saved_record_fields(xwb_u8 actor[0x1A0], const xwb_u8 saved[0x80]);

/* Wire format: 24-byte header + at most72 payload bytes. Integers are little
 * endian, independent of C structure padding. CRC covers header bytes0..19 and
 * the payload. decode returns a view into the input; copy before buffer reuse.
 * Packet size is a provisional adapter limit, not a verified SDK capacity.
 */
int xwb_encode(xwb_u8 *out, unsigned capacity, unsigned type, unsigned sender,
               xwb_u32 session, xwb_u32 sequence, const xwb_u8 *payload,
               unsigned length);
int xwb_decode(const xwb_u8 *wire, unsigned length, xwb_u32 expected_session,
               unsigned expected_sender, xwb_packet_view *out);

#endif
