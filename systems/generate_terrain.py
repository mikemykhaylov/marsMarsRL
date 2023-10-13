import numpy as np
import shapely

from entities.platform import Platform
from entities.terrain import Terrain
from systems.generate_polygon import generate_polygon


def generate_multioctave_noise(terrain: Terrain):
    octaves = 4
    noise = np.array([0.0] * terrain.points_per_screen)

    for i in range(octaves):
        noise += (
            generate_noise(
                terrain,
                terrain.base_noise_scale * 2**i,
                terrain.points_per_screen,
                terrain.screen_offset,
            )
            / 2**i
        )
    return noise


def generate_noise(terrain, noise_scale, points_per_screen, screen_offset):
    xs = np.linspace(
        noise_scale * screen_offset,
        noise_scale * (screen_offset + 1),
        points_per_screen + 1,
    )
    xs = xs[:-1]
    return terrain.noise_generator.noise2array(xs, np.array([0])).reshape(-1)


def generate_platforms(terrain, start_point):
    i = start_point
    points = terrain.compute_points()
    platforms = {}

    last_platform = terrain.last_platform

    while i < len(points):
        platform = Platform(0, 0)
        platform.set_pos_from_center(points[i])

        while True:
            polygon_points = platform.get_edges()
            top = shapely.LineString(polygon_points[:2])
            if not terrain.terrain_intersects_shape(top):
                break
            platform.pos[1] -= 1

        platforms[i] = platform
        last_platform = i
        # skips 25 to 50 points
        i += np.random.randint(35, 50)

    return platforms, last_platform


def bootstrap_terrain(terrain: Terrain):
    terrain.screen_offset = 0
    terrain.y = np.append(terrain.y, generate_multioctave_noise(terrain))
    terrain.screen_offset = 1
    terrain.y = np.append(terrain.y, generate_multioctave_noise(terrain))

    generate_polygon(terrain)

    platforms, last_platform = generate_platforms(terrain, 26)
    terrain.platforms.update(platforms)
    terrain.last_platform = last_platform


def generate_terrain_factory(terrain: Terrain):
    terrain.x = np.linspace(0, 2, terrain.points_per_screen * 2 + 1)
    terrain.x = terrain.x[:-1]
    terrain.y = np.array([])

    def internal():
        terrain.screen_offset += 1
        terrain.y = np.append(terrain.y, generate_multioctave_noise(terrain))
        terrain.y = terrain.y[terrain.points_per_screen :]

        generate_polygon(terrain)

        # Change the x coordinates to be the next screen
        terrain.last_platform -= terrain.points_per_screen

        terrain.platforms = {
            key - terrain.points_per_screen: platform
            for key, platform in terrain.platforms.items()
            if key >= terrain.points_per_screen
        }

        start_point = terrain.last_platform + np.random.randint(35, 50)
        platforms, last_platform = generate_platforms(terrain, start_point)
        terrain.platforms.update(platforms)
        terrain.last_platform = last_platform

    return internal
