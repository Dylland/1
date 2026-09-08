# QLab Resources

## Official (Figure 53)

- **QLab 5 docs home / scripting section**: `https://qlab.app/docs/v5/scripting/`
- **AppleScript dictionary**: v5 `https://qlab.app/docs/v5/scripting/applescript-dictionary-v5/` · v4 `https://qlab.app/docs/v4/scripting/applescript-dictionary-v4/` · v3 `https://qlab.app/docs/v3/scripting/applescript-dictionary-v3/`
- **OSC dictionary**: v5 `https://qlab.app/docs/v5/scripting/osc-dictionary-v5/` · v4 `https://qlab.app/docs/v4/scripting/osc-dictionary-v4/` · v3 `https://qlab.app/docs/v3/scripting/osc-dictionary-v3/`
- **Official annotated scripting/OSC examples**: v5 `https://qlab.app/docs/v5/scripting/examples/` · v4 `https://qlab.app/docs/v4/scripting/scripting-examples/`
- **Script cues**: `https://qlab.app/docs/v5/scripting/script-cues/`
- **Using OSC (networking setup, ports)**: `https://qlab.app/docs/v5/networking/using-osc/`
- **QLab Cookbook** (recipe-style projects): `https://qlab.app/cookbook/` — notably `https://qlab.app/cookbook/hotkeys-and-osc/` and `https://qlab.app/cookbook/touch-osc-wizardry/` for control-surface build-outs

If you (the assistant) have live web access in the current session, these are the pages to check first for exact, current syntax — this skill's reference files were built from documentation search snippets and general domain knowledge, not a guaranteed firsthand fetch.

## Community code

These three were cloned and read directly (full source, not search snippets) while building this skill — the AppleScript reference (`applescript-dictionary.md`) is sourced from the two script repos below, not reconstructed from memory.

- **`samschloegel/qlab-scripts`** (`https://github.com/samschloegel/qlab-scripts`, guide at `https://samschloegel.github.io/qlab-scripts/guide/`) — **MIT licensed.** A large, actively maintained library of QLab AppleScripts with parallel `scripts v4/` and `scripts v5/` folders (batch cue edits, fades, triggers, console-recall generators for DiGiCo/Yamaha, DS100 rig-check tooling, stem-file versioning). The author asks that the attribution comment at the top of each script be kept intact when passed along — not a license requirement, just a courtesy worth honoring.
- **`bsmith96/qlab-scripts`** (`https://github.com/bsmith96/qlab-scripts`) — **MIT licensed.** Scripts oriented around live-sound workflow: mixing-desk scene recall (Yamaha CL/QL, Allen & Heath, DiGiCo), routing/gang templates, soundcheck and line-check automation, OSC/MIDI control-cue generators. Same attribution courtesy as above.
- **`hjwp/python-osc-qlab-interface`** (`https://github.com/hjwp/python-osc-qlab-interface`) — **GPLv3 licensed.** A small Python OSC client/listener pair built on `python-osc`: fires messages on port 53000, listens for replies on a separate port, and parses a JSON payload out of them. Useful as a *reference for the request/response pattern* — this skill's `scripts/qlab_osc_client.py` was written independently (different architecture: TCP length-prefix framing rather than a fixed UDP listener port) specifically so it isn't a derivative of GPL-licensed code. **Don't copy this repo's code verbatim into anything MIT/permissively-licensed** without accounting for the GPL — describing the pattern in your own words or writing an independent implementation (as this skill does) is the safe path.

Other resources found but not fetched in full:
- **`archiedestructo`'s TouchQlab and OSC-Script** (`http://archiedestructo.github.io/TouchQlab/`, `http://archiedestructo.github.io/OSC-Script/`) — examples of building custom control surfaces / side-car apps that talk OSC to QLab. Check the license before reusing code directly.

## When to point the user at these vs. just writing the code

If the ask is a small, well-defined script (fire a cue, batch-edit properties, build one integration message), just write it using the patterns in this skill's reference files — no need to send the user off to read source. Point to these links when: the user wants to browse for inspiration on a bigger build-out (e.g. "I want to build a full iPad control surface"), or the request is unusual enough that a community example might already solve it — `samschloegel/qlab-scripts` in particular covers a lot of ground (console recalls, rig checks, stem versioning) that's faster to adapt from than to write fresh.
