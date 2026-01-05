import math
import random
import rtc

from adafruit_led_animation.animation import Animation

PADDLE_HEIGHT = 3
PADDLE_WIDTH = 1
PADDLE_SPEED = 1
BALL_SIZE = 1
BALL_SPEED = 1

class Pong(Animation):
    def __init__(self, grid_object, speed, paddle_color, ball_color, name=None):
        self.paddle_color = paddle_color
        self.ball_color = ball_color

        super().__init__(grid_object, speed, 0x0, name=name)

        self.reset()
    
    on_cycle_complete_supported = True

    def draw(self):
        self.pixel_object.fill(0x000000)

        # Ball movement
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy

        # Ball collision with top or bottom walls
        if self.ball_y <= 0 or self.ball_y >= self.pixel_object.height - BALL_SIZE:
            self.ball_dy = -self.ball_dy

        # Check if ball hits left or right wall
        if self.ball_x < 0 or self.ball_x >= self.pixel_object.width:
            self.cycle_complete = True
            self.reset()

        # Left paddle movement, only if the ball is coming toward the paddle
        if self.ball_dx < 0:
            if self.left_paddle_y + PADDLE_HEIGHT // 2 < self.ball_y:
                self.left_paddle_y += PADDLE_SPEED
            elif self.left_paddle_y + PADDLE_HEIGHT // 2 > self.ball_y:
                self.left_paddle_y -= PADDLE_SPEED

            # Boundary check
            if self.left_paddle_y < 0:
                self.left_paddle_y = 0
            if self.left_paddle_y > self.pixel_object.height - PADDLE_HEIGHT:
                self.left_paddle_y = self.pixel_object.height - PADDLE_HEIGHT

        # Right paddle movement, only if the ball is coming toward the paddle
        if self.ball_dx > 0:
            if self.right_paddle_y + PADDLE_HEIGHT // 2 < self.ball_y:
                self.right_paddle_y += PADDLE_SPEED
            elif self.right_paddle_y + PADDLE_HEIGHT // 2 > self.ball_y:
                self.right_paddle_y -= PADDLE_SPEED

            # Boundary check
            if self.right_paddle_y < 0:
                self.right_paddle_y = 0
            if self.right_paddle_y > self.pixel_object.height - PADDLE_HEIGHT:
                self.right_paddle_y = self.pixel_object.height - PADDLE_HEIGHT

        # Ball collision with paddles
        if self.ball_x <= PADDLE_WIDTH and self.left_paddle_y <= self.ball_y <= self.left_paddle_y + PADDLE_HEIGHT:
            self.ball_dx = -self.ball_dx
        if self.ball_x >= self.pixel_object.width - PADDLE_WIDTH - BALL_SIZE and self.right_paddle_y <= self.ball_y <= self.right_paddle_y + PADDLE_HEIGHT:
            self.ball_dx = -self.ball_dx

        # Draw ball
        self.pixel_object[self.ball_x, self.ball_y] = self.ball_color

        # Draw paddles
        for y in range(PADDLE_HEIGHT):
            self.pixel_object[0, self.left_paddle_y + y] = self.paddle_color
        for y in range(PADDLE_HEIGHT):
            self.pixel_object[self.pixel_object.width - 1, self.right_paddle_y + y] = self.paddle_color

    def reset(self):
        self.left_paddle_y = self.pixel_object.height // 2 - PADDLE_HEIGHT // 2
        self.right_paddle_y = self.pixel_object.height // 2 - PADDLE_HEIGHT // 2

        self.ball_x = self.pixel_object.width // 2
        self.ball_y = self.pixel_object.height // 2 + random.choice([-BALL_SIZE, BALL_SIZE])
        self.ball_dx = random.choice([-BALL_SPEED, BALL_SPEED])
        self.ball_dy = random.choice([-BALL_SPEED, BALL_SPEED])
