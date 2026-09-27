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
      # Set to 'true' in Dockge whenever you want to force sync the latest world save from GitHub, then set back to 'false'
      - FORCE_RESTORE_FROM_GITHUB=false
      # Automatically downloads world save + BepInEx mods on first launch (or when FORCE_RESTORE_FROM_GITHUB=true)
      - PRE_BOOTSTRAP_HOOK=([ "$$FORCE_RESTORE_FROM_GITHUB" = "true" ] || [ ! -d /config/worlds_local/valheimhard ]) && echo "Downloading Valheim world and mods from GitHub..." && curl -fsSL https://github.com/LukeKappa/valheim-backup/releases/download/v2026.09.24/valheim-server-config.tar.gz | tar -xz -C /config
      - PRE_BEPINEX_CONFIG_HOOK=[ -n "$$plugins_path" ] && mkdir -p "$$plugins_path"
      # Auto-updater for BepInEx plugins (Jotunn, ValheimCommunityPatch, NetworkPerformanceSystem) on restart
      - PRE_SERVER_RUN_HOOK=[ -f /config/bepinex/update-mods.sh ] && bash /config/bepinex/update-mods.sh || (mkdir -p /opt/valheim/bepinex/BepInEx/plugins && [ -d /config/bepinex/plugins ] && rsync -a --delete /config/bepinex/plugins/ /opt/valheim/bepinex/BepInEx/plugins/)
    volumes:
      - ./config:/config
      - ./data:/opt/valheim
    restart: unless-stopped
    stop_grace_period: 2m
```

---

## 🔄 Updates & Mod Management

### 1. How Valheim Updates (Base Game)
- The container uses SteamCMD to check for game updates on **every container restart**, plus daily at 4:00 AM (`UPDATE_CRON`).
- To update Valheim when a game patch drops: click **Restart** on the stack in Dockge.

### 2. How Mods Auto-Update
- `PRE_SERVER_RUN_HOOK` executes `update-mods.sh` on every server boot.
- It queries the GitHub Releases API for the latest releases of:
  - `Valheim-Modding/Jotunn`
  - `MidnightsFX/Valheim-Community-Patch`
  - `MidnightsFX/Valheim-Network-Performance-System`
- When newer versions exist, it automatically downloads and replaces the `.dll` files in `./config/bepinex/plugins/` and syncs them to BepInEx before the server starts.

### 3. How to Pull the Latest World Save to Dockge
If you want to pull the latest world save from GitHub onto your Dockge server:
1. In Dockge, edit the stack and change:
   ```yaml
   - FORCE_RESTORE_FROM_GITHUB=true
   ```
2. Click **Deploy** / **Update**. The server boots, downloads the latest world save from GitHub, and restores it into `./config/worlds_local/valheimhard`.
3. Change it back to `FORCE_RESTORE_FROM_GITHUB=false` and Deploy so subsequent restarts keep in-game progress.
