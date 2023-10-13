from entities.player import Player
from entities.terrain import Terrain
from systems.update_terrain_polygon import update_terrain_polygon


def update_terrain_offset(player: Player, terrain: Terrain):
    delta_x = player.pos.x - player.prev_pos.x

    if delta_x > 0 and player.pos.x > terrain.scene_width / 4:
        terrain.offset += delta_x
        player.pos.x = player.prev_pos.x
        update_terrain_polygon(terrain, delta_x)
