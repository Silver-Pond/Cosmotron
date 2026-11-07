import pygame
import trimesh

from OpenGL.raw.GLU import gluLookAt
from PIL import Image
from OpenGL.GL import *

class Player:

    def __init__(self, model_path, texture_path=None):

        # LOAD PLAYER OBJ MODEL
        self.mesh = trimesh.load(
            model_path,
            force = "mesh",
            process = False
        )

        # Center the model
        self.mesh.apply_translation(
            -self.mesh.centroid
        )

        # Normalize model size
        max_dimension = max(self.mesh.extents)

        if max_dimension > 0:
            self.mesh.apply_scale(2.0 / max_dimension)

        # Extract model geometry
        self.vertices = self.mesh.vertices
        self.faces = self.mesh.faces
        self.normals = self.mesh.face_normals

        # Extract UV coordinates
        self.uv_coordinates = None

        if hasattr(self.mesh.visual, "uv"):
            self.uv_coordinates = self.mesh.visual.uv

        # CAMERA SETTINGS
        self.camera_distance = 6.0
        self.camera_height = 2.5
        self.camera_look_height = 0.5

        # PLAYER STATUS
        self.alive = True

        # PLAYER POSITION
        self.x = 0.0
        self.y = -2.5
        self.z = 300

        # Player rotation
        self.rotation = 0.0

        # Movement speed
        self.speed = 5.0

        # Automatic forward movement
        self.forward_speed = 1.5

        # Forward movement acceleration (optional)
        self.forward_acceleration = 0.1

        # Maximum forward speed
        self.max_forward_speed = 2.5

        # Reference to level map
        self.level_map = None

        # Collision settings
        self.collision_radius_x = 0.75
        self.collision_radius_z = 0.75

        # PLAYER TEXTURE
        self.texture_id = self.load_texture(
            texture_path if texture_path is not None
            else "assets/player/pyro_can.png"
        )

        # LOAD BULLET OBJ MODEL
        self.bullet_mesh = trimesh.load(
            "assets/player/bullet/bomber.obj",
            force = "mesh",
            process = False
        )

        # Center bullet model
        self.bullet_mesh.apply_translation(
            -self.bullet_mesh.centroid
        )

        # Normalize bullet size
        max_dimension = max(self.bullet_mesh.extents)

        if max_dimension > 0:
            self.bullet_mesh.apply_scale(2.0 / max_dimension)

        # Extract bullet geometry
        self.bullet_vertices = self.bullet_mesh.vertices
        self.bullet_faces = self.bullet_mesh.faces
        self.bullet_normals = self.bullet_mesh.face_normals

        # Extract bullet UV coordinates
        self.bullet_uv_coordinates = None

        if hasattr(self.bullet_mesh.visual, "uv"):
            self.bullet_uv_coordinates = self.bullet_mesh.visual.uv

        # BULLET TEXTURE
        self.bullet_texture_id = self.load_texture(
            "assets/player/bullet/bomber.png"
        )

        # BULLET SETTINGS
        self.bullets = []

        self.bullet_speed = 40.0
        self.bullet_cooldown = 0.5
        self.bullet_timer = 0.0
        self.bullet_scale = 0.2
        self.max_bullets = 10

        # Bullet collision radius
        self.bullet_collision_radius = 0.15

        # DEBUG INFORMATION
        print("Player UV:", self.uv_coordinates is not None)
        print("Bullet UV:", self.bullet_uv_coordinates is not None)

        print("Player texture ID:", self.texture_id)
        print("Bullet texture ID:", self.bullet_texture_id)

    # Load textures
    def load_texture(self, texture_source):

        # Load texture image
        if isinstance(texture_source, Image.Image):
            image = texture_source.copy()

        else:
            image = Image.open(texture_source)

        # Convert image to RGBA
        image = image.convert("RGBA")

        # Flip image vertically for OpenGL
        image = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        image_data = image.tobytes()
        width, height = image.size

        # Generate OpenGL texture
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)

        # Texture filtering
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        # Texture wrapping
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        # Upload PNG texture to GPU
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
        glBindTexture(GL_TEXTURE_2D, 0)

        # Test log
        print("Spaceship texture loaded successfully!")
        return texture_id

    # Shoot code
    def shoot(self):

        if len(self.bullets) >= self.max_bullets:
            return

        # Spawn bullet at spaceship position
        bullet = {"x": self.x, "y": self.y, "z": self.z - 1.5}

        self.bullets.append(bullet)

    # Set level map for collision detection
    def set_level_map(self, level_map):
        self.level_map = level_map

    # Player area restriction
    def restrict_movement(self):

        if self.level_map is None:
            return

        # Get arena boundaries
        half_width = (self.level_map.columns * self.level_map.cell_size) / 2
        half_depth = (self.level_map.rows * self.level_map.cell_size) / 2

        # Calculate movement boundaries
        min_x = -half_width + self.collision_radius_x
        max_x = half_width - self.collision_radius_x

        min_z = -half_depth + self.collision_radius_z
        max_z = half_depth - self.collision_radius_z

        # Restrict player position
        self.x = max(min_x, min(self.x, max_x))
        self.z = max(min_z, min(self.z, max_z))

    # Update code

    def update(self, keys, delta_time):

        movement = self.speed * delta_time

        target_rotation = 0

        # Gradually increase forward speed
        self.forward_speed += (
                self.forward_acceleration * delta_time
        )

        # Limit maximum forward speed
        self.forward_speed = min(
            self.forward_speed,
            self.max_forward_speed
        )

        # PLAYER MOVEMENT AND COLLISION
        move_z = -self.forward_speed * delta_time
        move_x = 0

        if keys[pygame.K_a]:
            move_x = -movement
            target_rotation = 10

        elif keys[pygame.K_d]:
            move_x = movement
            target_rotation = -10

        if self.level_map is not None:

            # Horizontal collision (X)
            new_x = self.x + move_x

            if not self.level_map.collides_with_wall(
                    new_x, self.z, self.collision_radius_x
            ):
                self.x = new_x

            # Forward collision (Z)
            new_z = self.z + move_z

            if not self.level_map.collides_with_wall(
                    self.x, new_z, self.collision_radius_z
            ):
                self.z = new_z

        else:
            self.x += move_x
            self.z += move_z

        # Restrict player movement to arena
        self.restrict_movement()

        # Smoothly interpolate rotation
        tilt_speed = 8

        self.rotation += (
                (target_rotation - self.rotation)
                * min(tilt_speed * delta_time, 1)
        )

        # SHOOTING COOLDOWN
        self.bullet_timer -= delta_time

        # Shoot while SPACE is held
        if keys[pygame.K_SPACE] and self.bullet_timer <= 0:
            self.shoot()
            self.bullet_timer = self.bullet_cooldown

        # UPDATE BULLETS, WALL AND TESSERACT COLLISIONS
        active_bullets = []

        for bullet in self.bullets:

            # Store previous bullet position
            previous_z = bullet["z"]

            # Move bullet forward
            bullet["z"] -= self.bullet_speed * delta_time

            # CHECK TESSERACT COLLISION FIRST
            hit_tesseract = self.check_tesseract_collision(
                bullet,
                previous_z
            )

            # CHECK WALL COLLISION
            hit_wall = False

            if not hit_tesseract and self.level_map is not None:

                # Check bullet's new position
                if self.level_map.collides_with_wall(
                        bullet["x"],
                        bullet["z"],
                        self.bullet_collision_radius
                ):
                    hit_wall = True

                # Check intermediate positions to prevent
                # bullets passing through walls
                if not hit_wall:

                    distance = abs(bullet["z"] - previous_z)

                    steps = max(
                        1,
                        int(
                            distance /
                            (self.level_map.cell_size * 0.2)
                        ) + 1
                    )

                    for step in range(1, steps):

                        check_z = previous_z + (
                                (bullet["z"] - previous_z)
                                * (step / steps)
                        )

                        if self.level_map.collides_with_wall(
                                bullet["x"],
                                check_z,
                                self.bullet_collision_radius
                        ):
                            hit_wall = True
                            break

            # KEEP SURVIVING BULLETS
            if (
                    not hit_wall
                    and not hit_tesseract
                    and bullet["z"] > -200
            ):
                active_bullets.append(bullet)

        # Replace bullet list with surviving bullets
        self.bullets = active_bullets

    # Update camera code
    def update_camera(self):
        camera_distance = 6.0
        camera_height = 2.5
        look_height = 0.5

        # Fixed camera position behind the spaceship
        camera_x = self.x
        camera_y = self.y + camera_height
        camera_z = self.z + camera_distance

        # Look towards the spaceship
        target_x = self.x
        target_y = self.y + look_height
        target_z = self.z

        gluLookAt(camera_x, camera_y, camera_z, target_x, target_y, target_z, 0, 1, 0)

    # Draw player code
    def draw(self):

        glPushMatrix()

        # Position spacecraft
        glTranslatef(self.x, self.y, self.z)

        # Rotate spacecraft
        glRotatef(self.rotation, 0, 0, 1)

        # Enable texture mapping
        if (self.texture_id is not None and self.uv_coordinates is not None):
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
            glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

        else:
            glDisable(GL_TEXTURE_2D)

        # White tint preserves original texture colours
        glColor4f(1, 1, 1, 1)

        # Render model
        glBegin(GL_TRIANGLES)

        for i, face in enumerate(self.faces):

            # Surface normal
            glNormal3fv(self.normals[i])

            for vertex_index in face:

                # Apply UV texture coordinates
                if self.uv_coordinates is not None:

                    glTexCoord2fv(self.uv_coordinates[vertex_index])

                # Draw vertex
                glVertex3fv(self.vertices[vertex_index])

        glEnd()

        # Disable texture
        glBindTexture(GL_TEXTURE_2D, 0)
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()

    # Draw bullets code
    def draw_bullets(self):

        # Enable bullet texture
        if self.bullet_texture_id is not None:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.bullet_texture_id)
            glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

        else:
            glDisable(GL_TEXTURE_2D)

        glColor4f(1, 1, 1, 1)

        # Render each bullet
        for bullet in self.bullets:

            glPushMatrix()

            glTranslatef(
                bullet["x"],
                bullet["y"],
                bullet["z"]
            )

            glScalef(
                self.bullet_scale,
                self.bullet_scale,
                self.bullet_scale
            )

            glBegin(GL_TRIANGLES)

            for i, face in enumerate(self.bullet_faces):
                glNormal3fv(self.bullet_normals[i])

                for vertex_index in face:
                    if self.bullet_uv_coordinates is not None:
                        glTexCoord2fv(self.bullet_uv_coordinates[vertex_index])

                    glVertex3fv(self.bullet_vertices[vertex_index])

            glEnd()

            glPopMatrix()

        # Disable bullet texture
        glBindTexture(GL_TEXTURE_2D, 0)
        glDisable(GL_TEXTURE_2D)

    # Tesseract bullet collision code
    def check_tesseract_collision(self, bullet, previous_z):

        if self.level_map is None:
            return False

        for tesseract in self.level_map.tesseracts:

            dx = bullet["x"] - tesseract.x
            dy = bullet["y"] - tesseract.y

            # Check bullet's movement along Z
            min_z = min(previous_z, bullet["z"])
            max_z = max(previous_z, bullet["z"])

            closest_z = max(
                min_z,
                min(tesseract.z, max_z)
            )

            dz = closest_z - tesseract.z

            distance = (dx ** 2 + dy ** 2 + dz ** 2) ** 0.5

            collision_distance = (
                    self.bullet_collision_radius +
                    tesseract.radius
            )

            if distance < collision_distance:
                self.level_map.tesseracts.remove(tesseract)

                return True

        return False

    # Cleanup code
    def cleanup(self):

        # Release spaceship texture
        if self.texture_id is not None:
            glDeleteTextures([self.texture_id])
            self.texture_id = None

        # Release bullet texture
        if self.bullet_texture_id is not None:
            glDeleteTextures([self.bullet_texture_id])
            self.bullet_texture_id = None

"""
REFERENCE LIST


"""