# Local wireless battle component

This is **not a playable battle mode**. Separate experimental ROMs install the
native module and selected engine hooks. Stable releases remain unchanged.
The original wireless test used the user's hardware-tested batch124. The
current isolated TEST builds roll forward from the batch125 UI checkpoint so
Red keeps its reviewed yellow Reserve frames.
The abandoned emulator disconnect experiments must not be included.

## Implemented component

`wireless_battle.c` is freestanding ARM946E-S code with no heap, SDK, game,
filesystem, or save dependencies. It provides a host-owned lobby state,
validated six-slot formations, ready revisions, seven host-only music choices,
match start/finish/abort, and per-side DigiXross limits. An accepted DigiXross
can be committed only after round1 and only once for each side. Final damage
is multiplied by0.90 with a minimum of1 for a positive incoming damage value;
zero damage stays zero. The engine adapter must call this only for DigiXross
damage in wireless matches, after the original damage computation.

Changing either team, either formation, or the music clears both ready flags.
Both players must confirm the latest revision before the host can start.
Positions0–2 are the Vanguard and3–5 the Rearguard. Formation values refer to
the six team members, not saved-party addresses or ownership indices.

The packet codec has explicit little-endian fields, a protocol version,
session and peer checks, exact lengths and CRC32. It does not implement radio
discovery, transfer retries, duplicate suppression, team serialization,
command legality, RNG synchronization, or battle-state checksums. A successful
decode alone must never authorize an engine action. The transport adapter must
bind the real peer to its role and validate each message type and phase.

An opaque team transfer buffer reassembles768 bytes in twelve64-byte chunks.
It accepts chunks out of order, accepts identical duplicates, rejects
conflicting duplicates and stale transfer IDs, and exposes a digest only after
all chunks arrive. The experimental session controller adds stop-and-wait
acknowledgements and retries above the SDK adapter. It also caches accepted
formation and music updates so a retransmission after a lost acknowledgement
does not apply a lobby revision twice. It still does not validate a Digimon
record or make received bytes safe to copy into a saved-party array.

`xwb_apply_saved_record_fields` now overlays only fields checked against six
live actors in the Blue battle fixture: species, name, current/max HP and MP,
five trained stats, two opaque four-halfword ranges, and a repeated halfword.
It rejects empty species/maximum HP/MP and current HP/MP above their maxima
before writing anything. The opaque ranges are copied without guessing whether
the game uses them for moves, equipment, or another purpose. The game must
first initialize an actor for that Digimon; this helper does not create actors
or populate engine-owned model/status pointers, and no current game hook calls
it for received teams.

## Music choices

1. Xros Wars normal battle
2. Xros Wars boss battle
3. Dawn/Dusk boss battle
4. Dawn/Dusk multiplayer battle
5. World DS normal battle
6. World DS boss battle
7. World DS multiplayer battle

These are choice IDs, **not verified SDAT sequence IDs**. Numbered source songs
must be identified before binding them to those labels. Native sequences and
their banks/waves have been staged separately with `stage_wireless_music.py`.
No original song indices or data are replaced in that staged archive.

## Build and execution checks

Run `tools/test_wireless_coordinator_arm.py` with `.tools/python` available.
It also exercises the saved-field adapter, including malformed-record
rejection, field-range isolation, and source-record immutability.
Run `tools/test_wireless_session_loopback_arm.py` for two independent ARM946
session controllers connected through a test-only in-memory packet queue. It
covers a lost lobby ACK/retry, concurrent formation edits, simultaneous host
music/guest formation, ready/start, action/result/RNG exchange, round advance
and DigiXross limits.
This verifies protocol logic, not the DS radio or game battle engine.
It invokes Zig0.14.1 from `.tools/ziglang/ziglang/zig.exe`, compiles for
`arm-freestanding-eabi / arm946e_s`, and executes the resulting instructions in
Unicorn. Results are in `build/experimental/wireless_battle_native/`.

`wireless_battle.ld` uses an address **only for the isolated CPU test**. That
address is not reserved in either game and must not be copied over retail RAM.
The separate game bridge instead reserves memory after the retail overlay2
code/BSS by advancing the original ARM9 main arena low literal. Its constructor
runs during fresh startup. All original wireless globals keep their addresses.

## Experimental game integration

