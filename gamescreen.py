import math
import pygame

from OpenGL.GL import *
from OpenGL.GLU import *
from player.player import Player
from levels.levels import LevelMap, LEVEL_MAPS

# MENU SETTINGS
WIDTH = 1000
HEIGHT = 700

MENU = 0
GAME = 1
EXIT = 2
GAME_OVER = 3
GAME_COMPLETED = 4

# MENU SOUNDTRACK
MENU_MUSIC = "assets/soundtracks/astroid_belt.mp3"
GAME_MUSIC = "assets/soundtracks/smoothcalamity.mp3"

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

    draw_text(
        f"Time: {int(level.timer // 60):02d}:{int(math.ceil(level.timer % 60)):02d}",
        30, 165, 25,
        (255, 255, 100)
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

    # Control labels - compact bottom-left layout
    draw_text("CONTROLS", panel_x + 12, panel_y + panel_height - 115,
              18, (50, 180, 255))

    draw_text("W  -  Accelerate", panel_x + 12, panel_y + panel_height - 90, 15)
    draw_text("A  -  Move Left", panel_x + 12, panel_y + panel_height - 68, 15)
    draw_text("D  -  Move Right", panel_x + 12, panel_y + panel_height - 46, 15)
    draw_text("SPACE  -  Shoot", panel_x + 12, panel_y + panel_height - 24, 15)

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

# PLAY MENU SOUNDTRACK
def play_menu_music():

    pygame.mixer.music.load(MENU_MUSIC)

    # -1 means repeat indefinitely
    pygame.mixer.music.play(-1)

    # Set soundtrack volume (0.0 - 1.0)
    pygame.mixer.music.set_volume(0.5)

# PLAY GAMEPLAY SOUNDTRACK
def play_game_music():

    pygame.mixer.music.load(GAME_MUSIC)

    # Repeat indefinitely
    pygame.mixer.music.play(-1)

    # Gameplay soundtrack volume
    pygame.mixer.music.set_volume(0.4)

# MAIN MENU
def main_menu():

    setup_menu()

    # Start soundtrack when entering the menu
    if not pygame.mixer.music.get_busy():
        play_menu_music()

    clock = pygame.time.Clock()

    while True:

        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                pygame.mixer.music.stop()
                return EXIT

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_RETURN:

                    # Stop menu soundtrack before gameplay
                    pygame.mixer.music.stop()

                    return GAME

                if event.key == pygame.K_ESCAPE:

                    pygame.mixer.music.stop()
                    return EXIT

            if event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:

                    mouse_x, mouse_y = event.pos

                    if 350 <= mouse_x <= 650:

                        if 350 <= mouse_y <= 420:

                            # Stop menu soundtrack before gameplay
                            pygame.mixer.music.stop()

                            return GAME

                        if 450 <= mouse_y <= 520:

                            pygame.mixer.music.stop()
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
            260, 150, 100,
            (50, 180, 255)
        )

        draw_text(
            "SPACE COMBAT",
            395, 250, 40,
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

        draw_text(
            "Press ESC to exit",
            410, 620, 30,
            (150, 170, 200)
        )

        pygame.display.flip()

        clock.tick(60)

# GAME OVER SCREEN
def game_over_screen(player, level, reason):

    setup_menu()

    clock = pygame.time.Clock()

    while True:

        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return EXIT

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_RETURN:
                    return MENU

            if event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:

                    mouse_x, mouse_y = event.pos

                    # MAIN MENU
                    if 350 <= mouse_x <= 650:
                        if 500 <= mouse_y <= 570:
                            return MENU

        # Clear screen
        glClearColor(0.01, 0.01, 0.08, 1.0)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glLoadIdentity()

        # Background
        glColor3f(0.01, 0.01, 0.01)

        glBegin(GL_QUADS)

        glVertex2f(0, 0)
        glVertex2f(WIDTH, 0)
        glVertex2f(WIDTH, HEIGHT)
        glVertex2f(0, HEIGHT)

        glEnd()

        # GAME OVER TITLE
        draw_text(
            "GAME OVER",
            245, 200, 120,
            (255, 255, 255)
        )

        # Display reason
        draw_text(
            reason,
            320, 360, 35,
            (255, 200, 100)
        )

        # Game statistics
        draw_text(
            f"Enemies Destroyed: {player.enemies_destroyed}",
            390, 400, 30,
            (100, 220, 255)
        )

        # MAIN MENU BUTTON
        draw_button(
            "CONTINUE",
            350, 500,
            300, 70,
            mouse_pos
        )

        # Instructions
        draw_text(
            "Press ENTER to continue",
            400, 610, 25,
            (150, 170, 200)
        )

        pygame.display.flip()

        clock.tick(60)

# GAME COMPLETED SCREEN
def game_completed_screen(player):

    setup_menu()

    clock = pygame.time.Clock()

    while True:

        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return EXIT

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_RETURN:
                    return MENU

                if event.key == pygame.K_ESCAPE:
                    return EXIT

            if event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:

                    mouse_x, mouse_y = event.pos

                    # MAIN MENU BUTTON
                    if 350 <= mouse_x <= 650:
                        if 460 <= mouse_y <= 530:
                            return MENU

                    # QUIT BUTTON
                    if 350 <= mouse_x <= 650:
                        if 550 <= mouse_y <= 620:
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

        # COMPLETION TITLE
        draw_text(
            "MISSION COMPLETED!",
            150, 150, 90,
            (50, 220, 255)
        )

        # Congratulations message
        draw_text(
            "CONGRATULATIONS, PILOT!",
            330, 270, 35,
            (255, 255, 255)
        )

        draw_text(
            "You have successfully completed all levels.",
            295, 325, 28,
            (180, 210, 255)
        )

        # Final statistics
        draw_text(
            f"Enemies Destroyed: {player.enemies_destroyed}",
            390, 390, 30,
            (100, 255, 150)
        )

        # MAIN MENU BUTTON
        draw_button(
            "MAIN MENU",
            350, 460,
            300, 70,
            mouse_pos,
            font_size=35
        )

        # QUIT BUTTON
        draw_button(
            "QUIT GAME",
            350, 550,
            300, 70,
            mouse_pos,
            font_size=35
        )

        # Instructions
        draw_text(
            "Press ENTER for the main menu",
            380, 650, 22,
            (150, 170, 200)
        )

        pygame.display.flip()

        clock.tick(60)

# GAME
def run_game():

    # Start gameplay soundtrack
    play_game_music()

    # Load level-switch sound effect
    level_switch_sound = pygame.mixer.Sound(
        "assets/soundtracks/lvlswitch.mp3"
    )

    level_switch_sound.set_volume(0.5)

    # Load game-over sound effect
    game_over_sound = pygame.mixer.Sound(
        "assets/soundtracks/game_over.mp3"
    )

    game_over_sound.set_volume(0.5)

    # Restore 3D projection
    glDisable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)

    glLoadIdentity()

    gluPerspective(45, WIDTH / HEIGHT, 0.1, 100.0)

    glMatrixMode(GL_MODELVIEW)

    # LEVEL MANAGEMENT
    level_index = 0

    # Load first level
    level = LevelMap(LEVEL_MAPS[level_index])

    # Create player spacecraft
    player = Player(
        model_path="assets/player/pyro_can.obj",
        texture_path="assets/player/pyro_can.png"
    )

    # Connect level map to player
    player.set_level_map(level)

    clock = pygame.time.Clock()

    running = True

    completed_all_levels = False

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

        # Update portal animation
        level.update_portal(delta_time)

        # Update black-hole animations
        level.update_black_holes(delta_time)

        # Update countdown timer
        level.update_timer(delta_time)

        # Check collision between player and tesseracts
        player.check_tesseract_collision(level.tesseracts)

        # Check collision with black holes
        for black_hole in level.black_holes:

            if black_hole.check_collision(player):
                print("PLAYER DESTROYED BY BLACK HOLE!")

                player.dead = True
                break

        # End the game when the player has no lives left
        # Check game over conditions
        if player.dead:
            game_over_reason = "YOUR SHIP WAS DESTROYED!"
            running = False
            break

        elif level.time_up:
            game_over_reason = "----TIME HAS RUN OUT!---"
            running = False
            break

        # CHECK PORTAL
        if level.check_portal_collision(player):

            print("PORTAL ENTERED!")

            # Play level-switch sound
            level_switch_sound.play()

            # Check whether another level exists
            if level_index + 1 < len(LEVEL_MAPS):

                level_index += 1

                print("Loading Level:", level_index + 1)

                # Replace the current map
                level = LevelMap(LEVEL_MAPS[level_index])

                # Connect the player to the new level
                player.set_level_map(level)

                # Reset player position to the center of the new map
                player.x = 0.0
                player.z = 300.0

                # Continue with the next level
                continue

            else:
                print("ALL LEVELS COMPLETED!")

                running = False
                completed_all_levels = True
                break

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

    # Stop gameplay soundtrack
    pygame.mixer.music.stop()

    # Show game over screen
    if player.dead or level.time_up:

        # Play game-over sound
        game_over_sound.play()

        # Wait until the sound finishes
        while game_over_sound.get_num_channels() > 0:
            pygame.time.wait(50)

        return game_over_screen(player, level, game_over_reason)

    # All levels completed
    if completed_all_levels:
        print("DISPLAYING GAME COMPLETED SCREEN!")

        return game_completed_screen(player)

    # ESC pressed - return to main menu
    return MENU

