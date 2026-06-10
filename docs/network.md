# 🌐 Network, IP Addresses & Remote Access

This document describes how the server communicates with the internet
and how remote access is configured.

## Local Network (Subnet)

The router and server use the standard `192.168.1.x` addressing.

- **Gateway (Movistar Router):** `192.168.1.1`
- **Proxmox Host:** `192.168.1.10`

> A migration to `192.168.50.0/24` was evaluated to avoid VPN IP
> conflicts, but abandoned due to the number of already-configured
> physical devices on the current subnet.

## Remote Access — WireGuard VPN (Node 102)

WireGuard provides encrypted remote access via `vpn.address.com`.
A custom Bash script keeps the DDNS record updated automatically
when the home IP address changes.

**Why WireGuard over other VPNs:**
- Minimal attack surface (small codebase)
- Significantly faster than OpenVPN
- Native kernel integration on Linux

## DNS-level Ad Blocking — AdGuard Home (Node 104)

AdGuard Home acts as the primary DNS server for the entire network,
blocking ads and telemetry before they reach any device.

- IPv6 explicitly disabled to prevent DNS leakage through secondary routes
- Positioned upstream of all devices — no per-device configuration needed
