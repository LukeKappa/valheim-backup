#!/usr/bin/env bash
set -e

echo "Configuring systemd-logind to ignore laptop lid close..."
mkdir -p /etc/systemd/logind.conf.d

cat << 'INNER_EOF' > /etc/systemd/logind.conf.d/lid.conf
[Login]
HandleLidSwitch=ignore
HandleLidSwitchExternalPower=ignore
HandleLidSwitchDocked=ignore
INNER_EOF

echo "Reloading systemd-logind configuration..."
systemctl kill -s HUP systemd-logind

echo "Done! Verifying active settings:"
loginctl show-session | grep -E "HandleLidSwitch" || true
echo "Success: Laptop will now stay awake at full performance with lid closed."
