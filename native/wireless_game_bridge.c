/* Initial integration bridge. Bootstraps the coordinator when the retail
 * wireless overlay loads. It does not yet replace any exchange handler or
 * launch a battle; those hooks require verified engine/transport adapters. */
#include "wireless_battle.h"
#include "wireless_actor_adapter.h"
#include "wireless_party.h"
#ifdef XWB_SESSION_CONTROLLER
#include "wireless_session.h"
#include "wireless_transport.h"
extern void xwb_linkbox_update_ui(void *root);
#endif

volatile xwb_u32 xwb_boot_marker;
xwb_match xwb_live_match;
xwb_team_transfer xwb_live_transfers[2];
/* Relocation builds redirect the retail actor pointers here. Extra slots are
 * not active until each affected engine routine has its own verified adapter. */
xwb_u32 xwb_actor_storage[(12 * 0x1A0) / 4];

/* The formation UI stores nine stable Digimon IDs at an 8-byte stride. The
 * first six are Vanguard then Rearguard. Saved records are 0x80 bytes and
 * expose the same ID at +0x74. These addresses were read-only checked against
 * fresh Blue and Red formation-screen states; record copies stay in native
 * scratch storage and are never written back. */
int xwb_capture_local_party(xwb_u8 out[768]) {
    return xwb_capture_formation_party(
        (const volatile xwb_u8 *)0x021F0700u, 108u,
        (const volatile xwb_u8 *)0x021F2EF4u, out);
}

#ifdef XWB_EXTENDED_ORDER
/* The build tool installs relocated retail instructions in this allocation.
 * A private context prevents twelve entries from overwriting retail fields. */
const xwb_u32 xwb_order_program[0x25C / 4] = { 0xFFFFFFFFu };
xwb_u32 xwb_order_context[0x990 / 4];

void *xwb_order_get_context(void) { return xwb_order_context; }

#ifdef XWB_SESSION_CONTROLLER
static unsigned xwb_remote_actors_ready;
static xwb_u8 xwb_remote_party_records[768];

/* Called at actor index6 in the retail initiative builder, after the retail
 * battle has initialized its three opponent templates and before it scans
 * them. A failed preparation aborts the wireless gates and keeps the retail
 * nine-actor bound instead of sorting zero-filled reserved records. */
__attribute__((used)) static int xwb_prepare_remote_actors(void) {
    xwb_match match;
    int side;
    if (xwb_remote_actors_ready) return 1;
    if (xwb_live_match.phase != XWB_BATTLE ||
        xwb_session_get_state() != XWB_SESSION_BATTLE) return 0;
    side = xwb_transport_get_side();
    if (side < 0 || xwb_session_get_match(&match) != XWB_OK ||
        match.phase != XWB_BATTLE || match.teams != 3 ||
        match.formations != 3 || match.ready != 3 ||
        xwb_session_copy_remote(xwb_remote_party_records) != XWB_OK ||
        xwb_validate_party_records(xwb_remote_party_records) != XWB_OK ||
        xwb_build_opponent_actors((xwb_u8 *)xwb_actor_storage,
            xwb_remote_party_records, match.formation[(unsigned)side ^ 1u]) != XWB_OK) {
        xwb_live_match.phase = XWB_ABORTED;
        return 0;
    }
    xwb_remote_actors_ready = 1;
    return 1;
}
#endif

/* Verified command ring IDs:0 opens tactics,4 opens consumable items. Keep
 * normal battles byte-for-byte on the retail path; restrict wireless input
 * as well as the initial ring mask so touch and button confirms agree. */
void xwb_ring_open(unsigned enabled, unsigned blocked) {
    if (xwb_live_match.phase == XWB_BATTLE) {
        enabled &= ~0x11u;
        blocked |= 0x11u;
    }
    ((void (*)(unsigned, unsigned))0x02205354)(enabled, blocked);
}

int xwb_ring_selection(void) {
    int selection = ((int (*)(void))0x022054EC)();
    if (xwb_live_match.phase == XWB_BATTLE && (selection == 0 || selection == 4))
        return -1;
    return selection;
}

