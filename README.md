# Valheim World Backup (`valheimhard`)

Automated and manual backup repository for the dedicated Valheim server.

## World Information
- **World Name:** `valheimhard`
- **Difficulty Preset:** `hard`
- **Server Version:** `1.0.15+` (Valheim post-Ashlands chunked format)
- **Save Generation:** 318
- **Snapshot Date:** 2026-09-24

## Files
- `valheimhard/` - Uncompressed world directory containing chunk files and generation metadata (`_main.318.*`).
- `valheimhard-latest.zip` - Standalone archive of the world folder for quick download and restore.

## How to Restore

### 1. Dedicated Server (Docker)
1. Stop the server container:
   ```bash
   docker stop valheim-server
   ```
2. Place the `valheimhard` folder into your `config/worlds_local/` directory:
   ```bash
   cp -r valheimhard /path/to/server/config/worlds_local/
   ```
3. Ensure proper file ownership and permissions:
   ```bash
   chown -R 1000:1000 /path/to/server/config/worlds_local/valheimhard
   ```
4. Start the server container:
   ```bash
   docker start valheim-server
   ```

### 2. Client / Singleplayer (PC)
- **Linux:** `~/.config/unity3d/IronGate/Valheim/worlds_local/`
- **Windows:** `%USERPROFILE%\AppData\LocalLow\IronGate\Valheim\worlds_local\`
- **macOS:** `~/Library/Application Support/IronGate/Valheim/worlds_local/`

Copy the `valheimhard` directory into `worlds_local/` and launch the game.
