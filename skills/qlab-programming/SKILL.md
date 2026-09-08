---
name: qlab-programming
description: Write and troubleshoot QLab show-control programming — OSC control strings and clients (Python, TouchOSC, Bitfocus Companion, Lemur, any OSC-capable controller), AppleScript scripts and QLab Script cues, and cue-list/workspace architecture (cue addressing by number/id/index, workspaces, cue types, network patches, triggers). Use this skill whenever the user mentions QLab, Figure 53, cue lists/cue carts, "GO" buttons, show control, or asks to build integrations between QLab and lighting/audio/video/automation systems (Eos, Companion, TouchOSC, MIDI/MSC/MTC/timecode gear) — even if they don't say "QLab" explicitly but describe firing cues, jumping cues, or syncing a console/controller to a show file. Also use it for general QLab operational questions (cue types, continue modes, groups, passcodes) that come up while building this kind of integration.
---

# QLab Programming

QLab (by Figure 53) is a macOS show-control app for cue-based playback of audio, video, lighting, and control cues in live production. This skill helps write code and scripts that drive or extend QLab: OSC clients/messages, AppleScript, and QLab's own Script cues.

QLab has shipped major versions 3, 4, and 5, each with its own scripting dictionary. **Ask (or infer from context) which version the user is on if it affects syntax** — the AppleScript application identifier and a handful of commands changed between versions (e.g. `com.figure53.qlab.5` vs `com.figure53.qlab.4`). Default to QLab 5 syntax if unstated, since it's current, but flag the version assumption to the user.

## Before writing anything, figure out which tool fits

QLab exposes three different ways to script it — pick based on where the logic needs to live:

| Approach | Runs where | Best for |
|---|---|---|
| **OSC** | Any external device/app on the network (or localhost) | Remote/hardware control surfaces, cross-app integration (lighting consoles, Companion, TouchOSC), anything that needs to live outside QLab |
| **AppleScript** | macOS, via Script Editor / `osascript` / a `.scpt`, talking to a running QLab | One-off automation, batch-editing a workspace (renumbering, bulk property changes), tooling that manages the **show file itself** rather than just firing cues during a show |
| **Script cue** | Inside the QLab cue list itself (an actual cue, of kind Script, containing AppleScript or shell) | Show-time logic that should live and travel *with the show file* — e.g. "when this cue fires, also nudge an external system" |

Ask which one the user wants if it's not obvious — "control QLab from my laptop/console/tablet" means OSC, "process my show file" or "batch edit cues" usually means AppleScript, "make this happen when the cue plays" usually means a Script cue.

For deep syntax reference, read the relevant file in `references/` rather than guessing:

- `references/osc-dictionary.md` — OSC addressing, ports, transport, commands, replies, passcodes
- `references/applescript-dictionary.md` — AppleScript syntax, targeting cues, common commands/properties
- `references/cue-concepts.md` — cue types, workspaces vs. cue lists vs. cue carts, triggers, continue modes, groups, network patches
- `references/community-resources.md` — official doc links by version, the Cookbook, and community code repos worth pointing the user at or borrowing patterns from

`scripts/qlab_osc_client.py` is a ready-to-run Python OSC client/listener skeleton (built on `python-osc`) — use it as the starting point for any "write me a Python script to control QLab" request instead of building the UDP/TCP plumbing from scratch each time.

## A critical caveat: verify exact syntax before it ships to a real show

The **AppleScript** reference (`references/applescript-dictionary.md`) is sourced from real, production-tested scripts pulled directly from two MIT-licensed community repos (`samschloegel/qlab-scripts`, `bsmith96/qlab-scripts`) — property names, command names, and the QLab 4 vs. 5 deltas documented there were confirmed against actual working code, not reconstructed from memory. Trust it, but it's not exhaustive; fall back to the official dictionary for anything it doesn't cover.

The **OSC** reference (`references/osc-dictionary.md`) is weaker: it was assembled from Figure 53's documentation via search-result snippets, because `qlab.app` is network-egress-blocked in the environment this skill was built in and could not be fetched directly. Treat its exact address spellings as a **strongly-informed draft, not gospel**:

- Before handing a script to the user for a real show, especially anything destructive (batch edits, renumbering, deleting) — tell them to test it against a scratch/copy workspace first, not their live show file.
- If you have live web access in this session and precision matters, cross-check the OSC dictionary against the official docs before finalizing:
  - `https://qlab.app/docs/v5/scripting/osc-dictionary-v5/` (swap `v5` for `v4`/`v3` for older shows)
- If you can't reach the web, say so plainly rather than presenting unverified OSC syntax as certain — this is a live-show tool, and a wrong cue number or a silently-failed script mid-performance is a real production problem, not just a bug.
- Community source repos (GitHub) are generally NOT egress-blocked even when `qlab.app` is — if you hit the same block, try `add_repo`/cloning a relevant repo directly rather than assuming all web access is unavailable.

## Quick-start patterns

**"Fire cue X and wait for it to finish" (Python/OSC):** use `scripts/qlab_osc_client.py`. Firing is fire-and-forget (`/cue/{number}/start`); "wait for it to finish" requires either polling `/cue/{number}/isRunning` or listening for the cue's completion via OSC status updates — see `references/osc-dictionary.md` for both patterns and their tradeoffs (polling is simpler and more portable; status updates are more efficient but need the workspace's OSC status-update setting enabled).

**"Give me the OSC address for X":** check the command tables in `references/osc-dictionary.md` first — most playback and property get/set commands follow a predictable `/cue/{id-or-number}/{verb}` shape, and the reference explains the addressing options (rootless vs. `/workspace/{id}/...`, by number vs. `/cue_id/{id}/...` vs. selected).

**"Write an AppleScript that batch-edits cues":** use `references/applescript-dictionary.md` for the `tell application ... tell workspace ... end tell` skeleton and property names, and remind the user to run it against a duplicate of the show file first — AppleScript property edits are immediate and don't go through an undo-friendly UI action.

**"How do I get a console/controller talking to QLab" (Eos, Companion, TouchOSC, etc.):** this is almost always OSC. Point to `references/osc-dictionary.md` for QLab's side, and ask what's on the other end — most consoles/controllers have their own OSC-string builders, so the deliverable is usually "here's the exact OSC address/argument QLab expects," not a full client.

## Talking to a domain expert

The user of this skill is often a working live-production professional (system tech, programmer, educator), not someone learning what a cue list is. Skip the 101-level explanations of what QLab or OSC *are* unless asked — get straight to the address strings, the script, or the property names. Do flag version-specific gotchas and untested-against-live-docs syntax, since those are the kind of thing that bites you during a tech rehearsal, not in a code review.
