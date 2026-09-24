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

## 🚀 1-Click Setup in Dockge (No SSH Needed)

To deploy this server directly inside the **Dockge Web UI**:

1. Open your Dockge web interface (`http://<server-ip>:5001`).
2. Click **+ Compose** in the top navigation.
3. Set **Stack Name** to `valheim-server` (or `valheim`).
4. Paste the following YAML directly into the Dockge editor:

```yaml
services:
  valheim:
    image: ghcr.io/community-valheim-tools/valheim-server:latest
    container_name: valheim-server
    cap_add:
      - sys_nice
    network_mode: host
    environment:
      - SERVER_NAME=ValheimHard
      - WORLD_NAME=valheimhard
      - SERVER_PASS=12345
      - SERVER_PUBLIC=true
      - TZ=Africa/Johannesburg
      - CROSSPLAY=false
      - BACKUPS=true
      - UPDATE_CRON=0 4 * * *
      - RESTART_CRON=0 5 * * *
      - SERVER_ARGS=-preset hard
      - BEPINEX=true
      # Automatically downloads and restores world save + BepInEx mods on first launch if /config is empty
      - PRE_BOOTSTRAP_HOOK=[ ! -d /config/worlds_local/valheimhard ] && echo "Downloading Valheim world and mods from GitHub..." && curl -fsSL https://github.com/LukeKappa/valheim-backup/releases/download/v2026.09.24/valheim-server-config.tar.gz | tar -xz -C /config
      - PRE_BEPINEX_CONFIG_HOOK=[ -n "$$plugins_path" ] && mkdir -p "$$plugins_path"
      - PRE_SERVER_RUN_HOOK=mkdir -p /opt/valheim/bepinex/BepInEx/plugins && [ -d /config/bepinex/plugins ] && rsync -a --delete /config/bepinex/plugins/ /opt/valheim/bepinex/BepInEx/plugins/
    volumes:
      - ./config:/config
      - ./data:/opt/valheim
    restart: unless-stopped
    stop_grace_period: 2m
```

5. Click **Deploy**.

#### How it works:
- On the very first run, the container detects that `./config` is empty on the new PC.
- It automatically downloads `valheim-server-config.tar.gz` from GitHub, extracting your **world save (`valheimhard`)**, **BepInEx plugins (`Jotunn`, `ValheimCommunityPatch`, `NetworkPerformanceSystem`)**, and all configuration files directly into `./config`.
- SteamCMD downloads the game binaries into `./data`.
- For all future restarts, `./config` already has your world and files saved locally, so it never downloads again and writes all progress straight to your disk.

---

## Alternative: Standard CLI Deploy

If you prefer standard Docker Compose via terminal:

```bash
git clone https://github.com/LukeKappa/valheim-backup.git valheim-server
cd valheim-server
docker compose up -d
```

---

## Auto-Pause & Auto-Wake Daemon (Optional)

The included `valheim-autopause.py` script automatically pauses the Docker container when 0 players have been connected for 15 minutes, and instantly wakes it up when an incoming UDP packet hits game port 2456.

```bash
mkdir -p ~/.config/systemd/user/
cp valheim-autopause.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now valheim-autopause.service
```

---

## Laptop Server (Lid Close Settings)

If running the server on a laptop that you want to keep closed without sleeping:
```bash
chmod +x setup-lid.sh
sudo ./setup-lid.sh
```
