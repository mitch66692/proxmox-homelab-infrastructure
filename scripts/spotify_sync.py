#!/usr/bin/env python3
# scripts/spotify_sync.py
import sys, os, re, json, subprocess, urllib.request, urllib.parse
from spotify_scraper import SpotifyClient
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, APIC

# Paths configured to match the unified /data volume architecture
MUSIC_DIR    = "/data/media/music"
ARCHIVE_FILE = os.path.join(MUSIC_DIR, "downloaded_archive.txt")

def clean_filename(s):
    s = re.sub(r'[<>:\"/\\|?*]', '', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s[:100]

def get_cover_art(artist, title):
    try:
        query = urllib.parse.quote(f"{artist} {title}")
        url = f"https://itunes.apple.com/search?term={query}&media=music&limit=1"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        data = json.loads(urllib.request.urlopen(req, timeout=10).read())
        results = data.get('results', [])
        if results:
            art_url = results[0].get('artworkUrl100', '').replace('100x100bb', '600x600bb')
            if art_url:
                return urllib.request.urlopen(art_url, timeout=10).read()
    except Exception as e:
        print(f"  [WARN] Cover art not found: {e}")
    return None

def tag_file(filepath, artist, title):
    try:
        audio = MP3(filepath, ID3=ID3)
        try:
            audio.add_tags()
        except Exception:
            pass
        audio.tags['TIT2'] = TIT2(encoding=3, text=title)
        audio.tags['TPE1'] = TPE1(encoding=3, text=artist)
        print(f"  [TAG] Searching for cover art...")
        cover_data = get_cover_art(artist, title)
        if cover_data:
            audio.tags['APIC'] = APIC(encoding=3, mime='image/jpeg', type=3, desc='Cover', data=cover_data)
            print(f"  [TAG] Cover art embedded")
        else:
            print(f"  [TAG] No cover art found")
        audio.save()
        print(f"  [TAG] ID3 tags successfully written")
        return True
    except Exception as e:
        print(f"  [WARN] Tagging error: {e}")
        return False

def get_tracks(playlist_url):
    client = SpotifyClient()
    try:
        playlist = client.get_playlist_info(playlist_url)
        tracks = []
        for t in playlist.get("tracks", []):
            name = t.get("name", "")
            raw_artist = t.get("artists", [{}])[0].get("name", "Unknown") if t.get("artists") else "Unknown"
            artist = re.split(r'[,\xa0]+', raw_artist)[0].strip()
            if name:
                tracks.append({"title": name, "artist": artist})
        return tracks
    except Exception as e:
        print(f"Error reading playlist: {e}")
        return []
    finally:
        client.close()

def is_file_present(title, artist, local_files):
    title_clean  = re.sub(r'[^\w\s]', '', title.lower())
    artist_clean = re.sub(r'[^\w\s]', '', artist.lower())
    for f in local_files:
        f_clean = re.sub(r'[^\w\s]', '', f.lower())
        if title_clean in f_clean and artist_clean in f_clean:
            return True
    return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 spotify_sync.py <PLAYLIST_URL>")
        sys.exit(1)

    os.makedirs(MUSIC_DIR, exist_ok=True)
    os.chdir(MUSIC_DIR)

    print("\n=== Fetching Playlist Data ===")
    tracks = get_tracks(sys.argv[1])
    if not tracks:
        print("No tracks found.")
        sys.exit(1)

    print(f"=== Found {len(tracks)} tracks. Starting download process ===\n")
    local_files = [f for f in os.listdir(MUSIC_DIR) if f.endswith((".mp3", ".flac", ".ogg", ".m4a"))]
    downloaded, skipped, errors = 0, 0, 0

    for t in tracks:
        if not t["title"]:
            continue

        artist_clean = clean_filename(t['artist'])
        title_clean  = clean_filename(t['title'])
        file_name    = f"{artist_clean} - {title_clean}.mp3"
        filepath     = os.path.join(MUSIC_DIR, file_name)

        search_title = re.sub(r'(?i)\s*-\s*(from|remastered|live|radio|bonus|acoustic).*', '', t['title']).strip()

        print(f"\n-> {t['artist']} - {t['title']}  [YT Search: {search_title}]")

        if is_file_present(t["title"], t["artist"], local_files):
            print("  [SKIP] File already exists.")
            skipped += 1
            continue

        files_before = set(os.listdir(MUSIC_DIR))
        result = subprocess.run([
            "yt-dlp", f"ytsearch1:{t['artist']} - {search_title}",
            "--js-runtimes", "node:/usr/bin/node",
            "--remote-components", "ejs:github",
            "--extract-audio", "--audio-format", "mp3",
            "--audio-quality", "0",
            "--no-embed-metadata",
            "--no-embed-thumbnail",
            "--download-archive", ARCHIVE_FILE,
            "--no-playlist", "--quiet", "--progress",
            "-o", f"{artist_clean} - {title_clean}.%(ext)s"
        ])

        if result.returncode != 0:
            print("  [WARN] yt-dlp could not fetch this track.")
            errors += 1
            continue

        files_after  = set(os.listdir(MUSIC_DIR))
        new_files = [f for f in (files_after - files_before) if f.endswith(".mp3")]

        if new_files:
            downloaded_file = os.path.join(MUSIC_DIR, new_files[0])
            if new_files[0] != file_name:
                os.rename(downloaded_file, filepath)
                print(f"  [OK] Renamed to -> {file_name}")
            tag_file(filepath, t['artist'], t['title'])
            downloaded += 1
        else:
            print("  [WARN] File not found after download completion.")
            errors += 1

    print(f"\n=== Process Complete: {downloaded} downloaded | {skipped} skipped | {errors} errors ===")
