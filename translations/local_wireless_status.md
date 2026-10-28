# Local DS wireless battle — implementation status

## Current status (2026-10-27)

The latest experimental pair is built from the batch125 UI checkpoint under
`build/experimental/wireless_linkbox_battle_entry_batch125_lobby_ui5_20261027/`.
The Link Box fifth action enters the retail Wait/Find connection prompt. Once
both six-record transfers complete, it opens a new lobby with all 15 pairwise
formation swaps, the seven planned music choices, per-player readiness status, Start Battle, and Leave.
Formation edits and host music/ready/start actions use the native session
protocol. The parent hook refreshes the lobby only while its `0x7D0` child is
active, and drops its borrowed row pointer outside that state.

`python tools/test_wireless_linkbox_row_arm.py` passes the renderer trampoline,
five-row selection, lobby opening, formation swaps, music, readiness, START,
leave, and the retail connection prompt route under ARM946 emulation.
`python tools/test_wireless_session_loopback_arm.py` passes the in-memory
two-controller handshake/transfer/lobby/action/result/DigiXross checks.
`python tools/test_wireless_actor_scene_hook_arm.py` confirms the remote team
preparation hook runs before actor finalization and only enables twelve actors
after successful preparation. `python tools/test_native_turn_order_arm.py`
passes 160 ordinary differential cases and 80 twelve-actor ordering cases.
These tests run isolated code or mocked queues and do not prove that the lobby
renders in the retail overlay or that DS radio messages exchange in a match.

Blue SHA-256 is
`97d64a001bf130e90796b354a86ec2ad7654b134fa14df9fbe5c4ac787992430`; Red is
`df7d2830a45d0c989d0f6db6c275163f0e2bac69929279f002966385fac2cb9e`.
The build preserves the reviewed batch125 inputs and labels the pair
experimental. The user-tested retail connection flow worked on real 3DS; that
does not test the custom protocol or the new lobby. A fresh melonDS capture
failed twice (`FrameArrived timed out` / `window capture timed out`), so the
provided emulator was not operated this turn.

The mode is still **not playable as a battle**. Start sends the protocol START
and arms the native phase, but it does not launch the retail battle engine.
Command selection/validation/execution, turn ownership, mirrored result and
RNG checks, six-opponent rendering/target UI, music playback, battle-end/save
policy, and a live two-system match remain unimplemented or unverified. Do not
describe these ROMs as ready to play.

## Batch125 roll-forward (2026-10-27)

The integration builder now defaults to batch125 and accepts an explicit
`--baseline batch124|batch125` selector. A fresh Blue/Red test pair is in
`build/experimental/wireless_extended_order_session_transport_batch125/`;
neither ROM was made by patching the stable release in place. This carries
Red's reviewed yellow Reserve palette forward directly from its checkpoint.
The previous batch124-based experiments remain intact.

The fresh batch125-based Blue TEST ROM passed the existing ordinary-battle
runtime regression through results under the headless DeSmuME core. Its
screenshots and report are under
`build/qa/native_extended_order_session_transport_batch125/`. This confirms
the ordinary Blue battle path still works on the rolled-forward build; it does
not test wireless battle or Red's gameplay.

### Link Box menu trace

The batch125 ARM9 disassembly identifies two cooperating Link Box menu
constructors. `0x020D03FC` allocates the outer four-row object (`0x190` bytes),
draws/releases its rows, and owns the user-name/play-time panel. The child
constructor `0x020D41EC` allocates four `0x50`-byte rows (`0x140` bytes), then
builds the four labels with direct message IDs10-13 at `0x020D4340`,
`0x020D437C`, `0x020D43B0`, and `0x020D43E4`. Its selection handler is
`0x020D44D8` and dispatches only indices0-3. The outer touch mapper at
`0x020D0EDC` accepts vertical grid coordinates9-16, mapping them to indices
0-3. The help-text ID table at `0x0210C1D8` contains14-17. The appending
message-table helper now allows the new label and help text to use IDs106 and
107 without moving existing messages.

