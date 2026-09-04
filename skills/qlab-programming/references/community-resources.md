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

- **`hjwp/python-osc-qlab-interface`** (`https://github.com/hjwp/python-osc-qlab-interface`) — a Python OSC client/listener pair built on the `python-osc` library: a `Client` that sends to QLab on port 53000, a `Listener` that receives replies on a separate port and parses the JSON payload, and an `Interface` layer with helpers like `get_cue_property()` / `set_cue_property()` / `select_next_cue()`. Good reference for the request/response pattern this skill's `scripts/qlab_osc_client.py` also implements.
- **`samschloegel/qlab-scripts`** + guide (`https://github.com/samschloegel/qlab-scripts`, `https://samschloegel.github.io/qlab-scripts/guide/`) — a collection of practical AppleScripts for QLab automation, with a how-to guide explaining conventions like preferring cue number over index as the stable-ish identifier for readable scripts.
- **`bsmith96/Qlab-Scripts`** (`https://github.com/bsmith96/Qlab-Scripts`) — more AppleScripts for QLab 4, oriented around hotkey-driven automation of repetitive tasks.
- **`archiedestructo`'s TouchQlab and OSC-Script** (`http://archiedestructo.github.io/TouchQlab/`, `http://archiedestructo.github.io/OSC-Script/`) — examples of building custom control surfaces / side-car apps that talk OSC to QLab.

## When to point the user at these vs. just writing the code

If the ask is a small, well-defined script (fire a cue, batch-edit properties, build one integration message), just write it using the patterns in this skill's reference files — no need to send the user off to read source. Point to these links when: the user wants to browse for inspiration on a bigger build-out (e.g. "I want to build a full iPad control surface"), when the request is unusual enough that a community example might already solve it, or when you flagged something in this skill's own reference files as unverified and precision genuinely matters for the user's situation.
