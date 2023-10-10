import pygame

from entities.player import Player
from entities.terrain import Terrain


def process_collisions(player: Player, terrain: Terrain):
    # if player intersects terrain, change color to red
    if terrain.player_intersects_terrain(player):
        player.color = "red"
    else:
        player.color = "#3D93AF"

    platform = terrain.player_intersects_platform(player)
    if not platform:
        return None

    player.vel.x = 0
    player.vel.y = 0
    player.pos = platform.get_center() - pygame.Vector2(
        0, platform.platform_height / 2 + player.radius
    )
    player.fuel = min(1000, player.fuel + 20)

    if not platform.visited:
        platform.visited = True

        terrain.prev_player_platform = platform
        # next platform is the platform to the right of the current platform
        # meaning with the next smallest x value
        next_platform = filter(
            lambda p: p.pos.x > platform.pos.x, terrain.platforms.values()
        )
        next_platform = min(next_platform, key=lambda p: p.pos.x)
        terrain.next_player_platform = next_platform
        return platform
    return None