The Wait/Find connection-method modal is constructed separately at
`0x020D2190`; its parent state machine calls it from `0x020D4E3C`. The child
constructor's row loop also controls the five visible y positions (start 5,
step 4), while its destructor independently frees four rows. The outer touch
mapper's inclusive y-grid range is 9-16, and the child's selection loop uses
four rows. These are separate patch sites; increasing only a message count or
one allocation would leave the menu inconsistent.

The child selection handler at `0x020D44D8` has four-entry selection geometry
and explicit action cases for indices0-3. The confirm path at `0x020D4800`
routes actions0 and1 through different availability checks, while actions2 and
3 set separate retail states. It does not expose an existing battle action.
The `0x020D4E3C` Wait/Find call is reached by the larger Link Box state
machine; its required parent/context fields must be identified before a fifth
action can safely invoke it. A first isolated fifth-row render patch is now in
the batch125 TEST pair; it does not yet add touch bounds, button navigation,
help-table lookup, or a fifth-action state transition. Runtime proof that the
retail Link Box constructor reaches the hook is still pending.

The session-controller module contains `xwb_linkbox_draw_battle_row` and the
naked constructor trampoline in `native/wireless_linkbox.c`. The ARM946 test
checks the retail text builder call (entry21, message106), fifth row address
(base+0x140), draw/finalize calls, caller-register preservation, replay of the
four displaced setup instructions, and resume at `0x020D4420`. The renderer
hook is at `0x0222481C` in the experimental module. Batch125 Blue and Red TEST
ROMs are built under
`build/experimental/wireless_linkbox_battle_entry_batch125/`; each appends
message106 `Wireless Battle` and107 `Battle nearby over DS Wireless.`. The ARM9
patch expands/clears the child row buffer to `0x190`, initializes/destroys five
rows, shifts the first row up four grid units so the fifth fits at the former
fourth-row position, and branches to the tested renderer trampoline. Existing
Link Box actions remain on their original paths.

`python tools/test_wireless_linkbox_row_arm.py` passes. The full 26-test
pipeline suite passed before this menu patch. DeSmuME loaded the patched Blue
TEST ROM from a saved Gatomon-PC state and advanced dialogue without crashing,
but that state never entered the Link Box menu, so it is not proof that the new
constructor hook rendered in-game. The row is currently not selectable: the
touch bound, four-row navigation arithmetic, selection dispatch, and help
table remain unchanged. It does not start the wireless session. Both ROMs are
still explicitly experimental and not playable PvP builds.

## Latest implementation work: batch124 baseline and native component

### Native integration update

Separate TEST ROMs now install the coordinator, original SDK transport adapter,
relocated actor storage, and turn-order hooks. Stable batch124/batch125 ROMs and
their backups remain unchanged. **Local wireless battle is still not playable.**

The Red Reserve yellow palette from the already-reviewed batch125 release has
been carried into the current Red wireless TEST ROM variants. The ROMs
before this update are backed up under
`build/backups/red_reserve_yellow_wireless_test_rollforward_20261027/`. Only
`BG_NCLR.PAK` changed in each test ROM. Batch124 itself is preserved.

### Saved-record field adapter continuation

The native component now includes `xwb_apply_saved_record_fields`, a guarded
helper that overlays fields verified against live actors: species, name, HP/MP,
five trained stats, two opaque four-halfword ranges, and one repeated halfword.
The six-member Blue fixture checks both opaque ranges against every corresponding
live actor in `build/qa/wireless_battle_engine/party_layout_verified.json`.
The ARM946 component test checks malformed-record rejection, no writes outside
the verified ranges, and source-record immutability. This helper only updates an
actor already initialized by the game. No Link Box or battle hook calls it, and
the opaque fields' meanings remain unknown.

Both experimental ROMs were rebuilt with this helper. Their previous copies
were preserved by checksum under
`build/backups/party_adapter_prebuild_20261027/`. The Red Reserve-yellow palette
was reapplied from the reviewed batch125 UI build.

### Session handshake and party transfer controller

