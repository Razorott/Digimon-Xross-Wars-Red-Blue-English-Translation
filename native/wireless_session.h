#ifndef XWB_WIRELESS_SESSION_H
#define XWB_WIRELESS_SESSION_H
#include "wireless_battle.h"

enum xwb_session_state {
    XWB_SESSION_IDLE = 0,
    XWB_SESSION_CONNECTING = 1,
    XWB_SESSION_EXCHANGING = 2,
    XWB_SESSION_TEAMS_READY = 3,
    XWB_SESSION_BATTLE = 4,
    XWB_SESSION_FAILED = 5
};
enum xwb_action_kind {
    XWB_ACTION_ATTACK = 0,
    XWB_ACTION_SKILL = 1,
    XWB_ACTION_GUARD = 2,
    XWB_ACTION_DIGIXROSS = 3
};
typedef struct xwb_action {
    xwb_u32 round, action_id, result_digest, rng_state;
    xwb_u16 skill_id;
    xwb_u8 actor, kind, move_slot, target_side, target_slot, flags;
} xwb_action;

/* `records` is exactly six 0x80-byte saved-party records. This module only
 * transports the opaque bytes; it never writes them back to a save or treats
 * them as battle actors. Host supplies a nonzero session id; guest supplies 0. */
int xwb_session_begin(unsigned side, xwb_u32 session, const xwb_u8 records[768]);
/* Drive retries and receive callbacks from the owning game's active update path. */
void xwb_session_frame_tick(void);
int xwb_session_pump(xwb_u32 frame);
int xwb_session_get_state(void);
int xwb_session_copy_remote(xwb_u8 records[768]);
int xwb_session_get_match(xwb_match *out);
int xwb_session_set_formation(const xwb_u8 positions[6]);
int xwb_session_select_music(unsigned music);
int xwb_session_set_ready(unsigned ready);
int xwb_session_start(void);
int xwb_session_submit_action(const xwb_action *action);
int xwb_session_take_action(xwb_action *action);
int xwb_session_confirm_action(xwb_u32 action_id, xwb_u32 state_digest, xwb_u32 rng_state);
int xwb_session_next_round(void);
int xwb_session_end(void);

#endif
