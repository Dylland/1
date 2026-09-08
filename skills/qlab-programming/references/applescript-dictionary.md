# QLab AppleScript Reference

Property, command, and pattern names on this page are verified against real, production-tested scripts pulled directly from two community repositories (not paraphrased from search snippets):

- **Sam Schloegel, `samschloegel/qlab-scripts`** (MIT license) — scripts for both QLab 4 and QLab 5, actively maintained, documented at `https://samschloegel.github.io/qlab-scripts/`
- **Ben Smith, `bsmith96/qlab-scripts`** (MIT license) — scripts for QLab 4, oriented around live sound/theatre workflow automation

Both authors ask (not a license requirement, just a courtesy) that the attribution comment at the top of a script be kept intact if it's passed along inside a show file. Do the same if you hand a user one of their scripts largely as-is.

This page still doesn't replace QLab's own dictionary for anything not covered here — check `https://qlab.app/docs/v5/scripting/applescript-dictionary-v5/` (or the `v4`/`v3` equivalent) or open the dictionary in Script Editor (File → Open Dictionary → QLab) for full coverage.

## Basic skeleton

```applescript
tell application id "com.figure53.QLab.5" to tell front workspace
	-- commands/property access go here
end tell
```

**Bundle ID capitalization is version-specific and was confirmed to differ, not just guessed**: QLab 5 scripts consistently use `com.figure53.QLab.5` (capital QLab), while QLab 4 scripts consistently use `com.figure53.Qlab.4` (capital Q, lowercase lab). Match whichever your source scripts use — don't assume they're interchangeable typos of each other.

- `tell front workspace` targets whichever workspace window is frontmost. Target a specific one with `workspace "Name"` regardless of window focus.
- Get the current selection with `(selected as list)` — this is the pattern used throughout both repos, not `selected cues`.
- `current cue list` refers to whichever cue list tab is active; switch it with `set current cue list to (first cue list whose q name is "...")`.

## Targeting cues

| Reference | Example | Notes |
|---|---|---|
| By number | `cue "12"` | Numbers are strings, not necessarily numeric-looking. |
| By unique ID | `cue id (uniqueID of someCue)` | `uniqueID` is a readable property; stable across renumbering. Used this way in real move/reorder scripts. |
| Selection | `(selected as list)` | The confirmed idiom — coerce `selected` to a list before iterating or counting. |
| Whole list | `cues of current cue list` | Iterate to batch-process. |

## Verified properties

| Property | Notes |
|---|---|
| `q name` | Editable display name. Note the `q` prefix — plain `name` collides with AppleScript's own reserved term. |
| `q number` | The cue number (string, not necessarily numeric). |
| `q display name` | Read-only combined "number + name" style label, used for building human-readable output/log strings. |
| `q type` | Read-only, e.g. `"Audio"`, `"Fade"`, `"Mic"`, `"Network"`, `"Group"`, `"cue list"`. Used to branch logic (e.g. only touch cues where `q type is "Network"`). |
| `q color` | Set to a color name string. Confirmed base set: `none, red, orange, green, blue, purple`. QLab 5's expanded palette (seen in production use) also includes names like `grey, edgecombGray, mauve, chartreuse, cerulean, indigo` and dozens more themed names — treat the extended list as version-dependent and confirm in the workspace's own color picker if a specific extended name doesn't apply. |
| `armed` | Boolean. |
| `uniqueID` | Read-only stable identifier, read via `uniqueID of eachCue`. |
| `cue target` | On Start/Stop/Pause/Fade/Goto/etc. control cues — set to the cue object it should act on. |
| `parent of eachCue` | Reference to the containing group/cue list. |
| `playback position of (cue list)` | Sets/reads the list's playhead — the actual property behind "go to this cue without firing it." |
| `network patch name` (QLab 5) / `patch` (QLab 4) | On a Network cue, which named network patch it sends through — **property name itself changed between QLab 4 and 5**, not just a minor rename to assume is safe across versions. |
| `network patch number` (QLab 5) | Alternative to `network patch name` — addresses the patch by number instead of name. |
| `custom string` (QLab 5) / `custom message` (QLab 4) | On a Network cue with a custom OSC message type, the literal OSC address/argument text QLab sends when it fires — **also renamed between versions**. |
| `osc message type` (QLab 4) | Set to `custom` to unlock the `custom message` property on a Network cue. |

## Verified commands

| Command | Notes |
|---|---|
| `make type "Network"` / `"Group"` / `"Start"` / `"GoTo"` / `"cue list"` | Creates a new cue of that kind at the current position. **Note the type string for a cue list is lowercase `"cue list"`, while cue kinds like `Network`/`Group`/`Start` are capitalized** — this isn't a typo, both forms appear consistently across scripts from two different authors. After `make type "..."`, the new cue becomes the selection — grab a reference to it with `last item of (selected as list)`. |
| `moveSelectionUp` / `moveSelectionDown` | Moves the **selection** to the adjacent cue in the list — this is the actual command, not a guessed `movePlayheadUp`/`Down` name. Used to walk up/down from a cue to find a sibling (e.g. locating the cue above a Fade cue to auto-set its target). |
| `movePlayheadUpASequence` | Moves the **playhead** (not the selection) up one step in sequence — distinct from the selection-moving commands above. Seen used before `stop theSelection` to implement an "undo the last GO" script. |
| `stop theSelection` | Playback commands like `stop`/`start` can take a cue or a list of cues directly as an argument, not only via `tell someCue to stop`. |
| `move cue id (uniqueID of eachCue) of parent of eachCue to end of theGroup` | The verified pattern for reprogrammatically restructuring cues into a new group after creating them. |
| `collapse cueList` | Collapses a cue list/group in the UI. |
| `getLevel eachCue row 0 column N` | Reads an audio cue's fader/crosspoint level at a given output column — used to build "find all cues routed above threshold on output N" tooling. |
| `set network external output enabled of overrides to false` / `set overrides visibility of overrides to true` | The application-level (not workspace-level) `overrides` object — used for disabling all outbound OSC/network cues at once (e.g. for a "rig check" mode) and showing the overrides HUD. Note this is `tell application id "..."` without the nested `tell front workspace`. |

