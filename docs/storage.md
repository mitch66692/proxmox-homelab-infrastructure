# 💾 Storage, Disks & Media Management

## Physical Disks

| Disk         | Mount Point          | Use                              |
|--------------|----------------------|----------------------------------|
| NVMe 2TB     | `/mnt/pve/storage2tb`| Immich photo database & app data |
| SSD 500GB    | `/data`              | Movies, TV shows, downloads      |

### NVMe 2TB
Used for Immich (self-hosted Google Photos alternative).
Permissions set to UID/GID `1000:1000` to allow LXC containers
to write without permission errors.

### SSD 500GB (USB)
Dedicated to the media library.
Mounted via UUID in `/etc/fstab` for fault-tolerant persistence.

**Problem solved:** The drive was remounting under a different
device path (`/dev/sdb` → `/dev/sdc`) after a brief disconnect,
causing the entire stack to crash. UUID-based mounting eliminates
this — the system identifies the disk by its unique identity,
not its port position.

## Automated Audio Sync — SpotDL (Node 103)

A custom Python script (`scripts/spotify_sync.py`) runs nightly
via cron at 03:00, launched by `scripts/run_sync.sh`.

**Pipeline:**
1. Fetches playlist data via a custom Spotify scraper
2. Downloads audio from YouTube via `yt-dlp`
3. Queries the iTunes API for high-resolution cover art
4. Injects ID3 tags (artist, title, artwork) via `mutagen`
5. Skips already-downloaded tracks via deduplication logic

**Storage:** All files saved flat in `/root/Music/` — no subfolders.

> ⚠️ **Do not restructure into subfolders.**
> Deduplication is based on filenames in a flat directory.
> Reorganizing would cause the entire library to re-download.

### Critical yt-dlp flags
Recent YouTube bot-detection requires a JavaScript runtime.
Without these flags the script fails silently:

```bash
--js-runtimes node:/usr/bin/node
--remote-components ejs:github
```

## Immich Backup Strategy

Two-layer backup to Infomaniak kDrive via WebDAV/rclone:

1. **Media files** — synced via rclone
2. **PostgreSQL database dumps** — scheduled export + sync

> Both layers are required. Syncing only media files would lose
> all albums, metadata, and sharing configuration stored in the DB.
