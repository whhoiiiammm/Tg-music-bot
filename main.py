import os
import re
import asyncio
from datetime import timedelta

from pyrogram import Client, filters
from pyrogram.types import Message

from yt_dlp import YoutubeDL

API_ID = int(os.getenv("API_ID", "12345"))          # Replace or export
API_HASH = os.getenv("API_HASH", "your_api_hash")   # Replace or export
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")# Replace or export

app = Client(
    "music-bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

YDL_OPTS = {
    "format": "bestaudio/best",
    "outtmpl": "%(title).200s.%(ext)s",
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "192",
    }],
}

def sec_to_hhmmss(s):
    try:
        return str(timedelta(seconds=int(s)))
    except Exception:
        return "00:00:00"

def yt_search(query: str):
    if not re.match(r"https?://", query):
        query = f"ytsearch1:{query}"
    with YoutubeDL(YDL_OPTS) as ydl:
        info = ydl.extract_info(query, download=False)
        if "entries" in info:
            info = info["entries"][0]
        return info

async def download_audio(info):
    with YoutubeDL(YDL_OPTS) as ydl:
        out = ydl.extract_info(info["webpage_url"], download=True)
        title = out.get("title") or "Audio"
        duration = out.get("duration") or 0
        base = ydl.prepare_filename(out)
        audio_path = re.sub(r"\.(webm|m4a|opus|mp4|mkv)$", ".mp3", base)
        return audio_path, title, duration

@app.on_message(filters.command(["start", "help"]))
async def start_cmd(_, m: Message):
    await m.reply_text("👋 Send me a song name or YouTube link with `/song <query>`")

@app.on_message(filters.command(["song"]))
async def song_cmd(_, m: Message):
    if len(m.command) < 2:
        return await m.reply_text("Usage: `/song kesariya` or YouTube link")
    query = " ".join(m.command[1:])
    status = await m.reply_text("🔎 Searching…")
    info = yt_search(query)
    audio_path, title, duration = await download_audio(info)
    await m.reply_audio(
        audio=audio_path,
        caption=f"🎵 {title}\n⏱ {sec_to_hhmmss(duration)}"
    )
    os.remove(audio_path)
    await status.delete()

if __name__ == "__main__":
    print("Bot is running…")
    app.run()
