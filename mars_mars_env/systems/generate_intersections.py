import pygame
import shapely

from mars_mars_env.entities.player import Player
from mars_mars_env.entities.terrain import Terrain


def generate_intersections(player: Player, terrain: Terrain):
    intersections = []
    distances = []

    for i in range(0, 360, 10):
        unit_v = pygame.Vector2(0, -1000).rotate(i) + player.pos
        # draw the line
        ray = shapely.LineString([player.pos, unit_v])
        intersection = terrain.terrain_intersects_shape(ray)
        if intersection is not False:
            # if it's LineString, get first point
            # elif it's MultiLineString, get first point of first line

            if isinstance(intersection, shapely.geometry.Point):
                intersection = intersection.coords[0]
            elif isinstance(intersection, shapely.geometry.MultiPoint):
                # find the closest point to the player
                intersection = min(
                    intersection.geoms,
                    key=lambda p: player.pos.distance_to(p.coords[0]),
                ).coords[0]
            elif isinstance(intersection, shapely.geometry.MultiLineString):
                intersection = intersection.geoms[0].coords[0]
            elif isinstance(intersection, shapely.geometry.LineString):
                intersection = intersection.coords[0]

            intersections.append(intersection)
            distances.append(player.pos.distance_to(intersection))
        else:
            intersections.append(player.pos)
            distances.append(1000)

    return intersections, distances
