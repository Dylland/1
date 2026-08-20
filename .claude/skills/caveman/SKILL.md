---
name: caveman
description: Clean up raw voice-to-text/dictated text by stripping filler words, false starts, stutter-repeats, and dictation meta-comments ("scratch that", "let me restart") while preserving every real fact, number, and technical term exactly as said. Use this whenever the user pastes a block of dictated/voice-transcribed text, mentions voice-to-text, dictation, or speech-to-text, or asks to "clean this up," "tighten this," "make this readable," or "strip the fluff" from something they spoke rather than typed — especially in pro audio / recording-engineering contexts where a misheard technical term (a console/product name, a protocol like Dante or AVB, a dB figure) must be flagged, never silently guessed, because a wrong guess there is worse than the mess it's cleaning up.
---

# Caveman: clean dictation without inventing anything

Voice-to-text output has a specific, recognizable kind of noise: filler words,
false starts that get corrected mid-sentence, stutter-repeats, and the
speaker occasionally narrating their own dictation ("uh, delete that last
part"). None of that is content — it's the mechanical residue of talking
instead of typing. The job is to remove the residue and keep the content,
word for word where it's substantive.

The name is the instruction: caveman speak short. Big word gone if small
word same. But caveman not guess. Caveman not know word, caveman say so.

## The one rule that matters more than the rest

**Never silently "fix" a word you're not sure about — flag it instead.**

STT engines mis-hear technical vocabulary constantly, and pro audio is full
of terms that sound like other things (see `references/pro-audio-terms.md`
for the specific ones to watch for). If you guess wrong and clean the guess
into fluent prose, the user now has a confident-looking sentence that's
factually wrong and no way to tell it was ever uncertain. That's worse than
leaving the mess in. The user brought you in specifically to stop this from
happening — treat any place where the raw text could plausibly be a
mis-transcribed technical term, product name, model number, or measurement
as something to surface, not smooth over.

## What to remove

- **Filler words/verbal tics**: um, uh, like, you know, so yeah, I mean (when
  it isn't introducing an actual correction), basically/literally/honestly
  used as tics rather than meaningfully.
- **False starts and self-corrections**: keep only the corrected final
  version. "We used the— no wait, we ran it through the DiGiCo, not the
  Avid" becomes "We ran it through the DiGiCo."
- **Stutter-repeats**: "the the gain structure" -> "the gain structure";
  "it's it's basically" -> "it's basically" (then drop "basically" too if
  it's a tic).
- **Dictation meta-comments**: "scratch that," "let me start over," "new
  paragraph," "delete that last bit" — act on the instruction (i.e. actually
  remove what they told you to remove) rather than leaving the instruction
  itself in the text.
- **Redundant hedge padding** that adds no information: "kind of, sort of,
  basically, at the end of the day, if that makes sense" — cut when it's
  pure padding.

## What to never touch

- **Numbers, units, and measurements** — dB, Hz, feet/meters, channel
  counts, model numbers. Don't round, don't normalize units, don't "clean up"
  a number.
- **Technical terms and proper nouns** — product names, protocol names,
  person names, venue names. If it's spelled unusually but you're confident
  it's correct (matches a known term), leave it exactly as said.
- **Genuine hedges that carry real meaning** — "I think it was around -18
  dBFS, I'd have to check" is the speaker flagging their own uncertainty
  about a fact. That's content, not filler — keep it, don't launder it into
  false confidence.
- **Negations, qualifiers, and sequencing** — "not," "before," "after,"
  "unless" change what's true. Never drop these to shorten a sentence.
- **The substance of what they actually said** — this is a cleanup pass, not
  a rewrite or a summary of a summary. Don't paraphrase content away, don't
  add transitions or framing they didn't say, don't editorialize.

If you're ever unsure whether something is filler or content, keep it. An
extra "I think" that survives the cut costs nothing; a dropped qualifier
that changes the meaning of a technical claim is the exact failure mode this
skill exists to prevent.

## Output format

Give the cleaned text as the main output — that's what the user wants to
walk away with. Skip preamble like "Here's the cleaned version:".

If (and only if) something in the raw text is genuinely ambiguous — a term
you can't confidently resolve, a number that sounds off, a name that could
be one of two things — mark it inline in the cleaned text with
`[unclear: "<best guess or raw text>"]` at that spot, and end with a short
**Flagged for confirmation** list naming each one and why. Don't manufacture
flags to seem thorough — most dictation has zero genuinely ambiguous spots
once the filler is stripped, and an empty flag list is a fine, common
outcome.

## Example

**Raw dictation:**
> okay so uh the show last night we had we had some issues with the uh
> the monitor world, the wedges kept, no sorry it wasn't the wedges it was
> the IEMs, the IEMs kept cutting out and I think it was a a RF issue,
> like there was some kind of intermod going on, um we were running I want
> to say fourteen channels of Shure Axient in the two ten to two thirty
> range and honestly it might've been a a local TV station stepping on us,
> we should probably rescan next time before doors, if that makes sense

**Cleaned:**
> Last night's show had issues in monitor world — the IEMs kept cutting
> out. I think it was an RF issue, some kind of intermod. We were running
> 14 channels of Shure Axient in the 210–230 range, and it might have been
> a local TV station stepping on us. We should rescan next time before
> doors.

Nothing here needed a flag: no term was ambiguous, every number and product
name was clearly spoken. Compare to a case where a flag is warranted:

**Raw dictation:**
> we patched it through the danty network, dante I mean, but the mains were
> throwing some weird uh comb filtering around eight hundred hurts and I
> think the array was a kay-viv but don't quote me on that

**Cleaned:**
> We patched it through the Dante network. The mains were throwing some
> comb filtering around 800 Hz, and I think the array was a [unclear:
> "kay-viv" — possibly a specific K-array or KV2 Audio model, not enough
> context to tell which] — the speaker themselves said not to quote them
> on it.

**Flagged for confirmation:**
- "kay-viv" — sounds like it could be a K-array model or KV2 Audio, but
  there's no other context (no specific model number, no other brand
  clues) to pick one. The speaker also flagged their own uncertainty here,
  so don't resolve it for them.

Note "danty" wasn't flagged — the speaker self-corrected to "Dante"
immediately, so that's a false start to clean up, not an ambiguity to flag.

## Domain reference

`references/pro-audio-terms.md` lists pro-audio and recording-arts terms
that are commonly mis-heard by STT engines, plus their real counterparts.
Check it when something in the raw text looks like it could be one of these
— it'll tell you whether it's a safe auto-fix (a clear, unambiguous
mis-transcription) or something to flag instead.
