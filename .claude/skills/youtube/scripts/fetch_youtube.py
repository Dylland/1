#!/usr/bin/env python3
"""Fetch metadata and transcript/captions for a YouTube video, no API key required.

Prints a human-readable report by default (title, channel, duration, description,
then the transcript with timestamps). Pass --json for structured output instead.

Strategy, in order of preference:
  1. yt-dlp, if it's installed on PATH -- most robust against YouTube changes.
  2. Plain HTTP scraping via urllib (stdlib only, no extra dependencies):
     - oEmbed endpoint for basic metadata (title, channel, thumbnail).
     - The watch page's embedded ytInitialPlayerResponse JSON for duration,
       description, view count, and the list of available caption tracks.
     - The caption track's timedtext URL for the actual transcript (XML).

Usage:
  python3 fetch_youtube.py <youtube-url-or-id> [--lang en] [--json]
  python3 fetch_youtube.py <youtube-url-or-id> --metadata-only
  python3 fetch_youtube.py <youtube-url-or-id> --list-languages
"""
import argparse
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


def extract_video_id(url_or_id: str) -> str:
    """Accepts a full YouTube URL (watch/youtu.be/shorts/embed) or a bare 11-char ID."""
    s = url_or_id.strip()
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", s):
        return s
    parsed = urllib.parse.urlparse(s)
    if parsed.hostname in ("youtu.be",):
        vid = parsed.path.lstrip("/")
        if vid:
            return vid
    if parsed.hostname and "youtube.com" in parsed.hostname:
        qs = urllib.parse.parse_qs(parsed.query)
        if "v" in qs:
            return qs["v"][0]
        m = re.match(r"^/(shorts|embed|live)/([A-Za-z0-9_-]{11})", parsed.path)
        if m:
            return m.group(2)
    raise ValueError(f"Could not extract a video ID from: {url_or_id!r}")


def http_get(url: str, timeout: int = 20) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def fetch_oembed(video_id: str) -> dict:
    url = (
        "https://www.youtube.com/oembed?url="
        + urllib.parse.quote(f"https://www.youtube.com/watch?v={video_id}", safe="")
        + "&format=json"
    )
    try:
        return json.loads(http_get(url))
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError):
        return {}


def _extract_balanced_json(text: str, start_idx: int) -> str:
    """Given text[start_idx] == '{', return the substring of the balanced object."""
    depth = 0
    in_str = False
    escape = False
    for i in range(start_idx, len(text)):
        c = text[i]
        if in_str:
            if escape:
                escape = False
            elif c == "\\":
                escape = True
            elif c == '"':
                in_str = False
        else:
            if c == '"':
                in_str = True
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    return text[start_idx : i + 1]
    raise ValueError("Unbalanced JSON object in page source")


def fetch_player_response(video_id: str) -> dict:
    page = http_get(f"https://www.youtube.com/watch?v={video_id}").decode(
        "utf-8", errors="replace"
    )
    marker = "var ytInitialPlayerResponse = "
    idx = page.find(marker)
    if idx == -1:
        marker = "ytInitialPlayerResponse\":"
        idx = page.find(marker)
        if idx == -1:
            raise ValueError(
                "Could not find ytInitialPlayerResponse in the watch page "
                "(YouTube may have changed its page layout, or served a "
                "consent/age/login wall instead of the video)."
            )
        brace_start = page.find("{", idx)
    else:
        brace_start = idx + len(marker)
    raw_json = _extract_balanced_json(page, brace_start)
    return json.loads(raw_json)


def pick_caption_track(tracks: list, lang: str) -> dict:
    if not tracks:
        return {}
    def score(t):
        code = t.get("languageCode", "")
        is_asr = t.get("kind") == "asr"
        exact = code == lang
        prefix = code.startswith(lang.split("-")[0])
        return (exact, prefix and not is_asr, prefix, not is_asr)
    return max(tracks, key=score)


def fetch_transcript_xml(base_url: str) -> list:
    xml_bytes = http_get(base_url)
    root = ET.fromstring(xml_bytes)
    segments = []
    for node in root.findall("text"):
        start = float(node.get("start", "0"))
        dur = float(node.get("dur", "0"))
        text = html.unescape(node.text or "").replace("\n", " ").strip()
        if text:
            segments.append({"start": start, "dur": dur, "text": text})
    return segments


