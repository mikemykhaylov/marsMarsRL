import pygame
import shapely

from entities.player import Player
from entities.terrain import Terrain


def debug_raycasting(
    screen: pygame.Surface, player: Player, terrain: Terrain, font: pygame.font.Font
):
    for i in range(0, 360, 10):
        unit_v = pygame.Vector2(0, -1000).rotate(i) + player.pos
        # draw the line
        pygame.draw.aaline(screen, "white", player.pos, unit_v, 1)
        ray = shapely.LineString([player.pos, unit_v])
        intersection = terrain.terrain_intersects_shape(ray)
        if intersection is not False:
            # if it's LineString, get first point
            # elif it's MultiLineString, get first point of first line

            if isinstance(intersection, shapely.geometry.MultiLineString):
                intersection = intersection.geoms[0].coords[0]
            elif isinstance(intersection, shapely.geometry.LineString):
                intersection = intersection.coords[0]

            pygame.draw.circle(screen, "red", intersection, 5)

            # at the midpoint of the ray, put text with the distance
            # from the player to the intersection
            midpoint = (
                shapely.LineString([player.pos, intersection])
                .interpolate(0.5, normalized=True)
                .coords[0]
            )
            # distance from player to intersection
            distance = player.pos.distance_to(intersection)
            text = font.render(str(int(distance)), True, "white")
            screen.blit(text, midpoint)