`native/wireless_session.c/.h` now add an experimental controller above the
native transport: host HELLO with protocol/party-format checks, guest session
adoption, stop-and-wait acknowledgements and retries, duplicate chunk checks,
and bidirectional transfer of six opaque 0x80-byte records (768 bytes per
party). Once both records are complete, both sides build the same lobby team
digests and identity formations. The controller now also carries formation,
host music selection, ready/start, and round updates. Its sequential action
messages include actor/target/move fields plus the post-action state digest and
RNG state; the peer must apply the action and confirm both values before play
can advance. No save data is written. The copied records still require a
game-specific decoder and actor initialization before received records can be
used in battle. The field-copy helper described above is not yet called by the
game.

The lobby receiver now remembers its last accepted formation and music update.
If a lost acknowledgement causes the peer to retransmit one of those updates,
the receiver acknowledges the same packet without applying the revision a
second time. A changed payload with the same cached sequence is rejected. The
session-controller TEST ROMs were rebuilt after this change; this was a build
and structural check only, not a two-console radio test.

The latest two-controller loopback also drops a formation ACK on purpose,
verifies the sender retries, and verifies that the duplicate is acknowledged
without advancing the lobby revision twice. This adds a duplicate/loss recovery
check to the protocol simulation; it does not exercise the retail radio.

`tools/test_wireless_session_loopback_arm.py` now runs two independent session
controllers under ARM946 emulation and passes their packets through a test-only
in-memory queue. It covers six-record exchange, simultaneous formation edits,
an overlapping host music/guest formation update, both ready/start, commands
from both sides with result/RNG confirmation, round advance, once-per-side
DigiXross after round1, duplicate rejection, and cleanup. The simultaneous-edit
case exposed a revision race; the controller now merges disjoint same-revision
formation/music changes and invalidates readiness. This remains a protocol
simulation with no battle-engine call or real radio.

The controller is included in a new isolated TEST build:
`build/experimental/wireless_extended_order_session_transport/`. The new Red
TEST ROM has the yellow Reserve palette and a preserved pre-palette copy under
`build/backups/red_reserve_yellow_wireless_test_rollforward_20261027/`. This
build has a Link Box root update hook that pumps the controller when a session
has been started. There is still no visible Battle choice or code path that
starts a session, no formation editor or actor-construction hook, and no
command-to-engine adapter. It is not ready to play, and no live-radio test was
run.

### Readiness estimate

Roughly **one third of the engineering work to a playable release** is complete.
This is an estimate, not a schedule: transport, lobby/action protocol, reserved
actor storage, partial turn-order capacity, and ordinary-battle compatibility
checks exist. Most of the work remains in the Link Box flow, constructing and
presenting both six-Digimon teams, expanding the remaining nine-actor engine
paths, connecting commands to the battle engine, music mapping, and complete
two-system testing.

- Loader: original ARM9 arena low is advanced beyond the native module. Original
  wireless code/globals retain their addresses. The constructor runs at fresh
  startup; seeing its marker is not evidence of entering Link Box.
- Actor storage: 419 verified literal references now use a twelve-record reserved
  allocation. Battle initialization clears the full twelve-record allocation;
  the normal turn order remains capped at nine. Six trained-stat/name records
  plus two opaque four-halfword ranges and one repeated field match their saved
  sources in the Blue fixture. The new copy helper is ARM-tested but has no game
  call site. The extra three actors are still not populated, and other engine
  subsystems still assume nine.
- Turn order: four original routines use a private thirteen-entry array and
  sentinel.160 original-versus-relocated cases and80 twelve-actor cases pass
  ARM946 execution using retail software float/memcpy helpers. This supports
  twelve actors in turn ordering only, not the entire engine.
- Tactics/items: native command-ring masks and selection gates now restrict
  tactics and consumables when the coordinator is in the wireless battle phase.
  The All Tactics input is separately gated. Normal battles retain their inputs.
  `check_wireless_input_gates.py` forces that phase only in isolated QA RAM:
  All Tactics stays closed, restricted ring icons are removed, and confirming
  after navigation does not enter tactics or consumable screens. This is input
  integration evidence, not a connected match. Report and screenshot are under
  `build/qa/native_extended_order_transport/`.
