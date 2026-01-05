from micropython import const
from adafruit_led_animation.animation import Animation
import adafruit_framebuf

HORIZONTAL = const(1)
VERTICAL = const(2)

def color_to_int(color):
    if isinstance(color, tuple):
        return (color[0] << 16) | (color[1] << 8) | color[2]
    return color

class Weather(Animation):
    icon_map = {
        '01d': 0, '01n': 1,
        '02d': 2, '02n': 3,
        '03d': 4, '03n': 4,
        '04d': 4, '04n': 4,
        '09d': 5, '09n': 5,
        '10d': 5, '10n': 5,
        '11d': 6, '11n': 6,
        '13d': 7, '13n': 7,
        '50d': 8, '50n': 8,
    }

    def __init__(self, grid_object, speed, color, bitmap, palette, orientation=VERTICAL, font_name='font5x8.bin', name=None):
        self._bitmap = bitmap
        self._palette = palette
        self._frame = 0
        self._font_name = font_name
        self._font_height = adafruit_framebuf.BitmapFont(font_name).font_height

        # We're using the frame buffer for color
        self._buffer = bytearray(grid_object.width * grid_object.height * 3)
        self._fb = adafruit_framebuf.FrameBuffer(self._buffer, grid_object.width, grid_object.height, buf_format=adafruit_framebuf.RGB888)

        super().__init__(grid_object, speed, color=color, name=name)

        # We assume each frame is a square
        if orientation == VERTICAL:
            self._frame_size = self._bitmap.width
            self._frame_count = (self._bitmap.height // self._bitmap.width)
            self._offset_mapper = lambda f: f * self._bitmap.width
            self._pixel_mapper = lambda x, y, o: self._bitmap[x, y + o]
        else:
            self._frame_size = self._bitmap.height
            self._frame_count = (self._bitmap.width // self._bitmap.height)
            self._offset_mapper = lambda f: f * self._bitmap.height
            self._pixel_mapper = lambda x, y, o: self._bitmap[x + o, y]

    on_cycle_complete_supported = False

    def set_weather(self, weather_data):
        try:
            location = weather_data['name']
            condition = weather_data['weather'][0]['main']
            condition_icon = weather_data['weather'][0]['icon']
            temperature = f'{weather_data['main']['temp']:3.0f}°'
            # sunrise_dt = time.localtime(weather_data['sys']['sunrise'] + (TZ_OFFSET * 3600))
            # sunset_dt = time.localtime(weather_data['sys']['sunset'] + (TZ_OFFSET * 3600))
            # print(sunrise_dt)

            self._fb.fill(0x000000)
            if condition_icon is not None:
                self._frame = Weather.icon_map[condition_icon]
                x_offset = (self._fb.width - self._frame_size) // 2
                frame_offset = self._offset_mapper(self._frame)
                for x in range(0, self._frame_size):
                    for y in range(0, self._frame_size):
                        self._fb.pixel(x_offset + x, y, self._palette[self._pixel_mapper(x, y, frame_offset)])

            # Show temperature in lower half, below the bitmap
            # Align to bottom and assume the font numbers are not full height
            y_offset = (self._frame_size) - self._font_height + 1
            self._fb.text(temperature, 0, y_offset, color_to_int(self.color), font_name=self._font_name)
        except (KeyError, NameError) as e:
            print('Set Weather Error:', e)

    def draw(self):
        for y in range(self._fb.height):
            for x in range(self._fb.width):
                index = (y * self._fb.stride + x) * 3
                self.pixel_object[x, y] = tuple(self._buffer[index : index + 3])
