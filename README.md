# proxmox-homelab-infrastructure
This is my first experience creating a personal homelab to reduce my reliance on big IT services, set up a local media center, and spend the next months testing and learning something I’ve started to enjoy.
This repository documents my personal self-hosted infrastructure. It serves as a testing ground for system administration, containerization, networking, and automation. The environment is built on Proxmox VE, utilizing a mix of Linux Containers (LXC) for lightweight services and Virtual Machines (VMs) for complete hardware isolation.

All the following instructions are for testing use only and have been created using documentation from official an unofficial sources from blog to youtube guides. 

## Documentation

| Document | Description |
|---|---|
| [Network & VPN](./docs/network.md) | Subnet layout, WireGuard, AdGuard DNS |
| [Proxmox Nodes](./docs/proxmox-nodes.md) | Full node map, VM vs LXC explained |
| [Docker Stack](./docs/docker-containers.md) | Arr-stack, hardlinks, volume architecture |
| [Storage & Media](./docs/storage.md) | Disks, UUID mounting, SpotDL pipeline |
| [Home Automation](./docs/home-automation.md) | Frigate NVR, Home Assistant, problems solved |


## Architecture Overview

The hypervisor manages multiple isolated nodes, balancing resources between raw performance (NVMe storage) and bulk media storage.

* Hypervisor: Proxmox VE
* Virtualization: LXC (Linux Containers) for low-overhead apps, VMs for OS-level requirements (e.g., Home Assistant OS).
* Container Engine: Docker & Docker Compose (running inside an unprivileged LXC node).
* Storage:
  * A local mounted SSD with 256GB of storage for images, file system and installations.
  * 2TB NVMe for high-speed database and app data.
  * External SSD mounted via UUID in `fstab` for persistent, fault-tolerant storage.


## Networking & Security

The network is designed to avoid conflicts with standard ISP subnets and to block trackers at the DNS level.

* Subnetting: Network runs on `192.168.1.0/24`. A migration to `192.168.50.0/24` was evaluated to avoid VPN IP conflicts with external networks, but abandoned due to the number of already-configured devices on the existing subnet.
* Remote Access (VPN): Deployed WireGuard as a split-tunnel VPN. Remote access is dynamically maintained via a custom Bash script that updates the DDNS record for my personal domain.
* DNS Sinkhole: AdGuard Home acts as the primary DNS server, blocking ads and telemetry network-wide. IPv6 is explicitly disabled to prevent DNS leakages through secondary routes.

## Key Technical Implementations

### 1. Storage Optimization (Atomic Moves & Hardlinks)
Initially, duplicate files between download directories and media libraries caused disk exhaustion. I restructured the volume mounts into a single unified `/data` directory structure. By configuring Docker containers to share the same underlying volume, the file system now uses Hardlinks. This allows multiple services to access the same physical file across different paths, saving hundreds of gigabytes of storage and eliminating I/O bottlenecks.

### 2. Service Orchestration & Media Automation (Docker)
A dedicated node acts as the Docker engine hosting an automated stack. Services communicate via internal Docker networks.
* Arr-Stack: Automated fetching and categorization.
* Custom Bash Automation: Scheduled cron jobs handle post-processing, utilizing lightweight CLI tools to merge or split media files automatically without heavy UI applications.
 **[View docker-compose docs](./docker-compose.yml)**

### 3. Automated Audio Fetching (Python Integration)
A dedicated LXC node runs a scheduled task to synchronize external playlists. Instead of relying on pre-packaged tools, I developed a custom Python application to manage the entire pipeline.
 **[View Python Audio Automation Script](./scripts/spotify_sync.py)**

* **Features:** It uses a custom scraper to fetch playlist data, orchestrates `yt-dlp` via subprocesses for audio extraction, queries the iTunes API for high-resolution cover art, and utilizes the `mutagen` library to inject ID3 tags directly into the MP3 files. It includes a custom deduplication algorithm to optimize I/O and network bandwidth.

### 4. AI Video Surveillance (Frigate)
Deployed Frigate NVR for local AI object detection.
* Local only security system for a Reolink camera to use at home for security and main entrance surveillance.
* The real challenged was to optimize it for a mini pc like mine with just n150 processor. 

## Monitoring & Dashboarding

* UptimeKuma: Actively monitors the health of all HTTP endpoints and internal Docker containers, sending alerts upon failure.
