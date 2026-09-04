# QLab AppleScript Reference

Source: Figure 53's official AppleScript dictionaries (`https://qlab.app/docs/v5/scripting/applescript-dictionary-v5/`, `v4`, `v3`) plus community examples (Sam Schloegel's `qlab-scripts` guide, `bsmith96/Qlab-Scripts`). Assembled from documentation search snippets and QLab domain knowledge, not a firsthand full-page fetch of the dictionary — **open the dictionary in Script Editor (File → Open Dictionary → QLab) or check the live docs to confirm exact command/property names for the target QLab version before relying on this for anything destructive.**

## Basic skeleton

QLab can have multiple workspaces open, and each workspace can have cues with the same number, so AppleScript against QLab is normally a **nested tell**: outer `tell` targets the application, inner `tell` targets a specific workspace.

```applescript
tell application id "com.figure53.qlab.5"
	tell front workspace
		-- commands/property access go here
	end tell
end tell
```

Notes:
- The application identifier is version-specific: `com.figure53.qlab.5` for QLab 5, `com.figure53.qlab.4` for QLab 4, `com.figure53.qlab.3` for QLab 3. `tell application "QLab 5"` (by name rather than bundle ID) also generally works if QLab 5 is installed and that's the only version present.
- `front workspace` targets whichever workspace window is frontmost. To target a specific one regardless of window focus/order, use `workspace "Name"` or `workspace id "..."` if you know the identifier.
- A one-line form is fine for a single command: `tell application id "com.figure53.qlab.5" to tell front workspace to set armed of cue "4" to false`.

## Targeting cues

Inside a `tell workspace` block:

| Reference | Example | Notes |
|---|---|---|
| By number | `cue "12"` | Cue numbers are strings, not necessarily numeric-looking (`cue "panda"` is valid). This is the identifier a human programmer actually sees and edits, so it's usually the most legible choice for scripts a person will read/maintain later. |
| By unique ID | `cue id "XXXXXXXX-..."` | Stable across renumbering/renaming — best for scripts that must survive a programmer reshuffling the cue list. |
| By index | `cue index 3` (or similar) | Position in the list; brittle if cues are inserted/removed. |
| Selection | `selected cues` | Whatever's currently selected in the QLab UI — useful for "operate on what I've got highlighted" tooling, not for unattended scripts. |
| Whole list | `cues of cue list "Main"` (or `every cue of ...`) | Iterate to batch-process. |

## Common commands (verify names against the live dictionary)

Typical verbs exposed on cues/workspaces — names below are the commonly-documented/expected ones, but confirm exact spelling/capitalization for the target version:

- `start` / `stop` / `pause` / `resume` / `hardStop` / `hardPause`
- `load` / `preview`
- `panic` (workspace-level hard stop)
- `reset`
- `movePlayheadTo` / `movePlayheadDown` / `movePlayheadUp` — reposition the "next cue" pointer in a list without firing anything
- `dispatch` (send an OSC/network message cue's payload without necessarily "playing" it, in some versions)

## Common properties

Readable/settable on a cue object (again, confirm exact names in the live dictionary — property names shown with the conventional AppleScript spacing):

- `q number`, `q name` — number and display name (note: often `number`/`name` alone, or `q number`/`q name` depending on version — QLab's dictionary sometimes prefixes to avoid clashing with AppleScript's own `name`)
- `armed` (boolean)
- `flagged` (boolean)
- `broken` (boolean, read-only — true if the cue has a configuration problem, e.g. missing media file)
- `notes` (text)
- `pre wait`, `post wait` (numbers, seconds)
- `duration` (number, seconds, read-only for most media cue types)
- `continue mode` (enum — e.g. do not continue / auto-continue / auto-follow)
- `color name` (text/enum)
- `cue type` or `kind` (read-only, tells you Audio/Video/Group/Script/etc.)

## Script cues vs. external AppleScript

Two different things both called "AppleScript" in a QLab context:

1. **A Script cue** — an actual cue *inside* the cue list, of kind "Script," whose body is AppleScript (or shell) that QLab runs when that cue fires. This is how you make "when cue 12 plays, also do X" logic travel with the show file itself. See `references/cue-concepts.md` for where Script cues fit among the other cue types.
2. **External AppleScript talking to QLab** — a `.scpt`/`.applescript` file, or a script run via `osascript` from Terminal/another app, that uses `tell application id "com.figure53.qlab.5"` to control a *running* QLab instance from outside. This is what the skeleton and examples above are for — batch-editing, tooling, automation that isn't part of the show's own playback logic.

## Example patterns

**Renumber cues sequentially, keeping the list order (illustrative — confirm property names live before running against a real show):**
```applescript
tell application id "com.figure53.qlab.5"
	tell front workspace
		set cueList to cues of cue list 1
		set i to 1
		repeat with theCue in cueList
			set q number of theCue to (i as text)
			set i to i + 1
		end repeat
	end tell
end tell
```
Always run something like this against a duplicate of the show file first — it's a bulk, immediate edit with no confirmation dialog.

**Set armed = false on a specific cue by number:**
```applescript
tell application id "com.figure53.qlab.5" to tell front workspace to set armed of cue "4" to false
```

**Dump every cue's number and name to a log (for auditing a show file):**
```applescript
tell application id "com.figure53.qlab.5"
	tell front workspace
		set output to ""
		repeat with theCue in cues of cue list 1
			set output to output & (q number of theCue) & tab & (q name of theCue) & linefeed
		end repeat
	end tell
end tell
return output
```

## Further reading / patterns to borrow

- `https://qlab.app/docs/v5/scripting/applescript-dictionary-v5/` — the authoritative command/property list for QLab 5 (swap `v5` for `v4`/`v3`)
- `https://qlab.app/docs/v5/scripting/examples/` — Figure 53's own annotated scripting examples
- `https://samschloegel.github.io/qlab-scripts/guide/` and `https://github.com/samschloegel/qlab-scripts` — community AppleScript patterns, including the "prefer cue number as identifier" convention reflected above
- `https://github.com/bsmith96/Qlab-Scripts` — more community AppleScript automation/hotkey examples