# MAIN
def run():

    pygame.init()

    # Initialise audio mixer
    pygame.mixer.init()

    pygame.display.set_mode(
        (WIDTH, HEIGHT),
        pygame.DOUBLEBUF | pygame.OPENGL
    )

    # Display screen caption
    pygame.display.set_caption("CosmoTron")

    # Preserve original PNG colors
    glDisable(GL_LIGHTING)

    # Main application loop
    while True:

        choice = main_menu()

        if choice == EXIT:
            break

        if choice == GAME:

            while True:

                result = run_game()

                if result == EXIT:
                    pygame.quit()
                    return

                elif result == MENU:
                    break

                elif result == GAME:
                    # Start a fresh game
                    continue

    # Stop any remaining music
    pygame.mixer.music.stop()

    pygame.quit()

"""
REFERENCE LIST

Gregory, J., 2018. Game Engine Architecture. 3rd edn.
Boca Raton: CRC Press.

Pygame, n.d. Pygame documentation. [Online] Available at:
https://www.pygame.org/docs/
[Accessed: 10 November 2026].

Python Software Foundation, n.d. math — Mathematical functions.
Python documentation. [Online] Available at:
https://docs.python.org/3/library/math.html
[Accessed: 10 November 2026].

Rogers, S., 2014. Level Up! The Guide to Great Video Game Design.
2nd edn. Chichester: Wiley.

Shreiner, D., Sellers, G., Kessenich, J. and Licea-Kane, B., 2013.
OpenGL Programming Guide: The Official Guide to Learning OpenGL.
8th edn. Upper Saddle River, NJ: Addison-Wesley.
"""