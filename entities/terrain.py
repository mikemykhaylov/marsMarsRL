import numpy as np
import pygame
import shapely


class Terrain:
    def __init__(self, scaling, scene_width, scene_height):
        self.scene_width = scene_width
        self.scene_height = scene_height

        self.color = "#5F1514"

        self.base_noise_scale = 5
        self.points_per_screen = 100
        self.scaling = scaling
        self.offset = 0

        self.x = np.array([])
        self.y = np.array([])

        self.platforms = {}
        self.last_platform = 26
        self.screen_offset = 1

        self.prev_player_platform = None
        self.next_player_platform = None

    def compute_points(self):
        scaled_x = self.x / self.x[-1] * self.scene_width * 2 - self.offset
        scaled_y = self.y * self.scaling + self.scene_height - 300
        scaled_y = np.clip(scaled_y, 0, self.scene_height - 1)

        points = np.array([scaled_x, scaled_y]).T
        # add two bottom corners to make a closed polygon
        bottom_left = np.array([[points[0][0], self.scene_height]])
        bottom_right = np.array([[points[-1][0], self.scene_height]])

        return np.concatenate((bottom_left, points, bottom_right))

    def draw(self, screen):
        points = self.compute_points()
        pygame.draw.polygon(screen, self.color, points)
        for point, platform in self.platforms.items():
            # draw point
            platform.pos[0] = points[point][0] - platform.platform_width / 2
            platform.draw(screen)

    def player_intersects_terrain(self, player):
        points = self.compute_points()

        terrain_polygon = shapely.geometry.Polygon(points)
        player_circle = shapely.geometry.Point(player.pos).buffer(player.radius)

        return terrain_polygon.intersects(player_circle)

    def player_intersects_platform(self, player):
        for platform in self.platforms.values():
            if platform.intersects_player(player):
                return platform
        return False

    def terrain_intersects_shape(self, shape):
        points = self.compute_points()
        terrain_polygon = shapely.geometry.Polygon(points)

        intersection = terrain_polygon.intersection(shape)
        if intersection.is_empty:
            return False
        return intersection
