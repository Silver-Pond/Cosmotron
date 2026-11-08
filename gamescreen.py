import pygame

from OpenGL.GL import *
from OpenGL.GLU import *

from player.player import Player
from levels.level_1 import LevelMap

# MENU SETTINGS
WIDTH = 1000
HEIGHT = 700

MENU = 0
GAME = 1
EXIT = 2

# INITIALISE OPENGL 2D MENU
def setup_menu():

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    glOrtho(0, WIDTH, HEIGHT, 0, -1, 1)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glDisable(GL_DEPTH_TEST)

    # Enable transparency for Pygame text
    glEnable(GL_BLEND)

    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

# DRAW MENU TEXT
def draw_text(text, x, y, font_size, colour=(255, 255, 255)):

    font = pygame.font.Font(None, font_size)

    surface = font.render(text, True, colour)
    text_data = pygame.image.tostring(surface, "RGBA", True)

    # Position text
    glWindowPos2d(x, HEIGHT - y - surface.get_height())

    # Render text with transparency
    glDrawPixels(
        surface.get_width(), surface.get_height(),
        GL_RGBA, GL_UNSIGNED_BYTE, text_data
    )

# GAME HUD
def draw_hud(player, level):

    # Save current OpenGL state
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()

    glLoadIdentity()

    # Switch to 2D screen coordinates
    glOrtho(0, WIDTH, HEIGHT, 0, -1, 1)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()

    glLoadIdentity()

    # Disable 3D rendering features
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_LIGHTING)

    # Enable transparency
    glEnable(GL_BLEND)

    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # HUD background
    glColor4f(0.01, 0.03, 0.10, 0.85)

    glBegin(GL_QUADS)

    glVertex2f(15, 15)
    glVertex2f(300, 15)
    glVertex2f(300, 125)
    glVertex2f(15, 125)

    glEnd()

    # HUD border
    glColor3f(0.1, 0.6, 1.0)

    glLineWidth(2)

    glBegin(GL_LINE_LOOP)

    glVertex2f(15, 15)
    glVertex2f(300, 15)
    glVertex2f(300, 125)
    glVertex2f(15, 125)

    glEnd()

    # Calculate enemy count
    enemies_remaining = len(level.tesseracts)

    # Display HUD information
    draw_text(
        "COSMOTRON",
        30, 25, 30,
        (50, 180, 255)
    )

    draw_text(
        f"Enemies Remaining: {enemies_remaining}",
        30, 65, 25,
        (255, 255, 255)
    )

    draw_text(
        f"Enemies Destroyed: {player.enemies_destroyed}",
        30, 95, 25,
        (100, 255, 150)
    )

    # Restore OpenGL state
    glDisable(GL_BLEND)

    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()

    glMatrixMode(GL_MODELVIEW)

# DRAW HUD CONTROLS
def draw_controls():
    # Save the current OpenGL matrices
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, WIDTH, HEIGHT, 0, -1, 1)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Set up 2D overlay rendering
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Background panel in the bottom-left corner
    panel_x = 20
    panel_y = HEIGHT - 145
    panel_width = 220
    panel_height = 125

    glColor4f(0.02, 0.04, 0.10, 0.8)

    glBegin(GL_QUADS)
    glVertex2f(panel_x, panel_y)
    glVertex2f(panel_x + panel_width, panel_y)
    glVertex2f(panel_x + panel_width, panel_y + panel_height)
    glVertex2f(panel_x, panel_y + panel_height)
    glEnd()

    # Panel border
    glColor4f(0.2, 0.6, 1.0, 0.9)

    glBegin(GL_LINE_LOOP)
    glVertex2f(panel_x, panel_y)
    glVertex2f(panel_x + panel_width, panel_y)
    glVertex2f(panel_x + panel_width, panel_y + panel_height)
    glVertex2f(panel_x, panel_y + panel_height)
    glEnd()

    # Control labels
    draw_text("CONTROLS", 35, HEIGHT - 130, 22, (50, 180, 255))
    draw_text("A       -       Move Left", 35, HEIGHT - 98, 18)
    draw_text("D       -       Move Right", 35, HEIGHT - 70, 18)
    draw_text("SPACE   -       Shoot", 35, HEIGHT - 42, 18)

    # Restore OpenGL state and matrices
    glDisable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()

    glMatrixMode(GL_MODELVIEW)

