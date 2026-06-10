# 🖥️ Proxmox, LXC Containers & Virtual Machines

Proxmox VE is the hypervisor installed on the physical machine.
It divides hardware resources (CPU, RAM, storage) into isolated nodes.

## VM vs LXC — Key Difference

- **VM (Virtual Machine):** Allocates a dedicated slice of RAM exclusively.
  Used when full hardware isolation is needed (e.g., USB passthrough).
- **LXC (Linux Container):** Shares the host kernel — significantly lighter.
  RAM limit acts as a safety ceiling, not a reservation.

## Node Map

| ID  | Name        | Type | Role                                              |
|-----|-------------|------|---------------------------------------------------|
| 100 | Immich      | LXC  | Self-hosted photo management (Google Photos alt.) |
| 101 | Plex        | LXC  | Personal media server                             |
| 102 | WG-Easy     | LXC  | WireGuard VPN                                     |
| 103 | SpotDL      | LXC  | Automated audio sync from Spotify/YouTube         |
| 104 | AdGuard     | LXC  | Network-wide DNS ad blocking                      |
| 105 | HAOS        | VM   | Home Assistant OS (requires USB passthrough)      |
| 106 | Frigate     | LXC  | AI video surveillance (Docker inside LXC)         |
| 107 | UptimeKuma  | LXC  | Uptime monitoring and alerting                    |
| 109 | Docker/Arr  | LXC  | Media automation stack (Docker Compose)           |
| 110 | Tududi      | LXC  | Self-hosted task manager                          |

## Why Home Assistant runs as a VM

HAOS requires direct USB access for Zigbee/Z-Wave dongles.
LXC containers cannot pass through USB devices at the kernel level —
a full VM is the only supported path for HAOS.

