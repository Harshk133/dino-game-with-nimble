import pyautogui
import time

from detect import get_game_state


# -----------------------------
# SETTINGS
# -----------------------------

JUMP_DISTANCE = 180

JUMP_COOLDOWN = 0.8

last_jump_time = 0


# -----------------------------
# JUMP
# -----------------------------

def jump():

    global last_jump_time

    now = time.perf_counter()

    if now - last_jump_time < JUMP_COOLDOWN:
        return

    pyautogui.press("space")

    last_jump_time = now

    print(">>> JUMP")


# -----------------------------
# MAIN LOOP
# -----------------------------

print("Dino controller starting...")
print("Focus Chrome Dino window.")
print("Starting in 3 seconds...")

time.sleep(3)

print("GO!\n")


while True:

    state = get_game_state()

    if not state["obstacle_detected"]:

        time.sleep(0.01)
        continue

    obstacle = state["obstacle"]

    distance = obstacle["distance"]

    print(
        f"Obstacle | "
        f"distance={distance} | "
        f"height={obstacle['height']} | "
        f"width={obstacle['width']}"
    )

    if distance <= JUMP_DISTANCE:

        jump()

    # time.sleep(0.01)