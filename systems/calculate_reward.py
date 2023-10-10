import pygame

from entities.platform import Platform
from entities.player import Player
from entities.terrain import Terrain


def calculate_reward(player: Player, terrain: Terrain, platform: Platform | None):
    # if the player touched a platform, give a reward
    if platform:
        player.score = 10
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
