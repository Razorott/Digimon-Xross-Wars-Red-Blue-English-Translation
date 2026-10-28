#include "wireless_session.h"
#include "wireless_transport.h"

void xwb_linkbox_draw_battle_row(void *owner);
void xwb_linkbox_update_ui(void *root);
int xwb_linkbox_lobby_dispatch(unsigned action, void *child);

volatile unsigned char xwb_test_owner[0x40];
volatile unsigned char xwb_test_root[0x80];
volatile unsigned xwb_test_request_count;
volatile unsigned xwb_test_session_state;
volatile unsigned xwb_test_side;
volatile unsigned xwb_test_start_count;
volatile unsigned xwb_test_end_count;
volatile unsigned xwb_test_music_count;
volatile unsigned xwb_test_ready_count;
volatile unsigned xwb_test_formation_count;
xwb_match xwb_test_match;

int xwb_session_request_from_linkbox(void) {
    ++xwb_test_request_count;
    return XWB_OK;
}
int xwb_session_get_state(void) { return (int)xwb_test_session_state; }
int xwb_transport_get_side(void) { return (int)xwb_test_side; }
int xwb_session_get_match(xwb_match *out) {
    unsigned i;
    xwb_u8 *dst = (xwb_u8 *)out;
    xwb_u8 *src = (xwb_u8 *)&xwb_test_match;
    for (i = 0; i < sizeof(*out); ++i) dst[i] = src[i];
    return XWB_OK;
}
int xwb_session_set_formation(const xwb_u8 positions[6]) {
    unsigned i;
    for (i = 0; i < 6; ++i) xwb_test_match.formation[xwb_test_side][i] = positions[i];
    ++xwb_test_formation_count;
    return XWB_OK;
}
int xwb_session_select_music(unsigned music) {
    if (xwb_test_side != 0) return XWB_HOST_ONLY;
    xwb_test_match.music = (xwb_u8)music;
    ++xwb_test_music_count;
    return XWB_OK;
}
int xwb_session_set_ready(unsigned ready) {
    if (ready) xwb_test_match.ready |= 1u << xwb_test_side;
    else xwb_test_match.ready &= ~(1u << xwb_test_side);
    ++xwb_test_ready_count;
    return XWB_OK;
}
int xwb_session_start(void) {
    if (xwb_test_side) return XWB_HOST_ONLY;
    ++xwb_test_start_count;
    xwb_test_session_state = XWB_SESSION_BATTLE;
    return XWB_OK;
}
int xwb_session_end(void) {
    ++xwb_test_end_count;
    xwb_test_session_state = XWB_SESSION_IDLE;
    return XWB_OK;
}

int xwb_test_main(void) {
    xwb_linkbox_draw_battle_row((void *)xwb_test_owner);
    return 0;
}
int xwb_test_dispatch(unsigned action) {
    return xwb_linkbox_lobby_dispatch(action, (void *)xwb_test_owner);
}
int xwb_test_update_ui(void) {
    xwb_linkbox_update_ui((void *)xwb_test_root);
    return 0;
}
