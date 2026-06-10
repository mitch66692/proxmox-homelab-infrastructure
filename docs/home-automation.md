# 🏠 Home Automation, Cameras & Security

## Home Assistant (Node 105)

Central hub for all home automation.
Runs as a full VM to allow direct USB passthrough for
Zigbee/Z-Wave dongles — not possible with LXC containers.

**Planned:** Geofencing automations to send Frigate alerts
only when the house is unoccupied.

## AI Video Surveillance — Frigate NVR (Node 106)

Frigate runs inside Docker within LXC node 106.
It performs local AI object detection — no cloud dependency.

- **Version:** v0.16
- **Hardware acceleration:** Intel GPU + OpenVINO
- **Model:** SSDLite MobileNet V2
- **Camera:** Reolink

### Why Docker inside LXC (not a VM)

Frigate needs GPU passthrough for hardware-accelerated inference.
An LXC with Docker gives direct access to the Intel iGPU
without the overhead of full virtualization.

## Problems Solved

### 1. Authentication error after upgrade to v0.16
`config.yml` required updates to match the new authentication
system introduced in v0.16. Updated accordingly.

### 2. ffmpeg crash loop / missed detections
**Root cause:** UDP packet loss on the camera stream, not an
AI configuration issue.

**Fix:**
- Switched detect stream from UDP to TCP
- Added `shm_size: 128mb` for shared memory stability

> Lesson learned: always check stream/network logs before
> tuning AI detection parameters. The problem was upstream.

### 3. False alerts from global illumination changes
Clouds passing, lights switching on/off, and sunrise/sunset
were triggering detections across the entire frame.

**Fix:** Added `lightning_threshold: 0.8` to the global config.
This tells Frigate to ignore frames where overall brightness
changes suddenly.

## Configuration Notes

- Detect stream: **TCP only** (not UDP)
- `shm_size: 128mb`
- `lightning_threshold: 0.8`
- The `stationary` tracking key does **not exist in v0.16** — do not add it

