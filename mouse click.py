import pyautogui
import time


x,y = pyautogui.position()
pyautogui.click(1033,173)
time.sleep(5)
pyautogui.rightClick(10,10)
print(f"x:{x},y:{y}")

time.sleep(5)
x,y = pyautogui.position()
 

print(f"x:{x},y:{y}")