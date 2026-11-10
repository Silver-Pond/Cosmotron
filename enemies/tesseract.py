import math
import itertools

from OpenGL.GL import *

class Tesseract:

    def __init__(self, x, z, level_map):

        self.x = x
        self.z = z

        self.level_map = level_map

        # Movement
        self.speed = 3.5
        self.direction = 1

        # Collision radius
        self.radius = 0.45

        # Tesseract visual size
        self.size = 0.45

        # Vertical position
        self.y = level_map.floor_y + 0.9

        # Rotation
        self.rotation = 0.0
        self.rotation_speed = 1.0

        # 4D vertices: all combinations of +/- 1
        self.vertices = list(
            itertools.product([-1, 1], repeat=4)
        )

        # Connect vertices differing in exactly one coordinate
        self.edges = []

        for i, vertex_a in enumerate(self.vertices):

            for j, vertex_b in enumerate(self.vertices):

                differences = sum(a != b
                    for a, b in zip(vertex_a, vertex_b)
                )

                if differences == 1 and i < j:
                    self.edges.append((i, j))

    # UPDATE ENEMY
    def update(self, delta_time):

        self.rotation += self.rotation_speed * delta_time

        # Calculate horizontal movement
        movement = self.speed * self.direction * delta_time

        next_x = self.x + movement

        # Check for wall collision
        if self.level_map.collides_with_wall(
            next_x, self.z, self.radius):

            # Reverse direction
            self.direction *= -1

        else:
            self.x = next_x

    # 4D ROTATION
    def rotate_4d(self, vertex):

        x, y, z, w = vertex

        angle = self.rotation

        # Rotate in the XW plane
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        new_x = x * cos_a - w * sin_a
        new_w = x * sin_a + w * cos_a

        # Rotate in the YZ plane
        angle2 = self.rotation * 0.7

        cos_b = math.cos(angle2)
        sin_b = math.sin(angle2)

        new_y = y * cos_b - z * sin_b
        new_z = y * sin_b + z * cos_b

        return new_x, new_y, new_z, new_w

    # 4D TO 3D PROJECTION
    def project_4d(self, vertex):

        x, y, z, w = vertex

        # Perspective projection from 4D into 3D
        distance = 3.0

        factor = distance / (distance - w)

        return (x * factor, y * factor, z * factor)

    # DRAW TESSERACT
    def draw(self):

        glPushMatrix()

        glTranslatef(self.x, self.y, self.z)

        # Store projected vertices
        projected_vertices = []

        for vertex in self.vertices:

            # Rotate in 4D
            rotated = self.rotate_4d(vertex)

            # Project into 3D
            projected = self.project_4d(rotated)

            projected_vertices.append(projected)

        glDisable(GL_TEXTURE_2D)
        glDisable(GL_LIGHTING)

        # Draw tesseract edges
        glLineWidth(3.0)

        glBegin(GL_LINES)

        for edge in self.edges:

            a = projected_vertices[edge[0]]
            b = projected_vertices[edge[1]]

            # Different colours for visual depth
            glColor3f(0.2, 0.9, 1.0)

            glVertex3f(a[0] * self.size, a[1] * self.size, a[2] * self.size)
            glVertex3f(b[0] * self.size, b[1] * self.size, b[2] * self.size)

        glEnd()

        glLineWidth(1.0)

        glPopMatrix()

"""
REFERENCE LIST

Gregory, J., 2018. Game Engine Architecture.
3rd edn. Boca Raton: CRC Press.

Lutz, M., 2013. Learning Python.
5th edn. Sebastopol: O'Reilly Media.

Millington, I. and Funge, J., 2009. Artificial Intelligence for Games.
2nd edn. Burlington, MA: Morgan Kaufmann.

Shreiner, D., Sellers, G., Kessenich, J. and Licea-Kane, B., 2013.
OpenGL Programming Guide: The Official Guide to Learning OpenGL.
8th edn. Upper Saddle River, NJ: Addison-Wesley.
"""