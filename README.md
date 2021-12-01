## Introduction
Adafruit's LED animation library supports some really cool effects and building blocks, while using a time-slicing approach that doesn't block the program execution. Animation Extrras is a collection of code that builds on the core functionality.

## Dependencies
This code depends on:

* [Adafruit CircuitPython](https://github.com/adafruit/circuitpython)
* [Adafruit LED Animation](https://github.com/adafruit/Adafruit_CircuitPython_LED_Animation)
* [Adafruit framebuf](https://github.com/adafruit/Adafruit_CircuitPython_framebuf) and 'font5x8.bin' (for `TextScroll`)
* [Adafruit ImageLoad](https://github.com/adafruit/Adafruit_CircuitPython_ImageLoad) (for `Sprite`)

Please make sure all dependencies are available on the CircuitPython filesystem.

## Usage Example
```
import board
import neopixel

from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.rainbowcomet import RainbowComet
from adafruit_led_animation.sequence import AnimationSequence
from adafruit_led_animation import helper
from adafruit_led_animation.color import AMBER
from adafruit_led_animation.grid import PixelGrid, VERTICAL

# Sprite animation requires 'adafruit_imageload'
import adafruit_imageload

from sprite_animation import Sprite
from matrix_animation import rectangular_lines
from textscroll_animation import TextScroll

# Update to match the pin connected to your NeoPixels
pixel_pin = board.D6
# Update to match the number of NeoPixels you have connected
pixel_num = 64

pixels = neopixel.NeoPixel(pixel_pin, pixel_num, brightness=0.1, auto_write=False)

# Set the size of the sprite to 8 pixels wide by 8 pixels tall
# (make sure 'orientation', 'alternating' and 'reverse_x' are correct for your display)
grid = PixelGrid(pixels, 8, 8, orientation=VERTICAL, alternating=False, reverse_x=True)

bitmap, palette = adafruit_imageload.load('/bmps/flame_simple.bmp')
flame_sprite = Sprite(grid, 0.25, bitmap, palette)

# TextScroll defaults to using 'font5x8.bin' so make sure the file is on the device
text_scroll = TextScroll(grid, 0.1, 'Hellow World', color=AMBER)

# Create a rectangular pattern
pixel_rectangular = rectangular_lines(pixels, 8, 8, helper.horizontal_strip_gridmap(8, alternating=False))
comet_rect = Comet(pixel_rectangular, speed=0.1, color=AMBER, tail_length=6, bounce=True)
rainbow_comet_rect = RainbowComet(pixel_rectangular, speed=0.1, tail_length=6, bounce=True)

animations = AnimationSequence(
    text_scroll,
    flame_sprite,
    comet_rect,
    rainbow_comet_rect,
    advance_interval=10
)

while True:
    animations.animate()
```

## What's Included
**sprite_animation.py**

* `Sprite`: Creates an animation from a vertical bitmap spritesheet, displaying a different frame of the spritesheet on each `animate()` call.

**textscroll_animation.py**

* `TextScroll`: Creates a horizontal marquee animation, scrolling one pixel on each `animate()` call.

**pixelmap_extras.py**

* `rectangular_lines`: Creates a PixelMap from concentric rectangular lines in the grid.
* `map_from_mask`: Creates a PixelMap from a Bitmap using the palette index to group pixels.