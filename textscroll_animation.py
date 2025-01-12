import re
import rtc

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


DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
DAYCOUNT = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
# leap_year = (tm_year % 4 == 0 && tm_year % 100 != 0) || tm_year % 400 == 0
# tm_yday = DAYCOUNT[tm_mon - 1] + tm_mday + ((tm_mon > 2 && leap_year) ? 1 : 0)

class TimeScroll(TextScroll):

    def __init__(self, grid_object, speed, format, color, font_name='font5x8.bin', name=None):
        self._format = format
        self._update = True
        super().__init__(grid_object, speed, self._strftime(), color, font_name=font_name, name=name)

    def _strftime(self):
        r = rtc.RTC()
        dt = r.datetime

        def _replace_func(match_obj):
            try:
                match = match_obj.group(0)
            except AttributeError:
                return ''
            else:
                if match == '%a': return DAYS[dt.tm_wday][:3]
                if match == '%A': return DAYS[dt.tm_wday]
                if match == '%b': return MONTHS[dt.tm_mon - 1][:3]
                if match == '%B': return MONTHS[dt.tm_mon - 1]
                if match == '%c': return '{:02}/{:02}/{} {:02}:{:02}:{:02}'.format(dt.tm_mon, dt.tm_mday, dt.tm_year, dt.tm_hour, dt.tm_min, dt.tm_sec)
                if match == '%d': return '{:02}'.format(dt.tm_mday)
                # if match == '%e': return '{}'.format(dt.tm_mday)
                if match == '%H': return '{:02}'.format(dt.tm_hour)
                if match == '%I': return '{:02}'.format((dt.tm_hour + 11) % 12 + 1)
                if match == '%j': return '{:03}'.format(dt.tm_yday)
                # if match == '%k': return '{}'.format(dt.tm_hour)
                # if match == '%l': return '{}'.format((dt.tm_hour + 11) % 12 + 1)
                if match == '%m': return '{:02}'.format(dt.tm_mon)
                if match == '%M': return '{:02}'.format(dt.tm_min)
                if match == '%n': return '{}'.format(dt.tm_mon)
                if match == '%p': return 'AM' if dt.tm_hour < 12 else 'PM'
                # if match == '%P': return 'am' if dt.tm_hour < 12 else 'pm'
                if match == '%S': return '{:02}'.format(dt.tm_sec)
                if match == '%u': return '{}'.format(dt.tm_wday + 1)
                if match == '%y': return '{:02}'.format(dt.tm_year)
                if match == '%Y': return '{}'.format(dt.tm_year)

        return re.sub(r'%[a-zA-Z]', _replace_func, self._format)

    def draw(self):
        if self._update:
            self._text = self._strftime()
            self._update = False

        super().draw()

        if self.cycle_complete:
            self._update = True

    def reset(self):
        super().reset()
        self._update = True
