from mars_mars_env.entities.player import Player


def update_jump_cooldown(player: Player, dt):
    player.jump_cooldown = max(0, player.jump_cooldown - 60 * dt)
