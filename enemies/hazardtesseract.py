from enemies.enemy import Enemy

class HazardTesseract(Enemy):

    def __init__(self, x, y, z, size=1.0):

        super().__init__(
            x=x,
            y=y,
            z=z,
            size=size,
            color=(1.0, 0.1, 0.1)
        )

    def update(self, delta_time):
        # Remains stationary
        pass

    def check_collision(self, player):

        # Check vertical distance
        vertical_distance = abs(
            self.y - player.y
        )

        if vertical_distance > self.size + 0.8:
            return False

        # Check horizontal distance
        dx = self.x - player.x
        dz = self.z - player.z

        collision_distance = (
            self.collision_radius
            + max(
                player.collision_radius_x,
                player.collision_radius_z
            )
        )

        distance_squared = dx * dx + dz * dz

        return distance_squared <= collision_distance ** 2