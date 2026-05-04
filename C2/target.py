"""
target.py — Run on the machine connected to the target drone.
Listens for commands relayed from commander.py and executes them.
"""

import socket
import time
from djitellopy import Tello

target_DRONE_IP = "192.168.1.102"   # target drone IP
RELAY_PORT        = 9000

# --- Listen socket ---
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(("0.0.0.0", RELAY_PORT))
server.settimeout(30)   # seconds to wait for next command before giving up

# --- Connect target drone ---
target = Tello(target_DRONE_IP)
target.connect()
print(f"[target] Battery: {target.get_battery()}%")
print(f"[target] Listening on port {RELAY_PORT} ...")

# --- Command dispatch table ---
# Maps string names → bound Tello methods that accept integer args
COMMANDS = {
    "takeoff":                    target.takeoff,
    "land":                       target.land,
    "move_up":                    target.move_up,
    "move_down":                  target.move_down,
    "move_forward":               target.move_forward,
    "move_back":                  target.move_back,
    "move_left":                  target.move_left,
    "move_right":                 target.move_right,
    "rotate_clockwise":           target.rotate_clockwise,
    "rotate_counter_clockwise":   target.rotate_counter_clockwise,
    "flip_forward":               target.flip_forward,
    "flip_back":                  target.flip_back,
}

# --- Receive loop ---
while True:
    try:
        data, addr = server.recvfrom(1024)
        parts = data.decode().split(":")
        cmd, args = parts[0], [int(a) for a in parts[1:]]

        if cmd not in COMMANDS:
            print(f"[target] Unknown command: {cmd}")
            continue

        print(f"[target] Executing: {cmd}({', '.join(str(a) for a in args)})")
        COMMANDS[cmd](*args)
        time.sleep(0.1)

        if cmd == "land":
            print("[target] Landed. Exiting.")
            break

    except socket.timeout:
        print("[target] Timeout — no command received. Landing for safety.")
        target.land()
        break
    except Exception as e:
        print(f"[target] Error: {e}. Landing for safety.")
        target.land()
        break

server.close()
target.end()
