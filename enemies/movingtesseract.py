import math
from enemies.enemy import Enemy

class MovingTesseract(Enemy):

    def __init__(
        self,
        x,
        y,
        z,
        size=1.0,
        movement_range=3.0,
        movement_speed=2.0
    ):

        super().__init__(
            x=x,
            y=y,
            z=z,
            size=size,
            color=(1.0, 0.7, 0.1)
        )

        # Original position
        self.start_x = x

        # Movement settings
        self.movement_range = movement_range
        self.movement_speed = movement_speed

        # Movement timer
        self.elapsed_time = 0.0

    def update(self, delta_time):

        self.elapsed_time += delta_time

        # Move side to side along X
        self.x = (
            self.start_x
            + math.sin(
                self.elapsed_time * self.movement_speed
            ) * self.movement_range
        )