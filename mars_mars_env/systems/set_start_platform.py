import pygame

from mars_mars_env.entities.player import Player
from mars_mars_env.entities.terrain import Terrain


def set_start_platform(player: Player, terrain: Terrain):
    start_platform = terrain.platforms[26]
    start_platform.visited = True

    terrain.prev_player_platform = start_platform
    next_platform = filter(
        lambda p: p.pos.x > start_platform.pos.x, terrain.platforms.values()
    )
    next_platform = min(next_platform, key=lambda p: p.pos.x)
    terrain.next_player_platform = next_platform

    player.pos = start_platform.get_center() - pygame.Vector2(
        0, start_platform.platform_height / 2 + player.radius
    )
    player.prev_pos = player.pos.copy()
