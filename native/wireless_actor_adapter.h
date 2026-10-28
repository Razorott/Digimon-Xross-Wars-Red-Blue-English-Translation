#ifndef XWB_WIRELESS_ACTOR_ADAPTER_H
#define XWB_WIRELESS_ACTOR_ADAPTER_H
#include "wireless_battle.h"

/* Populate opponent actor slots6-11 from six saved-record snapshots. Slots
 * 9-11 inherit display/position defaults from initialized opponent slots6-8;
 * the game's actor-record fields are then overlaid without touching save RAM.
 * Formation maps each roster record to an opponent position. */
int xwb_build_opponent_actors(xwb_u8 actors[12 * 0x1A0],
                              const xwb_u8 records[768],
                              const xwb_u8 formation[6]);

#endif
