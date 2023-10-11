import datetime

import numpy as np
import pygame
import shapely

from entities.player import Player
from entities.terrain import Terrain
from systems import (
    bootstrap_terrain,
    debug_raycasting,
    generate_terrain_factory,
    process_collisions,
    set_start_platform,
    update_jump_cooldown,
    update_platform_status,
    update_position,
    update_terrain_offset,
    update_velocity,
)


class Scene:
    def __init__(
        self,
        render=True,
        interactive=True,
        show_rays=False,
        screen_dimensions=(1440, 900),
    ):
        self.render = render
        self.interactive = interactive
        self.debug_raycasting = show_rays
        self.screen_dimensions = screen_dimensions

        if render is False and interactive is True:
            raise ValueError("Cannot be interactive without rendering")

        if self.render:
            pygame.init()
            flags = pygame.DOUBLEBUF | pygame.SCALED | pygame.RESIZABLE
            self.screen = pygame.display.set_mode(
                self.screen_dimensions, flags, vsync=1
            )
            self.clock = pygame.time.Clock()
            self.background = pygame.image.load("assets/background.jpg")
        self.dt = 0

        random_seed = np.random.randint(0, 100000)
        self.player = Player(20, "#3D93AF", *self.screen_dimensions)
        self.terrain = Terrain(200, random_seed, *self.screen_dimensions)
        self.iteration = 0

        # systems ran once
        self.generate_terrain = generate_terrain_factory(self.terrain)
        bootstrap_terrain(self.terrain)
        set_start_platform(self.player, self.terrain)

    def run(self):
        start_time = datetime.datetime.now().timestamp()

        running = True
        while running:
            if self.render:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

            if self.render and self.interactive:
                keys = pygame.key.get_pressed()
                game_input = {
                    "jump": keys[pygame.K_SPACE],
                    "left": keys[pygame.K_a],
                    "right": keys[pygame.K_d],
                }
            else:
                # TODO: get game input from AI
                game_input = {
                    "jump": False,
                    "left": False,
                    "right": False,
                }
                # randomly select an action or none with equal probability
                action = np.random.choice([0, 1, 2, None], p=[0.10, 0.25, 0.25, 0.40])
                if action == 0:
                    game_input["jump"] = True
                elif action == 1:
                    game_input["left"] = True
                elif action == 2:
                    game_input["right"] = True

            self.update(game_input)

            if self.terrain.player_intersects_terrain(self.player):
                running = False

            if self.render:
                self.draw()
                pygame.display.flip()
                self.dt = self.clock.tick(60) / 1000
            else:
                self.dt = 1 / 30

            self.iteration += 1
            if not self.render and self.iteration % 10000 == 0:
                end_time = datetime.datetime.now().timestamp()
                print(f"FPS: {1000 / (end_time - start_time)}")
                start_time = end_time

        pygame.quit()

    def update(self, game_input: dict):
        update_jump_cooldown(self.player, self.dt)
        update_velocity(game_input, self.player, self.terrain, self.dt)
        update_position(self.player, self.dt)
        process_collisions(self.player, self.terrain)
        update_terrain_offset(self.player, self.terrain)

        if self.terrain.offset >= self.screen_dimensions[0]:
            self.terrain.offset -= self.screen_dimensions[0]
            self.generate_terrain()

        update_terrain_offset(self.player, self.terrain)
        update_platform_status(self.player, self.terrain)

    def draw(self):
        self.screen.blit(self.background, (0, 0))

        self.terrain.draw(self.screen)
        self.player.draw(self.screen)

        # draw framerate in top left corner
        pygame.draw.rect(self.screen, "black", (0, 0, 30, 25))
        font = pygame.font.SysFont("Arial", 20)
        text = font.render(str(int(self.clock.get_fps())), True, "white")
        self.screen.blit(text, (0, 0))

        # cast a line from the player in every direction in increments of 20 degrees
        if self.debug_raycasting:
            debug_raycasting(self.screen, self.player, self.terrain, font)

    def produce_observations(self):
        observations = {
            "player_pos": np.array([self.player.pos.x, self.player.pos.y]),
            "player_vel": np.array([self.player.vel.x, self.player.vel.y]),
            "fuel": self.player.fuel,
        }

        ray_distances = np.array([])

        for i in range(0, 360, 10):
            unit_v = pygame.Vector2(0, -1000).rotate(i) + self.player.pos
            # draw the line
            ray = shapely.LineString([self.player.pos, unit_v])
            intersection = self.terrain.terrain_intersects_shape(ray)
            if intersection is not False:
                # if it's LineString, get first point
                # elif it's MultiLineString, get first point of first line

                if isinstance(intersection, shapely.geometry.MultiLineString):
                    intersection = intersection.geoms[0].coords[0]
                elif isinstance(intersection, shapely.geometry.LineString):
                    intersection = intersection.coords[0]

                distance_to_intersection = self.player.pos.distance_to(intersection)
                ray_distances = np.append(ray_distances, distance_to_intersection)
            else:
                ray_distances = np.append(ray_distances, 1000)

        observations["distances"] = ray_distances
        observations["prev_platform"] = np.array(
            [
                self.terrain.prev_player_platform.pos.x,
                self.terrain.prev_player_platform.pos.y,
            ]
        )
        observations["next_platform"] = np.array(
            [
                self.terrain.next_player_platform.pos.x,
                self.terrain.next_player_platform.pos.y,
            ]
        )
        return observations
