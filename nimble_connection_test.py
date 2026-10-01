import requests
import time
import json

URL = "http://localhost:11434/v1/systemone"

payload = {
    "model": "nimble",

    "state": {
        "game": "Chrome Dino",

        "dino": {
            "on_ground": True,
            "jumping": False
        },

        "obstacle_detected": True,

        "obstacle": {
            "type": "cactus",
            "distance": 200,
            "height": 29,
            "width": 10
        }
    },

    "questions": {
        "action": {
            "type": "choice",

            "instructions":
                "What should the dinosaur do next?",

            "criteria": {
                "jump":
                    "Jump over the cactus.",

                "duck":
                    "Duck under the obstacle.",

                "wait":
                    "Do nothing."
            }
        }
    }
}


print("Sending request to Nimble...")
print("Waiting for response...\n")

start = time.perf_counter()

try:

    response = requests.post(
        URL,
        json=payload,
        timeout=180
    )

    elapsed = (
        time.perf_counter() - start
    ) * 1000

    print(f"HTTP status: {response.status_code}")
    print(f"Response time: {elapsed:.0f} ms")
    print()

    print("Raw response:")
    print(response.text)

except Exception as e:

    elapsed = (
        time.perf_counter() - start
    ) * 1000

    print(f"ERROR after {elapsed:.0f} ms:")
    print(e)