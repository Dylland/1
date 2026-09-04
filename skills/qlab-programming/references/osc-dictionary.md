# QLab OSC Reference

Source: Figure 53's official OSC dictionaries (`https://qlab.app/docs/v5/scripting/osc-dictionary-v5/`, and the `v4`/`v3` equivalents) plus the "Using OSC" networking page (`https://qlab.app/docs/v5/networking/using-osc/`). Assembled from documentation search snippets and QLab domain knowledge, not a firsthand full-page fetch — **spot-check exact address spellings against the live docs before shipping anything that matters**, especially if the user is on QLab 3 or 4 where some addresses differ from v5.

## Transport and ports

- QLab listens for OSC on **UDP and TCP port 53000** by default (configurable in QLab's network settings).
- QLab also listens for **plain text on UDP port 53535** and interprets it as an OSC address — e.g. sending the literal ASCII text `/cue/selected/start` to port 53535 does the same thing as sending a real OSC packet with that address to port 53000. Handy for quick tests with `netcat` when you don't want to deal with OSC packet encoding.
- **Prefer TCP for anything that reads data back** (property queries, `/workspace/.../cueLists`, bulk queries) — some reply payloads are larger than a single UDP datagram can reliably carry. UDP is fine for one-way fire-and-forget control (`/go`, `/cue/12/start`).
- OSC replies come back on the same connection (TCP) or to the sender's address (UDP), on an address prefixed with `/reply/`, e.g. a query to `/cue/12/name` gets a reply at `/reply/cue/12/name` whose first argument is a JSON string like `{"status":"ok","address":"/cue/12/name","data":"Opening SFX"}`.

## Addressing a workspace and cues

QLab can have multiple workspaces (show files) open at once, so every cue-scoped OSC address has two forms:

- **Rootless**: `/cue/...` — applies to whichever workspace is currently front-most/active in QLab.
- **Workspace-scoped**: `/workspace/{workspace_id}/cue/...` — targets a specific workspace regardless of which one is frontmost. Use this for anything running unattended or where you can't guarantee window focus.

Within either form, the cue itself can be addressed several ways:

| Selector | Address fragment | Notes |
|---|---|---|
| By cue number | `/cue/{number}/...` | Numbers are human-assigned, don't have to be numeric (can be `"panda"`), and can repeat across different cue lists — least stable if the show gets renumbered |
| By unique ID | `/cue_id/{id}/...` | The ID never changes even if number/name change; best choice for scripts/integrations that need to survive re-numbering |
| By list index | `/cue/{index}/...` (list-relative) or via a cue list's own indexing commands | Position-based, brittle if cues are inserted/removed |
| Currently selected | `/cue/selected/...` | Whatever's selected in the QLab UI — useful for interactive/manual testing, not for unattended automation |
| Active/playing | `/cue/active/...` in some contexts | Targets whatever's currently running |

**Recommendation for integrations that need to be robust**: address by cue number if the operator maintains stable, meaningful numbering (common in theatre — numbers map to the paper cue sheet), or by `cue_id` if the workspace structure is likely to be reshuffled by the programmer after the integration is built.

## Global / transport commands

These aren't scoped to a specific cue:

| Address | Effect |
|---|---|
| `/go` | Same as pressing the GO button — fires the next cue in the active cue list |
| `/stop` | Stop playback (scope depends on target — workspace-wide if sent to `/workspace/{id}/stop`) |
| `/pause` | Pause the active cue(s) |
| `/resume` | Resume paused cue(s) |
| `/load` | Load (arm/cue up) without starting |
| `/reset` | Reset playback position |
| `/panic` | Hard-stop everything immediately (the "oh no" button) — use with caution, this is not a graceful fade-out |
| `/save` | Save the workspace |
| `/undo` / `/redo` | Undo/redo the last edit |

## Per-cue commands

Pattern: `/cue/{selector}/{verb}` (or `/workspace/{id}/cue/{selector}/{verb}`)

Common verbs:
- `start` — start this specific cue (equivalent to selecting it and pressing GO, but only for this cue)
- `stop` — stop this cue if running
- `pause` / `resume`
- `load`
- `hardStop` / `hardPause` — stop/pause without fade-out
- `isRunning` (query, returns bool) — poll this to detect "cue finished" if you're not using status updates
- `isLoaded` (query)
- `duration` (query) — total cue duration in seconds, useful for computing a wait/sleep instead of polling
- Property get/set: most cue properties are readable and (for most types) settable via `/cue/{selector}/{propertyName}`, e.g.:
  - `/cue/12/name` (get) — send with no argument to query, reply comes back on `/reply/...`
  - `/cue/12/name "New Name"` (set) — send with a string argument to set
  - Same get/set pattern applies to `colorName`, `armed`, `flagged`, `notes`, `preWait`, `postWait`, `continueMode`, and most other visible cue properties.

**Verify exact verb names against the live OSC dictionary for the target QLab version** — the property-name casing and a few verb names (e.g. whether it's `hardStop` vs `hardstop`) can differ across QLab 3/4/5 and this list wasn't checked against a live fetch.

## "Waiting for a cue to finish" patterns

Two viable approaches for an external script:

1. **Poll `isRunning`** (or `/cue/{id}/isRunning`) every N milliseconds via TCP until it returns false. Simple, portable, adds slight latency (bounded by your poll interval) and periodic network chatter.
2. **Enable OSC status updates** on the workspace (a setting in QLab's workspace preferences) and listen for the automatic push messages QLab sends as playback state changes, matching on the cue's ID. Lower latency, no polling, but requires the listener to be running and correctly filtering messages before you fire the cue — more moving parts.

For most theatre/corporate-event integration scripts, polling is the easier and more debuggable starting point; reach for status-update listening only if timing precision genuinely matters (e.g. driving a fast lighting/audio handoff).

## Workspace passcodes and TCP connection

If a workspace has a passcode set (Workspace Settings → General → passcode), an OSC client must authenticate before QLab will act on its messages:

- Send `/workspace/{workspace_id}/connect` with the passcode as an argument (some versions accept it without an explicit `connect` call over UDP if the passcode is included per-message — TCP requires an explicit connect handshake).
- Until that handshake succeeds, QLab will reply with an error/reject status rather than executing the command.
- If a client is misbehaving or a script "does nothing" against a passcode-protected workspace, check the connect/auth step before assuming the address syntax is wrong — this is the single most common cause of "OSC used to work and now silently doesn't."

## Minimal examples

**Fire cue 12 (UDP, fire-and-forget) with `python-osc`:**
```python
from pythonosc.udp_client import SimpleUDPClient

client = SimpleUDPClient("127.0.0.1", 53000)  # QLab's IP/hostname, default port
client.send_message("/cue/12/start", [])
```

**Quick test over plain text (no OSC library needed), from a shell:**
```bash
printf '/cue/selected/start' | nc -u -w1 127.0.0.1 53535
```

**Query a cue's name and read the reply (TCP, needed for reliable replies):** see `scripts/qlab_osc_client.py` in this skill for a full client/listener pattern that handles the JSON-wrapped reply payload.
