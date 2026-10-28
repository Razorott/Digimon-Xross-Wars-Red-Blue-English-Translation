/* Adapter for the inspected batch124 native WH/WM application interface.
 * Keep inactive during all original Melody/DigiScore operations. */
#include "wireless_transport.h"

#define XWB_NATIVE_TAG 0x31425758u
#define XWB_BUSY (-7)
#define NATIVE_CONTEXT (*(volatile xwb_u32 *)0x02223460u)
#define NATIVE_TABLE (*(volatile xwb_u32 *)0x02220A90u)
typedef void (*native_receive)(int sequence, int tag, const xwb_u8 *bytes,
                               unsigned length, void *user);
typedef int (*set_receive)(native_receive callback, void *user);
typedef int (*native_send)(int tag, const xwb_u8 *bytes, unsigned length);
typedef int (*native_query)(void);

typedef struct xwb_radio {
    unsigned active, side, tx_pending, head, tail, count, dropped;
    xwb_u32 session, context, old_callback, old_user;
    xwb_u8 tx[96], rx[4][96];
    unsigned rx_length[4];
} xwb_radio;

static xwb_radio radio;

static int native_present(void) {
    /* Other overlays reuse the native wrapper addresses. Never call them when
     * the actual wireless overlay is absent. */
    return *(volatile xwb_u32 *)0x0221D4A8u == 0xE59F0004u &&
           *(volatile xwb_u32 *)0x0221D4ACu == 0xE590004Cu &&
           NATIVE_TABLE == 0x02220A98u;
}
static int pointer_valid(xwb_u32 address, unsigned size) {
    return address >= 0x02000000u && address <= 0x02400000u - size && !(address & 3);
}
static int connected(void) {
    return native_present() && radio.active && NATIVE_CONTEXT == radio.context &&
           ((native_query)0x0221D4A8u)() == 4;
}
static void receive_packet(int native_sequence, int tag, const xwb_u8 *bytes,
                            unsigned length, void *user) {
    xwb_packet_view view;
    unsigned i, slot;
    (void)native_sequence;
    if (user != &radio || !radio.active || (xwb_u32)tag != XWB_NATIVE_TAG) return;
    if (xwb_decode(bytes, length, radio.session, radio.side ^ 1u, &view) != XWB_OK) {
        ++radio.dropped;
        return;
    }
    if (radio.count == 4) { ++radio.dropped; return; }
    slot = radio.tail;
    for (i = 0; i < length; ++i) radio.rx[slot][i] = bytes[i];
    radio.rx_length[slot] = length;
    radio.tail = (slot + 1) & 3;
    ++radio.count;
}
int xwb_transport_bind(unsigned side, xwb_u32 session) {
    volatile xwb_u32 *context;
    xwb_u32 address;
    unsigned i;
    xwb_u8 *clear;
    if (side > 1 || (!side && !session)) return XWB_INVALID;
    if (radio.active) return XWB_BUSY;
    if (!native_present()) return XWB_NOT_READY;
    address = NATIVE_CONTEXT;
    if (!pointer_valid(address, 0x44)) return XWB_NOT_READY;
    context = (volatile xwb_u32 *)address;
    if (!pointer_valid(context[3], 96) || context[4] < 96) return XWB_NOT_READY;
    if (((native_query)0x0221D4A8u)() != 4 ||
        ((native_query)0x0221D4B8u)() != (int)side) return XWB_NOT_READY;
    clear = (xwb_u8 *)&radio;
    for (i = 0; i < sizeof(radio); ++i) clear[i] = 0;
    radio.side = side; radio.session = session; radio.context = address;
    radio.old_callback = context[5]; radio.old_user = context[6];
    radio.active = 1;
    if (!((set_receive)0x0221E210u)(receive_packet, &radio)) {
        radio.active = 0;
        return XWB_NOT_READY;
    }
    return XWB_OK;
}
int xwb_transport_get_side(void) {
    xwb_u32 address;
    int side;
    if (!native_present()) return XWB_NOT_READY;
    address = NATIVE_CONTEXT;
    if (!pointer_valid(address, 0x44) ||
        ((native_query)0x0221D4A8u)() != 4) return XWB_NOT_READY;
    side = ((native_query)0x0221D4B8u)();
    return side == 0 || side == 1 ? side : XWB_NOT_READY;
}
int xwb_transport_set_session(xwb_u32 session) {
    if (!session) return XWB_INVALID;
    if (!connected()) return XWB_NOT_READY;
    /* Changing the protocol filter does not touch the SDK's retained send
     * buffer. The receive queue must be empty so no old-session packet leaks. */
    if (radio.count) return XWB_BUSY;
    radio.session = session;
    return XWB_OK;
}
int xwb_transport_send(unsigned type, xwb_u32 sequence, const xwb_u8 *payload, unsigned length) {
    int encoded, result;
    if (!connected() || !radio.session) return XWB_NOT_READY;
    /* The retail sender retains the source pointer while its own64-byte
     * fragmentation/acknowledgment machinery works. Keep this buffer stable. */
    if (((native_query)0x0221E1D8u)()) return XWB_BUSY;
    radio.tx_pending = 0;
    encoded = xwb_encode(radio.tx, sizeof(radio.tx), type, radio.side,
                         radio.session, sequence, payload, length);
    if (encoded < 0) return encoded;
    result = ((native_send)0x0221E190u)((int)XWB_NATIVE_TAG, radio.tx, (unsigned)encoded);
    if (result < 0) return XWB_BUSY;
    radio.tx_pending = 1;
    return XWB_OK;
}
int xwb_transport_take(xwb_u8 *out, unsigned capacity) {
    unsigned i, slot, length;
    if (!connected()) return XWB_NOT_READY;
    if (!radio.count) return XWB_NOT_READY;
    slot = radio.head; length = radio.rx_length[slot];
    if (!out || capacity < length) return XWB_INVALID;
    for (i = 0; i < length; ++i) out[i] = radio.rx[slot][i];
    radio.head = (slot + 1) & 3;
    --radio.count;
    return (int)length;
}
int xwb_transport_detach(void) {
    volatile xwb_u32 *context;
    if (!radio.active) return XWB_OK;
    if (native_present() && NATIVE_CONTEXT == radio.context) {
        context = (volatile xwb_u32 *)radio.context;
        if (context[5] == (xwb_u32)receive_packet && context[6] == (xwb_u32)&radio)
            ((set_receive)0x0221E210u)((native_receive)radio.old_callback, (void *)radio.old_user);
    }
    radio.active = 0; radio.tx_pending = 0; radio.count = 0;
    return XWB_OK;
}
unsigned xwb_transport_dropped(void) { return radio.dropped; }
int xwb_transport_connected(void) { return connected(); }
int xwb_transport_radio_busy(void) {
    if (!connected()) return 1;
    return ((native_query)0x0221E1D8u)() != 0;
}