- SDK adapter: original send and receive callback conventions are implemented,
  with persistent outgoing buffers and validated incoming packet queues.
  The35-call ABI test intercepts send/busy; no radio transmission is established.
- The latest combined Blue TEST ROM SHA256 is
  `09dffb5fbd060e2b20c6604945e28f6bd4bf88e1f0a6425b655da1d62f8b17cf`;
  Red, with its Reserve-yellow palette reapplied, is
  `3a447ec73031ef6fa22beed5fd3b7186138a1ba9e2d9a88ef6f29a00d5202506`.
  Both prior test ROMs are backed up by checksum. A fresh-boot ordinary Blue
  battle on the latest build reached results; all three enemies reached zero
  HP and the twelve-entry private turn-order array populated. The test used a
  QA save and Wi-Fi-disabled DeSmuME, so it verifies ordinary-battle
  compatibility only. No user save was modified. Batch124 checksums still
  match their backups.

Current build command: `tools/build_native_integration_probe.py --extended-order --transport-adapter --session-controller --baseline batch125`.
Output: `build/experimental/wireless_extended_order_session_transport_batch125/`.
Earlier native component checks are documented below; they do not verify the
new Link Box hook, session protocol over radio, or a two-player match.

Still required: fifth Link Box action and connection/session start flow, decode and
validate party records (including equipment and trained stats), opponent rear
positions/target masks/display, formation/ready/music UI, command legality and
battle-engine application, multiplayer-only rewards/save suppression, actual
theme mapping, complete two-system matches and rematches.

### Earlier component work

- User clarified that the real3DS test used batch124. Both batch124 ROMs are
  copied and checksummed under
  `build/backups/ui_checkpoint_batch124_user_hardware_verified/`. This is the
  gameplay baseline. Existing ROMs, original ROMs, saves and other checkpoints
  were not overwritten.
- New pre-battle requirement: both players can arrange their six-member team
  and confirm before battle. The host can choose among seven themes: Xros Wars
  normal/boss; Dawn/Dusk boss/multiplayer; World DS normal/boss/multiplayer.
  Any formation/team/music change must invalidate both ready confirmations.
- `native/wireless_battle.c` and `.h` implement a freestanding ARM9 lobby/rule
  component and wire codec. Stable releases do not contain these changes. There is
  no live Link Box battle option, actual formation screen or playable match.
- The component validates six-slot permutations, host-only music/start/round
  progression, revision-bound confirmations, one DigiXross per side after
  round1, and0.90 final DigiXross damage. Zero damage remains zero; positive
  damage has a minimum of1. The engine adapter must restrict that multiplier
  to wireless DigiXross damage after the native computation.
- The packet codec validates protocol/session/peer/length/CRC. The team buffer
  reassembles twelve64-byte chunks out of order, accepts identical duplicates,
  rejects conflicting/stale fragments, and exposes its CRC only when complete.
  Its opaque768 bytes are not engine-validated Digimon data and must not be
  copied into saved-party memory. The controller retries protocol packets, but
  no live game call site or radio-session test is present.
- `test_wireless_coordinator_arm.py` builds with Zig0.14.1 for ARM946E-S and
  executes on Unicorn's ARM946 CPU model. The latest report passes2338 native
  function calls, including all720 formation permutations, all seven music
  choices, malformed packets, source buffers, and DigiXross limit/damage cases.
  This is component evidence only, not a multiplayer or hardware test.
- Dusk and World DS ROMs were inspected read-only. Their native SDAT sequences
  have numbered names. `stage_wireless_music.py` stages all81 candidate BGM
  sequences with79 banks and79 wave archives, preserving all original Xros
  entries and checking imported content after serialization. The resulting
  SDAT is under `build/experimental/wireless_music/`, not installed in a ROM.
  Exact battle-theme identities, pruning and playback/memory use are unverified.
  Blue and Red batch124 SDATs are byte-identical.
