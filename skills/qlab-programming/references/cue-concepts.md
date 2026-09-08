# QLab Concepts: Workspaces, Cue Lists, Cue Types, Triggers

Background reference for QLab's object model — useful when a script or OSC/AppleScript integration needs to reason about *what* it's addressing, not just the syntax to address it with. Assembled from QLab domain knowledge and documentation search snippets; version-specific feature availability (a cue type or setting introduced in QLab 4 or 5) should be confirmed against the changelog/docs for the user's actual version if it matters.

## Workspace

A **workspace** is one open show file (`.qlab` document). QLab can have multiple workspaces open simultaneously, each with its own cue lists, cue carts, network patches, and settings (including its own OSC passcode). Every OSC address and most AppleScript targeting decisions ultimately resolve to "which workspace" — see the addressing sections in `osc-dictionary.md` and `applescript-dictionary.md`.

## Cue lists vs. cue carts

- **Cue list** — the traditional sequential list, driven by the GO button. Has a "playhead" pointing at the next cue to fire. A workspace can have multiple cue lists (tabs).
- **Cue cart** — a grid of cues fired independently/out-of-order (like a soundboard), not by sequential GO. Common for corporate/AV work needing ad-hoc triggering rather than a scripted sequence.
- A **Group cue** can itself behave like a mini list, cart, or **timeline** (parallel, time-based playback of its children) depending on its Group Mode — relevant when addressing "child of group X" via OSC/AppleScript.

## Cue types (non-exhaustive, current as of QLab 5)

| Type | Purpose |
|---|---|
| Audio | Play an audio file/device output |
| Video | Play video, with output patch to a screen/projector |
| Camera | Live camera input passthrough |
| Text | Render text (e.g. supertitles) to a video output |
| Light | Send lighting control (via a Light Patch, often DMX/Art-Net/sACN or OSC/MIDI to a console) |
| Fade | Fade properties (e.g. audio level) of another cue over time |
| Network | Send OSC or other network messages out to a third-party device (this is QLab acting as the *client*, distinct from receiving OSC control) |
| MIDI / MSC / MTC | Send MIDI messages, MIDI Show Control, or MIDI Timecode |
| Timecode | Chase/generate timecode to drive the cue list |
| Script | Run AppleScript or shell script when the cue fires (see `applescript-dictionary.md`) |
| Group | Container for child cues (List / Cart / Timeline mode) |
| Start / Stop / Load / Pause / Goto / Target / Devamp | Control cues that act on *other* cues — e.g. a Goto cue that jumps the playhead, a Stop cue that stops a target |
| Notes | Non-executing annotation cue for documentation within the list |
| Memo | Similar — a non-firing note cue |

For an integration, the two most relevant for "make an external event happen" are **Network** (QLab pushes OSC/MIDI out to something else when this cue plays — no external script needed) and **Script** (QLab runs your AppleScript/shell when this cue plays). If the ask is "make QLab talk to another system when a cue fires," a Network cue built entirely in QLab's UI may be simpler than writing external code at all — worth suggesting when appropriate.

## Cue states relevant to scripting

- **Armed** — whether the cue will fire as part of a GO/sequence; disarmed cues are skipped.
- **Broken** — QLab flags a cue as broken if it's misconfigured (e.g. missing media file, invalid target for a control cue). Check this before assuming a script's failure is your code's fault rather than the show file's.
- **Flagged** — a user-set marker (visual highlight), no playback effect — often repurposed by programmers as an ad-hoc "needs review" tag.
- **Selected** — whatever's highlighted in the UI; addressable via `cue/selected/...` in OSC or `selected cues` in AppleScript, but not reliable for unattended automation since it depends on UI state.
- **Running / Paused / Loaded** — playback state, pollable via OSC (`isRunning` etc.) as described in `osc-dictionary.md`.

## Continue modes

Set per-cue, they control what happens after this cue's own playback:
- **Do not continue** — playhead stops here; operator must press GO again for the next cue.
- **Auto-continue** — automatically starts the next cue immediately (or after that cue's own pre-wait) without waiting for a GO.
- **Auto-follow** — starts the next cue only once *this* cue finishes playing.

These interact with pre-wait/post-wait timing on each cue — relevant when a script needs to predict "how long until cue N actually starts" rather than just "when was GO pressed."

## Network patches

A workspace's **Network settings** define named patches (endpoints) that Network cues send to, and can define QLab's own listening behavior (the OSC/MIDI in described in `osc-dictionary.md`). When troubleshooting "my external OSC device doesn't seem to reach QLab" or "QLab isn't sending OSC out," check whether the issue is on QLab's *inbound* listener (network settings, workspace passcode) or an *outbound* Network cue's patch configuration — they're separate systems even though both are "OSC."

## Triggers

Ways a cue (or GO) can be fired, independent of the cue's own type:
- Manual GO (keyboard/mouse/on-screen button)
- **Hotkey** — a keyboard shortcut bound to a specific cue or action
- **MIDI** — an incoming MIDI note/CC bound to fire a cue or GO
- **OSC** — external OSC message, per `osc-dictionary.md`
- **Wall clock** — fire at a specific time of day
- **Timecode** — fire at a specific timecode position while chasing an external or internal timecode source

Most "controller integration" requests (TouchOSC, Companion, a lighting console, a custom Python tool) are really about the OSC trigger path — build the OSC address/message per `osc-dictionary.md` and configure the other side to send it.
