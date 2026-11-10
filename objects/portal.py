import math
import pygame

from OpenGL.GL import *

class Portal:

    def __init__(self, x, z, level_map):

        self.x = x
        self.z = z
        self.level_map = level_map

        # Portal position and dimensions
        self.y = level_map.floor_y + 1.0
        self.radius = 0.85

        # Animation
        self.rotation = 0.0
        self.pulse = 0.0

        # Player activation distance
        self.activation_radius = 1.0

        # Portal image
        self.texture = self.load_texture()

    # UPDATE PORTAL ANIMATION
    def update(self, delta_time):

        self.rotation += 90.0 * delta_time

        if self.rotation >= 360:
            self.rotation -= 360

        self.pulse += 2.5 * delta_time

    # CHECK PLAYER COLLISION
    def check_collision(self, player):

        dx = player.x - self.x
        dz = player.z - self.z

        distance = math.sqrt(dx * dx + dz * dz)

        return distance <= self.activation_radius

    # Loading in the mage for the portal
    def load_texture(self):

        image = pygame.image.load("assets/worm_hole.png").convert_alpha()

        image_data = pygame.image.tostring(image, "RGBA", True)

        width, height = image.get_size()

        texture_id = glGenTextures(1)

        glBindTexture(GL_TEXTURE_2D, texture_id)

        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA,
            width, height, 0,
            GL_RGBA, GL_UNSIGNED_BYTE, image_data
        )

        # Texture filtering
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        # Texture wrapping
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        glBindTexture(GL_TEXTURE_2D, 0)

        return texture_id

    # DRAW PORTAL
    def draw(self):

        glPushAttrib(
            GL_ENABLE_BIT | GL_COLOR_BUFFER_BIT |
            GL_TEXTURE_BIT | GL_LINE_BIT
        )

        glPushMatrix()

        glTranslatef(self.x, self.y, self.z)

        # Portal faces the approaching player
        glRotatef(self.rotation, 0, 0, 1)

        # Animated pulse
        pulse_scale = 1.0 + 0.05 * math.sin(self.pulse)
        glScalef(pulse_scale, pulse_scale, 1.0)

        # Enable transparency
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_LIGHTING)

        # DRAW WORMHOLE IMAGE
        glEnable(GL_TEXTURE_2D)

        glBindTexture(GL_TEXTURE_2D, self.texture)

        glColor4f(1.0, 1.0, 1.0, 1.0)

        size = self.radius

        glBegin(GL_QUADS)

        # Bottom-left
        glTexCoord2f(0.0, 0.0)
        glVertex3f(-size, -size, 0.0)

        # Bottom-right
        glTexCoord2f(1.0, 0.0)
        glVertex3f(size, -size, 0.0)

        # Top-right
        glTexCoord2f(1.0, 1.0)
        glVertex3f(size, size, 0.0)

        # Top-left
        glTexCoord2f(0.0, 1.0)
        glVertex3f(-size, size, 0.0)

        glEnd()

        glBindTexture(GL_TEXTURE_2D, 0)

        glDisable(GL_TEXTURE_2D)

        # OUTER PURPLE RING
        glLineWidth(5)

        glColor4f(0.55, 0.1, 1.0, 1.0)

        glBegin(GL_LINE_LOOP)

        for i in range(64):
            angle = 2.0 * math.pi * i / 64

            x = math.cos(angle) * self.radius
            y = math.sin(angle) * self.radius

            glVertex3f(x, y, 0.02)

        glEnd()

        # INNER CYAN RING
        glLineWidth(2)

        glColor4f(0.1, 0.7, 1.0, 0.8)

        glBegin(GL_LINE_LOOP)

        for i in range(64):
            angle = 2.0 * math.pi * i / 64

            x = math.cos(angle) * (self.radius * 0.82)
            y = math.sin(angle) * (self.radius * 0.82)

            glVertex3f(x, y, 0.025)

        glEnd()

        glLineWidth(1)

        glPopMatrix()

        glPopAttrib()

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