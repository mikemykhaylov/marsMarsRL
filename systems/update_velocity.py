import numpy as np

from entities.player import Player
from entities.terrain import Terrain


def update_velocity(game_input: dict, player: Player, terrain: Terrain, dt: float):
    fuel_consumption_per_second = 500 * dt
    sideways_acceleration = 5 * dt
    full_upward_acceleration = 14 * dt
    gravity_acceleration = 7.5 * dt
    atmospheric_drag = 0.05 + 0.01 * player.vel.x**2

    launch_up_velocity = 8.33
    launch_sideways_velocity = 1.66

    if game_input["jump"]:
        # jump if on ground and fuel full
        if terrain.player_intersects_platform(player) and player.fuel == 1000:
            player.vel.y -= launch_up_velocity
            player.vel.x += launch_sideways_velocity
            player.jump_cooldown = 10
        elif (
            not terrain.player_intersects_platform(player)
            and player.jump_cooldown == 0
            and player.fuel >= 8.33
        ):
            player.fuel -= fuel_consumption_per_second
            player.vel.y -= full_upward_acceleration

    # if a or d were also pressed, add some horizontal velocity
    if (
        game_input["left"]
        and not terrain.player_intersects_platform(player)
        and player.fuel >= 1
    ):
        player.fuel -= fuel_consumption_per_second
        player.vel.x -= sideways_acceleration
        player.vel.y -= full_upward_acceleration / 2
    if (
        game_input["right"]
        and not terrain.player_intersects_platform(player)
        and player.fuel >= 1
    ):
        player.fuel -= fuel_consumption_per_second
        player.vel.x += sideways_acceleration
        player.vel.y -= full_upward_acceleration / 2

    # take gravity into account if not on ground
    if not terrain.player_intersects_platform(player):
        player.vel.y += gravity_acceleration

    # take air resistance into account for horizontal velocity
    player.vel.x = max(0.0, abs(player.vel.x) - atmospheric_drag * dt) * (
        1 if player.vel.x > 0 else -1
    )

    # clamp horizontal velocity
    player.vel.x = np.clip(player.vel.x, -50, 50)
