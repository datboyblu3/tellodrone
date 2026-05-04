"""
follower.py — Run on the machine connected to the FOLLOWER drone.
Listens for commands relayed from commander.py and executes them.
"""

import socket
import time
from djitellopy import Tello

FOLLOWER_DRONE_IP = "192.168.1.102"   # follower drone IP
RELAY_PORT        = 9000

# --- Listen socket ---
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(("0.0.0.0", RELAY_PORT))
server.settimeout(30)   # seconds to wait for next command before giving up

# --- Connect follower drone ---
follower = Tello(FOLLOWER_DRONE_IP)
follower.connect()
print(f"[FOLLOWER] Battery: {follower.get_battery()}%")
print(f"[FOLLOWER] Listening on port {RELAY_PORT} ...")

# --- Command dispatch table ---
# Maps string names → bound Tello methods that accept integer args
COMMANDS = {
    "takeoff":                    follower.takeoff,
    "land":                       follower.land,
    "move_up":                    follower.move_up,
    "move_down":                  follower.move_down,
    "move_forward":               follower.move_forward,
    "move_back":                  follower.move_back,
    "move_left":                  follower.move_left,
    "move_right":                 follower.move_right,
    "rotate_clockwise":           follower.rotate_clockwise,
    "rotate_counter_clockwise":   follower.rotate_counter_clockwise,
    "flip_forward":               follower.flip_forward,
    "flip_back":                  follower.flip_back,
}

# --- Receive loop ---
while True:
    try:
        data, addr = server.recvfrom(1024)
        parts = data.decode().split(":")
        cmd, args = parts[0], [int(a) for a in parts[1:]]

        if cmd not in COMMANDS:
            print(f"[FOLLOWER] Unknown command: {cmd}")
            continue

        print(f"[FOLLOWER] Executing: {cmd}({', '.join(str(a) for a in args)})")
        COMMANDS[cmd](*args)
        time.sleep(0.1)

        if cmd == "land":
            print("[FOLLOWER] Landed. Exiting.")
            break

    except socket.timeout:
        print("[FOLLOWER] Timeout — no command received. Landing for safety.")
        follower.land()
        break
    except Exception as e:
        print(f"[FOLLOWER] Error: {e}. Landing for safety.")
        follower.land()
        break

server.close()
follower.end()