int xwb_all_tactics_pressed(void) {
    if (xwb_live_match.phase == XWB_BATTLE) {
#ifdef XWB_SESSION_CONTROLLER
        /* The Link Box parent may stop updating after the game enters its
         * battle overlay. This battle-loop status check is the active point
         * where wireless tactics are already suppressed, so keep the local
         * radio/session controller moving while the battle runs too. */
        xwb_session_frame_tick();
#endif
        return 0;
    }
    return ((int (*)(void))0x022123B8)();
}

/* Called in place of the retail CMP r8,#9. Preserve every register except ip
 * and the condition flags, as required at this exact instruction boundary. */
__attribute__((naked)) void xwb_order_compare_actor(void) {
    __asm__ volatile (
#ifdef XWB_SESSION_CONTROLLER
        "ldr r12, =xwb_live_match\n"
        "ldrb r12, [r12, #39]\n"
        "cmp r12, #2\n"
        "bne 3f\n"
        "ldr r12, =xwb_remote_actors_ready\n"
        "ldr r12, [r12]\n"
        "cmp r12, #1\n"
        "beq 2f\n"
        "cmp r8, #6\n"
        "bne 3f\n"
        "stmdb sp!, {r0-r3, r12, lr}\n"
        "bl xwb_prepare_remote_actors\n"
        "cmp r0, #1\n"
        "ldmia sp!, {r0-r3, r12, lr}\n"
        "bne 3f\n"
        "2: mov r12, #12\n"
        "b 4f\n"
        "3: mov r12, #9\n"
        "4: cmp r8, r12\n"
        "bx lr\n"
#else
        "ldr r12, =xwb_live_match\n"
        "ldrb r12, [r12, #39]\n"
        "cmp r12, #2\n"
        "moveq r12, #12\n"
        "movne r12, #9\n"
        "cmp r8, r12\n"
        "bx lr\n"
#endif
    );
}

#ifdef XWB_SESSION_CONTROLLER
/* Battle setup calls this immediately before its per-actor finalization loop.
 * Install the exchanged team before the engine reads slots 9-11, then replay
 * the displaced actor-base load and resume retail setup. */
__attribute__((naked)) void xwb_prepare_remote_setup_hook(void) {
    __asm__ volatile (
        "stmdb sp!, {r0-r3, r12, lr}\n"
        "bl xwb_prepare_remote_actors\n"
        "ldmia sp!, {r0-r3, r12, lr}\n"
        "ldr r6, =xwb_actor_storage\n"
        "ldr pc, =0x022169F0\n"
    );
}

/* Retail actor finalization scans slots 0-8. Use twelve only after the
 * wireless actor adapter has populated all six opponent records. */
__attribute__((naked)) void xwb_actor_setup_limit_hook(void) {
    __asm__ volatile (
        "ldr r0, =xwb_live_match\n"
        "ldrb r0, [r0, #39]\n"
        "cmp r0, #2\n"
        "bne 1f\n"
        "ldr r0, =xwb_remote_actors_ready\n"
        "ldr r0, [r0]\n"
        "cmp r0, #1\n"
        "moveq r0, #12\n"
        "movne r0, #9\n"
        "b 2f\n"
        "1: mov r0, #9\n"
        "2: cmp r4, r0\n"
        "ldr pc, =0x02216A14\n"
    );
}
#endif
#endif

void xwb_overlay_boot(void) {
    /* A local initialization token only. The battle handler must establish a
     * fresh session with its peer before sending any protocol packets. */
    if (xwb_init(&xwb_live_match, 1) == XWB_OK)
        xwb_boot_marker = 0x58424F4Bu;
}

#ifdef XWB_SESSION_CONTROLLER
/* The Link Box controller runs from ARM9. This small inter-overlay hook keeps
 * radio/session work on that menu's ordinary update path. It does nothing until
 * a future battle action has explicitly begun a session. */
static xwb_u32 xwb_session_frame;
static xwb_u32 xwb_session_counter;
static xwb_u32 xwb_session_request_frames;
static unsigned xwb_session_requested;