- `read_reference_wireless.py` records partial Latin text from the supplied
  originals with source hashes. The decoded Dusk help describes its own battle
  restrictions. These references do not authorize copying Dusk's battle rules
  over the requested Xros Wars mechanics.
- The ARM9 literal at0x02005E70 supplies the original main arena low value
  0x022234A0, equal to overlay2's code+BSS end. This is a candidate reservation
  point used by the experimental native loader described above.
  The isolated test ELF's0x02040000 address is not usable retail RAM space.

## Current direction, 2026-10-27

The user tested the existing exchange connection on a real3DS and reports that
it works correctly. At the user's explicit request, abandon the emulator
"Please wait" investigation. Neither experimental disconnect patch is approved
for inclusion in the normal game builds. Keep the original native wireless
shutdown behavior for the battle implementation. The experimental files remain
labelled diagnostics; they are not stable releases.

Wireless battle remains **unimplemented and not playable**.

### Earlier battle-engine inspection (superseded by native integration update above)

- A separate headless instance loaded the existing Blue battle fixture. Its
  RAM dump and screenshots are in `build/qa/wireless_battle_engine/`. This core
  has Wi-Fi disabled and supplies no multiplayer test evidence.
- Six live actor records match six saved Digimon sources by species, full
  name bytes, HP/MP and trained stats. Saved record stride is0x80; live actor
  stride is0x1A0. In this fixture the actor array starts at0x0221AFD4.
- `tools/check_wireless_battle_layout.py` reproduces the six matches. An isolated
  change to one actor's HP field persists for60 update frames while all six
  source records stay byte-identical. This proves separate storage for this
  fixture only, not save protection after battle completion. HUD text remains
  cached at this planning screen; no visual current-HP update is established.
- Native initialization at0x021F7B44 clears0xEA0 bytes: nine actors. Turn-order
  construction at0x021F3D60 iterates nine actors. Existing battles therefore
  provide six player actors plus three enemy actors, not a ready twelve-actor
  PvP engine. Expanding opponent capacity needs allocation, all indexing and
  masks, targeting, turn order, rear positions, and display changes together.
- Assembly excerpts identify the turn-order builder0x021F3D60, next-actor
  selection0x021F3F38, battle context accessor0x021F7B30, and battle initializer
  0x021F7B44. Names are inferred; they are not exported source symbols.
- Next required implementation step: resolve battle construction and command
  submission, then provide storage and behavior for both six-member teams.
  No new Link Box option or executable battle patch has been installed.

## Status at batch124

**Not implemented and not playable.** The Link Box still has its original four
working actions. No battle menu item or network battle handler has been installed.
Online connectivity is outside the requested scope.

## Confirmed in this inspection

- Original Blue and Red ROMs have six ARM9 overlays.
- Overlay0 contains the battle engine and the live UI palette table at
  decompressed offset `0x26758`. Batch124 changes only the 168-byte palette
  region; all executable instructions and pointers in that overlay are checked
  unchanged after decompression.
- Overlay2 loads at `0x0221BF80`, with 19,456 bytes of decompressed data and
  10,528 bytes of BSS. Its embedded diagnostics identify Nintendo's WH/WM local
  wireless parent/child discovery, connection, MP send/receive, and data sharing.
  Blue and Red's decompressed overlay2 hashes match.
- String references identify candidate SDK wrapper functions:
  `0x0221C8AC` (scan callback diagnostics), `0x0221CF94` (child data-sharing
  diagnostics), `0x0221D2F8` (MP send callback diagnostics), and `0x0221DBBC`
  (initialization diagnostics). These names are inferred from diagnostic strings;
  complete signatures and ownership are not yet verified.
- The read-only audit records literal references and direct branch candidates
  in `build/qa/batch124/local_wireless_audit.json`. Overlays3/4/5 reuse overlay2's
  RAM address, so a branch into that range alone does not identify a wireless
  call. The `0x020562CC` region, for example, explicitly loads overlay4.
