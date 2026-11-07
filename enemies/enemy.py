import itertools
from OpenGL.GL import *

class Enemy:

    def __init__(
        self,
        x=0.0,
        y=-2.5,
        z=0.0,
        size=1.0,
        color=(0.2, 0.8, 1.0)
    ):

        # Enemy position
        self.x = x
        self.y = y
        self.z = z

        # Enemy appearance
        self.size = size
        self.color = color

        # Collision settings
        self.collision_radius = size * 0.8

        # Generate tesseract geometry
        self.vertices, self.edges = self.create_tesseract()

    # =====================================
    # CREATE TESSERACT GEOMETRY
    # =====================================

    def create_tesseract(self):

        # Generate 16 vertices in 4D space
        vertices_4d = list(
            itertools.product((-1, 1), repeat=4)
        )

        vertices_3d = []

        # Project 4D vertices into 3D space
        for x, y, z, w in vertices_4d:

            distance = 3.5
            denominator = distance - w

            projected_x = x / denominator
            projected_y = y / denominator
            projected_z = z / denominator

            vertices_3d.append((
                projected_x,
                projected_y,
                projected_z
            ))

        # Connect vertices differing in one coordinate
        edges = []

        for i in range(len(vertices_4d)):

            for j in range(i + 1, len(vertices_4d)):

                differences = sum(
                    a != b
                    for a, b in zip(
                        vertices_4d[i],
                        vertices_4d[j]
                    )
                )

                if differences == 1:
                    edges.append((i, j))

        return vertices_3d, edges

    # =====================================
    # UPDATE ENEMY
    # =====================================

    def update(self, delta_time):
        pass

    # =====================================
    # COLLISION DETECTION
    # =====================================

    def check_collision(self, player):
        return False

    # =====================================
    # DRAW TESSERACT
    # =====================================

    def draw(self):

        glPushMatrix()

        glTranslatef(
            self.x,
            self.y,
            self.z
        )

        glScalef(
            self.size,
            self.size,
            self.size
        )

        glColor3f(*self.color)

        glLineWidth(2.0)

        glBegin(GL_LINES)

        for start, end in self.edges:

            glVertex3fv(self.vertices[start])
            glVertex3fv(self.vertices[end])

        glEnd()

        glLineWidth(1.0)

        glPopMatrix()
