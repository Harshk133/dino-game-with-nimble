import pyautogui
import cv2
import numpy as np
import time

# Screenshot region (left, top, width, height)
GAME_REGION = (500, 300, 850, 170)

# Only search for obstacles in front of the dino (game X, inside the crop)
SEARCH_START_X = 220
SEARCH_END_X = 840

# Ignore sky / UI chrome at the top of the crop
SEARCH_START_Y = 25

# Dark pixels in the dino game (threshold works for normal and slightly dim backgrounds)
THRESHOLD_VALUE = 140


def _frame_to_mask(frame: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    _, mask = cv2.threshold(
        gray,
        THRESHOLD_VALUE,
        255,
        cv2.THRESH_BINARY_INV,
    )
    return mask


def _find_ground_y(mask: np.ndarray, x_start: int, x_end: int) -> int:
    """Ground line row: thin horizontal track (not GAME OVER text or UI)."""
    height = mask.shape[0]
    y0 = int(height * 0.58)
    y1 = min(height - 12, int(height * 0.78))

    for y in range(y1, y0 - 1, -1):
        count = int(np.count_nonzero(mask[y, x_start:x_end]))
        if 12 <= count <= 120:
            return y

    return 116


def _find_dino_right(mask: np.ndarray, ground_y: int) -> int:
    """Right edge of the dino silhouette (crop stops above ground to avoid merging)."""
    y0 = max(SEARCH_START_Y, ground_y - 58)
    y1 = max(y0 + 20, ground_y - 2)
    roi = mask[y0:y1, 0:240]

    contours, _ = cv2.findContours(
        roi,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )

    best_right = 200
    best_area = 0
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = w * h
        if area < 350 or h < 22:
            continue
        right = x + w
        if area > best_area:
            best_area = area
            best_right = right

    return best_right


def detect_obstacle():
    screenshot = pyautogui.screenshot(region=GAME_REGION)
    frame = np.array(screenshot)
    mask = _frame_to_mask(frame)

    ground_y = _find_ground_y(mask, SEARCH_START_X, SEARCH_END_X)
    dino_right = _find_dino_right(mask, ground_y)

    search_end_y = min(mask.shape[0] - 10, ground_y + 6)
    roi = mask[
        SEARCH_START_Y:search_end_y,
        SEARCH_START_X:SEARCH_END_X,
    ]

    contours, _ = cv2.findContours(
        roi,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )

    candidates = []
    ground_tol = 10

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)

        x += SEARCH_START_X
        y += SEARCH_START_Y

        if w < 4 or h < 18:
            continue
        if w > 70 or h > 95:
            continue

        # Skip flat ground specks and very wide low blobs (clouds / UI)
        if h < 12 and w > 20:
            continue
        if h < 25 and w > h * 2:
            continue

        if x <= dino_right + 5:
            continue

        bottom = y + h
        if abs(bottom - ground_y) > ground_tol:
            continue

        candidates.append(
            {
                "x": x,
                "y": y,
                "width": w,
                "height": h,
            }
        )

    if not candidates:
        return None

    candidates.sort(key=lambda o: o["x"])
    obstacle = candidates[0]
    distance = obstacle["x"] - dino_right

    return {
        "distance": distance,
        "height": obstacle["height"],
        "width": obstacle["width"],
        "x": obstacle["x"],
        "ground_y": ground_y,
        "dino_right": dino_right,
    }


def get_game_state():
    obstacle = detect_obstacle()

    if obstacle is None:
        return {
            "obstacle_detected": False,
        }

    return {
        "obstacle_detected": True,
        "obstacle": {
            "type": "cactus",
            "distance": obstacle["distance"],
            "height": obstacle["height"],
            "width": obstacle["width"],
        },
    }


# Test the detector
if __name__ == "__main__":
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
