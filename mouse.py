# Re-running the essential part of the code to print mouse position

import pyautogui
import time

print("Moving the mouse to the top-left corner will stop the program.")

try:
    while True:
        # Get the current mouse x and y position
        x, y = pyautogui.position()
        print(f"Position: ({x}, {y})", end="\r")
        time.sleep(0.1)  # Slow down the loop to make it readable

        # Stop if the mouse is in the top-left corner
        if x == 0 and y == 0:
            break
except KeyboardInterrupt:
    print("\nDone")