from enemies.enemy import Enemy

class StationaryTesseract(Enemy):

    def __init__(self, x, y, z, size=1.0):

        super().__init__(
            x=x,
            y=y,
            z=z,
            size=size,
            color=(0.2, 0.8, 1.0)
        )

    def update(self, delta_time):
        # Remains in its original position
        pass