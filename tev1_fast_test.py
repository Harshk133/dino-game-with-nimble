import requests
import time

URL = "http://localhost:11434/v1/systemone"

payload = {
    "model": "tev1:4b-q4_K_M",

    "state": {
        "distance": 180,
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

print("Testing fast Tev1 request...\n")

start = time.perf_counter()

response = requests.post(
    URL,
    json=payload,
    timeout=60
)

elapsed = (time.perf_counter() - start) * 1000

print(f"HTTP status: {response.status_code}")
print(f"Response time: {elapsed:.0f} ms")
print()
print(response.text)