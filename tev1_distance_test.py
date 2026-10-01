import requests
import time

URL = "http://localhost:11434/v1/systemone"

distances = [400, 300, 250, 200, 150, 100, 50]

for distance in distances:

    payload = {
        "model": "tev1:0.8b",

        "state": {
            "distance": distance,
            "height": 29
        },

        "questions": {
            "action": {
                "type": "choice",
                "instructions": "Choose the next action.",
                "criteria": {
                    "jump": "Jump over the obstacle.",
                    "duck": "Duck.",
                    "wait": "Do nothing."
                }
            }
        }
    }

    start = time.perf_counter()

    response = requests.post(
        URL,
        json=payload,
        timeout=60
    )

    elapsed = (time.perf_counter() - start) * 1000

    result = response.json()

    answer = result["answers"]["action"]

    print(
        f"distance={distance:3} | "
        f"action={answer['choice']:4} | "
        f"confidence={answer['confidence']:.3f} | "
        f"{elapsed:.0f} ms"
    )