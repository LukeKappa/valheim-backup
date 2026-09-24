# Valheim Dedicated Server (`ValheimHard`)

Turnkey Docker configuration, BepInEx mods, and world save backup for the `ValheimHard` dedicated server.

## Overview
- **World Name:** `valheimhard`
- **Server Name:** `ValheimHard`
- **Password:** `12345`
- **Difficulty Preset:** `hard`
- **Network Mode:** `host` (UDP ports 2456-2458)
- **Container Image:** `ghcr.io/community-valheim-tools/valheim-server:latest`
- **Installed BepInEx Plugins:**
  - `ValheimCommunityPatch`
  - `NetworkPerformanceSystem`
  - `Jotunn` (the Valheim Library)

---

## Moving / Running on a New PC

### 1. Prerequisites
Install Docker and the Docker Compose plugin on the target machine:
- **Arch / CachyOS:** `sudo pacman -S docker docker-compose && sudo systemctl enable --now docker`
- **Debian / Ubuntu:** Install docker via official Docker repo or `sudo apt install docker.io docker-compose-v2`
- Add your user to the docker group: `sudo usermod -aG docker $USER` (then log out and back in).

### 2. Clone Repository
```bash
git clone https://github.com/LukeKappa/valheim-backup.git valheim-server
cd valheim-server
```

### 3. Launch Server
```bash
docker compose up -d
```
On first launch, the container will:
1. Automatically download the game server binary via SteamCMD into `./data`.
2. Install BepInEx and sync plugins from `./config/bepinex/plugins/`.
3. Load the world from `./config/worlds_local/valheimhard/`.

Monitor startup logs:
```bash
docker compose logs -f
```

---

## Auto-Pause & Auto-Wake Daemon (Optional)

The included `valheim-autopause.py` script automatically pauses the Docker container when 0 players have been connected for 15 minutes, and instantly wakes it up when an incoming UDP packet hits game port 2456.

### Setup as a Systemd User Service:
1. Ensure the path inside `valheim-autopause.service` matches your directory (default is `/home/luke/Projects/valheim-autopause.py` or update to your new path).
2. Install the service:
   ```bash
   mkdir -p ~/.config/systemd/user/
   cp valheim-autopause.service ~/.config/systemd/user/
   systemctl --user daemon-reload
   systemctl --user enable --now valheim-autopause.service
   ```
3. Check status:
   ```bash
   systemctl --user status valheim-autopause.service
   ```

---

## Laptop Server (Lid Close Settings)

If running the server on a laptop that you want to keep closed without sleeping:
```bash
chmod +x setup-lid.sh
sudo ./setup-lid.sh
```

---

## World Backups

- Active world files are located in `config/worlds_local/valheimhard/`.
- Automatic daily backups are handled by the container into `config/backups/`.
- Standalone zip archive `valheimhard-latest.zip` is included in this repository and attached to the [GitHub Releases](https://github.com/LukeKappa/valheim-backup/releases).
