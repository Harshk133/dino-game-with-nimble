import requests
import pyautogui
import time

OLLAMA_URL = "http://localhost:11434/v1/systemone"


def ask_nimble(distance, obstacle_height):

    payload = {
        "model": "nimble",

        "state": {
            "game": "Chrome Dino",

            "dino": {
                "on_ground": True,
                "jumping": False
            },

            "obstacle": {
                "type": "cactus",
                "distance": distance,
                "height": obstacle_height
            }
        },

        "questions": {
            "action": {
                "type": "choice",

                "instructions":
                    "What should the dinosaur do next?",

                "criteria": {
                    "jump": "Jump over the obstacle.",
                    "duck": "Duck under the obstacle.",
                    "wait": "Do nothing."
                }
            }
        }
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=5
    )

    data = response.json()

    action = data["answers"]["action"]["choice"]

    return action


while True:

    distance = int(input("Obstacle distance: "))

    action = ask_nimble(
        distance,
        40
    )

    print("Nimble:", action)

    if action == "jump":

        pyautogui.press("space")

    elif action == "duck":

        pyautogui.keyDown("down")

        time.sleep(0.2)

        pyautogui.keyUp("down")

    time.sleep(0.1)