# DRAW MENU BUTTON
def draw_button(text, x, y, width, height, mouse_pos, font_size=40):

    mouse_x, mouse_y = mouse_pos
    hovered = (x <= mouse_x <= x + width and y <= mouse_y <= y + height)

    if hovered:
        glColor3f(0.1, 0.5, 0.9)
    else:
        glColor3f(0.05, 0.15, 0.3)

    glBegin(GL_QUADS)

    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)

    glEnd()

    # Button border
    glColor3f(0.2, 0.7, 1.0)

    glLineWidth(2)

    glBegin(GL_LINE_LOOP)

    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)

    glEnd()

    # Button text
    font = pygame.font.Font(None, font_size)

    text_surface = font.render(text, True, (255, 255, 255))

    text_width = text_surface.get_width()
    text_height = text_surface.get_height()

    draw_text(
        text, x + (width - text_width) // 2,
        y + (height - text_height) // 2, font_size
    )

    return hovered

# MAIN MENU
def main_menu():

    setup_menu()

    while True:

        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return EXIT

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_RETURN:
                    return GAME

                if event.key == pygame.K_ESCAPE:
                    return EXIT

            if event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:

                    mouse_x, mouse_y = event.pos

                    if 350 <= mouse_x <= 650:

                        if 350 <= mouse_y <= 420:
                            return GAME

                        if 450 <= mouse_y <= 520:
                            return EXIT

        # Clear screen
        glClearColor(0.01, 0.01, 0.08, 1.0)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glLoadIdentity()

        # Background
        glColor3f(0.01, 0.02, 0.10)

        glBegin(GL_QUADS)

        glVertex2f(0, 0)
        glVertex2f(WIDTH, 0)
        glVertex2f(WIDTH, HEIGHT)
        glVertex2f(0, HEIGHT)

        glEnd()

        # Game title
        draw_text(
            "COSMOTRON",
            260, 150,
            100,
            (50, 180, 255)
        )

        draw_text(
            "SPACE COMBAT",
            395, 250,
            40,
            (180, 210, 255)
        )

        # Buttons
        draw_button(
            "START GAME",
            350, 350,
            300, 70,
            mouse_pos
        )

        draw_button(
            "QUIT GAME",
            350, 450,
            300, 70,
            mouse_pos
        )

        # Instructions
        draw_text(
            "Press ENTER to start",
            390, 590, 30,
            (150, 170, 200)
        )

        pygame.display.flip()

        pygame.time.Clock().tick(60)

# GAME
def run_game():

    # Restore 3D projection
    glDisable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)

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

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    running = False

        # Keyboard controls
        keys = pygame.key.get_pressed()

        # Update player
        player.update(keys, delta_time)

        # Update tesseract animations
        level.update_tesseracts(delta_time)

        # Clear screen
        glClearColor(0.01, 0.01, 0.05, 1.0)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glLoadIdentity()

        # Camera follows spacecraft
        player.update_camera()

        # Update map loading position
        level.update(player.z)

        # Draw level
        level.draw()

        # Draw player
        player.draw()

        # Draw player bullets
        player.draw_bullets()

        # Draw 2D HUD over 3D game
        draw_hud(player, level)
        draw_controls()

        pygame.display.flip()

    # Clean up
    player.cleanup()

# MAIN
def run():

    print("CosmoTron started!")

    pygame.init()

    pygame.display.set_mode(
        (WIDTH, HEIGHT),
        pygame.DOUBLEBUF | pygame.OPENGL
    )

    pygame.display.set_caption("CosmoTron")

    # Preserve original PNG colors
    glDisable(GL_LIGHTING)

    # Main application loop
    while True:

        choice = main_menu()

        if choice == EXIT:
            break

        if choice == GAME:
            run_game()

    pygame.quit()

"""
REFERENCE LIST


"""