import pyautogui
import time 

time.sleep(3)

GAME_REGION = (500, 300, 850, 170)

img = pyautogui.screenshot(region=GAME_REGION)

img.save("game_region.png")

print("Saved game region!")
print("Size:", img.size)