static xwb_u32 xwb_new_session_id(void) {
    volatile xwb_u16 *timer = (volatile xwb_u16 *)0x04000100u;
    xwb_u32 value;
    ++xwb_session_counter;
    value = ((xwb_u32)timer[0] << 16) | timer[1];
    value ^= xwb_session_frame * 0x9E3779B9u;
    value ^= xwb_session_counter * 0x85EBCA6Bu;
    value ^= *(volatile xwb_u32 *)0x02223460u;
    value ^= 0x58574232u;
    return value ? value : 1u;
}

/* The existing Link Box has already completed WH/WM discovery and connected
 * one peer before this action is available. Start the application protocol
 * only on that live connection, with the current six formation records. */
int xwb_session_begin_from_linkbox(void) {
    static xwb_u8 local_party[768];
    int side = xwb_transport_get_side();
    xwb_u32 session;
    if (side < 0) return side;
    if (xwb_capture_local_party(local_party) != XWB_OK) return XWB_INVALID;
#ifdef XWB_EXTENDED_ORDER
    xwb_remote_actors_ready = 0;
#endif
    session = side == 0 ? xwb_new_session_id() : 0;
    return xwb_session_begin((unsigned)side, session, local_party);
}

/* Called only after the player confirms the Link Box Battle entry. Defer the
 * protocol start until the retail Wait/Find flow reports a connected peer. */
int xwb_session_request_from_linkbox(void) {
    int state = xwb_session_get_state();
    if (xwb_session_requested ||
        (state != XWB_SESSION_IDLE && state != XWB_SESSION_FAILED))
        return XWB_NOT_READY;
    if (state == XWB_SESSION_FAILED) xwb_session_end();
    xwb_session_requested = 1;
    xwb_session_request_frames = 0;
    return XWB_OK;
}

void xwb_session_frame_tick(void) {
    int state;
    if (xwb_session_requested) {
        int side = xwb_transport_get_side();
        if (side >= 0) {
            int result = xwb_session_begin_from_linkbox();
            xwb_session_requested = 0;
            xwb_session_request_frames = 0;
            if (result != XWB_OK && xwb_session_get_state() == XWB_SESSION_FAILED)
                xwb_session_end();
        } else if (++xwb_session_request_frames >= 1800u) {
            /* A canceled or abandoned retail connection cannot arm a later
             * unrelated link as a battle. One update tick is about one frame. */
            xwb_session_requested = 0;
            xwb_session_request_frames = 0;
        }
    }
    state = xwb_session_get_state();
    if (state >= XWB_SESSION_CONNECTING && state < XWB_SESSION_FAILED)
        xwb_session_pump(++xwb_session_frame);

    /* Engine hooks read xwb_live_match, while the protocol owns the canonical
     * lobby/battle state in its private runtime. Keep the engine view current
     * after pumping so a received START takes effect on this same frame. A
     * failed/disconnected session must immediately close the wireless battle
     * gates; an ended session returns the engine to its ordinary nine actors. */
    state = xwb_session_get_state();
    if (state == XWB_SESSION_FAILED) {
        xwb_live_match.phase = XWB_ABORTED;
    } else if (state == XWB_SESSION_IDLE) {
        if (xwb_live_match.phase != XWB_FORMATION || xwb_live_match.session != 1u)
            xwb_init(&xwb_live_match, 1u);
    } else if (xwb_session_get_match(&xwb_live_match) != XWB_OK) {
        xwb_live_match.phase = XWB_ABORTED;
    }
}

/* ARM9's Link Box parent state-machine update is patched at its first
 * instruction. It remains active while the Wait/Find child modal owns input. */
__attribute__((naked)) void xwb_linkbox_pump_hook(void) {
    __asm__ volatile (
        "stmdb sp!, {r0-r12, lr}\n"
        "bl xwb_session_frame_tick\n"
        "ldr r0, [sp]\n"
        "bl xwb_linkbox_update_ui\n"
        "ldmia sp!, {r0-r12, lr}\n"
        "stmdb sp!, {r4-r8, sb, lr}\n"
        "ldr pc, =0x020D4BAC\n");
}
#endif
