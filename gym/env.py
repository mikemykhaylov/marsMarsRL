import math
from typing import Any

import gymnasium as gym
import numpy as np
from gymnasium import spaces
from gymnasium.core import ObsType

from entities import Scene


class MarsMarsEnv(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": 60}

    def __init__(self, render_mode=None, screen_dimensions=(1440, 900)):
        self.default_screen_dimensions = screen_dimensions

        self.observation_space = spaces.Dict(
            {
                "player_pos": spaces.Tuple(
                    (
                        spaces.Box(low=0, high=screen_dimensions[0], dtype=np.float32),
                        spaces.Box(low=0, high=screen_dimensions[1], dtype=np.float32),
                    )
                ),
                "player_vel": spaces.Tuple(
                    (
                        spaces.Box(low=-math.inf, high=math.inf, dtype=np.float32),
                        spaces.Box(low=-50, high=50, dtype=np.float32),
                    )
                ),
                "fuel": spaces.Discrete(1001),
                "distances": spaces.Box(
                    low=0, high=1000, shape=(36,), dtype=np.float32
                ),
                "prev_platform": spaces.Tuple(
                    (
                        spaces.Box(low=0, high=screen_dimensions[0], dtype=np.float32),
                        spaces.Box(low=0, high=screen_dimensions[1], dtype=np.float32),
                    )
                ),
                "next_platform": spaces.Tuple(
                    (
                        spaces.Box(low=0, high=screen_dimensions[0], dtype=np.float32),
                        spaces.Box(low=0, high=screen_dimensions[1], dtype=np.float32),
                    )
                ),
            }
        )

        # jump, left, right, no-op
        self.action_space = spaces.Discrete(4)

        self._action_to_key = {0: "jump", 1: "left", 2: "right"}

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        self.scene: Scene | None = None
        self.create_scene()

    def create_scene(self):
        self.scene = Scene(
            render=self.render_mode is not None,
            interactive=False,
            screen_dimensions=self.default_screen_dimensions,
            debug_raycasting=self.render_mode is not None,
        )

        # we simulate at 60 fps, so set the timestep to 1/60
        self.scene.dt = 1 / 60

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> tuple[ObsType, dict[str, Any]]:
        super().reset(seed=seed, options=options)

        self.close()
        self.create_scene()

        observation = self._get_obs()
        info = self._get_info()

        return observation, info

    def step(self, action: int) -> tuple[ObsType, float, bool, bool, dict[str, Any]]:
        game_input = {
            "jump": False,
            "left": False,
            "right": False,
        }
        if action is not None and action in self._action_to_key:
            game_input[self._action_to_key[action]] = True

        self.scene.update(game_input)

        observation = self._get_obs()
        reward = self._get_reward()
        terminated = self._get_terminated()
        truncated = self._get_truncated()
        info = self._get_info()

        self.render()

        return observation, reward, terminated, truncated, info

    def render(self):
        if self.render_mode == "human":
            self.scene.draw()

    def close(self):
        self.scene.close()

    def _get_obs(self):
        return self.scene.produce_observations()

    def _get_reward(self):
        return self.scene.player.score

    def _get_terminated(self):
        return self.scene.terrain.player_intersects_terrain(self.scene.player)

    def _get_truncated(self):
        return self.scene.iteration >= 10000

    def _get_info(self):
        return {"terrain_seed": self.scene.terrain.noise_generator.get_seed()}
