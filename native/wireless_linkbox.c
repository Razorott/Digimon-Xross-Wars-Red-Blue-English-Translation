/* Experimental Link Box lobby controls. This adds a real configuration and
 * readiness screen to the existing wireless connection menu. The Start Match
 * action advances the protocol only; the retail battle launcher/command loop
 * is still a separate, unfinished integration. */
#include "wireless_session.h"
#include "wireless_transport.h"

typedef unsigned char xwb_ui_u8;
typedef unsigned int xwb_ui_u32;
extern int xwb_session_request_from_linkbox(void);

#ifndef XWB_UI_TEXT_FN
#define XWB_UI_TEXT_FN 0x0203BE64u
#endif
#ifndef XWB_UI_DRAW_FN
#define XWB_UI_DRAW_FN 0x0203A834u
#endif
#ifndef XWB_UI_FINISH_FN
#define XWB_UI_FINISH_FN 0x0203A85Cu
#endif

enum { XWB_UI_ENTRY, XWB_UI_LOBBY, XWB_UI_FORMATION, XWB_UI_ARMED };
enum { XWB_MSG_BATTLE = 106, XWB_MSG_HELP = 107, XWB_MSG_OPEN = 108,
       XWB_MSG_FORMATION = 109, XWB_MSG_START = 110, XWB_MSG_LEAVE = 111,
       XWB_MSG_PAIR_BASE = 112, XWB_MSG_SWAP = 127, XWB_MSG_RESET = 128,
       XWB_MSG_READY_BASE = 129, XWB_MSG_DONE = 131,
       XWB_MSG_MUSIC_BASE = 132, XWB_MSG_ARMED = 139,
       XWB_MSG_NONE_READY = 140, XWB_MSG_BOTH_READY = 141,
       XWB_MSG_WAIT_HOST = 142 };

static void *xwb_linkbox_owner;
static unsigned xwb_linkbox_ui_mode;
static unsigned xwb_linkbox_pair;
static void *xwb_linkbox_last_owner;
static unsigned xwb_linkbox_last_state = ~0u;
static unsigned xwb_linkbox_last_mode = ~0u;
static unsigned xwb_linkbox_last_revision = ~0u;
static unsigned xwb_linkbox_last_ready = ~0u;
static unsigned xwb_linkbox_last_music = ~0u;
static unsigned xwb_linkbox_last_pair = ~0u;

static void xwb_linkbox_draw_row(void *owner, unsigned index, unsigned message) {
    typedef void *(*text_fn)(unsigned, unsigned);
    typedef void (*draw_fn)(void *, int, int, int, int, void *);
    typedef void (*finish_fn)(void *);
    volatile xwb_ui_u8 *object = (volatile xwb_ui_u8 *)owner;
    xwb_ui_u32 rows = (xwb_ui_u32)object[0x2c] |
                      (xwb_ui_u32)object[0x2d] << 8 |
                      (xwb_ui_u32)object[0x2e] << 16 |
                      (xwb_ui_u32)object[0x2f] << 24;
    void *row = (void *)(rows + index * 0x50u);
    void *text = ((text_fn)XWB_UI_TEXT_FN)(21u, message);
    ((draw_fn)XWB_UI_DRAW_FN)(row, 0, 0, 0, 3, text);
    ((finish_fn)XWB_UI_FINISH_FN)(row);
}

static unsigned xwb_linkbox_ready_message(void) {
    xwb_match match;
    unsigned ready = 0;
    if (xwb_session_get_match(&match) == XWB_OK) ready = match.ready & 3u;
    if (!ready) return XWB_MSG_NONE_READY;
    if (ready == 1) return XWB_MSG_READY_BASE;
    if (ready == 2) return XWB_MSG_READY_BASE + 1u;
    return XWB_MSG_BOTH_READY;
}

