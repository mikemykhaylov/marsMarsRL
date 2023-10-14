from gymnasium.envs.registration import register

from .env import MarsMarsEnv

register(
    id="MarsMars-v0",
    entry_point="mars_mars_env.gym:MarsMarsEnv",
)

__all__ = ["MarsMarsEnv"]
