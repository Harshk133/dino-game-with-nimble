import pyautogui
import cv2
import numpy as np
import time

# Screenshot region
GAME_REGION = (400, 330, 850, 170)

# Dino's approximate right edge inside the crop
DINO_RIGHT = 240

# Only search for obstacles in front of Dino
SEARCH_START_X = 250
SEARCH_END_X = 840

# Vertical search area
SEARCH_START_Y = 35
SEARCH_END_Y = 125

# Approximate ground position
GROUND_Y = 135


def detect_obstacle():

    screenshot = pyautogui.screenshot(
        region=GAME_REGION
    )

    frame = np.array(screenshot)

    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_RGB2GRAY
    )

    # Detect dark pixels
    _, threshold = cv2.threshold(
        gray,
        120,
        255,
        cv2.THRESH_BINARY_INV
    )

    # Only search useful gameplay area
    roi = threshold[
        SEARCH_START_Y:SEARCH_END_Y,
        SEARCH_START_X:SEARCH_END_X
    ]

    contours, _ = cv2.findContours(
        roi,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    candidates = []

    for contour in contours:

        x, y, w, h = cv2.boundingRect(contour)

        # Convert ROI coordinates back to game coordinates
        x += SEARCH_START_X
        y += SEARCH_START_Y

        # Ignore small noise
        if w < 5 or h < 20:
            continue

        # Ignore huge objects
        if w > 50 or h > 80:
            continue

        # Cactus should be taller than it is wide
        if h < w:
            continue

        # Must be in front of Dino
        if x <= DINO_RIGHT:
            continue

        # Bottom of cactus should be close to ground
        bottom = y + h

        if abs(bottom - GROUND_Y) > 15:
            continue

        candidates.append({
            "x": x,
            "y": y,
            "width": w,
            "height": h
        })

    if not candidates:
        return None

    # Closest obstacle
    candidates.sort(key=lambda o: o["x"])

    obstacle = candidates[0]

    distance = obstacle["x"] - DINO_RIGHT

    return {
        "distance": distance,
        "height": obstacle["height"],
        "width": obstacle["width"],
        "x": obstacle["x"]
    }


def get_game_state():

    obstacle = detect_obstacle()

    if obstacle is None:

        return {
            "obstacle_detected": False
        }

    return {
        "obstacle_detected": True,

        "obstacle": {
            "type": "cactus",
            "distance": obstacle["distance"],
            "height": obstacle["height"],
            "width": obstacle["width"]
        }
    }


# Test the detector
while True:

    state = get_game_state()

    if state["obstacle_detected"]:

        obstacle = state["obstacle"]

        print(
            f"Obstacle | "
            f"distance={obstacle['distance']} | "
            f"height={obstacle['height']} | "
            f"width={obstacle['width']}"
        )

    else:

        print("No obstacle")

    time.sleep(0.03)