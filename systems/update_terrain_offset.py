from entities.player import Player
from entities.terrain import Terrain


def update_terrain_offset(player: Player, terrain: Terrain):
    delta_x = player.pos.x - player.prev_pos.x

    if delta_x > 0 and player.pos.x > terrain.scene_width / 4:
        terrain.offset += delta_x
        player.pos.x = player.prev_pos.x