- The supplied Dusk backup was read without modification. It carries WH state
  strings in ARM9 and overlay3, rather than Super Xros Wars' overlay2 layout.
  Its networking/battle code has not been transplanted.
- Link Box labels are `MSG/MESPAK01.PAK`, entry21, indices10–13. This identifies
  the text, not the menu dispatcher or its available action count.
- The headless DeSmuME core used for visual QA reports **WIFI emulation OFF**.
  These visual checks establish no two-console communication.

## Remaining executable work

1. Add and verify the fifth Link Box Battle row: expand the menu allocation and
   layout, update keyboard and touch navigation, provide its label/help text,
   and route selection into a real wireless session start. Preserve all four
   existing operations and the Back control.
2. Establish verified party/move/equipment data layouts and a temporary battle
   copy. Find the battle setup and command submission interfaces; do not point
   the battle engine at unvalidated received data or write results to the save.
3. Reuse the game's local wireless transport with an explicit protocol version,
   peer/edition validation, validated six-Digimon team exchange, acknowledgments,
   timeout/disconnect recovery, and agreed random state.
4. Synchronize both players' legal commands and turn resolution; compare state
   checksums so a mismatch aborts the match cleanly.
5. Add host/join/ready/cancel/results UI and test complete matches using two
   local-wireless-capable emulator instances. DS/3DS hardware compatibility
   remains unverified until a real two-system test.

## Accepted rules to carry into implementation

- Six Digimon: three Vanguard and three Rearguard; normal formation mechanics.
- Retain trained stats and equipped items.
- One DigiXross per side per match, prohibited during the first complete round.
- Provisional **0.90× final damage** for DigiXross in wireless battles only.
  This is a proposed balance value, not an implemented or tested balance result.
- No consumable items. No saved-party losses, consumption, or persistence of
  temporary battle changes. A disconnect must release the local link and return
  safely to the Link Box.

## Batch125 continuation

- The supplied Red save was successfully loaded from a QA copy. Both supplied
  512-KiB saves contain 64 KiB of save data followed only by `0xFF` padding;
  only the copies used with DeSmuME were trimmed. Source saves are unchanged.
- UI-only Blue/Red batch125 ROMs are backed up with SHA-256 checksums under
  `build/backups/ui_checkpoint_batch125_before_local_wireless/`.
- The Link Box root menu handler is identified at ARM9 `0x020D44D8` in the
  inspected Blue source. The menu state is read from context+`0x1C`, its widget
  from context+`0x28`, and its cursor from context+`0x34`.
- Its constructor at `0x020D03FC` allocates `0x190` bytes of `0x50`-byte
  widgets, builds four action rows, then builds Back as a separate fifth
  widget. Five actions plus Back need six widgets (`0x1E0`) and an additional
  row-layout iteration; the existing objects cannot simply be relabeled.
- Its keyboard cursor logic at `0x020D4730` and `0x020D4778` implements modulo4
  using shifts/rotations. Touch code treats item4 as Cancel. Expanding to five
  items therefore requires both navigation paths, layout and hitboxes to change.
- The root help lookup copies four halfword IDs (14–17) from `0x0210C1D8` to its
  stack frame. A fifth action also needs a fifth help ID and a valid stack slot;
  this and the selection dispatcher are not yet patched.
- Selection dispatch appears at `0x020D4800`–`0x020D4868`; its existing actions
  check Melody/DigiScore availability before progressing. Help-text lookups at
  `0x020D4614` and `0x020D48BC` use message entry21.
- The accessor `0x020CF0CC` sets entry21 and jumps to the general message
  accessor `0x0203BE64`. The two-choice connection-method menu is in the
  `0x020CFA94` region; it is distinct from the four-action root menu.
- Overlay2 wrappers `0x0221DFCC`, `0x0221E058`, `0x0221E0D0`, and
  `0x0221E190` dispatch through callback-table slots `+0x0C`, `+0x14`, `+0x1C`,
  and `+0x24`; `0x0221E00C` reads session state at context+`0x20`.
  These are disassembly observations, not verified battle interfaces.
