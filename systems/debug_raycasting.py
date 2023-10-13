import pygame
import shapely

from entities.player import Player
from entities.terrain import Terrain
from systems.generate_intersections import generate_intersections


def debug_raycasting(
    screen: pygame.Surface, player: Player, terrain: Terrain, font: pygame.font.Font
):
    intersections, _ = generate_intersections(player, terrain)

    for i in range(0, 360, 10):
        unit_v = pygame.Vector2(0, -1000).rotate(i) + player.pos
        # draw the line
        pygame.draw.aaline(screen, "white", player.pos, unit_v, 1)

        intersection = intersections[i // 10]
        if intersection != player.pos:
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
