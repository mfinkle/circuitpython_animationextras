from micropython import const
from adafruit_led_animation.animation import Animation

HORIZONTAL = const(1)
VERTICAL = const(2)

class Sprite(Animation):

    def __init__(self, grid_object, speed, bitmap, palette, orientation=VERTICAL, name=None):
        self._bitmap = bitmap
        self._palette = palette
        self._frame = 0

        super().__init__(grid_object, speed, color=None, name=name)

        if orientation == VERTICAL:
            self._frame_count = (self._bitmap.height // self.pixel_object.height)
            self._offset_mapper = lambda f: f * self.pixel_object.height
            self._pixel_mapper = lambda x, y, o: self._bitmap[x, y + o]
        else:
            self._frame_count = (self._bitmap.width // self.pixel_object.width)
            self._offset_mapper = lambda f: f * self.pixel_object.width
            self._pixel_mapper = lambda x, y, o: self._bitmap[x + o, y]

    on_cycle_complete_supported = True

    def draw(self):
        frame_offset = self._offset_mapper(self._frame)
        for x in range(0, self.pixel_object.width):
            for y in range(0, self.pixel_object.height):
                self.pixel_object[x, y] = self._palette[self._pixel_mapper(x, y, frame_offset)]

        self._frame += 1
        if self._frame >= self._frame_count:
            self.cycle_complete = True
            self._frame = 0

    def reset(self):
        self._frame = 0