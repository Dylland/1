---
name: youtube
description: Fetch and understand YouTube videos by pulling their transcript/captions and metadata (title, channel, duration, description) without needing an API key. Use this whenever the user pastes a youtube.com or youtu.be link, or asks Claude to "watch", "summarize", "transcribe", "pull quotes/timestamps from", or "answer questions about" a YouTube video — even if they don't say "transcript" explicitly. Also use it for requests like "what does this video say about X" or "give me the key points of this talk" when a YouTube URL is involved.
---

# YouTube video understanding

Claude can't literally watch video, but it can read what the video says. This
skill fetches a video's transcript/captions plus its metadata (title, channel,
duration, description) and hands you plain text to reason over — enough to
summarize, answer questions, pull quotes, or build a timestamped outline.

## Workflow

1. **Get the URL.** If the user pasted one, use it. If they only described the
   video, ask for the link (or a search) rather than guessing an ID.

2. **Run the fetch script**, using the URL as-is:

   ```
   python3 .claude/skills/youtube/scripts/fetch_youtube.py "<url>"
   ```

   This prints a text report: title, channel, duration, description, and the
   transcript with `[h:mm:ss]` timestamps on each line. It tries `yt-dlp`
   first if installed (more robust against YouTube layout changes), and
   otherwise falls back to a dependency-free scrape (oEmbed + the watch
   page's embedded player data + the caption track's timedtext XML). No
   YouTube API key is needed either way.

   Useful flags:
   - `--lang <code>` — preferred caption language (default `en`). Try this if
     the video is non-English or the auto-picked track isn't what you want.
   - `--metadata-only` — skip the transcript when you only need title/channel/
     duration (faster, and avoids dumping a huge transcript into context for
     a question that doesn't need it).
   - `--list-languages` — just list what caption languages exist, before
     committing to fetching one.
   - `--json` — structured output (`video_id`, `title`, `channel`,
     `duration_seconds`, `description`, `transcript: [{start, dur, text}]`,
     `available_caption_languages`, ...) if you need to process it
     programmatically rather than just read it.

3. **Read the transcript to do the actual task** — the script only fetches
   text, it doesn't summarize or analyze anything. That's your job:
   - *Summarize*: read through and write a real summary, don't just truncate.
   - *Answer a question*: search the transcript for the relevant passage(s)
     and quote/cite them with their timestamp.
   - *Key points / outline*: group the transcript into topics as they change,
     using the timestamp of the first line in each group as its heading.
   - *Quotes*: pull the line verbatim and give its timestamp so the user can
     jump to it (link as `https://youtu.be/<video_id>?t=<seconds>`).

   For a long video (over ~30-40 minutes of speech), the transcript can be
   large. If you only need part of it (e.g. "what did they say about X"),
   it's fine to read the full output and search within it — it's plain text,
   not something you need to pre-chunk. Only pull `--metadata-only` when you
   genuinely don't need the transcript at all.

## When there's no transcript

Some videos have captions disabled entirely. The script still returns
metadata plus a `transcript_error` explaining why, and lists any caption
languages it *did* find (maybe just not the one you asked for — retry with
`--lang`). If there's truly nothing available:
- Say so plainly rather than guessing at the content from the title alone.
- Offer to work from the title + description if that's enough for the task.
- If the user has their own transcript/notes, offer to use those instead.

## Notes

- This only works for public, non-age-restricted, non-login-walled videos —
  the same content a logged-out browser could reach.
- Auto-generated ("auto") captions are often lower quality than manual ones
  (no punctuation cues, occasional mis-hearings) — the report tells you which
  kind you got via `transcript_auto_generated`/`(auto-generated)` so you can
  caveat quotes pulled from them if accuracy matters.
- The script needs outbound network access to `youtube.com` (and `ytimg.com`
  if using yt-dlp for thumbnails). If it fails with a connection/proxy error
  rather than a "no captions" error, that's an environment/network issue, not
  a bad video — say so rather than retrying repeatedly.
