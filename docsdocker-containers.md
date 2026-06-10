# 🐳 Docker & App Stack (Node 109)

Docker runs inside LXC node 109 and hosts multiple applications
via a single `docker-compose.yml` file.

## The Arr-Stack

Automated pipeline for fetching, categorizing, and managing
TV shows and movies. All containers communicate via an internal
Docker network.

| Service       | Role                                                        |
|---------------|-------------------------------------------------------------|
| Prowlarr      | Indexer manager — searches torrent sources                  |
| Jackett       | Additional indexer proxy for legacy torrent sites           |
| FlareSolverr  | Bypasses Cloudflare anti-bot protection on torrent sites    |
| Sonarr        | Monitors and auto-downloads TV shows                        |
| Radarr        | Monitors and auto-downloads movies                          |
| qBittorrent   | Torrent download client                                     |
| JDownloader2  | Direct HTTP download client (for non-torrent sources)       |

## Key Design Decisions

### DNS Override (1.1.1.1 / 8.8.8.8)
Containers use public DNS instead of the local AdGuard instance.
Torrent trackers are frequently blocked by DNS sinkholes —
bypassing AdGuard ensures these specific services reach the internet.
All other nodes still route through AdGuard.

### Shared Volume & Hardlinks
All containers mount the same `/data` directory.
This allows the filesystem to use **hardlinks**: a single physical
file accessible from multiple paths simultaneously.

**Problem solved:** The 500GB SSD was reaching 0 bytes free because
Sonarr/Radarr were copying files from the download folder into the
media library — doubling disk usage. With hardlinks, no data is
duplicated. The same file is visible in both locations, saving
hundreds of gigabytes.

### External SSD — Persistent Mount via UUID
The 500GB media drive is mounted using its UUID in `/etc/fstab`
rather than its device path (`/dev/sdb`).

**Why:** Device paths change if the drive is unplugged and
re-detected (`sdb` → `sdc`), which crashed the stack.
UUID-based mounting makes the path permanent and fault-tolerant.

## Planned

- Homepage dashboard for unified access to all services
  without memorizing IP addresses and ports.
