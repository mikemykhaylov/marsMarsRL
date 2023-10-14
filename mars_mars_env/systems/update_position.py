import numpy as np

from mars_mars_env.entities.player import Player


def update_position(player: Player, dt: float):
    player.prev_pos = player.pos.copy()

    # update position
    player.pos += player.vel * dt * 60

    # clamp x position to screen bounds
    player.pos.x = np.clip(
        player.pos.x, player.radius, player.scene_width - player.radius
    )

    # bounce off walls
    if (
        player.pos.x == player.radius
        or player.pos.x == player.scene_width - player.radius
    ):
        player.vel.x = -player.vel.x * 0.3