static void xwb_linkbox_redraw(void) {
    xwb_match match;
    int state = xwb_session_get_state();
    if (!xwb_linkbox_owner) return;
    if (state == XWB_SESSION_BATTLE) xwb_linkbox_ui_mode = XWB_UI_ARMED;
    if (state != XWB_SESSION_TEAMS_READY && state != XWB_SESSION_BATTLE) {
        xwb_linkbox_ui_mode = XWB_UI_ENTRY;
        xwb_linkbox_draw_row(xwb_linkbox_owner, 4, XWB_MSG_BATTLE);
        return;
    }
    if (xwb_linkbox_ui_mode == XWB_UI_ENTRY) {
        xwb_linkbox_draw_row(xwb_linkbox_owner, 4, XWB_MSG_OPEN);
        return;
    }
    if (xwb_linkbox_ui_mode == XWB_UI_ARMED) {
        if (xwb_session_get_match(&match) == XWB_OK) {
            xwb_linkbox_draw_row(xwb_linkbox_owner, 0, XWB_MSG_FORMATION);
            xwb_linkbox_draw_row(xwb_linkbox_owner, 1, XWB_MSG_MUSIC_BASE + match.music);
            xwb_linkbox_draw_row(xwb_linkbox_owner, 2, xwb_linkbox_ready_message());
        }
        xwb_linkbox_draw_row(xwb_linkbox_owner, 3, XWB_MSG_ARMED);
        xwb_linkbox_draw_row(xwb_linkbox_owner, 4, XWB_MSG_LEAVE);
        return;
    }
    if (xwb_linkbox_ui_mode == XWB_UI_FORMATION) {
        xwb_linkbox_draw_row(xwb_linkbox_owner, 0, XWB_MSG_PAIR_BASE + xwb_linkbox_pair);
        xwb_linkbox_draw_row(xwb_linkbox_owner, 1, XWB_MSG_SWAP);
        xwb_linkbox_draw_row(xwb_linkbox_owner, 2, XWB_MSG_RESET);
        xwb_linkbox_draw_row(xwb_linkbox_owner, 3, xwb_linkbox_ready_message());
        xwb_linkbox_draw_row(xwb_linkbox_owner, 4, XWB_MSG_DONE);
        return;
    }
    if (xwb_session_get_match(&match) != XWB_OK) return;
    xwb_linkbox_draw_row(xwb_linkbox_owner, 0, XWB_MSG_FORMATION);
    xwb_linkbox_draw_row(xwb_linkbox_owner, 1, XWB_MSG_MUSIC_BASE + match.music);
    xwb_linkbox_draw_row(xwb_linkbox_owner, 2, xwb_linkbox_ready_message());
    xwb_linkbox_draw_row(xwb_linkbox_owner, 3,
        xwb_transport_get_side() == 0 ? XWB_MSG_START : XWB_MSG_WAIT_HOST);
    xwb_linkbox_draw_row(xwb_linkbox_owner, 4, XWB_MSG_LEAVE);
}

/* Called from the Link Box root update, after the native packet pump. The
 * main action child is embedded at root+0x28 and is live only in state0x7D0;
 * clear our borrowed pointer whenever the parent switches to another modal. */
void xwb_linkbox_update_ui(void *root) {
    volatile xwb_ui_u8 *bytes = (volatile xwb_ui_u8 *)root;
    xwb_ui_u32 state, revision = ~0u, ready = ~0u, music = ~0u;
    xwb_match match;
    unsigned session_state;
    if (!root) return;
    state = (xwb_ui_u32)bytes[0x20] | (xwb_ui_u32)bytes[0x21] << 8 |
            (xwb_ui_u32)bytes[0x22] << 16 | (xwb_ui_u32)bytes[0x23] << 24;
    if (state != 0x7D0u) {
        xwb_linkbox_owner = 0;
        xwb_linkbox_last_owner = 0;
        return;
    }
    xwb_linkbox_owner = (void *)(bytes + 0x28);
    session_state = (unsigned)xwb_session_get_state();
    if (xwb_session_get_match(&match) == XWB_OK) {
        revision = match.revision;
        ready = match.ready;
        music = match.music;
    }
    if (xwb_linkbox_last_owner != xwb_linkbox_owner ||
        xwb_linkbox_last_state != session_state ||
        xwb_linkbox_last_mode != xwb_linkbox_ui_mode ||
        xwb_linkbox_last_revision != revision ||
        xwb_linkbox_last_ready != ready || xwb_linkbox_last_music != music ||
        xwb_linkbox_last_pair != xwb_linkbox_pair) {
        xwb_linkbox_redraw();
        xwb_linkbox_last_owner = xwb_linkbox_owner;
        xwb_linkbox_last_state = session_state;
        xwb_linkbox_last_mode = xwb_linkbox_ui_mode;
        xwb_linkbox_last_revision = revision;
        xwb_linkbox_last_ready = ready;
        xwb_linkbox_last_music = music;
        xwb_linkbox_last_pair = xwb_linkbox_pair;
    }
}

