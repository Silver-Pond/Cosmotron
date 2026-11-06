import pygame

from OpenGL.GL import *
from OpenGL.GLU import *
from player.player import Player
from levels.level_1 import LevelMap

def run():
    print("Game started!")

    # Initialise Pygame
    pygame.init()

    WIDTH = 1000
    HEIGHT = 700

    pygame.display.set_mode(
        (WIDTH, HEIGHT),
        pygame.DOUBLEBUF | pygame.OPENGL
    )

    pygame.display.set_caption("CosmoTron")

    # OpenGL settings
    glEnable(GL_DEPTH_TEST)

    # Preserve the original PNG colours
    glDisable(GL_LIGHTING)

    # Camera
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    gluPerspective(45, WIDTH / HEIGHT, 0.1, 100.0)

    glMatrixMode(GL_MODELVIEW)

    # Create level
    level = LevelMap()

    # Create player spacecraft
    player = Player(
        model_path="assets/player/pyro_can.obj",
        texture_path="assets/player/pyro_can.png"
    )

    # Connect level map to player
    player.set_level_map(level)

    clock = pygame.time.Clock()
    running = True

    while running:

        delta_time = clock.tick(60) / 1000.0

        # Events
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

        # Keyboard controls
        keys = pygame.key.get_pressed()

        player.update(keys, delta_time)

        # Clear screen
        glClearColor(0.01, 0.01, 0.05, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glLoadIdentity()

        # Camera follows the spacecraft
        player.update_camera()

        # Update player
        player.update(keys, delta_time)

        # Update map loading position
        level.update(player.z)

        # Draw level
        level.draw()

        # Draw player
        player.draw()

        # Draw player bullets
        player.draw_bullets()

        pygame.display.flip()

    # Clean up
    player.cleanup()

    pygame.quit()

"""
REFERENCE LIST


"""