from OpenGL.GL import *
from enemies.tesseract import Tesseract

class PurpleTesseract(Tesseract):

    def __init__(self, x, z, level_map):

        super().__init__(x, z, level_map)

        # Forward/backward movement
        self.speed = 3.5
        self.direction = 1

        # Purple enemy collision radius
        self.radius = 0.40

        # Purple tesseract rotation
        self.rotation_speed = 1.0

        # Movement boundaries
        self.min_z = z - 3.0
        self.max_z = z + 3.0

        # Purple colour
        self.colour = (0.65, 0.1, 1.0)

    # UPDATE ENEMY
    def update(self, delta_time):

        self.rotation += self.rotation_speed * delta_time

        # Calculate forward/backward movement
        movement = self.speed * self.direction * delta_time

        next_z = self.z + movement

        # Check movement boundaries
        if next_z <= self.min_z or next_z >= self.max_z:

            # Reverse direction
            self.direction *= -1

        else:
            # Move along Z-axis
            self.z = next_z

    # DRAW PURPLE TESSERACT
    def draw(self):

        glPushMatrix()

        glTranslatef(self.x, self.y, self.z)

        projected_vertices = []

        for vertex in self.vertices:

            rotated = self.rotate_4d(vertex)
            projected = self.project_4d(rotated)

            projected_vertices.append(projected)

        glDisable(GL_TEXTURE_2D)
        glDisable(GL_LIGHTING)

        glLineWidth(3.0)

        glBegin(GL_LINES)

        for edge in self.edges:

            a = projected_vertices[edge[0]]
            b = projected_vertices[edge[1]]

            # Purple colour
            glColor3f(*self.colour)

            glVertex3f(
                a[0] * self.size,
                a[1] * self.size,
                a[2] * self.size
            )

            glVertex3f(
                b[0] * self.size,
                b[1] * self.size,
                b[2] * self.size
            )

        glEnd()

        glLineWidth(1.0)

        glPopMatrix()