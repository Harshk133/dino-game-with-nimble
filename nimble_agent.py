# import requests
# import json
# import time

# from detect import get_game_state


# OLLAMA_URL = "http://localhost:11434/v1/systemone"
# MODEL = "nimble"


# def ask_nimble(game_state):

#     payload = {
#         "model": MODEL,

#         "state": {
#             "game": "Chrome Dino",

#             "dino": {
#                 "on_ground": True,
#                 "jumping": False
#             },

#             "obstacle_detected": game_state["obstacle_detected"],

#             "obstacle": game_state.get(
#                 "obstacle",
#                 None
#             )
#         },

#         "questions": {
#             "action": {
#                 "type": "choice",

#                 "instructions":
#                     "Choose the safest action for the dinosaur.",

#                 "criteria": {
#                     "jump":
#                         "Jump over the approaching cactus.",

#                     "duck":
#                         "Duck under the obstacle.",

#                     "wait":
#                         "Do nothing and continue running."
#                 }
#             }
#         }
#     }

#     start = time.perf_counter()

#     response = requests.post(
#         OLLAMA_URL,
#         json=payload,
#         timeout=10
#     )

#     elapsed = (
#         time.perf_counter() - start
#     ) * 1000

#     response.raise_for_status()

#     data = response.json()

#     action = (
#         data["answers"]["action"]["choice"]
#     )

#     return action, elapsed, data


# print("Nimble Dino Agent")
# print("=================")
# print("Press Ctrl+C to stop.\n")


# while True:

#     state = get_game_state()

#     # Don't ask Nimble when there is no obstacle.
#     if not state["obstacle_detected"]:

#         print("No obstacle")

#         time.sleep(0.1)

#         continue

#     obstacle = state["obstacle"]

#     distance = obstacle["distance"]

#     print(
#         f"Obstacle detected | "
#         f"distance={distance}"
#     )

#     # Only ask Nimble when the obstacle
#     # is reasonably close.
#     if distance <= 300:

#         try:

#             action, latency, raw = ask_nimble(
#                 state
#             )

#             print(
#                 f"Nimble → {action} "
#                 f"({latency:.0f} ms)"
#             )

#         except Exception as e:

#             print(
#                 "Nimble error:",
#                 e
#             )

#             time.sleep(1)

#     time.sleep(0.1)

import requests
import time
from detect import get_game_state

URL = "http://localhost:11434/v1/systemone"
MODEL = "nimble"


def ask_nimble(state):
    payload = {
        "model": MODEL,

        "state": state,

        "questions": {
            "action": {
                "type": "choice",
                "instructions": "What should the dinosaur do next?",
                "criteria": {
                    "jump": "Jump over the cactus.",
                    "duck": "Duck under the cactus.",
                    "wait": "Do nothing."
                }
            }
        }
    }

    print("\n🧠 Calling Nimble...", flush=True)

    start = time.perf_counter()

    response = requests.post(
        URL,
        json=payload,
        timeout=180
    )

    elapsed = (time.perf_counter() - start) * 1000

    print(
        f"🧠 Nimble response: {response.status_code} "
        f"({elapsed:.0f} ms)",
        flush=True
    )

    result = response.json()

    answer = result["answers"]["action"]

    choice = answer["choice"]
    confidence = answer["confidence"]

    print(
        f"👉 Nimble: {choice.upper()} "
        f"| confidence={confidence:.2f} "
        f"| {elapsed:.0f} ms",
        flush=True
    )

    return choice


print("🚀 Nimble Dino Agent Started")
print("Press Ctrl+C to stop\n")

while True:

    state = get_game_state()

    if state["obstacle_detected"]:

        obstacle = state["obstacle"]

        distance = obstacle["distance"]

        print(
            f"Obstacle | "
            f"distance={distance} | "
            f"height={obstacle['height']} | "
            f"width={obstacle['width']}",
            flush=True
        )

        if distance <= 300:

            action = ask_nimble({
                "game": "Chrome Dino",

                "dino": {
                    "on_ground": True,
                    "jumping": False
                },

                "obstacle_detected": True,

                "obstacle": {
                    "type": "cactus",
                    "distance": distance,
                    "height": obstacle["height"],
                    "width": obstacle["width"]
                }
            })

    else:

        print("No obstacle", flush=True)

    time.sleep(0.03)