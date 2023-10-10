import datetime

import numpy as np
import pygame
import shapely

from entities.player import Player
from entities.terrain import Terrain
from systems import (
    set_start_platform,
    generate_terrain_factory,
    update_jump_cooldown,
    update_velocity,
    update_position,
    process_collisions,
    calculate_reward,
    update_terrain_offset,
    bootstrap_terrain,
    update_platform_status,
    produce_observations,
)


class Scene:
    def __init__(self, interactive=True, visible_rays=False):
        self.interactive = interactive
        self.visible_rays = visible_rays

        if self.interactive:
            pygame.init()
            flags = pygame.DOUBLEBUF | pygame.SCALED | pygame.RESIZABLE
            self.screen = pygame.display.set_mode((1440, 900), flags, vsync=1)
            self.clock = pygame.time.Clock()
            self.background = pygame.image.load("assets/background.jpg")
        self.dt = 0

        self.screen_dimensions = self.screen.get_size() if interactive else (1440, 900)
        self.player = Player(20, "#3D93AF", *self.screen_dimensions)
        self.terrain = Terrain(200, *self.screen_dimensions)
        self.iteration = 0

        # systems ran once
        random_seed = np.random.randint(0, 100000)
        print(f"Random seed: {random_seed}")
        self.generate_terrain = generate_terrain_factory(self.terrain, random_seed)
        bootstrap_terrain(self.terrain)
        set_start_platform(self.player, self.terrain)

    def run(self):
        start_time = datetime.datetime.now().timestamp()

        running = True
        while running:
            if self.interactive:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

            if self.interactive:
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
                action = np.random.choice([0, 1, 2, None], p=[0.5, 0.20, 0.20, 0.10])
                if action == 0:
                    game_input["jump"] = True
                elif action == 1:
                    game_input["left"] = True
                elif action == 2:
                    game_input["right"] = True

            self.update(game_input)

            if self.interactive:
                self.draw()
                pygame.display.flip()
                self.dt = self.clock.tick(60) / 1000
            else:
                self.dt = 1 / 30

            if not self.interactive:
                end_time = datetime.datetime.now().timestamp()
                self.iteration += 1
                if self.iteration % 1000 == 0:
                    print(f"FPS: {1000 / (end_time - start_time)}")
                    start_time = end_time

        pygame.quit()

    def update(self, game_input: dict):
        update_jump_cooldown(self.player, self.dt)
        update_velocity(game_input, self.player, self.terrain, self.dt)
        update_position(self.player, self.dt)
        platform = process_collisions(self.player, self.terrain)
        calculate_reward(self.player, self.terrain, platform)
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
        if self.visible_rays:
            for i in range(45, 225, 10):
                unit_v = pygame.Vector2(0, -1000).rotate(i) + self.player.pos
                # draw the line
                pygame.draw.aaline(self.screen, "white", self.player.pos, unit_v, 1)
                ray = shapely.LineString([self.player.pos, unit_v])
                intersection = self.terrain.terrain_intersects_shape(ray)
                if intersection is not False:
                    # if it's LineString, get first point
                    # elif it's MultiLineString, get first point of first line

                    if isinstance(intersection, shapely.geometry.MultiLineString):
                        intersection = intersection.geoms[0].coords[0]
                    elif isinstance(intersection, shapely.geometry.LineString):
                        intersection = intersection.coords[0]

                    pygame.draw.circle(self.screen, "red", intersection, 5)

                    # at the midpoint of the ray, put text with the distance from the player to the intersection
                    midpoint = (
                        shapely.LineString([self.player.pos, intersection])
                        .interpolate(0.5, normalized=True)
                        .coords[0]
                    )
                    # distance from player to intersection
                    distance = self.player.pos.distance_to(intersection)
                    text = font.render(str(int(distance)), True, "white")
                    self.screen.blit(text, midpoint)
