import pyautogui
import requests
import time

from detect import get_game_state


# ============================================================
# SETTINGS
# ============================================================

OLLAMA_URL = "http://localhost:11434/v1/systemone"
MODEL = "tev1:4b-q4_K_M"

# Tev1 is called only when obstacle is inside this range
DECISION_DISTANCE = 300

# Don't ask Tev1 repeatedly for the same obstacle
DECISION_COOLDOWN = 1.5

# Prevent accidental repeated jumps
JUMP_COOLDOWN = 0.8


last_decision_time = 0
last_jump_time = 0


# ============================================================
# ASK TEV1
# ============================================================

def ask_tev1(distance, height, width):

    payload = {
        "model": MODEL,

        "state": {
            "game": "Chrome Dino",

            "dino": {
                "on_ground": True,
                "jumping": False
            },

            "obstacle": {
                "type": "cactus",
                "distance": distance,
                "height": height,
                "width": width
            }
        },

        "questions": {
            "action": {
                "type": "choice",

                "instructions": (
                    "Choose the safest next action for the Chrome Dino. "
                    "If a cactus is approaching, choose jump. "
                    "Choose wait only when there is enough distance."
                ),

                "criteria": {
                    "jump": "Jump over the cactus.",
                    "duck": "Duck under the cactus.",
                    "wait": "Do nothing."
                }
            }
        }
    }

    print("🧠 Asking Tev1...")

    start = time.perf_counter()

    try:

        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=10
        )

        elapsed = (time.perf_counter() - start) * 1000

        if response.status_code != 200:

            print(
                f"❌ Tev1 HTTP error: "
                f"{response.status_code}"
            )

            return "wait"

        result = response.json()

        answer = result["answers"]["action"]

        action = answer["choice"]
        confidence = answer["confidence"]

        print(
            f"🧠 Tev1 → {action.upper()} "
            f"| confidence={confidence:.3f} "
            f"| {elapsed:.0f} ms"
        )

        return action

    except Exception as e:

        print(f"❌ Tev1 error: {e}")

        return "wait"


# ============================================================
# JUMP
# ============================================================

def jump():

    global last_jump_time

    now = time.perf_counter()

    if now - last_jump_time < JUMP_COOLDOWN:
        return

    pyautogui.press("space")

    last_jump_time = now

    print(">>> JUMP")


# ============================================================
# MAIN LOOP
# ============================================================

print("===================================")
print("   TEV1 CHROME DINO CONTROLLER")
print("===================================")

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
    height = obstacle["height"]
    width = obstacle["width"]

    print(
        f"Obstacle | "
        f"distance={distance} | "
        f"height={height} | "
        f"width={width}"
    )

    now = time.perf_counter()

    # --------------------------------------------------------
    # ASK TEV1
    # --------------------------------------------------------

    if (
        distance <= DECISION_DISTANCE
        and
        now - last_decision_time >= DECISION_COOLDOWN
    ):

        last_decision_time = now

        action = ask_tev1(
            distance,
            height,
            width
        )

        # ----------------------------------------------------
        # EXECUTE TEV1 DECISION
        # ----------------------------------------------------

        if action == "jump":

            jump()

        elif action == "duck":

            print(">>> DUCK")

            pyautogui.keyDown("down")

            time.sleep(0.3)

            pyautogui.keyUp("down")

        else:

            print(">>> WAIT")

    time.sleep(0.01)