- The supplied melonDS1.1 executable is present. The computer-use runtime
  failed to initialize after its prescribed retry/reset recovery:
  `failed to write kernel assets ... path not found (os error3)`.
  No two-instance melonDS test has been performed. The user was asked to
  restart Codex to restore app control; this does not resolve the remaining
  battle-engine/network implementation work by itself.
- Disassembly excerpts are in `build/qa/batch125/`. No wireless executable
  patch or nonfunctional Battle menu item has been installed.

## Technical references

## Disconnect investigation, 2026-10-27

- App control now reads melonDS accessibility and sends keyboard input. Native
  screenshots still time out; coordinate input geometry is unavailable.
- User supplied both instance key mappings. Blue's physical semicolon key
  advanced the game far enough to load the wireless overlay, verified in a
  melonDS slot3 snapshot. This does not establish a successful link.
- `tools/inspect_wireless_state.py` validates melonDS v13.0 section boundaries
  and the actual WH getter signature before interpreting shared overlay RAM.
  Snapshot results are in `build/qa/local_wireless_session/runtime_samples.json`.
  The latest sample has session state0/error0, WH state0 and no callback table;
  it is not a reproduction of the reported disconnect loop.
- Native transport errors overwrite states12/13 (closing) with state14. An
  experimental guard preserves asynchronous shutdown state13 in that case.
  `tools/test_disconnect_guard_arm.py` passed150 ARM execution cases across
  both editions. The reset API was intercepted; this is not a radio test.
- Separate experimental ROMs and copied saves are under
  `build/experimental/local_wireless_disconnect/`, with `manifest.json`.
  Stable batch125 and its checkpoints are unchanged. Do not promote the guard
  until an actual two-instance exit/disconnect test confirms the behavior.
- Wireless battle remains unimplemented: no fifth menu item, party exchange,
  command synchronization, or verified multiplayer battle engine integration.

### Captured Red shutdown stall and revised recovery candidate

- User captured Red in slot2 after Blue returned to Link Box. Inspection of
  that actual state finds session13, error0, WH_BUSY3. SDK status is child8,
  MP flag0; the disconnect callback is registered. This does not match the
  earlier error-routing hypothesis. Do not describe that earlier guard as a
  fix for this captured stall.
- `local_wireless_busy_recovery.py` replaces only the 192-byte diagnostic print
  block. After300 consecutive update calls in session13/WH_BUSY, it requests
  the original WH_Reset once. The SDK reset callback and original shutdown
  dispatcher retain ownership of completion and freeing memory. No forced
  unload or fabricated callback occurs. A reset that never completes still
  waits; this is an explicit limitation.
- `test_busy_recovery_arm.py` passes330 state combinations and900-update
  sequences per edition, checking a single reset and counter clearing after
  simulated IDLE. Reset is intercepted; no real wireless behavior is proven.
- Separate ROMs are under `build/experimental/local_wireless_busy_recovery/`.
  A copy of the user's stuck Red snapshot has only that validated RAM code
  region replaced in `build/qa/local_wireless_session/Red_busy_recovery_runtime.mln`.
  Its source slot2 is unchanged. This copied snapshot is for a recovery test,
  not evidence of successful fresh link setup or real hardware compatibility.
- Both checkpoint wireless overlays and ARM7 binaries match their original
  ROMs exactly (`original_wireless_comparison.json`). This does not rule out
  timing effects or establish that hardware would or would not show the stall.
- Red's Load state dialog was opened through F9. The app-control runtime can
  inspect that dialog but cannot edit its field or activate it reliably. User
  was asked to select the copied runtime state and report recovery after10s.

