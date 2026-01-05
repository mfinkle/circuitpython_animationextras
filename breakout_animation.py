import random
import rtc

from adafruit_led_animation.animation import Animation

PADDLE_HEIGHT = 1
PADDLE_WIDTH = 3
PADDLE_SPEED = 1
BALL_SIZE = 1
BALL_SPEED = 1
BLOCK_SIZE = 2

class Breakout(Animation):
    def __init__(self, grid_object, speed, paddle_color, ball_color, row_color, name=None):
        self.paddle_color = paddle_color
        self.ball_color = ball_color
        if not isinstance(row_color, list):
            self.row_color = [row_color, row_color, row_color]

        self.row_color = row_color
        self.ROW_COUNT = len(row_color)

        super().__init__(grid_object, speed, 0x0, name=name)

        self.reset()
    
    on_cycle_complete_supported = True

    def draw(self):
        self.pixel_object.fill(0x000000)

        # Ball movement
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy

        # Paddle movement, only if the ball is coming toward the paddle
        if self.ball_dy > 0:
            if self.paddle_x + PADDLE_WIDTH // 2 < self.ball_x:
                self.paddle_x += PADDLE_SPEED
            elif self.paddle_x + PADDLE_WIDTH // 2 > self.ball_x:
                self.paddle_x -= PADDLE_SPEED

            # Boundary check
            if self.paddle_x < 0:
                self.paddle_x = 0
            if self.paddle_x > self.pixel_object.width - PADDLE_WIDTH:
                self.paddle_x = self.pixel_object.width - PADDLE_WIDTH

        # Ball collision with block
        hit_block = None
        for block in self.blocks:
            bx, by = block
            if (bx <= self.ball_x <= bx + BLOCK_SIZE) and by == self.ball_y:
                hit_block = block
                break

        if hit_block:
            self.blocks.remove(hit_block)
            self.ball_dy = -self.ball_dy

        # Else ball collision with top (top most ball and top wall can both be true, so only do one or the other)
        elif self.ball_y <= 0:
            self.ball_dy = -self.ball_dy

        # Ball collision with side walls
        if self.ball_x <= 0 or self.ball_x >= self.pixel_object.width - BALL_SIZE:
            self.ball_dx = -self.ball_dx

        # Ball collision with paddles
        if self.ball_y >= self.pixel_object.height - PADDLE_HEIGHT - BALL_SIZE and self.paddle_x <= self.ball_x <= self.paddle_x + PADDLE_WIDTH:
            self.ball_dy = -self.ball_dy

        # Check if ball hits bottom wall or if no blocks remain
        if self.ball_y >= self.pixel_object.height - BALL_SIZE or len(self.blocks) == 0:
            self.cycle_complete = True
            self.reset()

        # Draw blocks
        for bx, by in self.blocks:
            for x in range(BLOCK_SIZE):
                self.pixel_object[bx + x, by] = self.row_color[by]

        # Draw ball
        self.pixel_object[self.ball_x, self.ball_y] = self.ball_color

        # Draw paddle
        for x in range(PADDLE_WIDTH):
            self.pixel_object[self.paddle_x + x, self.pixel_object.height - PADDLE_HEIGHT] = self.paddle_color

    def reset(self):
        self.paddle_x = self.pixel_object.height // 2 - PADDLE_WIDTH // 2

        self.ball_x = self.pixel_object.width // 2
        self.ball_y = self.pixel_object.height // 2 + random.choice([-BALL_SIZE, BALL_SIZE])
        self.ball_dx = random.choice([-BALL_SPEED, BALL_SPEED])
        self.ball_dy = BALL_SPEED

        self.blocks = [(x, y) for y in range(self.ROW_COUNT) for x in range(0, self.pixel_object.width, BLOCK_SIZE)]
