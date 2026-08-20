# Pro audio / recording terms commonly mangled by voice-to-text

Two categories below. **Safe auto-fix**: the STT mis-hearing is unambiguous —
there's really only one thing the speaker could mean, so correct it silently
as part of normal cleanup (same as fixing "danty" -> "Dante"). **Flag,
don't guess**: multiple real terms sound similar, or the mis-hearing could
mask a genuine model/number the speaker said — surface these with
`[unclear: ...]` rather than picking one.

This list is a starting point, not exhaustive — use the same judgment on
anything similar that isn't listed here: if there's only one sane reading,
fix it; if a wrong guess would misinform, flag it.

## Safe auto-fix (unambiguous mis-hearings)

| STT often outputs | Really means |
|---|---|
| danty / dan tee | Dante (Audinate's audio-over-IP protocol) |
| ay ess ee sixty seven / a s e sixty seven | AES67 |
| em ay dee eye | MADI |
| dee ess pee | DSP |
| eff oh aitch | FOH |
| eye ee em | IEM |
| ex el are | XLR |
| are eff | RF |
| dee bee / dee bees | dB / dBs (context decides — see "dB variants" below) |
| eek / eeq | EQ |
| forty eight volt / phantom | 48V phantom power |
| gain before feedback / gain before feed back | gain before feedback (GBF) |
| comb filtering / calm filtering | comb filtering |
| smart / smaart | SMAART (Rational Acoustics measurement platform) |
| avid ess siks / avid s6 | Avid S6 (console) |
| dee and bee / d and b | d&b audiotechnik |
| kay array | K-array |
| kay vee two | KV2 Audio |
| meyer / meyer sound | Meyer Sound |
| digico / digi co | DiGiCo |
| yamaha rivage / rivage pm | Yamaha Rivage PM series |
| waves lv one / lv-1 | Waves LV1 (console) |
| dante domain manager / d d m | Dante Domain Manager |

## Flag, don't guess (genuinely ambiguous)

These have multiple real referents that sound alike, or the mis-hearing
could be swallowing a specific number/model the speaker actually said —
resolving them wrong states a false fact, so surface instead of fixing.

- **dB variants** — "dee bee" alone is ambiguous between dB, dBu, dBV,
  dBFS, dB SPL, dBA. If the speaker didn't specify and it matters (e.g. a
  level reading, not a generic "turn it down a few dB"), flag which
  variant they meant rather than picking one.
- **"kay something" speaker/array names** — K-array, KV2, Kling & Freitag
  ("K&F"), and Kara (L-Acoustics' line array model) can all reduce to a
  similar sound. Don't default to the most common one — flag it.
- **Line array model numbers** — L-Acoustics (K1/K2/Kara/Kiva/A15...),
  d&b (J/V/Y/GSL/KSL series), Meyer (LEO/LYON/PANTHER/LINA)... a mangled
  model number should be flagged with the possibilities, not rounded to
  "whichever's most popular."
- **"forty" vs "fourteen" vs "fifty"** and similar number pairs — STT
  confuses these regularly, especially for channel counts and frequencies.
  If a number changes a technical fact (channel count, MHz, dB) and the
  audio is ambiguous in context (e.g. no supporting math elsewhere in the
  sentence), flag rather than pick.
- **Console platform families** — "Avid" (VENUE/S6L), "DiGiCo" (Quantum/SD
  series), "Yamaha" (Rivage/CL/QL) each have several product lines; if the
  speaker only said the brand and STT may have dropped a model qualifier,
  don't invent one.
- **"comb filtering" vs "cone filtering" vs "combing"** — real term is comb
  filtering; if context doesn't clearly support that acoustic meaning
  (e.g. talking about something unrelated to interference), don't force it.
- **AVB vs AES67 vs Dante vs MADI vs CobraNet** — these are distinct,
  non-interchangeable audio networking protocols. Never substitute one for
  another because they're mentioned in a similar context — if the raw
  audio genuinely could be any of these, flag it.

## Why this list exists

The failure mode this skill guards against isn't "the transcript has typos"
— it's "the cleaned-up version looks authoritative and is wrong." A flagged
`[unclear: ...]` costs the reader five seconds to resolve from memory. A
silently wrong model number or protocol name can propagate into a report,
a purchase decision, or advice to someone else. When genuinely torn between
fixing and flagging, flag.
