import datetime

import numpy as np
import pygame

from mars_mars_env.systems import (
    bootstrap_terrain,
    debug_raycasting,
    generate_intersections,
    generate_terrain_factory,
    process_collisions,
    set_start_platform,
    update_jump_cooldown,
    update_platform_status,
    update_position,
    update_terrain_offset,
    update_velocity,
)

from .player import Player
from .terrain import Terrain


class Scene:
    def __init__(
        self,
        render=True,
        interactive=True,
        debug_raycasting=False,
        screen_dimensions=(1440, 900),
        terrain_seed=None,
        verbose=False,
    ):
        self.render = render
        self.interactive = interactive
        self.debug_raycasting = debug_raycasting
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

        if terrain_seed is None:
            terrain_seed = np.random.randint(0, 1000000)
            if verbose:
                print(f"Terrain seed not set, using random seed {terrain_seed}")
        elif verbose:
            print(f"Using terrain seed {terrain_seed}")

        self.player = Player(20, "#3D93AF", *self.screen_dimensions)
        self.terrain = Terrain(200, terrain_seed, *self.screen_dimensions)
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

            if not self.render and self.iteration % 1000 == 0:
                end_time = datetime.datetime.now().timestamp()
                print(f"FPS: {1000 / (end_time - start_time)}")
                start_time = end_time

        self.close()

    def close(self):
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

        self.iteration += 1

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

        pygame.display.flip()
        self.dt = self.clock.tick(60) / 1000

    def produce_observations(self):
        observations = {
            "player_pos": np.array([self.player.pos.x, self.player.pos.y]),
            "player_vel": np.array([self.player.vel.x, self.player.vel.y]),
            "fuel": self.player.fuel,
        }

        _, distances = generate_intersections(self.player, self.terrain)

        observations["distances"] = distances
        observations["prev_platform"] = np.array(
            self.terrain.prev_player_platform.get_center()
            - pygame.Vector2(0, self.terrain.prev_player_platform.platform_height / 2)
        )
        observations["next_platform"] = np.array(
            self.terrain.next_player_platform.get_center()
            - pygame.Vector2(0, self.terrain.next_player_platform.platform_height / 2)
        )
        return observations
