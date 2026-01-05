from micropython import const
from displayio import Bitmap, Palette, ColorConverter
from adafruit_led_animation.animation import Animation

HORIZONTAL = const(1)
VERTICAL = const(2)

def rgb565_to_rgb888(rgb565):
    """
    Convert from an integer representing rgb565 color into an integer
    representing rgb888 color.
    :param rgb565: Color to convert
    :return int: rgb888 color value
    """
    # Shift the red value to the right by 11 bits.
    red5 = rgb565 >> 11
    # Shift the green value to the right by 5 bits and extract the lower 6 bits.
    green6 = (rgb565 >> 5) & 0b111111
    # Extract the lower 5 bits for blue.
    blue5 = rgb565 & 0b11111

    # Convert 5-bit red to 8-bit red.
    red8 = round(red5 / 31 * 255)
    # Convert 6-bit green to 8-bit green.
    green8 = round(green6 / 63 * 255)
    # Convert 5-bit blue to 8-bit blue.
    blue8 = round(blue5 / 31 * 255)

    # Combine the RGB888 values into a single integer
    rgb888_value = (red8 << 16) | (green8 << 8) | blue8

    return rgb888_value


class Sprite(Animation):

    def __init__(self, grid_object, speed, bitmap, palette, orientation=VERTICAL, name=None):
        self._bitmap = bitmap
        self._palette = palette
        self._frame = 0

        super().__init__(grid_object, speed, color=None, name=name)

        if orientation == VERTICAL:
            self._frame_count = (self._bitmap.height // self._bitmap.width)
            self._offset_mapper = lambda f: f * self._bitmap.width
            self._pixel_mapper = lambda x, y, o: self._bitmap[x, y + o]
        else:
            self._frame_count = (self._bitmap.width // self._bitmap.height)
            self._offset_mapper = lambda f: f * self._bitmap.height
            self._pixel_mapper = lambda x, y, o: self._bitmap[x + o, y]

    on_cycle_complete_supported = True

    def draw(self):
        frame_offset = self._offset_mapper(self._frame)
        for x in range(0, self.pixel_object.width):
            for y in range(0, self.pixel_object.height):
                pixel = self._pixel_mapper(x, y, frame_offset)
                if isinstance(self._palette, Palette):
                    # Indexed bitmap
                    color = self._palette[pixel]
                elif isinstance(self._palette, ColorConverter):
                    # RGB bitmap
                    color_565 = self._palette.convert(pixel)
                    color = rgb565_to_rgb888(color_565)
                self.pixel_object[x, y] = color

        self._frame += 1
        if self._frame >= self._frame_count:
            self.cycle_complete = True
            self._frame = 0

    def reset(self):
        self._frame = 0