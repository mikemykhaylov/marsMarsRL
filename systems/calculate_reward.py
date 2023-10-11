import pygame

from entities.platform import Platform
from entities.player import Player
from entities.terrain import Terrain


def calculate_reward(player: Player, terrain: Terrain, platform: Platform | None):
    # if the player touched the landscape, game over with very negative reward
    if terrain.player_intersects_terrain(player):
        player.score = -100
    # if the player touched a platform, give a reward
    elif platform:
        # if player is moving too fast, they crash and get a negative reward
        if player.vel.length() > 5:
            player.score = -5 - player.vel.length()
        # else, give a positive reward, inversely proportional to the velocity
        else:
            velocity_bonus = 5 - player.vel.length()
            player.score = 10 + velocity_bonus
    # else, scale the distance between the previous and next platform to 0-1
    # then calculate the reward as the player gets closer to the next platform
    else:
        platform_to_platform = (
            terrain.next_player_platform.pos - terrain.prev_player_platform.pos
        )
        player_to_platform = (
            terrain.next_player_platform.get_center()
            - pygame.Vector2(0, terrain.next_player_platform.platform_height / 2)
        ) - (player.pos + pygame.Vector2(0, player.radius))

        distance = (
            platform_to_platform.length() - player_to_platform.length()
        ) / platform_to_platform.length()

        player.score = distance
