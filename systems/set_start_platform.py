import pygame

from entities.player import Player
from entities.terrain import Terrain


def set_start_platform(player: Player, terrain: Terrain):
    start_platform = terrain.platforms[26]
    player.pos = start_platform.get_center() - pygame.Vector2(
        0, start_platform.platform_height / 2 + player.radius
    )
    player.prev_pos = player.pos.copy()
