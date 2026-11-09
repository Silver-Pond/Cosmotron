import pygame
import trimesh

from OpenGL.raw.GLU import gluLookAt
from PIL import Image
from OpenGL.GL import *

class Player:

    def __init__(self, model_path, texture_path = None):

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
        self.lives = 1
        self.tesseract_collision_active = False
        self.player_collision_radius = 0.75
        self.dead = False

        # ENEMY KILL COUNT
        self.enemies_destroyed = 0

        # PLAYER POSITION
        self.x = 0.0
        self.y = -2.5
        self.z = 300

        # Player rotation
        self.rotation = 0.0

        # Movement speed
        self.speed = 11.5

        # Automatic forward movement
        self.forward_speed = 3

        # Forward movement acceleration (optional)
        self.forward_acceleration = 0.2

        # Maximum forward speed
        self.max_forward_speed = 5

        # Boost movement
        self.boost_acceleration = 0.5
        self.boost_max_speed = 8.0
        self.boost_deceleration = 2.0

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
        self.bullet_cooldown = 0.2
        self.bullet_timer = 0.0
        self.bullet_scale = 0.2
        self.max_bullets = 10

        # Bullet collision radius
        self.bullet_collision_radius = 0.15

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
        self.forward_speed += self.forward_acceleration * delta_time

        # W - Boost forward speed
        if keys[pygame.K_w]:

            self.forward_speed += self.boost_acceleration * delta_time

            # Allow the player to exceed normal maximum speed
            self.forward_speed = min(
                self.forward_speed,
                self.boost_max_speed
            )

        else:
            # Gradually return to normal maximum speed
            self.forward_speed = max(
                self.max_forward_speed,
                self.forward_speed - self.boost_deceleration * delta_time
            )

            # Prevent exceeding normal maximum speed
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
                    new_x, self.z, self.collision_radius_x):
                self.x = new_x

            # Forward collision (Z)
            new_z = self.z + move_z

            if not self.level_map.collides_with_wall(
                    self.x, new_z, self.collision_radius_z):
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
            previous_position = (
                bullet["x"], bullet["y"], bullet["z"]
            )

            # Move bullet forward
            bullet["z"] -= self.bullet_speed * delta_time

            # TESSERACT COLLISION
            hit_tesseract = self.check_tesseract_bullet_collision(
                bullet, previous_position
            )

            if hit_tesseract:
                # Bullet disappears after hitting enemy
                continue

            # WALL COLLISION
            hit_wall = False

            if self.level_map is not None:

                # Check bullet's movement between frames
                previous_z = previous_position[2]

                distance = abs(bullet["z"] - previous_z)
                steps = max(1, int(distance / (self.level_map.cell_size * 0.2)) + 1)

                for step in range(steps + 1):

                    progress = step / steps
                    check_z = previous_z + ((bullet["z"] - previous_z) * progress)

                    if self.level_map.collides_with_wall(
                            bullet["x"], check_z,
                            self.bullet_collision_radius):
                        hit_wall = True
                        break

            if hit_wall:
                continue

            # BULLET LIFETIME / ARENA LIMIT
            if bullet["z"] > -200:
                active_bullets.append(bullet)

        # Replace bullet list
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
        if self.texture_id is not None and self.uv_coordinates is not None:
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

            glTranslatef(bullet["x"], bullet["y"], bullet["z"])
            glScalef(self.bullet_scale, self.bullet_scale, self.bullet_scale)

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

    # Check tesseract collision
    def check_tesseract_collision(self, tesseracts):
        collision_detected = False

        for tesseract in tesseracts:
            dx = self.x - tesseract.x
            dy = self.y - tesseract.y
            dz = self.z - tesseract.z

            distance_squared = dx * dx + dy * dy + dz * dz

            collision_distance = (
                    self.player_collision_radius + tesseract.radius
            )

            if distance_squared <= collision_distance ** 2:
                collision_detected = True
                break

        # Only deduct a life once per contact
        if collision_detected and not self.tesseract_collision_active:
            self.lives -= 1
            self.tesseract_collision_active = True

            print("PLAYER HIT BY TESSERACT!")
            print("Lives remaining:", self.lives)

            if self.lives <= 0:
                self.dead = True
                print("PLAYER DIED!")

        # Allow another collision after the player moves away
        elif not collision_detected:
            self.tesseract_collision_active = False

    # Check tesseract bullet collision
    def check_tesseract_bullet_collision(self, bullet, previous_position):

        if self.level_map is None:
            return False

        # Previous bullet position
        px, py, pz = previous_position

        # Current bullet position
        cx = bullet["x"]
        cy = bullet["y"]
        cz = bullet["z"]

        # Bullet movement vector
        dx = cx - px
        dy = cy - py
        dz = cz - pz

        length_squared = dx * dx + dy * dy + dz * dz

        for tesseract in self.level_map.tesseracts[:]:

            # Find the closest point on bullet trajectory
            if length_squared > 0:

                t = ((tesseract.x - px) * dx + (tesseract.y - py) * dy +
                            (tesseract.z - pz) * dz) / length_squared

                t = max(0.0, min(1.0, t))

            else:
                t = 0.0

            # Closest point
            closest_x = px + t * dx
            closest_y = py + t * dy
            closest_z = pz + t * dz

            # Distance to tesseract centre
            distance_squared = (
                    (closest_x - tesseract.x) ** 2 +
                    (closest_y - tesseract.y) ** 2 +
                    (closest_z - tesseract.z) ** 2
            )

            # Adjusted collision radius
            collision_distance = (
                    self.bullet_collision_radius +
                    tesseract.radius + 0.15
            )

            if distance_squared <= collision_distance ** 2:
                self.level_map.tesseracts.remove(tesseract)

                self.enemies_destroyed += 1

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