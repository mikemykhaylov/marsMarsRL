import numpy as np
import pygame
import shapely

from entities.player import Player
from entities.terrain import Terrain


def produce_observations(player: Player, terrain: Terrain):
    observations = {
        "player_pos": np.array([player.pos.x, player.pos.y]),
        "player_vel": np.array([player.vel.x, player.vel.y]),
        "fuel": player.fuel,
    }

    ray_distances = np.array([])

    for i in range(0, 360, 10):
        unit_v = pygame.Vector2(0, -1000).rotate(i) + player.pos
        # draw the line
        ray = shapely.LineString([player.pos, unit_v])
        intersection = terrain.terrain_intersects_shape(ray)
        if intersection is not False:
            # if it's LineString, get first point
            # elif it's MultiLineString, get first point of first line

            if isinstance(intersection, shapely.geometry.MultiLineString):
                intersection = intersection.geoms[0].coords[0]
            elif isinstance(intersection, shapely.geometry.LineString):
                intersection = intersection.coords[0]

            distance_to_intersection = player.pos.distance_to(intersection)
            ray_distances = np.append(ray_distances, distance_to_intersection)
        else:
            ray_distances = np.append(ray_distances, 1000)

    observations["distances"] = ray_distances
    observations["next_platform"] = np.array(
        [terrain.next_player_platform.pos.x, terrain.next_player_platform.pos.y]
    )
    return observations
