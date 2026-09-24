#!/usr/bin/env python3
"""
Valheim Auto-Pause & Auto-Wake Daemon
- Pauses the Valheim container when 0 players are connected for IDLE_MINUTES.
- Instantly wakes (unpauses) the container when an incoming UDP packet arrives on 2456/2457.
"""

import os
import sys
import time
import socket
import subprocess

CONTAINER_NAME = "valheim-server"
IDLE_MINUTES = int(os.environ.get("IDLE_MINUTES", "15"))
IDLE_TIMEOUT_SECS = IDLE_MINUTES * 60
CHECK_INTERVAL_SECS = 20
# Only monitor game port 2456 (0x0998). Port 2457 (0x0999) receives constant
# public Steam server browser / master server pings which cause false wake-ups.
PORTS_HEX = {"0998"}

def log(msg):
    t = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{t}] {msg}", flush=True)

def get_container_status():
    try:
        r = subprocess.run(["docker", "inspect", "-f", "{{.State.Status}}", CONTAINER_NAME],
                           capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            return r.stdout.strip()
    except Exception:
        pass
    return "unknown"
def pause_container():
    log(f"💤 No players for {IDLE_MINUTES}m. Pausing {CONTAINER_NAME} to save CPU & power...")
    subprocess.run(["docker", "pause", CONTAINER_NAME], check=False)
    time.sleep(1.0)

def unpause_container(reason="incoming connection packet"):
    log(f"⚡ Waking up {CONTAINER_NAME} ({reason})...")
    subprocess.run(["docker", "unpause", CONTAINER_NAME], check=False)

def query_players():
    """Queries Valheim via Steam A2S_INFO on 127.0.0.1:2457."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(2.0)
    query = b"\xff\xff\xff\xffTSource Engine Query\x00"
    try:
        s.sendto(query, ("127.0.0.1", 2457))
        data, _ = s.recvfrom(4096)
        if len(data) > 5 and data[4] == 0x41: # Challenge
            challenge = data[5:9]
            s.sendto(query + challenge, ("127.0.0.1", 2457))
            data, _ = s.recvfrom(4096)
        
        if len(data) > 6 and data[4] == 0x49: # 'I'
            pos = 6
            for _ in range(4): # name, map, folder, game
                end = data.find(b"\x00", pos)
                if end == -1: return None
                pos = end + 1
            pos += 2 # appid
            players = data[pos]
            max_players = data[pos + 1]
            return players, max_players
    except Exception:
        return None
    finally:
        s.close()
    return None

def get_rx_queue():
    """Returns total bytes in kernel receive queues for ports 2456 and 2457."""
    total = 0
    for p in ("/proc/net/udp", "/proc/net/udp6"):
        try:
            with open(p, "r") as f:
                next(f)
                for line in f:
                    parts = line.split()
                    if len(parts) >= 5:
                        port_hex = parts[1].split(":")[1].upper()
                        if port_hex in PORTS_HEX:
                            rx = int(parts[4].split(":")[1], 16)
                            total += rx
        except Exception:
            pass
    return total

def main():
    log(f"🚀 Valheim Auto-Pause daemon started (idle threshold: {IDLE_MINUTES} minutes)")
    
    idle_time = 0
    while True:
        status = get_container_status()
        if status == "running":
            res = query_players()
            if res is not None:
                players, max_p = res
                if players > 0:
                    if idle_time > 0:
                        log(f"🎮 Player active ({players}/{max_p}). Resetting idle timer.")
                        idle_time = 0
                else:
                    idle_time += CHECK_INTERVAL_SECS
                    if idle_time % 300 == 0 or idle_time == CHECK_INTERVAL_SECS:
                        log(f"⏳ Server empty (0 players). Idle for {idle_time // 60}m / {IDLE_MINUTES}m")
                    
                    if idle_time >= IDLE_TIMEOUT_SECS:
                        pause_container()
                        idle_time = 0
                        continue
            else:
                # If query timed out, server might be loading/busy, don't accumulate idle time
                pass
            
            time.sleep(CHECK_INTERVAL_SECS)

        elif status == "paused":
            # Server is sleeping. Watch rx_queue for any incoming UDP packet!
            initial_queue = get_rx_queue()
            
            while True:
                time.sleep(0.25)
                current_queue = get_rx_queue()
                if current_queue > initial_queue:
                    unpause_container(f"incoming packet on port 2456 (queue: {initial_queue} -> {current_queue})")
                    # Grace period: allow 2 minutes for player to connect and spawn in
                    log("⏳ Waiting 120s grace period for connection to establish...")
                    time.sleep(120)
                    idle_time = 0
                    break
                
                # Verify container wasn't unpaused externally
                st = get_container_status()
                if st != "paused":
                    idle_time = 0
                    break
        else:
            time.sleep(10)

if __name__ == "__main__":
    main()
