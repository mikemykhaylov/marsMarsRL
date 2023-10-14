from gymnasium.envs.registration import register

from .env import MarsMarsEnv

register(
    id="MarsMars-v0",
    entry_point="env:MarsMarsEnv",
)

__all__ = ["MarsMarsEnv"]
