import pygame
import trimesh
import numpy as np

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

        # UPLOAD PLAYER MODEL TO GPU
        self.player_vbo, self.player_vertex_count = self.create_mesh_vbo(
            self.vertices,
            self.faces,
            self.normals,
            self.uv_coordinates
        )

        # CAMERA SETTINGS
        self.camera_distance = 6.0
        self.camera_height = 2.5
        self.camera_look_height = 0.5
        self.camera_fov = 55.0  # Narrower horizontal view

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
        self.boost_max_speed = 9.5
        self.boost_deceleration = 1.5

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

        # UPLOAD BULLET MODEL TO GPU
        self.bullet_vbo, self.bullet_vertex_count = self.create_mesh_vbo(
            self.bullet_vertices,
            self.bullet_faces,
            self.bullet_normals,
            self.bullet_uv_coordinates
        )

        # BULLET TEXTURE
        self.bullet_texture_id = self.load_texture(
            "assets/player/bullet/bomber.png"
        )

        # BULLET SETTINGS
        self.bullets = []

        self.bullet_speed = 40.0
        self.bullet_cooldown = 0.3
        self.bullet_timer = 0.0
        self.bullet_scale = 0.2
        self.max_bullets = 10

        # BULLET SOUND EFFECT
        self.shoot_sound = pygame.mixer.Sound(
            "assets/soundtracks/blast01.mp3"
        )

        self.shoot_sound.set_volume(0.35)

        # Bullet collision radius
        self.bullet_collision_radius = 0.15

    # CREATE GPU MESH BUFFER
    def create_mesh_vbo(self, vertices, faces, normals, uv_coordinates):

        # Expand indexed geometry into a triangle list
        triangle_vertices = vertices[faces].reshape(-1, 3)

        # Repeat each face normal for its three vertices
        triangle_normals = np.repeat(normals, 3, axis=0)

        # Use UV coordinates if available
        if uv_coordinates is not None:
            triangle_uvs = uv_coordinates[faces].reshape(-1, 2)
        else:
            triangle_uvs = np.zeros(
                (len(triangle_vertices), 2),
                dtype=np.float32
            )

        # Interleaved layout:
        # U, V, NX, NY, NZ, X, Y, Z
        mesh_data = np.hstack((
            triangle_uvs,
            triangle_normals,
            triangle_vertices
        )).astype(np.float32)

        mesh_data = np.ascontiguousarray(mesh_data)

        # Upload geometry to GPU
        vbo = glGenBuffers(1)

        glBindBuffer(GL_ARRAY_BUFFER, vbo)

        glBufferData(
            GL_ARRAY_BUFFER, mesh_data.nbytes,
            mesh_data, GL_STATIC_DRAW
        )

        glBindBuffer(GL_ARRAY_BUFFER, 0)

        return vbo, len(triangle_vertices)

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

    # Shoot Bullet
    def shoot(self):

        # Prevent exceeding the bullet limit
        if len(self.bullets) >= self.max_bullets:
            return

        # Create bullet at spacecraft position
        bullet = {
            "x": self.x,
            "y": self.y,
            "z": self.z - 1.5
        }

        self.bullets.append(bullet)

        # Play shooting sound effect
        self.shoot_sound.play()

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

                    # Check destructible walls first
                    destroyed_wall = self.level_map.check_destructible_wall_collision(
                        bullet["x"],
                        check_z,
                        self.bullet_collision_radius
                    )

                    if destroyed_wall:
                        hit_wall = True
                        break

                    # Check normal, indestructible walls
                    if self.level_map.collides_with_wall(
                            bullet["x"],
                            check_z,
                            self.bullet_collision_radius):
                        # Only remove the bullet if it hit a normal wall
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
        # CAMERA SETTINGS
        camera_distance = 5.0
        camera_height = 2.2
        look_height = 0.5

        # Camera position behind the spaceship
        camera_x = self.x
        camera_y = self.y + camera_height
        camera_z = self.z + camera_distance

        # Camera target
        target_x = self.x
        target_y = self.y + look_height
        target_z = self.z

        gluLookAt(camera_x, camera_y, camera_z, target_x, target_y, target_z, 0, 1, 0)

    # Draw player code
    def draw(self):

        glPushMatrix()

        # Position spacecraft
        glTranslatef(self.x, self.y, self.z)

        # Apply spacecraft rotation
        glRotatef(self.rotation, 0, 0, 1)

        # Enable player texture when available
        if self.texture_id is not None and self.uv_coordinates is not None:

            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)

            glTexEnvi(
                GL_TEXTURE_ENV,
                GL_TEXTURE_ENV_MODE,
                GL_MODULATE
            )

        else:
            glDisable(GL_TEXTURE_2D)

        # Preserve original model colours
        glColor4f(1.0, 1.0, 1.0, 1.0)

        # Bind player geometry
        glBindBuffer(GL_ARRAY_BUFFER, self.player_vbo)

        # Interleaved layout: UV, normal, vertex
        glInterleavedArrays(
            GL_T2F_N3F_V3F,
            0,
            None
        )

        # Render entire player mesh in one draw call
        glDrawArrays(
            GL_TRIANGLES,
            0,
            self.player_vertex_count
        )

        # Disable client-side arrays
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)

        # Unbind VBO and texture
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindTexture(GL_TEXTURE_2D, 0)

        glDisable(GL_TEXTURE_2D)

        glPopMatrix()

    # Draw bullets code
    def draw_bullets(self):

        if not self.bullets:
            return

        # Enable bullet texture
        if self.bullet_texture_id is not None and self.bullet_uv_coordinates is not None:

            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.bullet_texture_id)

            glTexEnvi(
                GL_TEXTURE_ENV,
                GL_TEXTURE_ENV_MODE,
                GL_MODULATE
            )

        else:
            glDisable(GL_TEXTURE_2D)

        glColor4f(1.0, 1.0, 1.0, 1.0)

        # Bind the shared bullet geometry once
        glBindBuffer(GL_ARRAY_BUFFER, self.bullet_vbo)

        glInterleavedArrays(
            GL_T2F_N3F_V3F,
            0,
            None
        )

        # Draw each bullet using the same GPU geometry
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

            glDrawArrays(
                GL_TRIANGLES,
                0,
                self.bullet_vertex_count
            )

            glPopMatrix()

        # Disable client-side arrays
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)

        # Unbind buffers and textures
        glBindBuffer(GL_ARRAY_BUFFER, 0)
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

            if self.lives <= 0:
                self.dead = True

        # Allow another collision after the player moves away
        elif not collision_detected:
            self.tesseract_collision_active = False

    # Check tesseract bullet collision
    def check_tesseract_bullet_collision(self, bullet, previous_position):

        if self.level_map is None:
            return False

        # Previous bullet position
        px, py, pz = previous_position

        # Bullet movement vector
        dx = bullet["x"] - px
        dy = bullet["y"] - py
        dz = bullet["z"] - pz

        length_squared = dx * dx + dy * dy + dz * dz

        tesseracts = self.level_map.tesseracts

        # Check each enemy
        for index, tesseract in enumerate(tesseracts):

            # Closest point on bullet trajectory
            if length_squared > 0:
                t = ((tesseract.x - px) * dx + (tesseract.y - py) * dy +
                            (tesseract.z - pz) * dz) / length_squared

                t = max(0.0, min(1.0, t))

            else:
                t = 0.0

            # Calculate closest point
            closest_x = px + t * dx
            closest_y = py + t * dy
            closest_z = pz + t * dz

            # Calculate squared distance
            distance_squared = (
                    (closest_x - tesseract.x) ** 2 +
                    (closest_y - tesseract.y) ** 2 +
                    (closest_z - tesseract.z) ** 2
            )

            # Combined collision radius
            collision_distance = (
                    self.bullet_collision_radius +
                    tesseract.radius + 0.15
            )

            # Check collision
            if distance_squared <= collision_distance * collision_distance:
                # Remove the enemy without copying the list
                tesseracts.pop(index)

                self.enemies_destroyed += 1

                return True

        return False

    # Cleanup code
    def cleanup(self):

        # Stop bullet sound effect
        if self.shoot_sound is not None:
            self.shoot_sound.stop()
            self.shoot_sound = None

        # Delete player VBO
        if self.player_vbo is not None:
            glDeleteBuffers(1, [self.player_vbo])
            self.player_vbo = None

        # Delete bullet VBO
        if self.bullet_vbo is not None:
            glDeleteBuffers(1, [self.bullet_vbo])
            self.bullet_vbo = None

        # Release player texture
        if self.texture_id is not None:
            glDeleteTextures([self.texture_id])
            self.texture_id = None

        # Release bullet texture
        if self.bullet_texture_id is not None:
            glDeleteTextures([self.bullet_texture_id])
            self.bullet_texture_id = None

"""
REFERENCE LIST

Ericson, C., 2005. Real-Time Collision Detection.
San Francisco: Morgan Kaufmann.

Gregory, J., 2018. Game Engine Architecture.
3rd edn. Boca Raton: CRC Press.

Pillow, n.d. Pillow documentation. [Online] Available at:
https://pillow.readthedocs.io/
[Accessed: 10 November 2026].

Pygame, n.d. Pygame documentation. [Online] Available at:
https://www.pygame.org/docs/
[Accessed: 10 November 2026].

Shreiner, D., Sellers, G., Kessenich, J. and Licea-Kane, B., 2013.
OpenGL Programming Guide: The Official Guide to Learning OpenGL.
8th edn. Upper Saddle River, NJ: Addison-Wesley.

Trimesh, n.d. Trimesh documentation. [Online] Available at:
https://trimesh.org/
[Accessed: 10 November 2026].
"""