/* Called by the fifth-row renderer after the first four retail rows are drawn. */
void xwb_linkbox_draw_battle_row(void *owner) {
    xwb_linkbox_owner = owner;
    xwb_linkbox_redraw();
}

static void xwb_linkbox_swap_pair(xwb_u8 positions[6], unsigned pair) {
    unsigned a = 0, b = 1, n = 0, i;
    for (a = 0; a < 6; ++a) {
        for (b = a + 1; b < 6; ++b) {
            if (n++ == pair) goto found;
        }
    }
    return;
found:
    for (i = 0; i < 6; ++i) {
        if (positions[i] == a) positions[i] = (xwb_ui_u8)b;
        else if (positions[i] == b) positions[i] = (xwb_ui_u8)a;
    }
}

static int xwb_linkbox_set_formation_pair(unsigned pair) {
    xwb_match match;
    xwb_u8 formation[6];
    unsigned side, i;
    int result;
    int actual_side = xwb_transport_get_side();
    if (actual_side < 0 || pair >= 15 || xwb_session_get_match(&match) != XWB_OK)
        return XWB_INVALID;
    side = (unsigned)actual_side;
    for (i = 0; i < 6; ++i) formation[i] = match.formation[side][i];
    xwb_linkbox_swap_pair(formation, pair);
    result = xwb_session_set_formation(formation);
    return result;
}

/* Returns one when a lobby action was consumed, zero for retail dispatch. */
int xwb_linkbox_lobby_dispatch(unsigned action, void *child) {
    xwb_match match;
    int side, result = XWB_OK;
    if (action > 4) return 0;
    if (child) xwb_linkbox_owner = child;
    side = xwb_transport_get_side();
    if (xwb_linkbox_ui_mode == XWB_UI_ENTRY) {
        if (action != 4 || xwb_session_get_state() != XWB_SESSION_TEAMS_READY)
            return 0;
        xwb_linkbox_ui_mode = XWB_UI_LOBBY;
        xwb_linkbox_redraw();
        return 1;
    }
    if (xwb_linkbox_ui_mode == XWB_UI_ARMED) {
        if (action == 4) {
            xwb_session_end();
            xwb_linkbox_ui_mode = XWB_UI_ENTRY;
        }
        xwb_linkbox_redraw();
        return 1;
    }
    if (xwb_session_get_state() != XWB_SESSION_TEAMS_READY) return 0;
    if (xwb_linkbox_ui_mode == XWB_UI_FORMATION) {
        if (action == 0) xwb_linkbox_pair = (xwb_linkbox_pair + 1u) % 15u;
        else if (action == 1) result = xwb_linkbox_set_formation_pair(xwb_linkbox_pair);
        else if (action == 2) {
            static const xwb_u8 identity[6] = {0,1,2,3,4,5};
            result = xwb_session_set_formation(identity);
        } else if (action == 3) {
            if (side >= 0 && xwb_session_get_match(&match) == XWB_OK)
                result = xwb_session_set_ready(((match.ready >> (unsigned)side) & 1u) == 0);
            else result = XWB_INVALID;
        } else xwb_linkbox_ui_mode = XWB_UI_LOBBY;
        xwb_linkbox_redraw();
        return 1;
    }
    if (action == 0) {
        xwb_linkbox_ui_mode = XWB_UI_FORMATION;
        xwb_linkbox_pair = 0;
    } else if (action == 1) {
        if (side >= 0 && xwb_session_get_match(&match) == XWB_OK)
            result = xwb_session_select_music((match.music + 1u) % XWB_MUSIC_COUNT);
        else result = XWB_INVALID;
    } else if (action == 2) {
        if (side >= 0 && xwb_session_get_match(&match) == XWB_OK)
            result = xwb_session_set_ready(((match.ready >> (unsigned)side) & 1u) == 0);
        else result = XWB_INVALID;
    } else if (action == 3) {
        result = xwb_session_start();
        if (result == XWB_OK) xwb_linkbox_ui_mode = XWB_UI_ARMED;
    } else {
        xwb_session_end();
        xwb_linkbox_ui_mode = XWB_UI_ENTRY;
    }
    /* Keep the menu open if a protocol operation is waiting on its ACK. */
    xwb_linkbox_redraw();
    return 1;
}

