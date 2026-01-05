import math
import rtc

import adafruit_framebuf

from micropython import const
from adafruit_led_animation.animation import Animation

ANALOG = const(1)
DIGITAL = const(2)

def color_to_int(color):
    if isinstance(color, tuple):
        return (color[0] << 16) | (color[1] << 8) | color[2]
    return color

class Clock(Animation):
    def __init__(self, grid_object, speed, color, mode=DIGITAL, font_name='font5x8.bin', name=None):
        self._minute_color = color
        self._hour_color = color
        self._font_name = font_name

        # We're using the frame buffer for color
        self._buffer = bytearray(grid_object.width * grid_object.height * 3)
        self._fb = adafruit_framebuf.FrameBuffer(self._buffer, grid_object.width, grid_object.height, buf_format=adafruit_framebuf.RGB888)

        super().__init__(grid_object, speed, 0x0, name=name)
    
    def draw(self):
        r = rtc.RTC()
        dt = r.datetime
        minute = dt.tm_min
        hour = (dt.tm_hour + 11) % 12 + 1

        self._fb.fill(color_to_int((0, 0, 0)))

        self._fb.rect(0, 0, self._fb.width, self._fb.height, color_to_int((255, 255, 255)), fill=False)

        self._fb.text(f'{hour:3.0f}', 2, 2, color_to_int(self._hour_color), font_name=self._font_name)
        self._fb.text(f':{minute:02.0f}', 2, (self._fb.height // 2) + 1, color_to_int(self._minute_color), font_name=self._font_name)

        for y in range(self._fb.height):
            for x in range(self._fb.width):
                index = (y * self._fb.stride + x) * 3
                self.pixel_object[x, y] = tuple(self._buffer[index : index + 3])
