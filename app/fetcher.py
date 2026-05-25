import os
import tempfile

import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi

# imageio-ffmpeg ships a bundled ffmpeg binary (needed only for Whisper fallback).
# Import is optional so the server starts even if the package is missing.
_FFMPEG_DIR = ""
try:
    import imageio_ffmpeg
    _FFMPEG_DIR = os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe())
    os.environ["PATH"] = _FFMPEG_DIR + os.pathsep + os.environ.get("PATH", "")
except ImportError:
    pass

WHISPER_ENABLED = os.getenv("WHISPER_ENABLED", "false").lower() == "true"


def fetch_video_info(url: str) -> dict:
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "ffmpeg_location": _FFMPEG_DIR,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    video_id = info["id"]
    transcript, transcript_source = _get_transcript(video_id, url)

    return {
        "title": info.get("title"),
        "channel": info.get("uploader"),
        "description": (info.get("description") or "")[:500],
        "tags": info.get("tags") or [],
        "transcript": transcript,
        "transcript_source": transcript_source,
        "thumbnail_path": None,  # CLIP disabled; re-enable when torch is available
    }


def _get_transcript(video_id: str, url: str) -> tuple[str | None, str | None]:
    try:
        entries = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join(e["text"] for e in entries)
        return text, "captions"
    except Exception:
        pass

    if WHISPER_ENABLED:
        return _whisper_transcribe(url)

    return None, None


def _whisper_transcribe(url: str) -> tuple[str | None, str | None]:
    try:
        from faster_whisper import WhisperModel

        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": f"{tmpdir}/audio.%(ext)s",
                "quiet": True,
                "no_warnings": True,
                "ffmpeg_location": _FFMPEG_DIR,
                "postprocessors": [
                    {"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}
                ],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            audio_files = [f for f in os.listdir(tmpdir) if f.endswith(".mp3")]
            if not audio_files:
                return None, None

            model = WhisperModel("small", device="cpu", compute_type="int8")
            segments, _ = model.transcribe(f"{tmpdir}/{audio_files[0]}")
            return " ".join(s.text for s in segments), "whisper"
    except Exception as e:
        print(f"[Whisper] transcription failed: {e}")
        return None, None
