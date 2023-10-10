from entities.player import Player
from entities.terrain import Terrain


def update_platform_status(player: Player, terrain: Terrain):
    terminal_velocity = 5

    for platform in terrain.platforms.values():
        platform.player_too_fast = player.vel.length() > terminal_velocity
