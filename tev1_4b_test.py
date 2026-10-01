import requests
import time

URL = "http://localhost:11434/v1/systemone"
MODEL = "tev1:4b-q4_K_M"

payload = {
    "model": MODEL,

    "state": {
        "distance": 180,
        "height": 29,
        "width": 10
    },

    "questions": {
        "action": {
            "type": "choice",
            "instructions": "Choose the next action.",
            "criteria": {
                "jump": "Jump over the obstacle.",
                "duck": "Duck under the obstacle.",
                "wait": "Do nothing."
            }
        }
    }
}

print("=" * 45)
print("       TEV1 4B Q4_K_M BENCHMARK")
print("=" * 45)
print()
print(f"Model: {MODEL}")
print("Sending request to Tev1...")
print("Waiting for response...\n")

start = time.perf_counter()

try:

    response = requests.post(
        URL,
        json=payload,
        timeout=120
    )

    elapsed = (time.perf_counter() - start) * 1000

    print(f"HTTP status: {response.status_code}")
    print(f"Response time: {elapsed:.0f} ms")
    print()

    print("Raw response:")
    print(response.text)

    if response.status_code == 200:

        result = response.json()

        answer = result["answers"]["action"]

        print()
        print("=" * 45)
        print("RESULT")
        print("=" * 45)

        print(f"Action     : {answer['choice']}")
        print(f"Confidence : {answer['confidence']:.4f}")

        print("\nProbabilities:")

        for action, probability in answer["probabilities"].items():
            print(f"  {action:6} : {probability:.4f}")

        print()
        print(f"Latency    : {elapsed:.0f} ms")

except Exception as e:

    elapsed = (time.perf_counter() - start) * 1000

    print()
    print(f"ERROR after {elapsed:.0f} ms:")
    print(e)