def format_timestamp(seconds: float) -> str:
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def scrape(video_id: str, lang: str) -> dict:
    result = {
        "video_id": video_id,
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "source": "scrape",
        "title": None,
        "channel": None,
        "duration_seconds": None,
        "description": None,
        "view_count": None,
        "available_caption_languages": [],
        "transcript": [],
        "transcript_error": None,
    }

    oembed = fetch_oembed(video_id)
    if oembed:
        result["title"] = oembed.get("title")
        result["channel"] = oembed.get("author_name")

    try:
        player = fetch_player_response(video_id)
    except (ValueError, urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError) as e:
        result["transcript_error"] = f"Could not load watch page metadata: {e}"
        player = {}

    details = player.get("videoDetails", {})
    if details:
        result["title"] = result["title"] or details.get("title")
        result["channel"] = result["channel"] or details.get("author")
        result["duration_seconds"] = int(details.get("lengthSeconds", 0)) or None
        result["description"] = details.get("shortDescription")
        result["view_count"] = details.get("viewCount")

    tracks = (
        player.get("captions", {})
        .get("playerCaptionsTracklistRenderer", {})
        .get("captionTracks", [])
    )
    result["available_caption_languages"] = [
        {
            "code": t.get("languageCode"),
            "name": t.get("name", {}).get("simpleText"),
            "auto_generated": t.get("kind") == "asr",
        }
        for t in tracks
    ]

    if not tracks:
        if result["transcript_error"] is None:
            result["transcript_error"] = (
                "No caption tracks are available for this video "
                "(captions may be disabled by the uploader)."
            )
        return result

    track = pick_caption_track(tracks, lang)
    try:
        result["transcript"] = fetch_transcript_xml(track["baseUrl"])
        result["transcript_language"] = track.get("languageCode")
        result["transcript_auto_generated"] = track.get("kind") == "asr"
    except (urllib.error.URLError, urllib.error.HTTPError, ET.ParseError) as e:
        result["transcript_error"] = f"Found caption tracks but failed to fetch transcript: {e}"

    return result


def parse_vtt(vtt_text: str) -> list:
    segments = []
    ts_re = re.compile(
        r"(\d{2}:\d{2}:\d{2}\.\d{3}|\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3}|\d{2}:\d{2}\.\d{3})"
    )

    def to_seconds(ts: str) -> float:
        parts = ts.split(":")
        if len(parts) == 3:
            h, m, s = parts
        else:
            h, m, s = "0", parts[0], parts[1]
        return int(h) * 3600 + int(m) * 60 + float(s)

    lines = vtt_text.splitlines()
    i = 0
    while i < len(lines):
        m = ts_re.search(lines[i])
        if m:
            start = to_seconds(m.group(1))
            end = to_seconds(m.group(2))
            i += 1
            text_lines = []
            while i < len(lines) and lines[i].strip():
                text_lines.append(re.sub(r"<[^>]+>", "", lines[i]).strip())
                i += 1
            text = " ".join(t for t in text_lines if t)
            if text and (not segments or segments[-1]["text"] != text):
                segments.append({"start": start, "dur": max(end - start, 0), "text": text})
        i += 1
    return segments