`tools/build_native_integration_probe.py --extended-order --transport-adapter`
builds both editions under `build/experimental/wireless_extended_order_transport_batch125/`.
Adding `--session-controller` builds a separate
`wireless_extended_order_session_transport_batch125/` TEST variant containing the
experimental `wireless_session.c` handshake and opaque party-record transfer
controller, lobby synchronization, and action/checksum protocol. It patches the
Link Box root update to pump an already-started session. The session's canonical
phase is copied into the engine-facing match state after each pump. A disconnect
closes the wireless command/turn-order gates, and an ended session restores the
retail nine-actor limit. `--linkbox-battle-entry` adds the fifth action, native
connection prompt routing, and an experimental lobby for formation swaps, host
music, readiness, and protocol START. START does not launch combat. The lobby
has not been verified in the retail UI, and no command-engine call site is
connected; these TEST ROMs are not playable battles.
These are TEST ROMs, not a wireless battle release. The builder accounts for
every cartridge edit and verifies all named game assets remain unchanged.

- The native module loads in reserved memory without using save-party storage.
- All419 directly referenced actor pointer literals are redirected to a
  twelve-record allocation. Ordinary battles retain nine active slots.
- Four retail turn-order functions are relocated with their original software
  floating-point computation. A private context holds thirteen entries,
  including the end sentinel. Only the wireless battle phase enables twelve
  actors in this subsystem. Battle initialization now clears all twelve records
  in the reserved allocation; normal turn ordering still uses nine. A guarded
  setup hook copies validated remote records into slots6-11 before per-actor
  finalization. Six-opponent rendering and target selection remain unverified;
  commands still need integration.
- The command-ring hooks block tactics and consumable-item selections during
  the wireless battle phase. The All Tactics input is also blocked. Ordinary
  battles retain the original input path. Complete wireless UI still needs work.
- The Link Box session controller and battle-engine hooks previously kept
  separate match phases. `xwb_session_frame_tick` now copies the session's
  canonical match after the radio pump; failed sessions mark the engine state
  aborted, and idle sessions restore the ordinary phase. The lobby START packet
  can activate this phase, but no retail battle launcher follows it; this does
  not establish a playable match.
- The controller now also calls the session tick from the battle engine's
  All Tactics status check while the synchronized battle phase is active. The
  Link Box parent update remains the lobby pump. Whether the battle check runs
  at a suitable cadence and survives the real menu-to-battle transition still
  needs runtime verification; commands are not yet dispatched through the
  native battle engine.
- `wireless_transport.c` binds the inspected original native receive callback
  and sender, retaining send buffers until the SDK is finished. It is not yet
  verified on a live battle. The experimental Link Box and battle-loop pump
  call sites invoke it only when the battle session is active; it must remain
  inactive during retail trades.

`test_native_turn_order_arm.py` passes160 differential ordinary-order cases and
80 twelve-actor cases, executing the original float/memory helpers on ARM946.
It also executes the session-enabled tactics wrapper with the session tick and
retail predicate intercepted, verifying one tick in wireless phase and none in
ordinary phase. The Link Box pump trampoline is also executed and checked for
register preservation and retail prologue replay. These tests do not measure
hook cadence in a running game. The input-gate tests intercept SDK input calls.
`test_native_transport_arm.py`
checks the retail callback/getter/setter ABI with send/busy operations intercepted;
neither test proves radio communication.

`check_native_actor_runtime.py --variant extended_order_transport` fresh-boots
an isolated Blue save copy, verifies six saved/live records, and exercises an
ordinary battle to results. Its DeSmuME core has Wi-Fi disabled. User saves and
the original batch124 checkpoints are preserved. Twelve-actor display, battle
construction, synchronized commands, menu integration and full PvP are unfinished.

## Required game integration

- Preserve the four original Link Box actions and add a real battle handler.
- Reuse the existing WH/WM discovery/connection functions with verified packet
  buffers, callbacks and lifetime ownership; do not substitute emulator APIs.
- Copy and validate six Digimon per side, including trained stats, moves and
  equipment, without pointing received data at saved records.
- Resolve the original nine-actor engine's capacity, target masks, turn-order
  storage and UI for both six-member teams.
- Verify the new pre-battle formation and host music controls in the retail UI;
  synchronize revisions and wait for both ready confirmations in a live session.
- Connect the action protocol to the real command engine, enforce move/target
  legality and the actual RNG state, and stop cleanly on a digest mismatch.
- Disable consumable items, saved-party writeback and battle rewards. Finish
  or disconnect through the original local wireless lifecycle.
- Verify complete matches and rematches in two instances, then real hardware.