- [melonDS local multiplayer documentation](https://melonds.kuribo64.net/faq.php)
- [DSWifi local multiplayer architecture and APIs](https://blocksds.skylyrac.net/dswifi/index.html)

DSWifi is an architecture reference, not a drop-in replacement for the retail
game's already-linked Nintendo wireless SDK. The existing WH/WM implementation
must be understood before any runtime integration is considered working.


## Opponent actor adapter checkpoint (2026-10-27)

The isolated batch125 pair now includes an ARM946 adapter that validates the
received six 0x80-byte saved-party records, maps them through the remote
formation permutation, and copies species, names, current/max HP and MP, trained
stats, and opaque move/equipment fields into opponent actor records 6-11. Slots
9-11 inherit initialized opponent templates from slots 6-8. Invalid records or
formations fail before writes. The actor-loop hook invokes this once at index6
only when the synchronized session is in battle; a stale ready flag cannot leave
twelve actors enabled in ordinary battles.

`python tools/test_wireless_actor_adapter_arm.py` passes record preservation,
formation mapping, and invalid-input checks. `python tools/test_native_turn_order_arm.py`
passes 160 normal-order cases, 80 twelve-actor ordering cases, hook-phase checks,
and the existing tactics/session trampoline checks. The session protocol loopback,
Link Box row, and native transport tests also pass; protocol actions remain
digest-synchronized data and are not dispatched into the game combat functions.

The fresh Blue TEST ROM at
`build/experimental/wireless_linkbox_battle_entry_batch125_actor_slots_20261027/`
booted from a copied QA save, completed an ordinary encounter, and reached
results with all three enemies defeated. This verifies ordinary-battle behavior
for Blue only. It does not exercise the remote actor adapter in-game. Blue
SHA-256: `bff9c04ce8cb811c8ccd4e4fe24a89b5642e44f32c71a017fbc682448964f7b1`;
Red SHA-256: `a04361ae12b3d049b968d3ce31b4b8b17fff1d0d42a16bb2a8763bd09f65fb1b`.
The QA report and screenshots are under
`build/qa/native_linkbox_battle_entry_batch125_actor_slots_20261027/`.

Still missing for a playable mode: lobby formation/music controls, reliable
transition into the battle overlay on both consoles, engine-owned display and
target objects for six opponents, mapping retail player inputs to synchronized
actions and executing them through combat routines on both systems, result and
reward handling, wireless teardown/reconnect behavior, and a live two-system
match. The current TEST pair remains experimental and is not playable PvP.


The current-session Computer Use retry found the running melonDS window but
could not capture it (`FrameArrived timed out: timed out waiting on channel`;
refresh retry: `window capture timed out`). No game inputs were sent. A live
two-instance match remains unverified.


## Actor finalization hook checkpoint (2026-10-27)

The Link Box battle TEST build now patches the retail battle setup before its
per-actor finalization loop. It calls `xwb_prepare_remote_actors` before the
engine finalizes the active actor records, replays the relocated actor-base
load, and changes the loop limit from9 to12 only when the match phase is battle and the
remote actor adapter reports success. The turn-order hook remains a guarded
fallback at actor6. The original actor array and native save records remain
separate; only experimental TEST ROMs are patched.

`python tools/test_wireless_actor_scene_hook_arm.py` checks the scene trampoline,
replayed actor-base address, wireless 12-object condition, and ordinary 9-object
condition. `python tools/test_native_turn_order_arm.py` still passes the 160
ordinary differential cases, 80 twelve-actor order cases, and session hooks.
Blue then completed a fresh ordinary battle through results on the new build;
its battle/results screenshots match the previous regression hashes. The ROM
manifest verifies patched assets and cartridge mutation ranges. The DeSmuME run
has Wi-Fi disabled and does not call the adapter with a remote roster, so it
does not prove six additional Digimon render, receive target UI, or battle correctly.

The new experimental pair is under
`build/experimental/wireless_linkbox_battle_entry_batch125_scene_actors_20261027/`.
Blue SHA-256: `f398eee71adb22021d7855dc84d22b16d935696791e0145c0e8c3dda920eea22`;
Red SHA-256: `da19de1cff3ab260a6b5c6f89d2bb9fa31d0443245dc15de4a212f468084c4f3`.
The build is not ready for play. The
formation/music lobby, synchronized battle launch, command-to-engine application,
6-opponent target and HUD behavior, multiplayer reward/save policy, and live
two-system verification remain unfinished.
