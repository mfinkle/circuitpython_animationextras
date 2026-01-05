import re
import rtc
import time

from adafruit_led_animation.animation import Animation
import adafruit_framebuf

class TextScroll(Animation):

    def __init__(self, grid_object, speed, text, color, font_name='font5x8.bin', name=None):
        self._text = text
        self._font_name = font_name
        self._frame = 0

        # Split text on newline for multi-line support
        self._lines = text.split('\n')

        # We're only using the frame buffer for on/off information, not color
        self._buffer = bytearray(grid_object.width * grid_object.height)
        self._fb = adafruit_framebuf.FrameBuffer(self._buffer, grid_object.width, grid_object.height, buf_format=adafruit_framebuf.MVLSB)

        super().__init__(grid_object, speed, color, name=name)

    on_cycle_complete_supported = True

    def _get_color(self, x, y):
       return self.color

    def draw(self):
        self._fb.fill(0x000000)

        # Get font height from the framebuffer font object
        # We need to initialize the font to get its height
        self._fb._font = adafruit_framebuf.BitmapFont(self._font_name)
        char_height = self._fb._font.font_height

        # Draw each line at appropriate y position
        for i, line in enumerate(self._lines):
            y_pos = i * char_height
            # Only draw lines that fit on the display
            if y_pos + char_height <= self.pixel_object.height:
                self._fb.text(line, self.pixel_object.width - self._frame, y_pos, 0xFFFFFF, font_name=self._font_name)

        # Cheating to get the character width
        char_width = self._fb._font.font_width

        # Use the longest line for scroll calculation
        max_line_len = max(len(line) for line in self._lines) if self._lines else 0

        for y in range(self.pixel_object.height):
            for x in range(self.pixel_object.width):
                self.pixel_object[x, y] = self._get_color(x, y) if self._fb.pixel(x, y) else (0, 0, 0)

        self._frame += 1
        if self._frame >= max_line_len * (char_width + 1) + self.pixel_object.width:
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


def color_to_int(color):
    if isinstance(color, tuple):
        return (color[0] << 16) | (color[1] << 8) | color[2]
    return color


class CountdownScroll(Animation):

    def __init__(self, grid_object, speed, color, event_name, event_dt, bitmap=None, palette=None, font_name='font5x8.bin', name=None):
        self._event_name = event_name
        self._event_dt = event_dt
        self._bitmap = bitmap
        self._palette = palette
        self._font_name = font_name
        self._frame = 0
        self._update = True

        # Determine if we're using RGB888 (for bitmap) or MVLSB (for text-only)
        if self._bitmap is not None and self._palette is not None:
            # RGB888 mode for bitmap support
            self._buffer = bytearray(grid_object.width * grid_object.height * 3)
            self._fb = adafruit_framebuf.FrameBuffer(
                self._buffer,
                grid_object.width,
                grid_object.height,
                buf_format=adafruit_framebuf.RGB888
            )
            self._use_bitmap = True
        else:
            # MVLSB mode for text-only (like original TextScroll)
            self._buffer = bytearray(grid_object.width * grid_object.height)
            self._fb = adafruit_framebuf.FrameBuffer(
                self._buffer,
                grid_object.width,
                grid_object.height,
                buf_format=adafruit_framebuf.MVLSB
            )
            self._use_bitmap = False

        super().__init__(grid_object, speed, color, name=name)

    on_cycle_complete_supported = True

    def _get_days_remaining(self):
        remaining = time.mktime(self._event_dt) - time.mktime(time.localtime())
        remaining //= 60
        mins_remaining = remaining % 60
        remaining //= 60
        hours_remaining = remaining % 24
        remaining //= 24
        days_remaining = remaining
        return days_remaining

    def _get_color(self, x, y):
        return self.color

    def draw(self):
        if self._update:
            self._update = False

        self._fb.fill(0x000000)

        # Get font dimensions
        font = adafruit_framebuf.BitmapFont(self._font_name)
        char_width = font.font_width
        char_height = font.font_height

        # Get days remaining
        days_remaining = self._get_days_remaining()

        # Build countdown text
        if days_remaining == 0:
            countdown_text = 'Today is '
        else:
            countdown_text = "{} day".format(days_remaining)
            if days_remaining != 1:
                countdown_text += "s"
            countdown_text += " til "

        # Calculate text width for countdown portion
        countdown_width = len(countdown_text) * (char_width + 1)

        # Calculate y position to center text vertically
        y_pos = (self.pixel_object.height - char_height) // 2

        # Draw the scrolling content
        x_offset = self.pixel_object.width - self._frame

        if self._use_bitmap:
            # Draw countdown text (in color)
            self._fb.text(countdown_text, x_offset, y_pos, color_to_int(self.color), font_name=self._font_name)

            # Draw bitmap after the text
            # Assume square bitmap
            bitmap_size = self._bitmap.width
            bitmap_x = x_offset + countdown_width
            bitmap_y = (self.pixel_object.height - bitmap_size) // 2

            for bx in range(bitmap_size):
                for by in range(bitmap_size):
                    pixel_x = bitmap_x + bx
                    pixel_y = bitmap_y + by
                    # Only draw if within framebuffer bounds
                    if 0 <= pixel_x < self._fb.width and 0 <= pixel_y < self._fb.height:
                        palette_index = self._bitmap[bx, by]
                        color_rgb = self._palette[palette_index]
                        self._fb.pixel(pixel_x, pixel_y, color_to_int(color_rgb))

            # Calculate total scroll width (text + bitmap)
            scroll_width = countdown_width + bitmap_size
        else:
            # Text-only mode: draw countdown + event name
            full_text = countdown_text + self._event_name
            self._fb.text(full_text, x_offset, y_pos, 0xFFFFFF, font_name=self._font_name)

            # Calculate total scroll width
            scroll_width = len(full_text) * (char_width + 1)

        # Copy framebuffer to pixel object
        if self._use_bitmap:
            # RGB888 mode
            for y in range(self.pixel_object.height):
                for x in range(self.pixel_object.width):
                    index = (y * self._fb.stride + x) * 3
                    self.pixel_object[x, y] = tuple(self._buffer[index : index + 3])
        else:
            # MVLSB mode (text-only)
            for y in range(self.pixel_object.height):
                for x in range(self.pixel_object.width):
                    self.pixel_object[x, y] = self._get_color(x, y) if self._fb.pixel(x, y) else (0, 0, 0)

        # Advance frame
        self._frame += 1
        if self._frame >= scroll_width + self.pixel_object.width:
            # Cycle completes after content scrolls completely out of view
            self.cycle_complete = True
            self._frame = 0
            self._update = True

    def reset(self):
        self._frame = 0
        self._update = True
