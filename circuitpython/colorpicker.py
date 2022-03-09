import busio
import math
import time
import neopixel
import adafruit_fancyled.adafruit_fancyled as fancy
from board import *
from digitalio import DigitalInOut, Pull
from analogio import AnalogIn
from lcd.lcd import LCD, CursorMode
from lcd.i2c_pcf8574_interface import I2CPCF8574Interface

# initialize LCD1602
i2c = busio.I2C(GP11, GP10)
lcd = LCD(I2CPCF8574Interface(i2c, 0x27), num_rows=2, num_cols=16)
lcd.set_cursor_mode(CursorMode.BLINK)

# initialize NeoPixel LED strip
pixel_pin = GP22
num_pixels = 8

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.1, auto_write=False)

# initialize joystick
x = AnalogIn(A2)
y = AnalogIn(A1)
btn = DigitalInOut(GP26)
btn.pull = Pull.UP


# initial colors
colors = [
    [0, 255, 180],
    [255, 255, 180],
]

# cursor position on the LCD
cursorPos = [0, 0]

while True:
    # interpolate colors between start and end colors
    for i in range(num_pixels):
        pixels[i] = fancy.CHSV(
            (colors[0][0] * (num_pixels - 1 - i) + colors[1][0] * i) // num_pixels,
            (colors[0][1] * (num_pixels - 1 - i) + colors[1][1] * i) // num_pixels,
            (colors[0][2] * (num_pixels - 1 - i) + colors[1][2] * i) // num_pixels,
        ).pack()
    pixels.show()
    
    # show the start color and end color
    lcd.set_cursor_pos(0, 0)
    lcd.print('S:(%3d,%3d,%3d)' % tuple(colors[0]))
    lcd.set_cursor_pos(1, 0)
    lcd.print('E:(%3d,%3d,%3d)' % tuple(colors[1]))
    
    # blink the cursor at current position 
    lcd.set_cursor_pos(cursorPos[0], cursorPos[1] * 4 + 5)
    
    # press down joystick to switch between start color and end color
    if not btn.value:
        cursorPos[0] = (cursorPos[0] + 1) % 2
    
    # calculate the joystick offsets
    dx = abs(x.value - 32768)
    dy = abs(y.value - 32768)
    
    # use 5000 deadzone to prevent drifting
    if dx > dy and dx > 5000:
        if x.value < 32768:
            cursorPos[1] -= 1
            if cursorPos[1] < 0:
                cursorPos[1] = 0
        else:
            cursorPos[1] += 1
            if cursorPos[1] > 2:
                cursorPos[1] = 2
                
    # use 5000 deadzone to prevent drifting
    elif dy > dx and dy > 5000:
        d = (dy - 5000) // 5000
        if y.value > 32768:
            colors[cursorPos[0]][cursorPos[1]] -= d
            if colors[cursorPos[0]][cursorPos[1]] < 0:
                colors[cursorPos[0]][cursorPos[1]] = 0
        else:
            colors[cursorPos[0]][cursorPos[1]] += d
            if colors[cursorPos[0]][cursorPos[1]] > 255:
                colors[cursorPos[0]][cursorPos[1]] = 255
            
    time.sleep(0.1)
