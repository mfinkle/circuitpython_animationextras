from adafruit_led_animation.animation import Animation
import adafruit_framebuf

class TextScroll(Animation):

    def __init__(self, grid_object, speed, text, color, font_name='font5x8.bin', name=None):
        self._text = text
        self._font_name = font_name
        self._frame = 0

        # We're only using the frame buffer for on/off information, not color
        self._buffer = bytearray(grid_object.width * grid_object.height)
        self._fb = adafruit_framebuf.FrameBuffer(self._buffer, grid_object.width, grid_object.height, buf_format=adafruit_framebuf.MVLSB)

        super().__init__(grid_object, speed, color, name=name)

    on_cycle_complete_supported = True

    def _get_color(self, x, y):
        return self.color

    def draw(self):
        self._fb.fill(0x000000)
        self._fb.text(self._text, self.pixel_object.width - self._frame, 0, 0xFFFFFF, font_name=self._font_name)

        # Cheating to get the character width
        char_width = self._fb._font.font_width

        for y in range(self.pixel_object.height):
            for x in range(self.pixel_object.width):
                self.pixel_object[x, y] = self._get_color(x, y) if self._fb.pixel(x, y) else (0, 0, 0)

        self._frame += 1
        if self._frame >= len(self._text) * (char_width + 1) + self.pixel_object.width:
            # Cycle completes after text scrolls completely out of view on the display
            self.cycle_complete = True
            self._frame = 0

    def reset(self):
        self._frame = 0