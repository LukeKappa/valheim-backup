#!/bin/bash
# Auto-updater for Valheim BepInEx plugins (Jotunn, ValheimCommunityPatch, NetworkPerformanceSystem)
set -u

CONFIG_PLUGINS_DIR="/config/bepinex/plugins"
PLUGINS_DIR="/opt/valheim/bepinex/BepInEx/plugins"
mkdir -p "$CONFIG_PLUGINS_DIR" "$PLUGINS_DIR"

echo "Checking for BepInEx mod updates from GitHub..."

# 1. Jotunn
JOTUNN_URL=$(curl -fsSL https://api.github.com/repos/Valheim-Modding/Jotunn/releases/latest 2>/dev/null | jq -r '.assets[]? | select(.name == "Jotunn.dll") | .browser_download_url' 2>/dev/null)
if [ -n "$JOTUNN_URL" ]; then
    mkdir -p "$CONFIG_PLUGINS_DIR/Jotunn"
    if curl -fsSL "$JOTUNN_URL" -o "$CONFIG_PLUGINS_DIR/Jotunn/Jotunn.dll" 2>/dev/null; then
        echo "✓ Jotunn is up to date"
    fi
fi

# 2. ValheimCommunityPatch
VCP_URL=$(curl -fsSL https://api.github.com/repos/MidnightsFX/Valheim-Community-Patch/releases/latest 2>/dev/null | jq -r '.assets[]? | select(.name | endswith(".zip")) | .browser_download_url' 2>/dev/null)
if [ -n "$VCP_URL" ]; then
    mkdir -p "$CONFIG_PLUGINS_DIR/ValheimCommunityPatch" /tmp/vcp
    if curl -fsSL "$VCP_URL" -o /tmp/vcp/vcp.zip 2>/dev/null; then
        unzip -qo /tmp/vcp/vcp.zip -d /tmp/vcp/ 2>/dev/null || true
        if [ -f /tmp/vcp/plugins/ValheimCommunityPatch.dll ]; then
            cp -f /tmp/vcp/plugins/ValheimCommunityPatch.dll "$CONFIG_PLUGINS_DIR/ValheimCommunityPatch/"
            echo "✓ ValheimCommunityPatch is up to date"
        fi
        rm -rf /tmp/vcp
    fi
fi

# 3. NetworkPerformanceSystem
NPS_URL=$(curl -fsSL https://api.github.com/repos/MidnightsFX/Valheim-Network-Performance-System/releases/latest 2>/dev/null | jq -r '.assets[]? | select(.name | endswith(".zip")) | .browser_download_url' 2>/dev/null)
if [ -n "$NPS_URL" ]; then
    mkdir -p "$CONFIG_PLUGINS_DIR/NetworkPerformanceSystem" /tmp/nps
    if curl -fsSL "$NPS_URL" -o /tmp/nps/nps.zip 2>/dev/null; then
        unzip -qo /tmp/nps/nps.zip -d /tmp/nps/ 2>/dev/null || true
        if [ -f /tmp/nps/plugins/NetworkPerformanceSystem.dll ]; then
            cp -f /tmp/nps/plugins/NetworkPerformanceSystem.dll "$CONFIG_PLUGINS_DIR/NetworkPerformanceSystem/"
            echo "✓ NetworkPerformanceSystem is up to date"
        fi
        rm -rf /tmp/nps
    fi
fi

# Sync config plugins to BepInEx runtime plugins
if [ -d "$CONFIG_PLUGINS_DIR" ]; then
    rsync -a --delete "$CONFIG_PLUGINS_DIR/" "$PLUGINS_DIR/"
fi
echo "BepInEx plugins synced successfully."
