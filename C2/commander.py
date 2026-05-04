"""
commander.py — Run on the machine connected to the COMMANDER drone.
Sends flight commands and relays them to the follower via UDP.
"""

import socket
import time
from djitellopy import Tello

TARGET_IP   = "192.168.1.102"   # machine running follower.py
RELAY_PORT    = 9000
COMMANDER_IP  = "192.168.1.101"   # commander drone IP

# --- Relay socket (UDP) ---
relay = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send(cmd: str, *args):
    """Execute command on commander and relay it to follower."""
    # Build a colon-delimited message: "cmd:arg1:arg2"
    message = ":".join([cmd] + [str(a) for a in args])
    relay.sendto(message.encode(), (FOLLOWER_IP, RELAY_PORT))
    print(f"[COMMANDER] Sending: {message}")

    # Execute locally on commander drone
    method = getattr(commander, cmd)
    method(*args)
    time.sleep(0.1)   # small gap to avoid SDK flooding

# --- Connect commander drone ---
commander = Tello(COMMANDER_IP)
commander.connect()
print(f"[COMMANDER] Battery: {commander.get_battery()}%")

# --- Mission ---
send("takeoff")
time.sleep(3)

send("move_up", 50)
time.sleep(2)

send("move_forward", 60)
time.sleep(2)

send("rotate_clockwise", 90)
time.sleep(2)

send("move_back", 60)
time.sleep(2)

send("rotate_counter_clockwise", 90)
time.sleep(2)

send("land")

relay.close()
commander.end()
print("[COMMANDER] Mission complete.")
