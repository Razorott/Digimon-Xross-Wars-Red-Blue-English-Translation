#ifndef XWB_WIRELESS_TRANSPORT_H
#define XWB_WIRELESS_TRANSPORT_H
#include "wireless_battle.h"

/* Bind only after the original connection flow has established exactly one
 * peer. Side0 is the native parent, side1 the child. Session0 is allowed only
 * while the child awaits the host's HELLO. No radio setup/reset is performed.
 */
int xwb_transport_bind(unsigned side, xwb_u32 session);
int xwb_transport_get_side(void);
int xwb_transport_set_session(xwb_u32 session);
int xwb_transport_send(unsigned type, xwb_u32 sequence, const xwb_u8 *payload, unsigned length);
int xwb_transport_take(xwb_u8 *out, unsigned capacity);
int xwb_transport_detach(void);
unsigned xwb_transport_dropped(void);
int xwb_transport_connected(void);
int xwb_transport_radio_busy(void);

#endif
