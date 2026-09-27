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
  - `ValheimCommunityPatch` (auto-updated from GitHub)
  - `NetworkPerformanceSystem` (auto-updated from GitHub)
  - `Jotunn` (auto-updated from GitHub)

---

## 🚀 Dockge Deployment

Paste the following YAML directly into your Dockge stack editor:

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
      # Only downloads world save if /config/worlds_local/valheimhard does not exist (never touches existing worlds)
      - PRE_BOOTSTRAP_HOOK=[ ! -d /config/worlds_local/valheimhard ] && echo "Downloading Valheim world and mods from GitHub..." && curl -fsSL https://github.com/LukeKappa/valheim-backup/releases/download/v2026.09.24/valheim-server-config.tar.gz | tar -xz -C /config
      - PRE_BEPINEX_CONFIG_HOOK=[ -n "$$plugins_path" ] && mkdir -p "$$plugins_path"
      # Auto-updater for BepInEx plugins (Jotunn, ValheimCommunityPatch, NetworkPerformanceSystem) on restart (never touches world saves)
      - PRE_SERVER_RUN_HOOK=curl -fsSL https://raw.githubusercontent.com/LukeKappa/valheim-backup/main/config/bepinex/update-mods.sh | bash
    volumes:
      - ./config:/config
      - ./data:/opt/valheim
    restart: unless-stopped
    stop_grace_period: 2m
```

---

## 🔄 How Updates Work

### 1. Game Updates (Base Valheim)
- SteamCMD checks for game updates on **every container restart**, plus daily at 4:00 AM (`UPDATE_CRON`).
- To apply a new game patch: click **Restart** (or **Deploy**) on the stack in Dockge.

### 2. Mod Updates (BepInEx Plugins)
- On every container start/restart, `PRE_SERVER_RUN_HOOK` fetches and executes `update-mods.sh` directly from GitHub.
- It queries GitHub Releases for the latest versions of **Jotunn**, **ValheimCommunityPatch**, and **NetworkPerformanceSystem**, downloads updated `.dll` files into `./config/bepinex/plugins/`, and syncs them to BepInEx before launching the game.
- It **only** touches `./config/bepinex/plugins/` and **never** touches your world save.

### 3. World Save Safety
- The world save in `./config/worlds_local/` is 100% persistent on the host.
- `PRE_BOOTSTRAP_HOOK` has an explicit guard `[ ! -d /config/worlds_local/valheimhard ]` so it will **never** overwrite your active world save.