## Example patterns (adapted from verified, MIT-licensed source scripts)

**Arm every selected cue** (from `samschloegel/qlab-scripts`):
```applescript
tell application id "com.figure53.QLab.5" to tell front workspace
	repeat with eachCue in (selected as list)
		set armed of eachCue to true
	end repeat
end tell
```

**Toggle armed state on every selected cue:**
```applescript
tell application id "com.figure53.QLab.5" to tell front workspace
	repeat with eachCue in (selected as list)
		set armed of eachCue to not armed of eachCue
	end repeat
end tell
```

**Rename selected cues in sequence with a prefix/number/suffix, prompted via dialog** (this is the real, common "renumber my selection" ask):
```applescript
tell application id "com.figure53.QLab.5" to tell front workspace
	set theSelection to (selected as list)
	set startNum to 1
	set thePrefix to "SFX "
	repeat with eachCue in theSelection
		set q name of eachCue to (thePrefix & startNum)
		set startNum to startNum + 1
	end repeat
end tell
```
(The production version of this script wraps each value in a `display dialog` prompt so the operator sets prefix/start number/increment/suffix at run time — worth doing if this will be reused across shows rather than run once.)

**Copy the unique ID(s) of the current selection to the clipboard** (handy for building `cue id`-addressed scripts/integrations that need to survive renumbering):
```applescript
tell application id "com.figure53.QLab.5" to tell front workspace
	set theIDs to ""
	repeat with eachCue in (selected as list)
		if theIDs is not "" then set theIDs to theIDs & linefeed
		set theIDs to theIDs & uniqueID of eachCue
	end repeat
	set the clipboard to theIDs
end tell
```

**Build a Network cue that fires another cue over OSC, then a Start cue targeting it** (the verified pattern for "make QLab tell itself, or another QLab, to GO on a cue" purely inside the show file, no external script needed):
```applescript
tell application id "com.figure53.QLab.5" to tell front workspace
	make type "Network"
	set theNetwork to last item of (selected as list)
	set network patch name of theNetwork to "This QLab"
	set custom string of theNetwork to ("/cue/" & "12" & "/start")
end tell
```
This is exactly the mechanism behind self-contained "when this happens, also fire that" show logic — a Network cue whose custom OSC string targets another cue, wrapped in a Group with the triggering logic. Worth suggesting over an external script when the whole interaction should live inside the show file.

**Find cues routed above a level threshold on a given output** (audio-specific batch query, from `bsmith96/qlab-scripts`):
```applescript
tell application id "com.figure53.QLab.5" to tell front workspace
	set userThresh to -100 -- match Workspace Settings > Audio > Volume Limits > Min
	set theOut to 1 -- output column to check
	set theList to {}
	repeat with eachCue in (selected as list)
		if q type of eachCue is in {"Audio", "Fade", "Mic"} and ((getLevel eachCue row 0 column theOut) > userThresh) then
			set end of theList to eachCue
		end if
	end repeat
	set selected to theList
end tell
```

## Script cues vs. external AppleScript

Two different things both called "AppleScript" in a QLab context:

1. **A Script cue** — an actual cue *inside* the cue list, of kind Script, whose body is AppleScript (or shell) that QLab runs when that cue fires. Both source repos above recommend creating a dedicated "Hotkeys" cue list for Script cues bound to keyboard shortcuts, so batch-edit tools stay reachable without cluttering the show's playback list.
2. **External AppleScript talking to QLab** — a `.scpt`/`.applescript` file, or `osascript` from Terminal, using `tell application id "..."` to control a *running* QLab from outside. All the examples above are written this way.

## QLab 4 → 5 migration notes (confirmed differences)

Only the deltas actually observed across the two repos' parallel v4/v5 script sets — treat this as a partial list, not exhaustive:

- Bundle ID: `com.figure53.Qlab.4` → `com.figure53.QLab.5` (capitalization changes)
- Network cue's outbound message text: `custom message` (v4) → `custom string` (v5)
- Network cue's patch reference: `patch` (v4, set to a plain string/number) → `network patch name` or `network patch number` (v5, two distinct properties)
- `samschloegel/qlab-scripts` maintains parallel `scripts v4/` and `scripts v5/` folders specifically because of deltas like these — when in doubt, compare the two folders for the same script name rather than assuming v4 syntax works unmodified on v5.

## Further reading

- `https://qlab.app/docs/v5/scripting/applescript-dictionary-v5/` (swap `v5` for `v4`/`v3`) — the authoritative full command/property list, needed for anything not covered above
- `https://samschloegel.github.io/qlab-scripts/guide/` and `https://github.com/samschloegel/qlab-scripts` — the source for most of this page; browse for many more ready-made scripts (console recalls for DiGiCo/Yamaha, DS100 rig checks, stem-file versioning, fade generation)
- `https://github.com/bsmith96/qlab-scripts` — mixing-desk programming, routing/gang templates, soundcheck automation, all AppleScript-driven from QLab