def try_yt_dlp(video_id: str, lang: str) -> dict:
    exe = shutil.which("yt-dlp")
    if not exe:
        return None
    url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        meta_raw = subprocess.run(
            [exe, "--dump-json", "--skip-download", "--no-warnings", url],
            capture_output=True, text=True, timeout=60, check=True,
        ).stdout
        meta = json.loads(meta_raw)
    except (subprocess.SubprocessError, json.JSONDecodeError, OSError):
        return None

    result = {
        "video_id": video_id,
        "url": url,
        "source": "yt-dlp",
        "title": meta.get("title"),
        "channel": meta.get("uploader") or meta.get("channel"),
        "duration_seconds": meta.get("duration"),
        "description": meta.get("description"),
        "view_count": meta.get("view_count"),
        "available_caption_languages": sorted(
            set(list(meta.get("subtitles", {}).keys()) + list(meta.get("automatic_captions", {}).keys()))
        ),
        "transcript": [],
        "transcript_error": None,
    }

    has_manual = lang in meta.get("subtitles", {})
    has_auto = lang in meta.get("automatic_captions", {})
    if not (has_manual or has_auto):
        result["transcript_error"] = (
            f"No '{lang}' captions available via yt-dlp for this video. "
            f"Available: {result['available_caption_languages']}"
        )
        return result

    with tempfile.TemporaryDirectory() as tmp:
        out_tmpl = str(Path(tmp) / "%(id)s.%(ext)s")
        cmd = [
            exe, "--skip-download", "--no-warnings", "--sub-lang", lang,
            "--sub-format", "vtt", "-o", out_tmpl,
        ]
        cmd += ["--write-subs"] if has_manual else ["--write-auto-subs"]
        cmd.append(url)
        try:
            subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=True)
        except subprocess.SubprocessError:
            result["transcript_error"] = "yt-dlp found captions but failed to download them."
            return result

        vtt_files = list(Path(tmp).glob("*.vtt"))
        if not vtt_files:
            result["transcript_error"] = "yt-dlp reported captions but produced no .vtt file."
            return result
        vtt_text = vtt_files[0].read_text(encoding="utf-8", errors="replace")
        result["transcript"] = parse_vtt(vtt_text)
        result["transcript_language"] = lang
        result["transcript_auto_generated"] = not has_manual

    return result


def render_text(data: dict) -> str:
    lines = []
    lines.append(f"Title:    {data.get('title') or '(unknown)'}")
    lines.append(f"Channel:  {data.get('channel') or '(unknown)'}")
    dur = data.get("duration_seconds")
    if dur:
        lines.append(f"Duration: {format_timestamp(dur)}")
    if data.get("view_count"):
        lines.append(f"Views:    {data.get('view_count')}")
    lines.append(f"URL:      {data.get('url')}")
    lines.append(f"Source:   {data.get('source')}")
    if data.get("description"):
        desc = data["description"].strip()
        if len(desc) > 800:
            desc = desc[:800] + "..."
        lines.append("")
        lines.append("Description:")
        lines.append(desc)

    lines.append("")
    if data.get("transcript"):
        lang = data.get("transcript_language", "?")
        kind = "auto-generated" if data.get("transcript_auto_generated") else "manual"
        lines.append(f"Transcript ({lang}, {kind}):")
        for seg in data["transcript"]:
            lines.append(f"[{format_timestamp(seg['start'])}] {seg['text']}")
    else:
        lines.append("Transcript: NOT AVAILABLE")
        if data.get("transcript_error"):
            lines.append(f"Reason: {data['transcript_error']}")
        if data.get("available_caption_languages"):
            lines.append(f"Other caption languages found: {data['available_caption_languages']}")

    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video", help="YouTube URL or bare 11-character video ID")
    ap.add_argument("--lang", default="en", help="Preferred caption language code (default: en)")
    ap.add_argument("--json", action="store_true", help="Print structured JSON instead of a text report")
    ap.add_argument("--metadata-only", action="store_true", help="Skip fetching the transcript")
    ap.add_argument("--list-languages", action="store_true", help="Only list available caption languages")
    ap.add_argument("--no-yt-dlp", action="store_true", help="Skip yt-dlp even if it's installed")
    args = ap.parse_args()

    try:
        video_id = extract_video_id(args.video)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    data = None
    if not args.no_yt_dlp:
        try:
            data = try_yt_dlp(video_id, args.lang)
        except Exception:
            data = None
    if data is None:
        try:
            data = scrape(video_id, args.lang)
        except Exception as e:
            print(f"Error: failed to fetch video info: {e}", file=sys.stderr)
            sys.exit(1)

    if args.metadata_only:
        data["transcript"] = []
        data.pop("transcript_error", None)

    if args.list_languages:
        print(json.dumps(data.get("available_caption_languages", []), indent=2))
        return

    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(render_text(data))


if __name__ == "__main__":
    main()