/* Called by a branch at 0x020D4410, after retail labels0-3 have been drawn.
 * Replay the four displaced setup instructions and resume the constructor. */
__attribute__((naked)) void xwb_linkbox_render_battle_row_hook(void) {
    __asm__ volatile (
        "stmdb sp!, {r0-r12, lr}\n"
        "mov r0, r8\n"
        "bl xwb_linkbox_draw_battle_row\n"
        "ldmia sp!, {r0-r12, lr}\n"
        "ldr r0, =0x020D4454\n"
        "ldr r0, [r0]\n"
        "add r6, sp, #8\n"
        "ldm r0, {r0-r3}\n"
        "stm r6, {r0-r3}\n"
        "ldr pc, =0x020D4420\n"
    );
}

/* Five actions plus the retail Back entry; row four holds Open/Leave. */
__attribute__((naked)) void xwb_linkbox_five_choice_result_hook(void) {
    __asm__ volatile (
        "cmp r0, #5\n" "moveq r6, r7\n"
        "cmp r0, #0\n" "moveq sb, #0\n"
        "cmp r0, #1\n" "moveq sb, #1\n"
        "cmp r0, #2\n" "moveq sb, #2\n"
        "cmp r0, #3\n" "moveq sb, #3\n"
        "cmp r0, #4\n" "moveq sb, #4\n"
        "ldr r0, [r4, #0x34]\n"
        "cmp sb, r0\n" "moveq r5, #1\n"
        "ldr pc, =0x020D469C\n"
    );
}

__attribute__((naked)) void xwb_linkbox_five_choice_up_hook(void) {
    __asm__ volatile (
        "cmp r0, #0\n" "beq 1f\n"
        "cmp sb, #0\n" "moveq sb, #4\n" "subne sb, sb, #1\n"
        "1: ldr pc, =0x020D4740\n"
    );
}

__attribute__((naked)) void xwb_linkbox_five_choice_down_hook(void) {
    __asm__ volatile (
        "cmp r0, #0\n" "beq 1f\n"
        "cmp sb, #4\n" "moveq sb, #0\n" "addne sb, sb, #1\n"
        "1: ldr pc, =0x020D4788\n"
    );
}

/* Pass lobby actions to the native menu, retaining the original connection
 * prompt for the first action while the team exchange is still underway. */
__attribute__((naked)) void xwb_linkbox_battle_dispatch_hook(void) {
    __asm__ volatile (
        "ldr r0, [r4, #0x34]\n"
        "mov r1, r4\n"
        "bl xwb_linkbox_lobby_dispatch\n"
        "cmp r0, #0\n"
        "bne 2f\n"
        "ldr r0, [r4, #0x34]\n"
        "cmp r0, #4\n"
        "bne 1f\n"
        "bl xwb_session_request_from_linkbox\n"
        "cmp r0, #0\n"
        "bne 2f\n"
        "mov r0, #0x7d0\n"
        "str r0, [r4, #0x1c]\n"
        "mov r0, #0x15\n"
        "str r0, [r4, #0x38]\n"
        "ldr pc, =0x020D49FC\n"
        "1: ldr pc, =0x020D4804\n"
        "2: ldr pc, =0x020D49FC\n"
    );
}
