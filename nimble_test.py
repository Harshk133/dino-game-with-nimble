import requests
import json

url = "http://localhost:11434/v1/systemone"

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
            "distance": 100,
            "height": 40
        }
    },
    "questions": {
        "action": {
            "type": "choice",
            "instructions": "What should the dinosaur do next?",
            "criteria": {
                "jump": "Jump over the cactus.",
                "duck": "Duck under the obstacle.",
                "wait": "Do nothing."
            }
        }
    }
}

response = requests.post(url, json=payload)

print("HTTP:", response.status_code)
print(json.dumps(response.json(), indent=2))