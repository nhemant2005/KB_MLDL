import sys
import json
import yt_dlp


def extract_playlist(url):
    ydl_opts = {
        "extract_flat": True,
        "quiet": True,
    }

    print(f"Extracting playlist info from: {url}")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    if "entries" not in info:
        print(
            "Error: Could not extract playlist entries. Ensure the URL is a valid playlist."
        )
        sys.exit(1)

    entries = info["entries"]

    playlist_data = []
    total_duration_sec = 0

    for index, entry in enumerate(entries, start=1):
        # Handle cases where videos might be private/deleted
        title = entry.get("title", "Unknown Title")

        # Ensure we construct a valid URL
        video_id = entry.get("id")
        video_url = entry.get("url")
        if not video_url and video_id:
            video_url = f"https://www.youtube.com/watch?v={video_id}"

        duration = entry.get("duration") or 0

        playlist_data.append(
            {
                "index": index,
                "title": title,
                "url": video_url,
                "duration_seconds": int(duration),
            }
        )

        total_duration_sec += duration

    with open("playlist_raw.json", "w", encoding="utf-8") as f:
        json.dump(playlist_data, f, indent=2, ensure_ascii=False)

    total_videos = len(playlist_data)
    total_duration_hours = total_duration_sec / 3600

    print("\nSummary:")
    print(f"Total videos: {total_videos}")
    print(f"Total duration: {total_duration_hours:.2f} hours")
    print("Saved output to playlist_raw.json")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python playlist_extractor.py <playlist_url>")
        sys.exit(1)

    playlist_url = sys.argv[1]
    extract_playlist(playlist_url)
